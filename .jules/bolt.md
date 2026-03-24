## 2024-05-24 - NumPy Vectorization for Grid-Based PDE Solvers
**Learning:** For dynamic programming and PDE solvers like HJB that operate over grids, Python-level nested loops iterating over state spaces (`x`) and control spaces (`u`) create massive performance bottlenecks (e.g. 1.4s for a 50x50x50 grid).
**Action:** Always refactor such numerical grid-based operations using `np.meshgrid` to broadcast and vectorially evaluate functions (like cost and dynamics) simultaneously across the entire state and control space, followed by `np.argmin` to select optimal controls. This achieved a ~50x speedup while producing identical numerical results.

## 2024-05-19 - NumPy Array Allocation in Tight Loops
**Learning:** In NumPy-heavy algorithms (like solving the HJB equation with backward value iteration), allocating recurrently accessed arrays (like `dVdx = np.empty(nx)`) inside tight Python loops creates significant allocation overhead. Replacing constant divisions with multiplication (e.g., pre-computing `1/dx`) further saves small amounts of time per iteration.
**Action:** Always pre-allocate arrays outside of recursive or iterative algorithms, pre-compute constants for multiplicative inversions, and hoist static slices (like `np.arange(nx)`) when dealing with vectorized hot paths.

## 2024-05-25 - Pre-computing State-Costate Block Matrices for TPBVP
**Learning:** In algorithms solving the Pontryagin Maximum Principle (TPBVP) using `scipy.integrate.solve_bvp`, the `bvp_system` function is called hundreds or thousands of times in a tight loop. Reconstructing the state-costate dynamics through multiple matrix multiplications (e.g., `A @ x`, `BR_invB @ lam`) and array concatenations (like `np.vstack`) on every call creates immense allocation and computational overhead.
**Action:** Pre-compute the full block matrix `M = [[A, -BR_invB], [-Q, -A.T]]` outside the solver loop, reducing the entire system dynamics to a single, highly optimized dot product `M @ y`. Also replace `np.linalg.inv` with `np.linalg.solve` for better numerical stability and performance when computing the inverse-dependent matrices like `BR_invB`.
