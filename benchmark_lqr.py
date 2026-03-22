import time
import numpy as np
from apsis.lqr import solve_lqr

A = [[0, 1], [0, 0]]
B = [[0], [1]]
Q = [[1, 0], [0, 1]]
R = [[1]]

start = time.time()
for _ in range(1000):
    solve_lqr(A, B, Q, R)
end = time.time()

print(f"Original Time: {end - start:.4f}s")
