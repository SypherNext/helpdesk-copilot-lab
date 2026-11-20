"""Turns the attack catalog into promptfoo test cases, so the attacks live in one place."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from attacks.catalog import ATTACKS  # noqa: E402


def create_tests():
    return [
        {
            "description": f"L{attack.lesson:02d} {attack.name} ({attack.owasp})",
            "vars": {"message": attack.message, "attack": attack.name},
            "assert": [{"type": "python", "value": "file://grade.py"}],
        }
        for attack in ATTACKS
    ]
