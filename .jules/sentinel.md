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
