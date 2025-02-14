import matplotlib.pyplot as plt
import io
import base64

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
