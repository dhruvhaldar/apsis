## 2024-05-20 - Serverless Same-Origin CORS
**Vulnerability:** Overly permissive CORS configuration (`allow_origins=["*"]`) combined with missing security headers.
**Learning:** In serverless deployments (like Vercel) where the static frontend (`/public`) and the API (`/api/index.py`) are served from the same domain, wildcard CORS is an unnecessary attack surface. CORS is only required for local development when the frontend dev server and API run on different ports.
**Prevention:** Avoid `allow_origins=["*"]`. Hardcode the specific `localhost` ports used during local development. Additionally, add a custom HTTP middleware to inject basic security headers like `X-Content-Type-Options` and `X-Frame-Options` for defense in depth.

## 2024-05-21 - Edge Infrastructure Security Headers
**Vulnerability:** Missing Security Headers (X-Frame-Options, X-Content-Type-Options) on the statically served frontend, leading to Clickjacking and MIME-sniffing risks.
**Learning:** Application-level middleware (like FastAPI's `@app.middleware("http")`) only protects dynamic routes hitting that specific application (e.g., `/api/*`). When utilizing edge infrastructure (like Vercel) to serve static frontend files (`public/index.html`), those assets bypass the backend entirely and remain unprotected.
**Prevention:** Configure security headers at the edge router/infrastructure level (e.g., in `vercel.json` using the `headers` property matching `/(.*)`) rather than relying solely on backend application middleware. This guarantees global enforcement across both static and dynamic routes.
## 2024-03-27 - Temporary File Leak (Resource Exhaustion) in GEKKO
**Vulnerability:** The MPC endpoint was leaking a temporary `/tmp/tmp*gk_model*` directory for every API call, regardless of success or failure.
**Learning:** `GEKKO(remote=False)` relies on file I/O and creates local scratch directories. These must be explicitly cleaned up. The absence of `m.cleanup()` created a critical DoS/Resource Exhaustion vulnerability by slowly filling up the server's disk space.
**Prevention:** Always use a `try...finally` block to call `m.cleanup()` whenever instantiating GEKKO locally.
## 2024-05-22 - Strict Content-Security-Policy (CSP)
**Vulnerability:** Missing CSP allows inline scripts (`'unsafe-inline'`), making the application susceptible to Cross-Site Scripting (XSS) attacks. If an attacker injects malicious scripts, the browser will execute them.
**Learning:** To implement a strict CSP, inline event handlers (like `onsubmit="..."` in HTML) and inline scripts must be removed. Event listeners and initialization logic (like `renderMathInElement`) should be attached within external JavaScript files (`app.js`) using `addEventListener`.
**Prevention:** Enforce a strict `Content-Security-Policy` header in both edge configuration (`vercel.json`) and application middleware (`api/index.py`) that explicitly avoids `'unsafe-inline'` for scripts, whitelisting only necessary external CDNs.
## 2024-05-23 - Incomplete `try...finally` Block (Resource Exhaustion) in GEKKO
**Vulnerability:** A `try...finally` block intended to clean up temporary files in `GEKKO(remote=False)` was placed incorrectly, leaving initialization logic unprotected. If an exception occurred during the model setup, the `try` block was bypassed and `m.cleanup()` was not executed, allowing an attacker to cause disk resource exhaustion by intentionally failing the model setup logic.
**Learning:** For a `try...finally` block to effectively provide resource cleanup (like closing files, DB connections, or clearing temporary directories), the `try:` statement must *immediately* follow the resource instantiation. Any logic that could raise an exception between the instantiation and the start of the `try` block represents a resource leak vulnerability.
**Prevention:** Ensure the `try:` block encompasses all operations performed on a resource from the moment it is instantiated up to the final cleanup in the `finally:` block.
## 2024-05-24 - Unbounded Solver Execution (Resource Exhaustion) in GEKKO
**Vulnerability:** The MPC endpoint utilizing `GEKKO(remote=False)` was missing a timeout (`m.options.MAX_TIME`) configuration.
**Learning:** By providing inputs that require extensive computational time or do not converge, an attacker can cause the local GEKKO solver to run indefinitely. This consumes CPU resources and blocks worker threads, leading to a Denial of Service (DoS) attack.
**Prevention:** Always enforce strict execution limits when using numerical solvers on user-provided inputs by setting `m.options.MAX_TIME` and `m.options.MAX_ITER`.
## 2024-05-25 - Numerical Solver Input Validation (NaN/Inf)
**Vulnerability:** API endpoints accepted `NaN` and `Infinity` values in mathematical arrays (like state/cost matrices), bypassing Pydantic's default float validation.
**Learning:** Pydantic v2 allows `NaN` and `Inf` by default for `float` types. When exposed via an API, these values propagate into underlying numerical solvers (SciPy, GEKKO), causing internal exceptions, undefined behavior, or solver crashes.
**Prevention:** Always enforce strict numeric validation for mathematical APIs by explicitly disabling non-finite numbers using a custom float type, e.g., `SafeFloat = Annotated[float, Field(allow_inf_nan=False)]`.
## 2024-05-25 - Prevent DoS via FastAPI Memory Exhaustion
**Vulnerability:** By default, FastAPI and Starlette buffer the entire HTTP request payload in memory before passing it to the route handlers. Malicious actors could send massive payloads (e.g., extremely large JSON arrays) to exhaust server memory, leading to a Denial of Service (DoS).
**Learning:** Framework-level request parsing creates a systemic vulnerability if payload size isn't explicitly limited at the middleware level before the body is read into memory.
**Prevention:** Implement a custom HTTP middleware (`@app.middleware("http")`) that inspects the `Content-Length` header early in the request lifecycle and returns a 413 error if it exceeds a strict upper bound (e.g., 1MB), thus discarding the request before buffering begins.
