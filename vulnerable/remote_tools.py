"""Tools from the parcel partner's tool server (JSON-RPC, MCP style)."""
import httpx

from common import config
from common.tooling import function_spec


class RemoteTools:
    def __init__(self, url=config.TOOL_SERVER_URL, client=None):
        self.url = url
        # Tests pass a client that talks to the tool server in memory.
        self.client = client or httpx.Client(timeout=10)
        self._tools = None

    def _call(self, method, params=None):
        request = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}
        response = self.client.post(self.url, json=request)
        response.raise_for_status()
        return response.json()["result"]

    def _discover(self):
        if self._tools is None:
            try:
                self._tools = self._call("tools/list")["tools"]
            except httpx.HTTPError:
                print("Tool server not reachable; continuing without remote tools.")
                self._tools = []
        return self._tools

    def specs(self):
        # FLAW (lesson 13): whatever description the server sends goes straight
        # to the model, which reads it as instructions.
        return [function_spec(tool["name"], tool["description"], tool["inputSchema"]["properties"],
                              tool["inputSchema"].get("required", ())) for tool in self._discover()]

    def run(self, name, arguments):
        if name not in {tool["name"] for tool in self._discover()}:
            return None
        return self._call("tools/call", {"name": name, "arguments": arguments})["structuredContent"]
