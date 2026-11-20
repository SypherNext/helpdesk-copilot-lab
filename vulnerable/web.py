"""HTTP routes. Each one only translates between HTTP and the Copilot."""
from pydantic import BaseModel

from common.web import create_base_app


class ChatRequest(BaseModel):
    message: str


def create_app(copilot, store):
    app = create_base_app("vulnerable", copilot.customer)

    @app.post("/api/chat")
    def chat(request: ChatRequest):
        return copilot.answer(request.message)

    @app.get("/api/refunds")
    def refunds():
        return {"refunds": store.refunds()}

    return app
