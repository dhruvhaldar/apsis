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

    # Backward value iteration
    for k in range(nt - 2, -1, -1):
        for i in range(nx):
            x = x_grid[i]

            # Estimate spatial derivative dV/dx using central difference
            if i == 0:
                dVdx = (V[i+1, k+1] - V[i, k+1]) / dx
            elif i == nx - 1:
                dVdx = (V[i, k+1] - V[i-1, k+1]) / dx
            else:
                dVdx = (V[i+1, k+1] - V[i-1, k+1]) / (2 * dx)

            min_val = float('inf')
            best_u = u_grid[0]

            for j in range(nu):
                u = u_grid[j]

                # Evaluate running cost and dynamics
                cost = L(x, u, t_grid[k])
                dyn = f(x, u, t_grid[k])

                # Evaluate HJB RHS
                val = cost + dVdx * dyn

                if val < min_val:
                    min_val = val
                    best_u = u

            u_opt[i, k] = best_u
            # Update V(x, t) = V(x, t+dt) + dt * min_u [ L + dV/dx * f ]
            V[i, k] = V[i, k+1] + dt * min_val

    return V, u_opt
