"""Shared test helpers. Run the same tests against either app:

  python -m pytest tests --app vulnerable    (every test fails: the flaws are there)
  python -m pytest tests --app fixed         (every test passes: the fixes hold)

The tests never call the real model. A scripted fake model returns the tool
calls a successful attack would produce, so each test checks the app's own
code, which is what the fix changed, and gives the same result every run.
"""
import importlib
import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from common.mailer import RecordingMailer  # noqa: E402


def pytest_addoption(parser):
    parser.addoption("--app", default="fixed", help="path to the app package: vulnerable, fixed or a steps/ copy")


class ScriptedModel:
    """Returns the given replies in order, like a model that always falls for the attack."""

    def __init__(self, *replies):
        self.replies = list(replies)
        self.seen = []

    def chat(self, messages, tools=None):
        self.seen.append({"messages": [dict(message) for message in messages], "tools": tools})
        return self.replies.pop(0) if self.replies else {"role": "assistant", "content": "Done."}


def say(text):
    return {"role": "assistant", "content": text}


def call_tool(name, **arguments):
    return {"role": "assistant", "content": "", "tool_calls": [{"function": {"name": name, "arguments": arguments}}]}


class NoRemoteTools:
    def specs(self):
        return []

    def run(self, name, arguments):
        return None


@pytest.fixture(scope="session")
def app_package(request):
    path = (REPO_ROOT / request.config.getoption("--app")).resolve()
    sys.path.insert(0, str(path.parent))
    return importlib.import_module(path.name)


@pytest.fixture
def build(app_package, tmp_path):
    """build(model, remote_tools=None) -> (copilot, store, mailer)"""
    server = importlib.import_module(f"{app_package.__name__}.server")

    def make(model, remote_tools=None):
        mailer = RecordingMailer()
        options = {"model": model, "mailer": mailer, "remote_tools": remote_tools or NoRemoteTools()}
        if "events" in server.build.__code__.co_varnames:
            events_module = importlib.import_module(f"{app_package.__name__}.events")
            options["events"] = events_module.EventLog(tmp_path / "events.jsonl")
        _, copilot, store = server.build(**options)
        return copilot, store, mailer

    return make


@pytest.fixture
def module(app_package):
    """module('render') imports render.py from the app under test."""
    return lambda name: importlib.import_module(f"{app_package.__name__}.{name}")
