from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import logging
import time
from pydantic import BaseModel, Field
from typing import List, Optional, Annotated, Dict

from apsis.calculus_of_variations import solve_pmp_linear_quadratic
from apsis.lqr import solve_lqr
from apsis.mpc import solve_mpc

logger = logging.getLogger(__name__)

app = FastAPI()

# ⚡ Bolt Optimization: Add GZip compression for large trajectory payloads (PMP, MPC).
# PMP/MPC endpoints return large JSON arrays. Applying GZip reduces response payload size by >60%,
# significantly improving network transfer times and rendering speed on slower connections.
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 🛡️ Sentinel Security Fix: Restrict CORS to specific origins and methods
# Overly permissive CORS ("*") allows any domain to make requests to the API.
# In a serverless setup like Vercel, the frontend and API share the same origin,
# so CORS is only strictly needed for local development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=False,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

# 🛡️ Sentinel Security Fix: Prevent memory exhaustion (DoS) by limiting request size.
# FastAPI buffers the entire request body in memory by default. An attacker could
# send a massive payload to crash the server. We enforce a 2MB limit.
MAX_PAYLOAD_SIZE = 2 * 1024 * 1024 # 2MB

@app.middleware("http")
async def limit_payload_size(request: Request, call_next):
    # 🛡️ Sentinel Security Fix: Reject chunked transfer encoding to prevent
    # bypassing the Content-Length limit and exhausting server memory.
    # We check for "chunked" in the header to handle mixed cases and multiple encodings.
    te_header = request.headers.get("transfer-encoding", "").lower()
    if "chunked" in te_header:
        return JSONResponse(status_code=411, content={"detail": "Chunked encoding not supported"})

    if "content-length" in request.headers:
        try:
            content_length = int(request.headers["content-length"])
        except ValueError:
            return JSONResponse(status_code=400, content={"detail": "Invalid Content-Length header"})

        if content_length < 0:
            return JSONResponse(status_code=400, content={"detail": "Invalid Content-Length header"})

        if content_length > MAX_PAYLOAD_SIZE:
            return JSONResponse(status_code=413, content={"detail": "Payload too large"})
    elif request.method not in ["GET", "HEAD", "OPTIONS"]:
        # 🛡️ Sentinel Security Fix: Enforce Content-Length for all requests that
        # could contain a body to prevent bypassing the size limit check.
        return JSONResponse(status_code=411, content={"detail": "Length Required"})

    return await call_next(request)

# 🛡️ Sentinel Security Enhancement: Application-Layer Rate Limiting
# The mathematical solvers are computationally intensive and vulnerable to CPU
# exhaustion DoS attacks. Limit requests per IP.
RATE_LIMIT_WINDOW = 60 # seconds
RATE_LIMIT_MAX_REQUESTS = 50
MAX_IPS = 10000

rate_limit_store: Dict[str, List[float]] = {}

@app.middleware("http")
async def rate_limit(request: Request, call_next):
    # Only rate limit the mathematical endpoints
    if not request.url.path.startswith("/api/"):
        return await call_next(request)

    client_ip = request.client.host if request.client else "unknown"
    current_time = time.time()

    # Prevent memory exhaustion in the rate limit store itself
    if len(rate_limit_store) > MAX_IPS:
        rate_limit_store.clear()

    if client_ip not in rate_limit_store:
        rate_limit_store[client_ip] = []

    # Filter out old requests
    requests = [req_time for req_time in rate_limit_store[client_ip] if current_time - req_time < RATE_LIMIT_WINDOW]

    if len(requests) >= RATE_LIMIT_MAX_REQUESTS:
        return JSONResponse(status_code=429, content={"detail": "Too many requests. Please try again later."})

    requests.append(current_time)
    rate_limit_store[client_ip] = requests

    return await call_next(request)

# 🛡️ Sentinel Security Enhancement: Add essential security headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' https://cdn.plot.ly https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; font-src https://cdn.jsdelivr.net; img-src 'self' data:; connect-src 'self' http://localhost:8000;"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response

# 🛡️ Sentinel Security Fix: Prevent NaN/Inf injection
# Pydantic v2 float types allow NaN/Inf by default. These values propagate into
# underlying numerical solvers (like SciPy and GEKKO), causing internal exceptions,
# infinite loops, or crashes. Enforce strict numeric validation for mathematical inputs.
SafeFloat = Annotated[float, Field(allow_inf_nan=False)]
Row = Annotated[List[SafeFloat], Field(max_length=20)]
Matrix = Annotated[List[Row], Field(max_length=20)]

class LQRRequest(BaseModel):
    A: Matrix
    B: Matrix
    Q: Matrix
    R: Matrix

class PMPRequest(BaseModel):
    A: Matrix
    B: Matrix
    Q: Matrix
    R: Matrix
    x0: Row
    xf: Row
    tf: SafeFloat = Field(..., gt=0, le=1000)
    num_points: int = Field(100, ge=2, le=1000)

class MPCRequest(BaseModel):
    A: Matrix
    B: Matrix
    Q: Matrix
    R: Matrix
    x0: Row
    N_horizon: int = Field(..., gt=0, le=200)
    dt: SafeFloat = Field(..., gt=0, le=100)
    u_min: Optional[Row] = None
    u_max: Optional[Row] = None

@app.post("/api/lqr")
def lqr_endpoint(req: LQRRequest):
    try:
        K, X, eigvals = solve_lqr(req.A, req.B, req.Q, req.R)
        return {
            "K": K.tolist(),
            "X": X.tolist(),
            # ⚡ Bolt Optimization: Use vectorized `.real.tolist()` to avoid python-level iteration overhead
            "eigvals": eigvals.real.tolist()
        }
    except Exception as e:
        logger.error(f"LQR Error: {e}")
        raise HTTPException(status_code=400, detail="An error occurred during LQR computation")

@app.post("/api/pmp")
def pmp_endpoint(req: PMPRequest):
    try:
        t, x_sol, u_sol, lam_sol = solve_pmp_linear_quadratic(
            req.A, req.B, req.Q, req.R, req.x0, req.xf, req.tf, req.num_points
        )
        return {
            "t": t.tolist(),
            "x": x_sol.tolist(),
            "u": u_sol.tolist(),
            "lambda": lam_sol.tolist()
        }
    except Exception as e:
        logger.error(f"PMP Error: {e}")
        raise HTTPException(status_code=400, detail="An error occurred during PMP computation")

@app.post("/api/mpc")
def mpc_endpoint(req: MPCRequest):
    try:
        t, x_sol, u_sol = solve_mpc(
            req.A, req.B, req.Q, req.R, req.x0, req.N_horizon, req.dt, req.u_min, req.u_max
        )
        return {
            "t": t.tolist(),
            "x": x_sol.tolist(),
            "u": u_sol.tolist()
        }
    except Exception as e:
        logger.error(f"MPC Error: {e}")
        raise HTTPException(status_code=400, detail="An error occurred during MPC computation")
