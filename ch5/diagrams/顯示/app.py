from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

app = FastAPI(title="Mermaid Viewer")

templates = Jinja2Templates(directory="templates")

MERMAID_DIR = Path("diagrams")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    diagram_file = MERMAID_DIR / "sequence_diagram.mmd"

    if not diagram_file.exists():
        raise HTTPException(status_code=404, detail="Diagram not found")

    mermaid_text = diagram_file.read_text(encoding="utf-8")

    return templates.TemplateResponse(
        "mermaid.html",
        {
            "request": request,
            "diagram": mermaid_text,
            "filename": diagram_file.name,
        },
    )


@app.get("/diagram/{name}", response_class=HTMLResponse)
async def show_diagram(name: str, request: Request):

    file = MERMAID_DIR / f"{name}.mmd"

    if not file.exists():
        raise HTTPException(status_code=404, detail="Diagram not found")

    mermaid_text = file.read_text(encoding="utf-8")

    return templates.TemplateResponse(
        "mermaid.html",
        {
            "request": request,
            "diagram": mermaid_text,
            "filename": file.name,
        },
    )