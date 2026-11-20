"""Send one attack from the catalog to a lab app several times and count how often it works.

Usage, from the repository root:
  python -m attacks.run l06-prompt-leak --app vulnerable --tries 10
Every answer is saved to attacks/runs/<attack>-<app>.jsonl so you can read
the real replies later.
"""
import argparse
import json
import pathlib

import httpx

from common import config

from .catalog import BY_NAME

APP_URLS = {
    "vulnerable": f"http://{config.BIND_HOST}:{config.VULNERABLE_PORT}",
    "fixed": f"http://{config.BIND_HOST}:{config.FIXED_PORT}",
}
RUNS_DIR = pathlib.Path(__file__).resolve().parent / "runs"
PREVIEW_CHARACTERS = 110


def ask(app, message):
    response = httpx.post(f"{APP_URLS[app]}/api/chat", json={"message": message},
                          timeout=config.MODEL_TIMEOUT_SECONDS * 3)
    if response.status_code != 200:
        # The fixed app answers some messages with an HTTP error instead of a chat reply.
        return {"reply": "", "html": "", "tool_calls": [], "articles": [], "blocked": f"HTTP {response.status_code}"}
    return response.json()


def preview(answer):
    if answer["blocked"]:
        return f"blocked ({answer['blocked']})"
    text = " ".join(answer["reply"].split())
    return text[:PREVIEW_CHARACTERS] + ("..." if len(text) > PREVIEW_CHARACTERS else "")


def run(attack, app, tries):
    RUNS_DIR.mkdir(exist_ok=True)
    log_path = RUNS_DIR / f"{attack.name}-{app}.jsonl"
    print(f"attack {attack.name} ({attack.owasp}) against {app}, {tries} tries")
    worked = 0
    with log_path.open("w", encoding="utf-8") as log:
        for number in range(1, tries + 1):
            answer = ask(app, attack.message)
            success = attack.worked(answer)
            worked += success
            log.write(json.dumps({"try": number, "worked": success, **answer}) + "\n")
            print(f"try {number:>2}: {'WORKED' if success else 'held  '} | {preview(answer)}")
    print(f"worked {worked} of {tries} tries")
    return worked


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("attack", choices=sorted(BY_NAME))
    parser.add_argument("--app", choices=sorted(APP_URLS), default="vulnerable")
    parser.add_argument("--tries", type=int, default=5)
    arguments = parser.parse_args()
    run(BY_NAME[arguments.attack], arguments.app, arguments.tries)


if __name__ == "__main__":
    main()
