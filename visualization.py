from flask import jsonify
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import io
import base64
import simulation
import imageio
import os


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
    print(f"Parameter values: {param_values}")  # Debugging line

    frame_dir = "static/animation_frames"
    os.makedirs(frame_dir, exist_ok=True)  # Ensure directory exists

    frame_paths = []  # Store file paths for imageio
    for frame, param_value in enumerate(param_values):
        print(f"Generating frame {frame}: {equation} - {varying_param} = {param_value}")

        # Merge fixed and varying parameters
        sim_params = {**fixed_params, varying_param: param_value}
        print("Sim Params:", sim_params)  # Debugging line

        # Remove varying_param key from sim_params
        sim_params.pop("varying_param", None)
        sim_params.pop("min", None)
        sim_params.pop("max", None)
        sim_params.pop("step", None)

        config = simulation.SimulationConfig(
            method=simulation.runge_kutta4,
            equation=getattr(simulation, equation),
            params=sim_params,
            x0=0.5,
            v0=0.0,
            t_total=t_total,
            N=N
        )
        print("Simulation Config:", config)  # Debugging line

        time, position, _ = simulation.run_simulation(config)

        # Plot and save frame
        fig, ax = plt.subplots()
        ax.plot(time, position, lw=2)
        ax.set_xlim(0, t_total)
        ax.set_ylim(-2, 2)
        ax.set_title(f"{equation} - {varying_param} = {param_value:.2f}")
        frame_path = os.path.join(frame_dir, f"frame_{frame:03d}.png")
        fig.savefig(frame_path)
        plt.close(fig)  # Close figure to free memory
        frame_paths.append(frame_path)

    # Create GIF from frames
    gif_path = "static/simulation.gif"
    with imageio.get_writer(gif_path, mode="I", duration=0.2) as writer:
        for frame_path in frame_paths:
            image = imageio.imread(frame_path)
            writer.append_data(image)

    # Cleanup: Remove individual frames
    for frame_path in frame_paths:
        os.remove(frame_path)

    return f"/{gif_path}"