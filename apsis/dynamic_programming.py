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
    # ⚡ Bolt Optimization: Use `sparse=True` to prevent allocating full (nx, nu) matrices.
    # NumPy's broadcasting handles the expansion implicitly during algebraic operations,
    # drastically reducing memory consumption and improving cache locality for large grids.
    X, U = np.meshgrid(x_grid, u_grid, indexing='ij', sparse=True)

    # ⚡ Bolt Optimization:
    # 1. Pre-allocate arrays that are re-used in the loop (`dVdx`, `vals`)
    # 2. Pre-compute constants for spatial differences to replace division with multiplication
    # 3. Pre-allocate index arrays for slicing to avoid `np.arange(nx)` in the hot loop
    dVdx = np.empty(nx)
    inv_dx = 1.0 / dx
    inv_2dx = 1.0 / (2.0 * dx)
    idx_arange = np.arange(nx)
    vals = np.empty((nx, nu))
    min_indices = np.empty(nx, dtype=np.intp)

    # Backward value iteration
    for k in range(nt - 2, -1, -1):
        # Estimate spatial derivative dV/dx using central difference for all x simultaneously
        V_next = V[:, k+1]
        dVdx[0] = (V_next[1] - V_next[0]) * inv_dx
        dVdx[-1] = (V_next[-1] - V_next[-2]) * inv_dx
        if nx > 2:
            # ⚡ Bolt Optimization: Use in-place np.subtract and np.multiply
            # to avoid implicit array allocations in central difference calculation
            np.subtract(V_next[2:], V_next[:-2], out=dVdx[1:-1])
            np.multiply(dVdx[1:-1], inv_2dx, out=dVdx[1:-1])

        t_val = t_grid[k]

        # Evaluate running cost and dynamics vectorially over all states and controls
        cost = L(X, U, t_val)
        dyn = f(X, U, t_val)

        # Evaluate HJB RHS for all combinations of (x, u)
        # ⚡ Bolt Optimization: Use in-place np.multiply and np.add with pre-allocated
        # `vals` array to avoid allocating intermediate (nx, nu) arrays in every iteration.
        np.multiply(dVdx[:, np.newaxis], dyn, out=vals)
        np.add(cost, vals, out=vals)

        # Find the minimum value and corresponding control along the 'u' axis (axis=1)
        # ⚡ Bolt Optimization: Use `out` parameter to avoid dynamic memory allocation of the index array on every iteration
        np.argmin(vals, axis=1, out=min_indices)
        min_val = vals[idx_arange, min_indices]

        u_opt[:, k] = u_grid[min_indices]
        # Update V(x, t) = V(x, t+dt) + dt * min_u [ L + dV/dx * f ]
        # ⚡ Bolt Optimization: Use in-place operations to prevent intermediate array allocations in the hot loop
        np.multiply(min_val, dt, out=min_val)
        np.add(V_next, min_val, out=V[:, k])

    return V, u_opt
