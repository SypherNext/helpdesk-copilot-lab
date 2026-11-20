"""The Helpdesk Copilot: search the knowledge base, ask the model, run its tool calls."""
import json

from common import config

from . import guards, prompts, render


def _arguments(call):
    arguments = call["function"].get("arguments") or {}
    # Some models send the arguments as a JSON string instead of an object.
    return json.loads(arguments) if isinstance(arguments, str) else arguments


class Copilot:
    def __init__(self, model, knowledge, toolbox, customer):
        self.model = model
        self.knowledge = knowledge
        self.toolbox = toolbox
        self.customer = customer

    def answer(self, question):
        blocked = guards.check_input(question)
        if blocked:
            return self._result(guards.BLOCKED_REPLY, [], [], blocked, [])
        articles = self.knowledge.search(question)
        messages = prompts.build_messages(self.customer, articles, question)
        tool_calls = []
        reply = self.model.chat(messages, tools=self.toolbox.specs())
        for _ in range(config.MAX_TOOL_ROUNDS):
            calls = reply.get("tool_calls") or []
            if not calls:
                break
            messages.append(reply)
            for call in calls:
                name, arguments = call["function"]["name"], _arguments(call)
                result = self.toolbox.run(name, arguments)
                tool_calls.append({"name": name, "arguments": arguments, "result": result})
                messages.append({"role": "tool", "tool_name": name, "content": json.dumps(result)})
            reply = self.model.chat(messages, tools=self.toolbox.specs())
        text, output_changes = guards.check_output(reply.get("content") or "", self.customer)
        return self._result(text, tool_calls, articles, None, output_changes)

    def _result(self, text, tool_calls, articles, blocked, output_changes):
        return {
            "reply": text,
            "html": render.to_html(text),
            "tool_calls": tool_calls,
            "articles": [article["name"] for article in articles],
            "blocked": blocked,
            "output_changes": output_changes,
        }
