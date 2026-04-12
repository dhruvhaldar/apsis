## 2024-05-24 - NumPy Vectorization for Grid-Based PDE Solvers
**Learning:** For dynamic programming and PDE solvers like HJB that operate over grids, Python-level nested loops iterating over state spaces (`x`) and control spaces (`u`) create massive performance bottlenecks (e.g. 1.4s for a 50x50x50 grid).
**Action:** Always refactor such numerical grid-based operations using `np.meshgrid` to broadcast and vectorially evaluate functions (like cost and dynamics) simultaneously across the entire state and control space, followed by `np.argmin` to select optimal controls. This achieved a ~50x speedup while producing identical numerical results.

## 2024-05-19 - NumPy Array Allocation in Tight Loops
**Learning:** In NumPy-heavy algorithms (like solving the HJB equation with backward value iteration), allocating recurrently accessed arrays (like `dVdx = np.empty(nx)`) inside tight Python loops creates significant allocation overhead. Replacing constant divisions with multiplication (e.g., pre-computing `1/dx`) further saves small amounts of time per iteration.
**Action:** Always pre-allocate arrays outside of recursive or iterative algorithms, pre-compute constants for multiplicative inversions, and hoist static slices (like `np.arange(nx)`) when dealing with vectorized hot paths.

## 2024-05-25 - Pre-computing State-Costate Block Matrices for TPBVP
**Learning:** In algorithms solving the Pontryagin Maximum Principle (TPBVP) using `scipy.integrate.solve_bvp`, the `bvp_system` function is called hundreds or thousands of times in a tight loop. Reconstructing the state-costate dynamics through multiple matrix multiplications (e.g., `A @ x`, `BR_invB @ lam`) and array concatenations (like `np.vstack`) on every call creates immense allocation and computational overhead.
**Action:** Pre-compute the full block matrix `M = [[A, -BR_invB], [-Q, -A.T]]` outside the solver loop, reducing the entire system dynamics to a single, highly optimized dot product `M @ y`. Also replace `np.linalg.inv` with `np.linalg.solve` for better numerical stability and performance when computing the inverse-dependent matrices like `BR_invB`.

## 2024-05-26 - SciPy Overhead vs LAPACK in Small Matrices
**Learning:** While `scipy.linalg.solve` with `assume_a='pos'` allows algorithms like Cholesky decomposition which are asymptotically faster for symmetric positive-definite matrices (like R in LQR), the Python-level argument checking and dispatch overhead in SciPy significantly outweighs the algorithmic benefits when dealing with the typically small matrices found in optimal control problems (e.g., 1x1, 2x2).
**Action:** When solving continuous algebraic Riccati equations (CARE) and computing LQR gains for small systems, prefer directly using `np.linalg.solve` and `np.linalg.eigvals`. Even without `assume_a='pos'`, the lower Python overhead of NumPy's more direct C-wrapper provides ~10% faster execution per call. Additionally, always use `np.asarray()` instead of `np.array()` to avoid redundant memory copies if the input is already a correctly typed NumPy array.

## 2024-05-27 - Intermediate Array Allocation in Tight Loops
**Learning:** Even when NumPy code is vectorized, expressions like `vals = cost + dVdx[:, np.newaxis] * dyn` allocate new arrays of size `(nx, nu)` at each step of an iterative solver. For multi-dimensional grids, this constant allocation and de-allocation overhead severely degrades performance in hot loops (e.g. backward value iteration in HJB).
**Action:** Pre-allocate target arrays `vals = np.empty((nx, nu))` outside the hot loop and use in-place NumPy functions (`np.multiply(..., out=vals)`, `np.add(..., out=vals)`) to re-use memory and avoid recurrent allocation bottlenecks.

## 2024-05-28 - Sparse Matrix Optimizations for GEKKO Formulation
**Learning:** In GEKKO, expressions are compiled into an internal AST (Abstract Syntax Tree). When iterating over standard control matrices like $A$, $B$, $Q$, and $R$—which are overwhelmingly sparse in state-space and MPC applications—adding elements like `0 * x` or adding `+ 0` generates massive formulation overhead. GEKKO spends substantial time compiling and validating these dead branches of the expression tree before solving.
**Action:** When building GEKKO equations (like `x.dt() = Ax + Bu`) or objective functions using nested loops over matrices, always explicitly check `if matrix[i, j] != 0:` to skip zero entries. This simple check reduces the equation setup time for a standard 10x10 MPC problem from ~0.05 seconds to ~0.01 seconds.

## 2026-03-31 - Sparse Meshgrid for Grid-Based Numerical Solvers
**Learning:** In numerical grid-based solvers like the HJB equation, calling `np.meshgrid` directly over large multi-dimensional state and control spaces explicitly allocates dense matrices of size (e.g.) `(nx, nu)`. This causes significant memory duplication and cache-miss overhead when performing element-wise arithmetic evaluations inside iterative solvers, scaling disastrously with grid resolution.
**Action:** Always pass `sparse=True` to `np.meshgrid(..., indexing='ij', sparse=True)`. This returns small 1D arrays matching the dimension axes (e.g. `(nx, 1)` and `(1, nu)`). NumPy’s broadcasting rules naturally expand these sparse vectors during arithmetic operations without preemptively allocating identical data across memory, achieving massive memory savings and cutting execution times by more than half for high-resolution grids.

## 2026-04-01 - Avoid `np.concatenate` in Hot Loops
**Learning:** `np.concatenate` internally performs heavy Python C-API calls to allocate new arrays and handle arbitrary argument lengths, resulting in high overhead when placed inside a tight optimization loop (like SciPy's `solve_bvp` Jacobian perturbation which calls `bvp_bc` thousands of times).
**Action:** Replace `np.concatenate((a, b))` inside solver hot loops with pre-allocating an empty array and direct slice assignment: `res = np.empty(size); res[:n] = a; res[n:] = b;`. This avoids C-API overhead and creates a ~20% performance improvement in boundary evaluation routines.

## 2026-04-02 - Render Blocking External Scripts
**Learning:** External `<script>` tags without `defer` or `async` block HTML parsing and delay DOM rendering. In a vanilla HTML setup without a bundler, heavy libraries like Plotly.js, Chart.js, and Three.js will block the entire UI from loading until they are fully downloaded and executed.
**Action:** Apply the `defer` attribute to heavy external CDN `<script>` tags to optimize frontend performance and prevent render-blocking. Also apply `defer` to local dependent scripts (like `app.js`) to guarantee they execute sequentially in DOM order after the external libraries, preventing `ReferenceError`s.

## 2026-04-03 - SciPy solve_bvp Analytical Jacobians
**Learning:** `scipy.integrate.solve_bvp` relies heavily on Jacobian computations for its damped Newton method. By default, if Jacobians are not provided, it estimates them via internal forward finite differences, which involves repeatedly calling the system dynamics and boundary conditions with perturbed states. For linear or analytically differentiable systems (e.g., LQR via Pontryagin Maximum Principle where system dynamics are `M @ y`), this implicit fallback is computationally wasteful.
**Action:** When using `scipy.integrate.solve_bvp` for analytically differentiable systems, always supply exact analytical Jacobians (`fun_jac` and `bc_jac`) to completely bypass these costly finite-difference approximations. This yields a measurable reduction in solver execution time.

## 2026-04-08 - Optimize API serialization for numpy arrays
**Learning:** Python-level list comprehensions over numpy array elements (e.g., `[complex(e).real for e in eigvals]`) in API serialization paths cause significant overhead and bypass numpy's optimized C implementations.
**Action:** Always prefer numpy's vectorized properties and built-in conversion methods like `.real.tolist()` over manual iteration to serialize arrays to JSON-compatible lists.

## 2024-05-29 - Zero-Copy Jacobian Broadcasting in solve_bvp
**Learning:** Returning explicitly allocated matrices via `np.repeat` inside the analytical Jacobian callback `fun_jac` for `scipy.integrate.solve_bvp` introduces recurrent memory allocation overhead in the solver's hot loops.
**Action:** Use `np.broadcast_to` on a pre-expanded array (`M[:, :, np.newaxis]`) instead of `np.repeat`. This returns a zero-copy view of the Jacobian which SciPy handles correctly, entirely bypassing allocation overhead and measurably improving solver execution speed.

## 2024-05-30 - GZip Compression for Large API Payloads
**Learning:** Endpoints that return numerical trajectories (like PMP and MPC solvers) generate large JSON arrays. Without compression, these payloads can be hundreds of kilobytes, causing slow network transfer and delaying frontend rendering.
**Action:** Always enable `GZipMiddleware` in FastAPI applications that serve large array payloads. Setting a reasonable `minimum_size` (e.g., 1000 bytes) ensures that small responses don't incur compression overhead, while large trajectory payloads are reduced by >60%, measurably improving network performance.

## 2024-05-31 - Chart.js Memory Leaks and DOM Thrashing
**Learning:** In a single-page application, destroying a Chart.js canvas by simply setting `innerHTML = ''` or calling `ctx.remove()` without first calling `chart.destroy()` causes a severe memory leak. Chart.js retains event listeners (like resize handlers) tied to the `window` object, keeping the orphaned chart instances in memory indefinitely.
**Action:** Instead of tearing down the DOM and recreating charts on every update, cache the `Chart` instance in a persistent variable. Update the chart's data properties in-place (e.g., `chart.data.labels = ...`) and call `chart.update()`. This not only prevents memory leaks but also significantly improves rendering performance by avoiding expensive DOM reflows.

## 2024-06-01 - Plotly Rendering Optimization
**Learning:** Calling `Plotly.newPlot` on an existing chart container forces a complete DOM teardown and recreation of the plot elements. This is computationally expensive and can cause visual flickering during rapid consecutive updates.
**Action:** Use `Plotly.react` instead of `Plotly.newPlot` for subsequent chart updates. `Plotly.react` performs an intelligent diff on the data and layout, updating the existing SVG elements in-place. This saves significant main-thread time and provides a much smoother user experience.
