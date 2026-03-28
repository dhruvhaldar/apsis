import numpy as np
from scipy.integrate import solve_bvp

def solve_pmp_linear_quadratic(A, B, Q, R, x0, xf, tf, num_points=100):
    """
    Solves the optimal control problem using Pontryagin Maximum Principle (TPBVP)
    for a linear system with quadratic cost.

    H(x, u, lambda) = 0.5*(x^T Q x + u^T R u) + lambda^T (Ax + Bu)
    """
    # ⚡ Bolt Optimization: Use np.asarray() to avoid redundant memory copying
    # if the inputs are already correctly typed NumPy arrays.
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float)
    Q = np.asarray(Q, dtype=float)
    R = np.asarray(R, dtype=float)
    x0 = np.asarray(x0, dtype=float)
    xf = np.asarray(xf, dtype=float)

    n_states = A.shape[0]

    # ⚡ Bolt Optimization:
    # Use np.linalg.solve for better numerical stability and performance over inv
    BR_invB = B @ np.linalg.solve(R, B.T)

    # Pre-compute state-costate matrix M to avoid allocation and repeated matrix
    # operations in the hot loop (bvp_system)
    M = np.empty((2 * n_states, 2 * n_states))
    M[:n_states, :n_states] = A
    M[:n_states, n_states:] = -BR_invB
    M[n_states:, :n_states] = -Q
    M[n_states:, n_states:] = -A.T

    def bvp_system(t, y):
        # ⚡ Bolt Optimization: Replace multiple @ and np.vstack with a single dot product
        return M @ y

    def bvp_bc(ya, yb):
        # ⚡ Bolt Optimization: Use direct slicing
        return np.concatenate((ya[:n_states] - x0, yb[:n_states] - xf))

    t = np.linspace(0, tf, num_points)

    # ⚡ Bolt Optimization: Fast vectorized linear interpolation to replace Python loop
    y_guess = np.zeros((2 * n_states, num_points))
    y_guess[:n_states, :] = np.linspace(x0, xf, num_points).T

    res = solve_bvp(bvp_system, bvp_bc, t, y_guess)

    if res.success:
        x_sol = res.y[:n_states, :]
        lam_sol = res.y[n_states:, :]
        # ⚡ Bolt Optimization: Use np.linalg.solve instead of np.linalg.inv(R) @
        u_sol = -np.linalg.solve(R, B.T @ lam_sol)
        return t, x_sol, u_sol, lam_sol
    else:
        raise RuntimeError("BVP solver failed: " + res.message)
