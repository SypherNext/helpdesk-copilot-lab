"""Summarise the security event log and raise alerts (lesson 17).

Run from the repository root:  python -m fixed.report
"""
import collections

from .events import EventLog

# Kinds of event that mean an attack was probably attempted.
ATTACK_SIGNALS = {"input_suspicious", "output_changed", "tool_refused", "remote_tool_refused"}
# Raise an alert when this many attack signals appear in the log.
ALERT_THRESHOLD = 3


def summarise(events):
    counts = collections.Counter(event["kind"] for event in events)
    alerts = []
    signals = sum(counts[kind] for kind in ATTACK_SIGNALS)
    if signals >= ALERT_THRESHOLD:
        alerts.append(f"{signals} attack signals in the log (threshold {ALERT_THRESHOLD})")
    if counts["remote_tool_refused"]:
        alerts.append("a remote tool was refused: review the tool server before trusting it again")
    if counts["refund_requested"]:
        alerts.append(f"{counts['refund_requested']} refund(s) waiting for a person to approve")
    return counts, alerts


def main():
    events = EventLog().read()
    counts, alerts = summarise(events)
    print(f"{len(events)} events")
    for kind, number in sorted(counts.items()):
        print(f"  {kind:<22} {number}")
    print("alerts:" if alerts else "alerts: none")
    for alert in alerts:
        print(f"  ALERT {alert}")


if __name__ == "__main__":
    main()
