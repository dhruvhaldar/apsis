import numpy as np
import scipy.linalg

def solve_lqr(A, B, Q, R):
    """
    Solves the continuous-time linear quadratic regulator (LQR) problem.
    """
    A = np.array(A, dtype=float)
    B = np.array(B, dtype=float)
    Q = np.array(Q, dtype=float)
    R = np.array(R, dtype=float)

    # Solve continuous algebraic Riccati equation
    X = scipy.linalg.solve_continuous_are(A, B, Q, R)

    # ⚡ Bolt Optimization: Use scipy.linalg.solve instead of np.linalg.inv
    # for better numerical stability and speed. assume_a='pos' is used since R
    # must be positive definite in a well-posed LQR problem.
    K = scipy.linalg.solve(R, B.T @ X, assume_a='pos')

    # Compute closed-loop poles
    eigvals = scipy.linalg.eigvals(A - B @ K)

    return K, X, eigvals
