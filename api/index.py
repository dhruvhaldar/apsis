from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Annotated

from apsis.calculus_of_variations import solve_pmp_linear_quadratic
from apsis.lqr import solve_lqr
from apsis.mpc import solve_mpc

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

Row = Annotated[List[float], Field(max_length=20)]
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
    tf: float = Field(..., gt=0, le=1000)
    num_points: int = Field(100, ge=2, le=1000)

class MPCRequest(BaseModel):
    A: Matrix
    B: Matrix
    Q: Matrix
    R: Matrix
    x0: Row
    N_horizon: int = Field(..., gt=0, le=200)
    dt: float = Field(..., gt=0, le=100)
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
        raise HTTPException(status_code=400, detail=str(e))

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
        raise HTTPException(status_code=400, detail=str(e))

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
        raise HTTPException(status_code=400, detail=str(e))
