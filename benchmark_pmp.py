import time
import numpy as np
from apsis.calculus_of_variations import solve_pmp_linear_quadratic

A = [[0, 1], [0, 0]]
B = [[0], [1]]
Q = [[1, 0], [0, 1]]
R = [[1]]
x0 = [1, 1]
xf = [0, 0]
tf = 10.0

start = time.time()
for _ in range(100):
    solve_pmp_linear_quadratic(A, B, Q, R, x0, xf, tf)
end = time.time()

print(f"Original Time: {end - start:.4f}s")
