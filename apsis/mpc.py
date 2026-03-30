import numpy as np
from gekko import GEKKO

def solve_mpc(A, B, Q, R, x0, N_horizon, dt, u_min=None, u_max=None):
    """
    Solves a model predictive control (MPC) problem using GEKKO over a finite horizon.
    """
    # ⚡ Bolt Optimization: Use np.asarray() to avoid redundant memory copying
    # if the inputs are already correctly typed NumPy arrays.
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float)
    Q = np.asarray(Q, dtype=float)
    R = np.asarray(R, dtype=float)
    x0 = np.asarray(x0, dtype=float)

    n_x = A.shape[0]
    n_u = B.shape[1]

    m = GEKKO(remote=False)

    try:
        m.time = np.linspace(0, N_horizon * dt, N_horizon + 1)

        # States
        x = [m.CV(value=x0[i]) for i in range(n_x)]
        for xi in x:
            xi.STATUS = 1 # Include in objective

        # Controls
        u = [m.MV(value=0) for i in range(n_u)]
        for i, ui in enumerate(u):
            ui.STATUS = 1 # Include in objective
            if u_min is not None:
                ui.LOWER = u_min[i]
            if u_max is not None:
                ui.UPPER = u_max[i]

        # ⚡ Bolt Optimization: Skip zero entries when building GEKKO expressions.
        # GEKKO builds internal expression trees for every algebraic operation.
        # Adding zero elements (e.g., `0 + 0*x_1 + 1*x_2`) creates massive formulation
        # overhead for sparse matrices commonly found in state-space and LQR models.
        # System equations x_dot = Ax + Bu
        for i in range(n_x):
            eq = 0
            for j in range(n_x):
                if A[i, j] != 0:
                    eq += A[i, j] * x[j]
            for j in range(n_u):
                if B[i, j] != 0:
                    eq += B[i, j] * u[j]
            m.Equation(x[i].dt() == eq)

        # Objective function
        # sum(x^T Q x + u^T R u)
        obj = 0
        for i in range(n_x):
            for j in range(n_x):
                if Q[i, j] != 0:
                    obj += x[i] * Q[i, j] * x[j]

        for i in range(n_u):
            for j in range(n_u):
                if R[i, j] != 0:
                    obj += u[i] * R[i, j] * u[j]

        m.Obj(m.integral(obj))

        # Solver configuration
        m.options.IMODE = 6 # Dynamic optimization
        m.options.NODES = 3 # Collocation nodes
        m.options.SOLVER = 3 # IPOPT

        m.solve(disp=False)

        x_sol = np.array([xi.value for xi in x])
        u_sol = np.array([ui.value for ui in u])

        return m.time, x_sol, u_sol
    finally:
        # 🛡️ Sentinel Security Enhancement: Prevent resource exhaustion by ensuring GEKKO temporary files are cleaned up
        m.cleanup()
