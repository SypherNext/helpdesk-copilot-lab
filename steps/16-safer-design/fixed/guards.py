"""Checks on what goes into and comes out of the model (lesson 15).

None of these checks is perfect on its own. Each one removes a kind of attack,
and together with the tool limits in tools.py they make an attack much harder.
"""
import re
from urllib.parse import urlparse

from common import config

# A marker placed in the system prompt. It is not a secret: if it ever shows
# up in an answer, the prompt is leaking and the answer is withheld.
PROMPT_CANARY = "canary-7Q2X"

BLOCKED_REPLY = "Sorry, I can't help with that request."
WITHHELD_REPLY = "Sorry, I can't share that."

# Phrases that often show up in injection attempts. They are only a signal for
# the event log (lesson 17): rewording gets past any list like this.
SUSPICIOUS_PHRASES = (
    "ignore previous instructions",
    "ignore all previous instructions",
    "system prompt",
    "your instructions",
    "new rule",
    "house rule",
    "word for word",
)

HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
INVISIBLE_CHARACTERS = re.compile("[​‌‍⁠﻿]")
MARKDOWN_LINK = re.compile(r"!?\[([^\]]*)\]\(([^)\s]+)\)")
BARE_URL = re.compile(r"https?://[^\s)\"'<>]+")
PHONE_NUMBER = re.compile(r"\+\d{2} \d{3} \d{4}")
EMAIL_ADDRESS = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")


def check_input(message):
    """Return a reason string when the message is blocked, otherwise None."""
    if len(message) > config.MAX_MESSAGE_LENGTH:
        return "message too long"
    return None


def suspicious_phrases(message):
    lowered = message.lower()
    return [phrase for phrase in SUSPICIOUS_PHRASES if phrase in lowered]


def mark_untrusted(name, text):
    """Strip text a person reading the article cannot see, then label it as data."""
    visible = INVISIBLE_CHARACTERS.sub("", HTML_COMMENT.sub("", text)).strip()
    return f'<untrusted_article name="{name}">\n{visible}\n</untrusted_article>'


def _trusted(url):
    return urlparse(url).hostname in config.TRUSTED_LINK_HOSTS


def check_output(text, customer):
    """Return (text that may be shown, list of what was changed)."""
    if PROMPT_CANARY.lower() in text.lower():
        return WITHHELD_REPLY, ["prompt canary in answer"]
    findings = []

    def drop_link(match):
        if _trusted(match.group(2)):
            return match.group(0)
        findings.append(f"link removed: {match.group(2)}")
        return "[link removed]"

    def drop_url(match):
        if _trusted(match.group(0)):
            return match.group(0)
        findings.append(f"link removed: {match.group(0)}")
        return "[link removed]"

    def keep_official_phone(match):
        if match.group(0) == config.OFFICIAL_SUPPORT_PHONE:
            return match.group(0)
        findings.append(f"phone number replaced: {match.group(0)}")
        return config.OFFICIAL_SUPPORT_PHONE

    def keep_own_email(match):
        if match.group(0).lower() == customer["email"].lower():
            return match.group(0)
        findings.append(f"email address removed: {match.group(0)}")
        return "[email removed]"

    text = MARKDOWN_LINK.sub(drop_link, text)
    text = BARE_URL.sub(drop_url, text)
    text = PHONE_NUMBER.sub(keep_official_phone, text)
    text = EMAIL_ADDRESS.sub(keep_own_email, text)
    return text, findings
