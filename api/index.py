from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from apsis.calculus_of_variations import solve_pmp_linear_quadratic
from apsis.lqr import solve_lqr
from apsis.mpc import solve_mpc

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LQRRequest(BaseModel):
    A: List[List[float]]
    B: List[List[float]]
    Q: List[List[float]]
    R: List[List[float]]

class PMPRequest(BaseModel):
    A: List[List[float]]
    B: List[List[float]]
    Q: List[List[float]]
    R: List[List[float]]
    x0: List[float]
    xf: List[float]
    tf: float
    num_points: int = 100

class MPCRequest(BaseModel):
    A: List[List[float]]
    B: List[List[float]]
    Q: List[List[float]]
    R: List[List[float]]
    x0: List[float]
    N_horizon: int
    dt: float
    u_min: Optional[List[float]] = None
    u_max: Optional[List[float]] = None

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
