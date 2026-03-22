import numpy as np

def solve_hjb(L, f, x_grid, u_grid, t_grid):
    """
    Solves continuous-time HJB equation using backward value iteration on a grid.
    -dV/dt = min_u [ L(x, u, t) + dV/dx * f(x, u, t) ]

    This is a simplified 1D state, 1D control example solver.
    """
    dt = t_grid[1] - t_grid[0]
    dx = x_grid[1] - x_grid[0]

    nx = len(x_grid)
    nu = len(u_grid)
    nt = len(t_grid)

    V = np.zeros((nx, nt))
    u_opt = np.zeros((nx, nt))

    # Terminal condition (assume V(x, tf) = 0 for simplicity or add a terminal cost function)
    V[:, -1] = 0

    # Pre-compute a meshgrid for vectorized evaluation over all x and u combinations
    X, U = np.meshgrid(x_grid, u_grid, indexing='ij')

    # Backward value iteration
    for k in range(nt - 2, -1, -1):
        # Estimate spatial derivative dV/dx using central difference for all x simultaneously
        dVdx = np.empty(nx)
        dVdx[0] = (V[1, k+1] - V[0, k+1]) / dx
        dVdx[-1] = (V[-1, k+1] - V[-2, k+1]) / dx
        if nx > 2:
            dVdx[1:-1] = (V[2:, k+1] - V[:-2, k+1]) / (2 * dx)

        t_val = t_grid[k]

        # Evaluate running cost and dynamics vectorially over all states and controls
        cost = L(X, U, t_val)
        dyn = f(X, U, t_val)

        # Evaluate HJB RHS for all combinations of (x, u)
        # dVdx is (nx,), we add a new axis to broadcast with (nx, nu) matrices
        vals = cost + dVdx[:, np.newaxis] * dyn

        # Find the minimum value and corresponding control along the 'u' axis (axis=1)
        min_indices = np.argmin(vals, axis=1)
        min_val = vals[np.arange(nx), min_indices]

        u_opt[:, k] = u_grid[min_indices]
        # Update V(x, t) = V(x, t+dt) + dt * min_u [ L + dV/dx * f ]
        V[:, k] = V[:, k+1] + dt * min_val

    return V, u_opt
