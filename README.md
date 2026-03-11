# Apsis

Apsis is a web-based mathematical workbench built for SF2852 Optimal Control Theory. It provides numerical solvers and interactive visualizations for calculating optimal trajectories, synthesizing feedback controllers, and managing system constraints over finite and infinite horizons.

The tool features a Dark Neumorphic (Soft UI) design, creating a tactile, "space-age guidance console" feel where components appear extruded from the background material.

## 📚 Syllabus Mapping (SF2852)

This project strictly adheres to the course learning outcomes:

| Module | Syllabus Topic | Implemented Features |
|---|---|---|
| Pontryagin | The Pontryagin maximum principle | Solves the necessary conditions for optimality via Two-Point Boundary Value Problems (TPBVP), handling costate vectors $\lambda(t)$. |
| Dynamic Prog. | Hamilton-Jacobi-Bellman equation | Grid-based numerical PDE solver to map the optimal Value Function $V(x,t)$. |
| LQR | Linear quadratic optimization | Algebraic Riccati Equation (ARE) solver for infinite-horizon optimal feedback ($u = -Kx$). |
| MPC | Model predictive control | Constrained rolling-horizon optimization using quadratic programming. |
| Numerical | Numerical methods for optimal control | Direct collocation and shooting methods for complex nonlinear trajectory optimization. |

## 🚀 Deployment (Vercel)

Apsis is designed to run as a serverless optimal control engine.

- Fork this repository.
- Deploy to Vercel (Python runtime is auto-detected).
- Access the Guidance Dashboard at `https://your-apsis.vercel.app`.

## 📊 Visualizations & Artifacts

### 1. Optimal Trajectories (Pontryagin Maximum Principle)
Solving the costate equations to find the optimal control input $u^*(t)$ that minimizes the performance index while navigating from an initial state to a target manifold.

*Figure 1: State-Space Trajectory. The plot shows the optimal path of an aerospace vehicle minimizing fuel consumption. The curve demonstrates the "Bang-Bang" control behavior typical of control-constrained maximum principle problems, where thrusters fire only at minimum/maximum bounds.*

### 2. Receding Horizon (Model Predictive Control)
Visualizing how MPC predicts future states over a finite window, applies the first control action, and then recalculates.

*Figure 2: The MPC Horizon. This visualization highlights the prediction horizon ($N_p$) and control horizon ($N_c$). The system anticipates future constraints (e.g., an obstacle or actuator limit) and preemptively adjusts the current control input to ensure a smooth, optimal response without violating bounds.*

### 3. The Value Function (Hamilton-Jacobi-Bellman)
A 3D surface mapping the minimum "cost-to-go" from any state in the state-space.

*Figure 3: HJB Value Surface $V(x,t)$. This Plotly.js 3D render illustrates the solution to the HJB partial differential equation. The "basin" of the surface represents the target equilibrium; the gradient of this surface at any point directly yields the optimal feedback control law.*
