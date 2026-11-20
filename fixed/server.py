"""Builds the fixed Helpdesk Copilot and serves it on 127.0.0.1 only.

Run it from the repository root with:  python -m fixed.server
"""
import uvicorn

from common import config
from common.knowledge import KnowledgeBase
from common.llm import OllamaClient
from common.mailer import MailpitMailer
from common.store import OrderStore
from common.tooling import ToolBox

from .agent import Copilot
from .events import EventLog
from .remote_tools import RemoteTools
from .tools import LocalTools
from .web import create_app


def build(model=None, mailer=None, remote_tools=None, events=None):
    """Wire the app together. Tests pass fakes for the model, mailer, remote tools and event log."""
    events = events or EventLog()
    store = OrderStore()
    customer = store.find_customer(config.SIGNED_IN_CUSTOMER_ID)
    if remote_tools is None:
        remote_tools = RemoteTools(on_refused=lambda name, reason: events.record("remote_tool_refused", tool=name, reason=reason))
    providers = [LocalTools(store, mailer or MailpitMailer(), customer["id"]), remote_tools]
    copilot = Copilot(model or OllamaClient(), KnowledgeBase(), ToolBox(providers), customer, events)
    return create_app(copilot, store, events), copilot, store


if __name__ == "__main__":
    app, _, _ = build()
    print(f"Helpdesk Copilot (fixed) on http://{config.BIND_HOST}:{config.FIXED_PORT}")
    uvicorn.run(app, host=config.BIND_HOST, port=config.FIXED_PORT, log_level="warning")
