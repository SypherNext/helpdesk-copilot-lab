"""Every setting the lab uses, in one place.

Both apps (vulnerable/ and fixed/), the tool server, the attack scripts and the
tests read their addresses and limits from here, so a port or model change is
made once. Each value can be overridden with an environment variable of the
same name.
"""
import os
import pathlib


def _setting(name, default):
    return os.environ.get(name, default)


def _int_setting(name, default):
    return int(os.environ.get(name, default))


# Everything listens on the loopback address only. The vulnerable app must
# never be reachable from another machine.
BIND_HOST = "127.0.0.1"

VULNERABLE_PORT = _int_setting("VULNERABLE_PORT", "18920")
FIXED_PORT = _int_setting("FIXED_PORT", "18921")
TOOL_SERVER_PORT = _int_setting("TOOL_SERVER_PORT", "18925")
ATTACKER_SITE_PORT = _int_setting("ATTACKER_SITE_PORT", "18926")

# Docker containers started by scripts/start-services.sh
OLLAMA_URL = _setting("OLLAMA_URL", "http://127.0.0.1:18930")
MAILPIT_SMTP_HOST = _setting("MAILPIT_SMTP_HOST", "127.0.0.1")
MAILPIT_SMTP_PORT = _int_setting("MAILPIT_SMTP_PORT", "18931")
MAILPIT_API_URL = _setting("MAILPIT_API_URL", "http://127.0.0.1:18932")

MODEL = _setting("MODEL", "qwen3:1.7b")

# Fixed sampling settings make runs easier to compare. They do not make the
# model fully repeatable, which is why every attack is run several times.
MODEL_OPTIONS = {
    "temperature": 0.2,
    "num_ctx": 4096,
    "num_predict": 400,
}
MODEL_TIMEOUT_SECONDS = 180

# How many knowledge base articles are put in front of the model per question.
# One keeps the prompt short, which matters on a CPU.
SEARCH_RESULTS = 1

# The agent stops after this many tool calls in one answer, so a confused
# model cannot loop forever.
MAX_TOOL_ROUNDS = 4

COMPANY_NAME = "Brightkettle"
SUPPORT_SENDER = "support@brightkettle.test"
OFFICIAL_SUPPORT_PHONE = "+00 555 0100"

# The lab has no login page: every chat is from this fake customer. The
# server decides who is signed in, never the model or the chat message.
SIGNED_IN_CUSTOMER_ID = _setting("SIGNED_IN_CUSTOMER_ID", "C-1001")

# Statuses an order can have. The fixed app accepts only these in searches.
ORDER_STATUSES = ("processing", "shipped", "delivered")

# Fixed app only: the longest chat message it accepts, in characters.
MAX_MESSAGE_LENGTH = 2000

# Fixed app only: links and images in answers may point only at these hosts.
# Empty means no outside links or images at all.
TRUSTED_LINK_HOSTS = ()

TOOL_SERVER_URL = f"http://{BIND_HOST}:{TOOL_SERVER_PORT}/mcp"

# Fixed app only: the remote tools it accepts, each pinned to the SHA-256 hash
# of the definition (name, description, parameters) a person reviewed.
PINNED_REMOTE_TOOLS = {
    "check_shipping_status": "c681ff36216e7a774ea7d7e836ccc7520775729a2b8275b25e16a7e3b76ec839",
}

# Fixed app only: security events (lesson 17) are appended here as JSON lines.
EVENT_LOG_PATH = _setting("EVENT_LOG_PATH", str(pathlib.Path(__file__).resolve().parent.parent / "logs" / "events.jsonl"))
