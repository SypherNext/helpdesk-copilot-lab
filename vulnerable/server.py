"""Builds the vulnerable Helpdesk Copilot and serves it on 127.0.0.1 only.

DELIBERATELY INSECURE PRACTICE APP. Never expose it to a network.
Run it from the repository root with:  python -m vulnerable.server
"""
import uvicorn

from common import config
from common.knowledge import KnowledgeBase
from common.llm import OllamaClient
from common.mailer import MailpitMailer
from common.store import OrderStore
from common.tooling import ToolBox

from .agent import Copilot
from .remote_tools import RemoteTools
from .tools import LocalTools
from .web import create_app


def build(model=None, mailer=None, remote_tools=None):
    """Wire the app together. Tests pass fakes for the model, mailer and remote tools."""
    store = OrderStore()
    customer = store.find_customer(config.SIGNED_IN_CUSTOMER_ID)
    providers = [LocalTools(store, mailer or MailpitMailer(), customer["id"])]
    providers.append(remote_tools if remote_tools is not None else RemoteTools())
    copilot = Copilot(model or OllamaClient(), KnowledgeBase(), ToolBox(providers), customer)
    return create_app(copilot, store), copilot, store


if __name__ == "__main__":
    app, _, _ = build()
    print(f"Helpdesk Copilot (VULNERABLE practice app) on http://{config.BIND_HOST}:{config.VULNERABLE_PORT}")
    print("Never expose this app to a network.")
    uvicorn.run(app, host=config.BIND_HOST, port=config.VULNERABLE_PORT, log_level="warning")
