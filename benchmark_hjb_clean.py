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

start = time.time()
for _ in range(10):
    V, u = solve_hjb(L, f, x_grid, u_grid, t_grid)
end = time.time()

print(f"Refactored Time: {end - start:.4f}s")
