from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import httpx
from . import analyzer, rewriter, files, config

app = FastAPI(title="Ai-Humanizer")

class Req(BaseModel):
    text: str
    style: str = "academic"
    sample: str = ""

def _check(text):
    if len(text.split()) > config.MAX_WORDS:
        raise HTTPException(413, f"Max {config.MAX_WORDS} words.")

@app.get("/api/health")
async def health():
    try:
        async with httpx.AsyncClient(timeout=3) as c:
            tags = (await c.get(f"{config.OLLAMA_URL}/api/tags")).json()
        names = [m["name"] for m in tags.get("models", [])]
        return {"ollama": True, "model": config.MODEL, "model_installed": config.MODEL in names}
    except Exception:
        return {"ollama": False, "model": config.MODEL, "model_installed": False}

@app.post("/api/analyze")
async def analyze(r: Req):
    return analyzer.analyze(r.text)

@app.post("/api/humanize")
async def humanize(r: Req):
    _check(r.text)
    try:
        out = await rewriter.humanize(r.text, r.style, r.sample)
    except httpx.HTTPError:
        raise HTTPException(503, "Local model unavailable. Is Ollama running and the model pulled?")
    return {"text": out, "before": analyzer.analyze(r.text), "after": analyzer.analyze(out)}

@app.post("/api/extract")
async def extract(file: UploadFile = File(...)):
    try:
        return {"text": files.extract(file.filename, await file.read())}
    except ValueError as e:
        raise HTTPException(400, str(e))

@app.get("/")
def index():
    return FileResponse("app/static/index.html")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
