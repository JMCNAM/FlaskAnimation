(function() {
    const paramPresets = {
        "free_fall": { "g": -9.8 },
        "fluid_resistance": { "g": -9.8, "k": 0.1, "m": 1.0 },
        "sho": { "k": 0.1, "m": 1.0 },
        "dho": { "k": 5.0, "b": 0.05, "m": 1.0, "Fo": 10.0, "Wo": 0.2 },
        "ddho": { "k": 5.0, "b": 0.05, "m": 1.0, "Fo": 10.0, "Wo": 0.2 },
        "pendulum": { "g": -9.8, "L": 1.0 },
        "complex_pendulum": { "g": 9.8, "L": 1.0, "m": 1.0, "damping": 0.1, "driving_force": 0.5, "driving_freq": 1.0 },
        "mass_spring_damper": { "m": 1.0, "k": 1.0, "c": 0.2, "F0": 0.0, "omega": 0.0 }
    };

    function updateParameters() {
        const equation = document.getElementById("equation")?.value;
        const container = document.getElementById("parameters-container");
        if(container)
            container.innerHTML = "";

        const params = paramPresets[equation] || {};
        let rowDiv = null;
        let count = 0;

        for (const key in params) {
            if (count % 2 === 0) {
                rowDiv = document.createElement("div");
                rowDiv.classList.add("row", "mb-2");
                if (container)
                    container.appendChild(rowDiv);
            }

            const colDiv = document.createElement("div");
            colDiv.classList.add("col");
            colDiv.innerHTML = `
                <label class='form-label'>${key}:</label>
                <input type='number' class='form-control' id='${key}' value='${params[key]}' step='0.1'>
            `;

            rowDiv.appendChild(colDiv);
            count++;
        }
    }

    document.addEventListener("DOMContentLoaded", updateParameters);

    const simulateBtn = document.getElementById("simulate-btn");
    if (simulateBtn) {
        simulateBtn.addEventListener("click", function() {
            const equation = document.getElementById("equation").value;
            const params = paramPresets[equation];

            const payload = {
                method: document.getElementById("method").value,
                equation: equation,
                x0: parseFloat(document.getElementById("x0").value),
                v0: parseFloat(document.getElementById("v0").value),
                t_total: parseFloat(document.getElementById("t_total").value),  // ✅ Ensure t_total is included
                N: parseInt(document.getElementById("N").value),  // ✅ Ensure N steps is included
                params: {}
            };

            for (const key in params) {
                const inputElement = document.getElementById(key);
                if (inputElement) {
                    payload.params[key] = parseFloat(inputElement.value);
                }
            }

            fetch("/simulate/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert("Simulation Error: " + data.error);
                } else {
                    document.getElementById("simulation-graph").src = data.graph_url;
                }
            })
            .catch(error => console.error("Fetch Error:", error));
        });
    }

    const animateBtn = document.getElementById("animate-btn");
    if (animateBtn) {
        animateBtn.addEventListener("click", function() {
            const equation = document.getElementById("equation").value;
            const params = {};

            for (const key in paramPresets[equation]) {
                params[key] = {
                    min: parseFloat(document.getElementById(`${key}-min`).value),
                    max: parseFloat(document.getElementById(`${key}-max`).value),
                    step: parseFloat(document.getElementById(`${key}-step`).value)
                };
            }

            const payload = {
                equation: equation,
                params: params,
                t_total: parseFloat(document.getElementById("t_total").value),  // ✅ Ensure t_total is included
                N: parseInt(document.getElementById("N").value)  // ✅ Ensure N steps is included
            };
            console.log("Sending Animation Request:", payload);
            fetch("/animate/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert("Animation Error SCRIPT: " + data.error);
                } else {
                    document.getElementById("simulation-animation").src = data.animation_url;
                }
            })
            .catch(error => console.error("Fetch Error:", error));
        });
    }

    // Expose updateParameters to the global scope
    window.updateParameters = updateParameters;
})();