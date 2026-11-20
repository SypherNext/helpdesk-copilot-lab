"""The parts of the web layer both apps share: the chat page and its files."""
import pathlib

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

STATIC_DIR = pathlib.Path(__file__).resolve().parent / "static"


def create_base_app(label, customer):
    """label is 'vulnerable' or 'fixed'; the page shows it in its banner."""
    app = FastAPI(title=f"Helpdesk Copilot ({label})")
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/")
    def chat_page():
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/api/info")
    def info():
        return {"app": label, "customer": customer["name"], "customer_id": customer["id"]}

    return app
