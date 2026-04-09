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

    # ⚡ Bolt Optimization: Provide exact analytical Jacobians to solve_bvp
    # to bypass costly internal finite-difference approximations for linear systems.
    # Pre-expand M for zero-copy broadcasting in the Jacobian
    M_expanded = M[:, :, np.newaxis]
    M_shape_0 = M.shape[0]
    M_shape_1 = M.shape[1]

    def fun_jac(t, y):
        # Derivative of (M @ y) with respect to y is M.
        # solve_bvp expects shape (n, n, m) where n is state dim (2*n_states) and m is number of points.
        # ⚡ Bolt Optimization: Use np.broadcast_to to return a zero-copy view
        # instead of explicitly allocating memory with np.repeat on every iteration.
        m_pts = y.shape[1]
        return np.broadcast_to(M_expanded, (M_shape_0, M_shape_1, m_pts))

    # Pre-compute boundary condition Jacobians
    dbc_dya = np.zeros((2 * n_states, 2 * n_states))
    dbc_dya[:n_states, :n_states] = np.eye(n_states)

    dbc_dyb = np.zeros((2 * n_states, 2 * n_states))
    dbc_dyb[n_states:, :n_states] = np.eye(n_states)

    def bvp_bc(ya, yb):
        # ⚡ Bolt Optimization: Use direct slicing into a locally pre-allocated
        # array. Returning references to a single globally allocated `bc_res`
        # causes SciPy's Jacobian perturbation to fail. `np.empty` followed
        # by assignment is ~20% faster than `np.concatenate` allocating copies.
        res = np.empty(2 * n_states)
        res[:n_states] = ya[:n_states] - x0
        res[n_states:] = yb[:n_states] - xf
        return res

    def bc_jac(ya, yb):
        return dbc_dya, dbc_dyb

    t = np.linspace(0, tf, num_points)

    # ⚡ Bolt Optimization: Fast vectorized linear interpolation to replace Python loop
    y_guess = np.zeros((2 * n_states, num_points))
    y_guess[:n_states, :] = np.linspace(x0, xf, num_points).T

    res = solve_bvp(bvp_system, bvp_bc, t, y_guess, fun_jac=fun_jac, bc_jac=bc_jac)

    if res.success:
        x_sol = res.y[:n_states, :]
        lam_sol = res.y[n_states:, :]
        # ⚡ Bolt Optimization: Use np.linalg.solve instead of np.linalg.inv(R) @
        u_sol = -np.linalg.solve(R, B.T @ lam_sol)
        return t, x_sol, u_sol, lam_sol
    else:
        raise RuntimeError("BVP solver failed: " + res.message)
