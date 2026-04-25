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
## 2024-05-26 - FastAPI Memory Exhaustion DoS
**Vulnerability:** Missing request payload size limit allows memory exhaustion Denial of Service (DoS) attacks because FastAPI/Starlette buffers the entire request body in memory by default.
**Learning:** Frameworks like FastAPI and Starlette are susceptible to memory exhaustion if they blindly buffer large request payloads without validation. An attacker could send massive, multi-gigabyte payloads to consume all server memory.
**Prevention:** Enforce a strict request payload size limit using HTTP middleware (e.g., checking `Content-Length`) to reject overly large payloads before they are completely buffered.

## 2025-04-07 - Denial of Service via Chunked Transfer Encoding Bypass
**Vulnerability:** FastAPIs buffer the entire payload into memory before executing body validations, making them vulnerable to memory exhaustion DoS attacks. A middleware size check on `Content-Length` does not prevent this if the request utilizes `Transfer-Encoding: chunked`, allowing massive payloads to completely bypass the check and hit the JSON parser.
**Learning:** Checking `Content-Length` provides incomplete protection if chunked encoding isn't handled correctly, as chunked payloads do not provide a `Content-Length` header upfront.
**Prevention:** In environments that do not support or require chunked payloads (like typical REST JSON endpoints), explicitly reject requests with `Transfer-Encoding: chunked` (e.g., returning `411 Length Required` or `411 Chunked encoding not supported`) in the same payload-limiting middleware.
## 2024-05-27 - Denial of Service via Missing Content-Length Bypass
**Vulnerability:** FastAPIs buffer the entire payload into memory, and a size check on `Content-Length` does not prevent memory exhaustion DoS attacks if an attacker simply omits the `Content-Length` header entirely. The request would pass the check and still be buffered.
**Learning:** If a security middleware relies on a specific HTTP header (like `Content-Length`) to enforce limits, omitting that header completely can bypass the limit entirely unless its absence is explicitly handled.
**Prevention:** For endpoints that expect a payload (like `POST`, `PUT`, `PATCH`), explicitly require the `Content-Length` header (e.g., returning `411 Length Required`) to ensure all requests are subject to the payload size limits.

## 2024-05-24 - Fix DoS via chunked encoding check bypass
**Vulnerability:** A Denial of Service (DoS) vulnerability via memory exhaustion could occur because the exact string check for the `Transfer-Encoding` header (`== "chunked"`) allowed bypassing the size limitation by sending mixed-case strings (e.g., `"Chunked"`) or multiple encodings (e.g., `"gzip, chunked"`).
**Learning:** Checking headers with exact equality can be dangerous when multiple values or different casings are valid according to HTTP specs.
**Prevention:** Always convert header values to lower case and use substring matching (e.g., `"chunked" in header_value`) when validating restricted encodings.

## 2025-04-10 - Denial of Service via Negative Content-Length Bypass
**Vulnerability:** A Denial of Service (DoS) vulnerability via memory exhaustion could occur because the payload size limit middleware checked if the `Content-Length` was greater than the maximum size, but did not check if it was negative. An attacker could bypass the check by providing a negative `Content-Length` (e.g., `-1`), which is less than the maximum limit, allowing an arbitrarily large payload to be buffered in memory.
**Learning:** When validating size limits, it's crucial to consider the entire range of potential integer values, including negative numbers, rather than just the upper bound.
**Prevention:** Always validate that size metrics (like `Content-Length`) are within the expected positive range (i.e., `>= 0`) in addition to checking the upper limit.
## 2024-05-24 - Rate Limiter Memory Exhaustion
**Vulnerability:** Implementing a custom in-memory rate limiter without capping the size of the tracking dictionary (e.g., maximum IPs tracked) creates a new memory exhaustion DoS vulnerability within the security middleware itself.
**Learning:** Security mechanisms must be designed with their own failure modes in mind. If an attacker spoofs IP addresses, an uncapped dictionary will grow indefinitely and crash the server.
**Prevention:** Always implement a hard cap on the size of in-memory data structures used for security tracking (e.g., `if len(rate_limit_store) > MAX_IPS: rate_limit_store.clear()`).

## 2025-04-12 - Proxy IP Rate Limiting (Denial of Service)
**Vulnerability:** The custom rate limiting middleware in FastAPI relied solely on `request.client.host` to identify the client IP. In a serverless deployment like Vercel (or behind any reverse proxy), this resulted in identifying all clients as the same proxy IP. This caused a Denial of Service (DoS) where rate limits were triggered for all legitimate users based on combined traffic, rather than per-user traffic.
**Learning:** When deploying applications behind reverse proxies or CDNs, `request.client.host` is insufficient for IP-based security mechanisms. It will always return the IP of the proxy itself.
**Prevention:** Always extract the actual client IP from the `X-Forwarded-For` header (or similar trusted headers injected by the proxy infrastructure) when implementing rate limiting or IP blocking.

## 2025-05-15 - Rate Limiter IP Spoofing Bypass
**Vulnerability:** The rate limiter relied on `request.headers.get("X-Forwarded-For").split(",")[0].strip()` to determine the client IP. An attacker could spoof the `X-Forwarded-For` header by prepending arbitrary IP addresses (e.g., `X-Forwarded-For: spoofed_ip, real_ip`). Since the 0th element was taken, the system incorrectly identified the client as the untrusted spoofed IP, allowing rate limits to be bypassed.
**Learning:** When deployed behind reverse proxies (like Vercel), the actual client IP is typically appended to the end of the `X-Forwarded-For` list. Extracting the first element from this list trusts potentially spoofed user input rather than the infrastructure-appended value.
**Prevention:** To prevent IP spoofing in environments where the real client IP is appended by a trusted reverse proxy, extract the rightmost IP address (e.g., `split(",")[-1].strip()`) from the `X-Forwarded-For` header.
## 2024-05-28 - Unpinned Dependencies Supply Chain Risk
**Vulnerability:** `requirements.txt` contained unpinned dependencies.
**Learning:** This is a supply chain security risk because a compromised new version of a dependency, or a broken update, will be automatically installed during the next build or deployment, potentially introducing vulnerabilities or bringing down the application. Note: Do not use `pip freeze` from the AI sandbox environment to determine and pin dependency versions in `requirements.txt`. The sandbox environment contains mocked or inaccurate package versions which will introduce build regressions.
**Prevention:** Always pin dependencies to specific, verified versions in `requirements.txt` or use a lockfile.

## 2026-04-13 - Rate Limiter Capacity Flooding Bypass
**Vulnerability:** The in-memory rate limiter implemented in FastAPI cleared the entire `rate_limit_store` using `.clear()` whenever the tracked IPs reached `MAX_IPS`. An attacker could spoof IPs or use a distributed attack to rapidly flood the store. This would trigger the reset condition, wiping out all active rate limit counters and completely bypassing the rate limits for themselves and all other users.
**Learning:** Security mechanisms (like rate limiters) must be designed with their own failure modes in mind. If an attacker can predictably trigger a reset state that fails open, the entire mechanism can be bypassed.
**Prevention:** Instead of clearing the entire security tracking store upon reaching maximum capacity, selectively evict expired/stale entries to reclaim memory. If the store remains full and cannot evict anything, reject the request with a `503 Service Unavailable` rather than abandoning the tracking altogether.

## 2026-03-27 - Disable Default OpenAPI Documentation Endpoints
**Vulnerability:** Information Disclosure
**Learning:** FastAPI automatically generates and exposes `/docs`, `/redoc`, and `/openapi.json` endpoints by default. In a production environment, this can inadvertently leak the API's internal structure, parameter requirements, and validation rules to potential attackers, facilitating reconnaissance.
**Prevention:** Always explicitly disable these endpoints in production by initializing `FastAPI(docs_url=None, redoc_url=None, openapi_url=None)`.

## 2026-04-13 - Rate Limiter Bypass via Multiple X-Forwarded-For Headers
**Vulnerability:** The rate limiter relied on `request.headers.get("X-Forwarded-For")` to extract the client IP. In FastAPI/Starlette, `.get()` only returns the value of the *first* matching header. If an attacker sends a spoofed `X-Forwarded-For` header, and the reverse proxy (e.g., Vercel) injects a *second* `X-Forwarded-For` header containing the real IP, the application only reads the attacker's spoofed header. This completely bypassed the rate limit, allowing DoS.
**Learning:** HTTP allows multiple headers with the same name. Reverse proxies may append their values as a comma-separated list to the existing header, or they may inject a completely new header row. Framework methods like `.get()` often arbitrarily return the first occurrence, ignoring subsequent headers.
**Prevention:** Always use `.getlist("X-Forwarded-For")` (or equivalent) to retrieve all header values, join them into a single string, and then parse the rightmost IP address to ensure you extract the proxy-appended value regardless of how the proxy formatted the injection.

## 2026-04-14 - Transfer-Encoding Multiple Headers Bypass
**Vulnerability:** The server was vulnerable to memory exhaustion DoS via `Transfer-Encoding: chunked`. While there was a check for chunked encoding, it only retrieved the first `Transfer-Encoding` header using `request.headers.get("transfer-encoding")`. If a client sent multiple `Transfer-Encoding` headers (e.g., `Transfer-Encoding: identity` and `Transfer-Encoding: chunked`), the check would only process the first one (`identity`), allowing the `chunked` payload to bypass the check and be buffered in memory, leading to exhaustion.
**Learning:** HTTP headers can appear multiple times in a request, and frameworks often provide methods like `.get()` that only return the first occurrence. Relying on `.get()` for security checks on headers that can have multiple values is a bypass risk.
**Prevention:** Always use `.getlist()` (or equivalent) to retrieve all values of a header when performing security validations to ensure no values are missed, especially for headers like `Transfer-Encoding` or `X-Forwarded-For`.

## 2024-05-28 - Multiple Content-Length Bypass
**Vulnerability:** A Denial of Service (DoS) vulnerability via memory exhaustion could occur because the payload size limit middleware checked `request.headers.get("content-length")` or `request.headers["content-length"]`. In FastAPI/Starlette, this only retrieves the first instance of the header. An attacker could bypass the check by providing a small value in the first `Content-Length` header (which passes the validation) and a huge value in a subsequent `Content-Length` header (which gets buffered into memory).
**Learning:** HTTP allows multiple headers with the same name. Framework methods like `.get()` often arbitrarily return the first occurrence, ignoring subsequent headers.
**Prevention:** Always use `getlist("content-length")` (or equivalent) to retrieve all header values, iterate over them, and apply the validation logic to all instances to ensure no bypasses occur.
