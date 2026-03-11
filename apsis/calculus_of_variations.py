import numpy as np
from scipy.integrate import solve_bvp

def solve_pmp_linear_quadratic(A, B, Q, R, x0, xf, tf, num_points=100):
    """
    Solves the optimal control problem using Pontryagin Maximum Principle (TPBVP)
    for a linear system with quadratic cost.

    H(x, u, lambda) = 0.5*(x^T Q x + u^T R u) + lambda^T (Ax + Bu)
    """
    A = np.array(A, dtype=float)
    B = np.array(B, dtype=float)
    Q = np.array(Q, dtype=float)
    R = np.array(R, dtype=float)
    x0 = np.array(x0, dtype=float)
    xf = np.array(xf, dtype=float)

    n_states = A.shape[0]

    R_inv = np.linalg.inv(R)
    BR_invB = B @ R_inv @ B.T

    def bvp_system(t, y):
        x = y[:n_states, :]
        lam = y[n_states:, :]

        dx = A @ x - BR_invB @ lam
        dlam = -Q @ x - A.T @ lam

        return np.vstack((dx, dlam))

    def bvp_bc(ya, yb):
        xa = ya[:n_states]
        xb = yb[:n_states]

        return np.concatenate((xa - x0, xb - xf))

    t = np.linspace(0, tf, num_points)
    y_guess = np.zeros((2 * n_states, num_points))
    for i in range(n_states):
        y_guess[i, :] = np.linspace(x0[i], xf[i], num_points)

    res = solve_bvp(bvp_system, bvp_bc, t, y_guess)

    if res.success:
        x_sol = res.y[:n_states, :]
        lam_sol = res.y[n_states:, :]
        u_sol = -R_inv @ B.T @ lam_sol
        return t, x_sol, u_sol, lam_sol
    else:
        raise RuntimeError("BVP solver failed: " + res.message)
