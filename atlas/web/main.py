import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse

from .api.v1.query import router as query_router

logging.basicConfig(
    level=logging.INFO
)
app = FastAPI(
    title="CodeAtlas+Dev API",
    description="Developer API for querying relational, vector, graph databases, and LLMs.",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware, # type: ignore
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="atlas/web/static"), name="static")
templates = Jinja2Templates(directory="atlas/web/templates")

app.include_router(query_router, prefix="/api/v1")

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})