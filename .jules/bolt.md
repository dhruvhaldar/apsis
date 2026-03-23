## 2024-05-24 - NumPy Vectorization for Grid-Based PDE Solvers
**Learning:** For dynamic programming and PDE solvers like HJB that operate over grids, Python-level nested loops iterating over state spaces (`x`) and control spaces (`u`) create massive performance bottlenecks (e.g. 1.4s for a 50x50x50 grid).
**Action:** Always refactor such numerical grid-based operations using `np.meshgrid` to broadcast and vectorially evaluate functions (like cost and dynamics) simultaneously across the entire state and control space, followed by `np.argmin` to select optimal controls. This achieved a ~50x speedup while producing identical numerical results.

## 2024-05-19 - NumPy Array Allocation in Tight Loops
**Learning:** In NumPy-heavy algorithms (like solving the HJB equation with backward value iteration), allocating recurrently accessed arrays (like `dVdx = np.empty(nx)` or `np.arange(nx)`) inside tight Python loops creates significant allocation overhead. Replacing constant divisions with multiplication (e.g., pre-computing `1/dx`) further saves small amounts of time per iteration.
**Action:** Always pre-allocate arrays outside of recursive or iterative algorithms, pre-compute constants for multiplicative inversions, and hoist static slices (like `np.arange(nx)`) when dealing with vectorized hot paths.
