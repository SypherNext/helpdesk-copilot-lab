"""Shared pieces for tools: the JSON schema format the model expects, and the
ToolBox that puts several tool providers behind one interface.

A tool provider is any object with two methods:
  specs()               -> list of tool descriptions for the model
  run(name, arguments)  -> dict result, or None if the provider has no such tool
The app's own tools and the remote tool server both follow it, so the agent
does not care where a tool lives.
"""


def function_spec(name, description, properties, required=()):
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {"type": "object", "properties": properties, "required": list(required)},
        },
    }


def text_param(description):
    return {"type": "string", "description": description}


def number_param(description):
    return {"type": "number", "description": description}


class ToolBox:
    def __init__(self, providers):
        self.providers = providers

    def specs(self):
        return [spec for provider in self.providers for spec in provider.specs()]

    def run(self, name, arguments):
        for provider in self.providers:
            result = provider.run(name, arguments)
            if result is not None:
                return result
        return {"error": f"unknown tool {name}"}
