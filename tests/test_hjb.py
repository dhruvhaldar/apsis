import numpy as np
from apsis.dynamic_programming import solve_hjb

def test_hjb_basic():
    def L(x, u, t):
        return x**2 + u**2

    def f(x, u, t):
        return x + u

    x_grid = np.linspace(-1, 1, 10)
    u_grid = np.linspace(-1, 1, 10)
    t_grid = np.linspace(0, 1, 10)

    V, u = solve_hjb(L, f, x_grid, u_grid, t_grid)
    assert V.shape == (10, 10)
    assert u.shape == (10, 10)
