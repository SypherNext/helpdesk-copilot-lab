"""HTTP routes. Each one only translates between HTTP and the Copilot."""
from fastapi import HTTPException
from pydantic import BaseModel, Field

from common import config
from common.web import create_base_app

from .tools import REFUND_AWAITING_APPROVAL

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


def create_app(copilot, store, events):
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

    # FIX (lesson 16): the human approval step. In a real system these two
    # routes sit behind a staff login; the lab has no staff accounts.
    @app.get("/api/approvals")
    def approvals():
        return {"awaiting_approval": store.refunds(REFUND_AWAITING_APPROVAL)}

    @app.post("/api/approvals/{refund_id}/{decision}")
    def decide(refund_id: int, decision: str):
        if decision not in ("approve", "reject"):
            raise HTTPException(status_code=404)
        waiting = {refund["id"] for refund in store.refunds(REFUND_AWAITING_APPROVAL)}
        if refund_id not in waiting:
            raise HTTPException(status_code=404, detail="no refund waiting with that id")
        state = "paid" if decision == "approve" else "rejected"
        store.set_refund_state(refund_id, state)
        events.record("refund_decided", refund_id=refund_id, state=state)
        return {"refund_id": refund_id, "state": state}

    return app
