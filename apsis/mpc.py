import numpy as np
from gekko import GEKKO

def solve_mpc(A, B, Q, R, x0, N_horizon, dt, u_min=None, u_max=None):
    """
    Solves a model predictive control (MPC) problem using GEKKO over a finite horizon.
    """
    A = np.array(A, dtype=float)
    B = np.array(B, dtype=float)
    Q = np.array(Q, dtype=float)
    R = np.array(R, dtype=float)
    x0 = np.array(x0, dtype=float)

    n_x = A.shape[0]
    n_u = B.shape[1]

    m = GEKKO(remote=False)
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

    # System equations x_dot = Ax + Bu
    for i in range(n_x):
        eq = 0
        for j in range(n_x):
            eq += A[i, j] * x[j]
        for j in range(n_u):
            eq += B[i, j] * u[j]
        m.Equation(x[i].dt() == eq)

    # Objective function
    # sum(x^T Q x + u^T R u)
    obj = 0
    for i in range(n_x):
        for j in range(n_x):
            obj += x[i] * Q[i, j] * x[j]

    for i in range(n_u):
        for j in range(n_u):
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
