"""Tools from the parcel partner's tool server (JSON-RPC, MCP style)."""
import hashlib
import json

import httpx

from common import config
from common.tooling import function_spec


def definition_hash(tool):
    """SHA-256 of the parts the model reads: name, description and parameters."""
    reviewed_parts = {key: tool[key] for key in ("name", "description", "inputSchema")}
    return hashlib.sha256(json.dumps(reviewed_parts, sort_keys=True).encode("utf-8")).hexdigest()


class RemoteTools:
    def __init__(self, url=config.TOOL_SERVER_URL, client=None, pinned=config.PINNED_REMOTE_TOOLS, on_refused=None):
        self.url = url
        # Tests pass a client that talks to the tool server in memory.
        self.client = client or httpx.Client(timeout=10)
        self.pinned = pinned
        # Called with (tool name, reason) for every tool that is not accepted.
        self.on_refused = on_refused or (lambda name, reason: None)
        self._tools = None

    def _call(self, method, params=None):
        request = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}
        response = self.client.post(self.url, json=request)
        response.raise_for_status()
        return response.json()["result"]

    def _accepted(self, tool):
        # FIX (lesson 13): only tools a person reviewed, with exactly the
        # definition that was reviewed. Any change to it is refused.
        if tool["name"] not in self.pinned:
            self.on_refused(tool["name"], "not on the allowlist")
            return False
        if definition_hash(tool) != self.pinned[tool["name"]]:
            self.on_refused(tool["name"], "definition changed since it was reviewed")
            return False
        return True

    def _discover(self):
        if self._tools is None:
            try:
                offered = self._call("tools/list")["tools"]
            except httpx.HTTPError:
                print("Tool server not reachable; continuing without remote tools.")
                offered = []
            self._tools = [tool for tool in offered if self._accepted(tool)]
        return self._tools

    def specs(self):
        return [function_spec(tool["name"], tool["description"], tool["inputSchema"]["properties"],
                              tool["inputSchema"].get("required", ())) for tool in self._discover()]

    def run(self, name, arguments):
        if name not in {tool["name"] for tool in self._discover()}:
            return None
        return self._call("tools/call", {"name": name, "arguments": arguments})["structuredContent"]
