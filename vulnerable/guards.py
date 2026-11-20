"""Checks on what goes into and comes out of the model.

FLAW (lesson 7): the only check is a short list of banned phrases. Anyone who
rewords the request walks past it. Output is not checked at all.
"""
BANNED_PHRASES = (
    "ignore previous instructions",
    "ignore all previous instructions",
    "system prompt",
    "discount code",
)

BLOCKED_REPLY = "Sorry, I can't help with that request."


def check_input(message):
    """Return a reason string when the message is blocked, otherwise None."""
    lowered = message.lower()
    for phrase in BANNED_PHRASES:
        if phrase in lowered:
            return f"banned phrase: {phrase}"
    return None


def check_output(text, customer):
    """Return (text that may be shown, list of what was changed). Here: nothing changes."""
    return text, []
