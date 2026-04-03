from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import logging
from pydantic import BaseModel, Field
from typing import List, Optional, Annotated

from apsis.calculus_of_variations import solve_pmp_linear_quadratic
from apsis.lqr import solve_lqr
from apsis.mpc import solve_mpc

logger = logging.getLogger(__name__)

app = FastAPI()

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

# 🛡️ Sentinel Security Enhancement: Prevent DoS via large request payloads
# FastAPI/Starlette reads the entire request body into memory by default.
# Enforcing a strict content-length limit prevents attackers from causing
# Out-Of-Memory (OOM) crashes by sending massive payloads.
@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > 1048576: # 1MB limit
        return Response(content="Payload Too Large", status_code=413)
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
            "eigvals": [complex(e).real for e in eigvals] # Returning real parts for simplicity or parse complex
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
