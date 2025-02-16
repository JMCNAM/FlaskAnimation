const paramPresets = {
    "free_fall": ["g"],
    "fluid_resistance": ["g", "k", "m"],
    "sho": ["k", "m"],
    "dho": ["k", "b", "m", "Fo", "Wo"],
    "ddho": ["k", "b", "m", "Fo", "Wo"],
    "pendulum": ["g", "L"],
    "complex_pendulum": ["g", "L", "m", "damping", "driving_force", "driving_freq"],
    "mass_spring_damper": ["m", "k", "c", "F0", "omega"]
};

// Update parameter selection based on chosen equation
function updateAnimationParameters() {
    const equation = document.getElementById("equation").value;
    const paramDropdown = document.getElementById("varying-param");
    paramDropdown.innerHTML = "";

    paramPresets[equation].forEach(param => {
        let option = document.createElement("option");
        option.value = param;
        option.textContent = param;
        paramDropdown.appendChild(option);
    });
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

    let payload = { 
        equation: equation,
        method: method,
        t_total: t_total,
        N: N,
        params: {
            varying_param: varyingParam,
            min: minVal,
            max: maxVal,
            step: step
        }
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
            alert("Animation Error BTN: " + data.error);
        } else {
            document.getElementById("animation-preview").src = data.animation_url;
        }
    })
    .catch(error => console.error("Fetch Error:", error));
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
