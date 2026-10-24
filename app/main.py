from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import os

from utils.scanner import LabelScanner

app = FastAPI(title="MSIP Label Scanner", version="1.0.0")

# Setup paths
BASE_DIR = Path(__file__).parent.parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

scanner = LabelScanner()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "results": None})

@app.post("/scan", response_class=HTMLResponse)
async def scan_files(request: Request, files: list[UploadFile] = File(...)):
    try:
        results = scanner.scan_files(files)
        return templates.TemplateResponse("results.html", {"request": request, "results": results})
    except Exception as e:
        return templates.TemplateResponse("results.html", {"request": request, "results": [], "error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
