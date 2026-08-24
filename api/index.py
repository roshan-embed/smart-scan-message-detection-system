import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn

from detector import analyze_message
from url_analyzer import analyze_url
from scenarios import get_scenarios

app = FastAPI(title="Smart Scam Detector API")

# Allow CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    text: str
    channel: str = "Unknown"

class UrlAnalyzeRequest(BaseModel):
    url: str

@app.post("/api/analyze")
def api_analyze_message(req: AnalyzeRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    result = analyze_message(req.text, req.channel)
    return result

@app.post("/api/analyze-url")
def api_analyze_url(req: UrlAnalyzeRequest):
    if not req.url.strip():
        raise HTTPException(status_code=400, detail="URL cannot be empty.")
    result = analyze_url(req.url)
    return result

@app.get("/api/scenarios")
def api_get_scenarios():
    return get_scenarios()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
