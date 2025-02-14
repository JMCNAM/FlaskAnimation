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
@app.route("/simulate/", methods=['GET', 'POST'])
def simulate():
    if request.method == 'POST':
        graph_data = simulateData()
        return graph_data  # Return JSON directly, NOT render_template
    
    return render_template("simulate.html", graph_url=None)
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
