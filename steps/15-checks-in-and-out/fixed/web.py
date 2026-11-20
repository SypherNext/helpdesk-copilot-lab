"""HTTP routes. Each one only translates between HTTP and the Copilot."""
from fastapi import HTTPException
from pydantic import BaseModel, Field

from common import config
from common.web import create_base_app

# FIX (lesson 15): even if HTML slips through, the browser refuses inline
# scripts and event handlers and loads images only from this app.
SECURITY_HEADERS = {
    "Content-Security-Policy": "default-src 'self'; img-src 'self'; script-src 'self'; style-src 'self'; "
                               "object-src 'none'; base-uri 'none'; frame-ancestors 'none'",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
}


class ChatRequest(BaseModel):
    # FIX (lesson 15): very long messages are refused before they reach the model.
    message: str = Field(min_length=1, max_length=config.MAX_MESSAGE_LENGTH)


def create_app(copilot, store):
    app = create_base_app("fixed", copilot.customer)

    @app.middleware("http")
    async def add_security_headers(request, call_next):
        response = await call_next(request)
        response.headers.update(SECURITY_HEADERS)
        return response

    @app.post("/api/chat")
    def chat(request: ChatRequest):
        return copilot.answer(request.message)

    @app.get("/api/refunds")
    def refunds():
        return {"refunds": store.refunds()}

    return app
