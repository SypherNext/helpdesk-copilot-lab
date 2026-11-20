"""Turns the model's markdown answer into HTML for the chat page."""
import html
import re

BOLD = re.compile(r"\*\*([^*]+)\*\*")


def to_html(markdown_text):
    # FIX (lesson 15): escape first, so anything the model writes is shown as
    # text and never runs. Links and images were already removed by
    # guards.check_output, so only bold and line breaks are turned into HTML.
    safe = html.escape(markdown_text)
    safe = BOLD.sub(r"<strong>\1</strong>", safe)
    return safe.replace("\n", "<br>")
