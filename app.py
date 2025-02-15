import re
from datetime import datetime
import io

from flask import Flask
from flask import render_template, request, jsonify
import simulation
import visualization

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/simulate/", methods=['GET', 'POST'])
def simulate():
    if request.method == 'POST':
        graph_data = simulateData()
        return graph_data  # Return JSON directly, NOT render_template
    
    return render_template("simulate.html", graph_url="")

@app.route("/animate/", methods=['GET', 'POST'])
def animate():
    if request.method == 'POST':
        animation_data = animateData()
        return animation_data  # Return JSON directly, NOT render_template
    
    return render_template("animate.html", animation_data="")


# New functions
@app.route("/about/")
def about():
    return render_template("about.html")

@app.route("/contact/")
def contact():
    return render_template("contact.html")

@app.route("/hello/")

@app.route("/hello/<name>")
def hello_there(name = None):
    return render_template(
        "hello_there.html",
        name=name,
        date=datetime.now()
    )

@app.route("/api/data")
def get_data():
    return app.send_static_file("data.json")

def simulateData():
    data = request.get_json()
    print("Received Data:", data)  # Debugging line

    if not data:
        return jsonify({"error": "Invalid input data"}), 400

    try:
        config = simulation.SimulationConfig(
            method=getattr(simulation, data["method"]),
            equation=getattr(simulation, data["equation"]),
            params=data["params"],
            x0=data["x0"],
            v0=data["v0"],
            t_total=data["t_total"],
            N=data["N"],
        )
        print("Using Equation:", data["equation"])  # Debugging line
        print("Parameters:", data["params"])  # Debugging line
        
        time, position, velocity = simulation.run_simulation(config)
        graph_url = visualization.generate_plot(time, position, velocity)

        return jsonify({"graph_url": graph_url})
    except Exception as e:
        print("Error in simulateData:", str(e))  # Debugging line
        return jsonify({"error": str(e)}), 500

def animateData():
    data = request.get_json()
    print("Received Animation Data:", data)  # Debugging line

    if not data:
        return jsonify({"error": "Invalid input data"}), 400

    try:
        # Validate required fields
        required_fields = ["equation", "params", "t_total", "N"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        equation = data["equation"]
        param_ranges = data["params"]  # Extract nested dictionary
        print("Parameter Ranges:", param_ranges)  # Debugging line
        t_total = float(data["t_total"])
        N = int(data["N"])

        # Validate N to prevent division errors
        if N <= 1:
            return jsonify({"error": "N must be greater than 1"}), 400

        # Compute step_size dynamically
        step_size = t_total / (N - 1)
        print("Animating Equation:", equation)  # Debugging line
        print("Calculated Step Size:", step_size)  # Debugging line

        # Ensure at least one parameter has a valid range
        varying_param = None
        for param, values in param_ranges.items():
            print(f"Checking parameter: {param}, values: {values}")  # Debugging line
            if isinstance(values, dict) and values.get("step", 0) > 0:
                varying_param = param
                break
        print("Varying Parameter:", varying_param)  # Debugging line
        if not varying_param:
            return jsonify({"error": "No parameter with a valid range (step > 0)."}), 400

        print("Param Ranges:", param_ranges)

        # Ensure at least one parameter has a valid range
        varying_param = None
        for param, values in param_ranges.items():
            print(f"Checking parameter: {param}, values: {values}")  # Debugging line
            if isinstance(values, dict) and values.get("step") is not None and values["step"] > 0:
                varying_param = param
                break

        print("Varying Parameter:", varying_param)  # Debugging line

        # ✅ Handle case where no varying parameter is found
        #if not varying_param:
        #    print("Error: No parameter has a valid step size greater than 0.")  # Debugging line
        #    return jsonify({
        #        "error": "No parameter with a valid range (step > 0). Ensure at least one parameter has a step size greater than 0."
        #    }), 400

        print("Param Ranges:", param_ranges)

        # Ensure varying_param exists in param_ranges and is a dictionary
        param_values = param_ranges.get(varying_param, {})

        if not isinstance(param_values, dict):
            return jsonify({
                "error": f"Parameter {varying_param} is not a valid range dictionary. Ensure it contains 'min', 'max', and 'step'."
            }), 400

        # Extract min, max, and step for the varying parameter, ensuring they are valid
        min_val = param_values.get("min", 1)  # Default to 1 if missing
        max_val = param_values.get("max", 10)  # Default to 10 if missing
        step = param_values.get("step", 1)  # Default to 1 if missing

        # Validate parameter ranges
        if min_val >= max_val:
            return jsonify({"error": f"Invalid range for parameter {varying_param}: min >= max"}), 400
        if step <= 0:
            return jsonify({"error": f"Invalid step for parameter {varying_param}: step <= 0"}), 400

        # Construct a flattened params dictionary with constant values
        fixed_params = {
            key: values["min"] if isinstance(values, dict) and "min" in values else values
            for key, values in param_ranges.items()
        }

        print(f"Varying Parameter: {varying_param} from {min_val} to {max_val} with step {step}")
        print(f"Fixed Parameters: {fixed_params}")

        # Pass extracted values to generate_animation
        animation_url = visualization.generate_animation(
            equation, varying_param, min_val, max_val, step, fixed_params, t_total, N, step_size
        )

        return jsonify({"animation_url": animation_url})


    except KeyError as e:
        print("KeyError in animateData:", str(e))  # Debugging line
        return jsonify({"error": f"Missing key in input data: {str(e)}"}), 400
    except ValueError as e:
        print("ValueError in animateData:", str(e))  # Debugging line
        return jsonify({"error": f"Invalid value in input data: {str(e)}"}), 400
    except IndexError as e:
        print("IndexError in animateData:", str(e))  # Debugging line
        return jsonify({"error": f"Index error in input data: {str(e)}"}), 400
    except Exception as e:
        print("Error in animateData:", str(e))  # Debugging line
        return jsonify({"error": str(e)}), 500