import numpy as np
import pytest
from apsis.lqr import solve_lqr
from apsis.calculus_of_variations import solve_pmp_linear_quadratic

def test_lqr_simple_integrator():
    # Double integrator: x_ddot = u
    A = [[0, 1], [0, 0]]
    B = [[0], [1]]
    Q = [[1, 0], [0, 1]]
    R = [[1]]

    K, X, eigvals = solve_lqr(A, B, Q, R)

    # Expected analytical limits for simple case are generally stable
    assert all(e.real < 0 for e in eigvals)
    assert K.shape == (1, 2)
    assert X.shape == (2, 2)
    assert np.allclose(X, X.T) # X must be symmetric

def test_pmp_simple():
    A = [[0, 1], [0, 0]]
    B = [[0], [1]]
    Q = [[1, 0], [0, 1]]
    R = [[1]]
    x0 = [1.0, 0.0]
    xf = [0.0, 0.0]
    tf = 5.0

    t, x_sol, u_sol, lam_sol = solve_pmp_linear_quadratic(A, B, Q, R, x0, xf, tf, num_points=50)

    assert len(t) == 50
    assert x_sol.shape == (2, 50)
    assert u_sol.shape == (1, 50)
    assert lam_sol.shape == (2, 50)

    # Check boundary conditions approximately
    assert np.allclose(x_sol[:, 0], x0, atol=1e-1)
    assert np.allclose(x_sol[:, -1], xf, atol=1e-1)
