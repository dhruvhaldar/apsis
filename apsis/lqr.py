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

    # Compute optimal feedback gain
    K = np.linalg.inv(R) @ B.T @ X

    # Compute closed-loop poles
    eigvals = np.linalg.eigvals(A - B @ K)

    return K, X, eigvals
