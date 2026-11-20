"""Security event log (lesson 17): one JSON object per line.

The log records what happened (a check fired, a tool ran, a tool was refused),
never the customer's full messages or personal details, so the log itself does
not become a second copy of private data.
"""
import datetime
import json
import pathlib

from common import config


class EventLog:
    def __init__(self, path=config.EVENT_LOG_PATH):
        self.path = pathlib.Path(path)

    def record(self, kind, **details):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        event = {"time": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), "kind": kind, **details}
        with self.path.open("a", encoding="utf-8") as log:
            log.write(json.dumps(event) + "\n")

    def read(self):
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]


class NoEventLog:
    """Stand-in for tests that do not look at events."""

    def record(self, kind, **details):
        pass
