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

// Update parameter selection based on chosen equation
function updateAnimationParameters() {
    const equation = document.getElementById("equation").value;
    const paramDropdown = document.getElementById("varying-param");
    paramDropdown.innerHTML = "";

    Object.keys(paramPresets[equation]).forEach(param => {
        let option = document.createElement("option");
        option.value = param;
        option.textContent = param;
        paramDropdown.appendChild(option);
    });

    updateNonVaryingParameters();
}

// Update non-varying parameters based on selected varying parameter
function updateNonVaryingParameters() {
    const equation = document.getElementById("equation").value;
    const varyingParam = document.getElementById("varying-param").value;
    const nonVaryingParamsContainer = document.getElementById("non-varying-params-container");
    nonVaryingParamsContainer.innerHTML = "";

    Object.keys(paramPresets[equation]).forEach(param => {
        if (param !== varyingParam) {
            let paramDiv = document.createElement("div");
            paramDiv.classList.add("mb-3");
            paramDiv.innerHTML = `
                <label for="param-${param}" class="form-label">${param}:</label>
                <input type="number" id="param-${param}" class="form-control" value="${paramPresets[equation][param]}">
            `;
            nonVaryingParamsContainer.appendChild(paramDiv);
        }
    });

    // Set default values for min, max, and step
    document.getElementById("param-min").value = paramPresets[equation][varyingParam];
    document.getElementById("param-max").value = paramPresets[equation][varyingParam] * 2;
    document.getElementById("param-step").value = Math.abs(paramPresets[equation][varyingParam] / 10);
}

// Generate Animation Request
document.getElementById("generate-animation-btn").addEventListener("click", function() {
    let equation = document.getElementById("equation").value;
    let method = document.getElementById("method").value;
    let t_total = parseFloat(document.getElementById("t_total").value);
    let N = parseInt(document.getElementById("N").value);
    let varyingParam = document.getElementById("varying-param").value;
    let minVal = parseFloat(document.getElementById("param-min").value);
    let maxVal = parseFloat(document.getElementById("param-max").value);
    let step = parseFloat(document.getElementById("param-step").value);

    // Ensure step value is greater than 0
    if (step <= 0) {
        alert("Step value must be greater than 0");
        return;
    }

    let params = {};
    Object.keys(paramPresets[equation]).forEach(param => {
        if (param !== varyingParam) {
            params[param] = parseFloat(document.getElementById(`param-${param}`).value);
        }
    });

    let payload = { 
        equation: equation,
        method: method,
        t_total: t_total,
        N: N,
        params: {
            varying_param: varyingParam,
            min: minVal,
            max: maxVal,
            step: step,
            ...params
        }
    };

    console.log("Sending Animation Request:", payload);

    // Show spinner
    document.getElementById("spinner").style.display = "block";

    fetch("/animate/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        // Hide spinner
        document.getElementById("spinner").style.display = "none";

        if (data.error) {
            alert("Animation Error BTN: " + data.error);
        } else {
            const animationPreview = document.getElementById("animation-preview");
            document.getElementById("animation-preview").style.display = "block"; // Show only after generation
            animationPreview.src = "";  // Clear the src to force reload
            animationPreview.src = data.animation_url + "?t=" + Date.now();   // Set the src to the new URL
        }
    })
    .catch(error => {
        // Hide spinner
        document.getElementById("spinner").style.display = "none";
        console.error("Fetch Error:", error);
    });
});

// Replay Animation
document.getElementById("replay-animation-btn").addEventListener("click", function() {
    const animationPreview = document.getElementById("animation-preview");
    const currentSrc = animationPreview.src;
    animationPreview.src = "";  // Clear the src to force reload
    animationPreview.src = currentSrc;  // Set the src back to the current URL
});

// Initialize parameters when the page loads
document.addEventListener("DOMContentLoaded", updateAnimationParameters);
document.getElementById("varying-param").addEventListener("change", updateNonVaryingParameters);
