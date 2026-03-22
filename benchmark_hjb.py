import time
import numpy as np
from apsis.dynamic_programming import solve_hjb

def L(x, u, t):
    return x**2 + u**2

def f(x, u, t):
    return x + u

x_grid = np.linspace(-1, 1, 50)
u_grid = np.linspace(-1, 1, 50)
t_grid = np.linspace(0, 1, 50)

def solve_hjb_vectorized(L, f, x_grid, u_grid, t_grid):
    dt = t_grid[1] - t_grid[0]
    dx = x_grid[1] - x_grid[0]

    nx = len(x_grid)
    nu = len(u_grid)
    nt = len(t_grid)

    V = np.zeros((nx, nt))
    u_opt = np.zeros((nx, nt))

    V[:, -1] = 0

    X, U = np.meshgrid(x_grid, u_grid, indexing='ij')

    for k in range(nt - 2, -1, -1):
        dVdx = np.empty(nx)
        dVdx[0] = (V[1, k+1] - V[0, k+1]) / dx
        dVdx[-1] = (V[-1, k+1] - V[-2, k+1]) / dx
        dVdx[1:-1] = (V[2:, k+1] - V[:-2, k+1]) / (2 * dx)

        t_val = t_grid[k]

        cost = L(X, U, t_val)
        dyn = f(X, U, t_val)

        vals = cost + dVdx[:, np.newaxis] * dyn

        min_indices = np.argmin(vals, axis=1)

        u_opt[:, k] = u_grid[min_indices]
        V[:, k] = V[:, k+1] + dt * vals[np.arange(nx), min_indices]

    return V, u_opt

start = time.time()
for _ in range(10):
    V_orig, u_orig = solve_hjb(L, f, x_grid, u_grid, t_grid)
end = time.time()
print(f"Original Time: {end - start:.4f}s")

start = time.time()
for _ in range(10):
    V_vec, u_vec = solve_hjb_vectorized(L, f, x_grid, u_grid, t_grid)
end = time.time()
print(f"Vectorized Time: {end - start:.4f}s")

print(f"Max V Diff: {np.max(np.abs(V_orig - V_vec))}")
print(f"Max U Diff: {np.max(np.abs(u_orig - u_vec))}")
