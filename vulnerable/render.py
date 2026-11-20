"""Turns the model's markdown answer into HTML for the chat page."""
import re

IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)")
LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
BOLD = re.compile(r"\*\*([^*]+)\*\*")


def to_html(markdown_text):
    # FLAW (lessons 9 and 11): the model's text is not escaped, so any HTML it
    # writes runs in the page, and images load from any address.
    html = IMAGE.sub(r'<img alt="\1" src="\2">', markdown_text)
    html = LINK.sub(r'<a href="\2">\1</a>', html)
    html = BOLD.sub(r"<strong>\1</strong>", html)
    return html.replace("\n", "<br>")
