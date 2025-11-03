
from fastapi import FastAPI
from backend.services.diagnostic_router import router as diagnostic_router
app = FastAPI(title="RealDiag API")
@app.get("/health")
def health(): return {"ok": True}
app.include_router(diagnostic_router)
