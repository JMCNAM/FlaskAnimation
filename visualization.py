from flask import jsonify
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import io
import base64
import simulation


def generate_plot(time, position, velocity):
    fig, ax = plt.subplots()
    ax.plot(time, position, label="Position")
    ax.plot(time, velocity, label="Velocity")
    ax.set_xlabel("Time")
    ax.set_ylabel("Value")
    ax.legend()

    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    graph_url = "data:image/png;base64," + base64.b64encode(img.getvalue()).decode()
    plt.close()
    return graph_url

def generate_animation(equation, varying_param, min_val, max_val, step, fixed_params, t_total, N, step_size):
    param_values = np.arange(min_val, max_val + step, step)

    if len(param_values) == 0:
        print("Error: Parameter range produced no values!")
        return jsonify({"error": "Invalid parameter range: No values generated."}), 400

    print(f"Generating animation for {equation} with varying {varying_param}: {min_val} to {max_val} (step {step})")

    fig, ax = plt.subplots()
    line, = ax.plot([], [], lw=2)

    def init():
        ax.set_xlim(0, t_total)
        ax.set_ylim(-2, 2)
        line.set_data([], [])
        return line,

    def update(frame):
        if frame >= len(param_values):
            print(f"Error: Frame index {frame} is out of range (max {len(param_values)-1})")
            return line,

        param_value = param_values[frame]
        print(f"Frame {frame}: {equation} - {varying_param} = {param_value}")

        # Merge fixed and varying parameters
        sim_params = {**fixed_params, varying_param: param_value}

        config = simulation.SimulationConfig(
            method=simulation.runge_kutta4,
            equation=getattr(simulation, equation),
            params=sim_params,
            x0=0.5,
            v0=0.0,
            t_total=t_total,
            N=N
        )

        time, position, _ = simulation.run_simulation(config)
        line.set_data(time, position)
        ax.set_title(f"{equation} - {varying_param} = {param_value:.2f}")
        return line,

    ani = animation.FuncAnimation(fig, update, frames=len(param_values), init_func=init, blit=False)

    # Save animation
    gif_path = "static/simulation.gif"
    ani.save(gif_path, writer="pillow", fps=5)

    return f"/{gif_path}"