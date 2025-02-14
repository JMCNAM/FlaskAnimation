document.getElementById("simulate-btn").addEventListener("click", function() {
    let equation = document.getElementById("equation").value;
    let params = paramPresets[equation];

    let payload = {
        method: document.getElementById("method").value,
        equation: equation,
        x0: parseFloat(document.getElementById("x0").value),
        v0: parseFloat(document.getElementById("v0").value),
        t_total: parseFloat(document.getElementById("t_total").value),
        N: parseInt(document.getElementById("N").value),
        params: {}
    };

    // Extract parameters from UI inputs
    for (const key in params) {
        let inputElement = document.getElementById(key);
        if (inputElement) {
            payload.params[key] = parseFloat(inputElement.value);
        }
    }

    console.log("Payload Sent:", payload);  // Debugging line

    fetch("/simulate/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error("Simulation Error:", data.error);
            alert("Simulation Error: " + data.error);
        } else {
            document.getElementById("simulation-graph").src = data.graph_url;
        }
    })
    .catch(error => console.error("Fetch Error:", error));
});