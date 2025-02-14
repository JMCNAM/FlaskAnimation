# Define numerical methods

def euler(state, time, dt, derivs):
    """Euler's method for numerical integration."""
    return state + derivs(state, time) * dt


def runge_kutta2(state, time, dt, derivs):
    """Second-order Runge-Kutta method (midpoint method)."""
    k1 = dt * derivs(state, time)
    k2 = dt * derivs(state + k1, time + dt)
    return state + 0.5 * (k1 + k2)


def runge_kutta4(state, time, dt, derivs):
    """Fourth-order Runge-Kutta method."""
    k1 = dt * derivs(state, time)
    k2 = dt * derivs(state + 0.5 * k1, time + 0.5 * dt)
    k3 = dt * derivs(state + 0.5 * k2, time + 0.5 * dt)
    k4 = dt * derivs(state + k3, time + dt)
    return state + (k1 + 2 * k2 + 2 * k3 + k4) / 6.0

def velocity_verlet(state, time, dt, derivs):
    """Corrected Velocity Verlet method for symplectic integration."""
    acc = derivs(state, time)  # Compute acceleration at step n
    state_half = state + np.array([state[1] * dt / 2, 0])  # Half-step velocity update
    new_acc = derivs(state_half, time + dt / 2)  # Compute acceleration at step n+1
    state_next = state_half + np.array([state_half[1] * dt / 2, new_acc[1] * dt])  # Full step update
    return state_next


# Define differential equations

def free_fall(state, time, g=-9.8):
    """Free fall motion under gravity."""
    print(f"free_fall called with g={g}")
    return np.array([state[1], g])

def fluid_resistance(state, time, g=9.8, k=0.1, m=1.0):
    """Free fall with fluid resistance."""
    return np.array([state[1], g * np.exp(-k * time / m)])

def sho(state, time, k=1.0, m=1.0):
    """Simple Harmonic Oscillator (Spring-Mass System)."""
    return np.array([state[1], -k / m * state[0]])

def dho(state, time, k=1.0, b=0.1, m=1.0, Fo=1.0, Wo=1.0):
    """Damped Harmonic Oscillator."""
    return np.array([state[1], - (k * state[0] + b * state[1]) / m])

def ddho(state, time, k=1.0, b=0.1, m=1.0, Fo=1.0, Wo=1.0):
    """Damped Driven Harmonic Oscillator."""
    return np.array([state[1], - (k * state[0] + b * state[1]) / m - Fo * np.cos(10 * Wo * time)])

def pendulum(state, time, g=9.8, L=1.0):
    """Simple Pendulum Equation (small-angle approximation not used)."""
    return np.array([state[1], -g / L * np.sin(state[0])])

def complex_pendulum(state, time, g=9.8, L=1.0, m=1.0, damping=0.1, driving_force=0.5, driving_freq=1.0):
    """Complex Pendulum Equation with damping and external driving force."""
    theta, omega = state[0], state[1]
    damping_term = -damping * omega  # Damping force proportional to velocity
    driving_term = driving_force * np.cos(driving_freq * time)  # External periodic driving force
    acceleration = (-g / L * np.sin(theta)) + damping_term + driving_term
    return np.array([omega, acceleration])

def mass_spring_damper(state, time, m=1.0, k=1.0, c=0.2, F0=0.0, omega=0.0):
    """Mass-Spring-Damper System with external forcing."""
    x, v = state[0], state[1]
    acceleration = (-k / m * x) - (c / m * v) + (F0 / m) * np.cos(omega * time)
    return np.array([v, acceleration])


# Simulation Configuration Class
class SimulationConfig:
    def __init__(self, method, equation, params, x0, v0, t_total, N):
        """
        Stores parameters for running a numerical simulation.

        Args:
            method (function): Numerical method (e.g., Euler, Runge-Kutta).
            equation (function): Differential equation to solve.
            params (dict): Physical parameters including:
                - k: Spring constant (N/m) - stiffness of the spring.
                - b: Damping coefficient (kg/s) - resistance reducing motion.
                - m: Mass (kg) - the object's mass.
                - Fo: Driving force amplitude (N) - external force magnitude.
                - Wo: Driving frequency (rad/s) - frequency of the external force.
            x0 (float): Initial position.
            v0 (float): Initial velocity.
            t_total (float): Total simulation time.
            N (int): Number of time steps.
        """
        self.method = method
        self.equation = equation
        self.params = params
        self.x0 = x0
        self.v0 = v0
        self.t_total = t_total
        self.N = N

import numpy as np
import matplotlib.pyplot as plt

def run_simulation(config):
    """Runs a simulation using specified numerical method and equation."""
    dt = config.t_total / float(config.N - 1)
    time = np.linspace(0, config.t_total, config.N)
    
    y = np.zeros([config.N, 2])
    y[0] = [config.x0, config.v0]
    
    for j in range(config.N - 1):
        y[j + 1] = config.method(y[j], time[j], dt, lambda s, t: config.equation(s, t, **config.params))
    
    return time, y[:, 0], y[:, 1]

def compare_simulations(configs):
    """Compares multiple simulations with different configurations."""
    plt.figure(figsize=(10, 5))
    
    for config in configs:
        time, xdata, _ = run_simulation(config)
        plt.plot(time, xdata, label=f"{config.method.__name__} - {config.equation.__name__}")
    
    plt.xlabel("Time")
    plt.ylabel("Position")
    plt.title("Comparison of Numerical Methods")
    plt.legend()
    plt.show()