import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from .models import AnalyzeRequest, AnalyzeResponse
from .agent import run_agent

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from .models import AnalyzeRequest, AnalyzeResponse
from .agent import run_agent

load_dotenv()

app = FastAPI(title="FinSight AI-Powered Personal Finance Advisor", version="0.1.0")

origins = os.getenv("CORS_ORIGINS", "http://localhost:8000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"ok": True}

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(data: AnalyzeRequest):
    result = await run_agent(data.model_dump())
    return result

# Mount frontend AFTER defining API routes
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


@app.get("/health")
async def health():
    return {"ok": True}

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(data: AnalyzeRequest):
    # data is validated by Pydantic
    result = await run_agent(data.model_dump())
    return result
