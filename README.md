# Helpdesk Copilot (AI security practice lab)

Helpdesk Copilot is a small support assistant for Brightkettle, a fictional company that sells kettles and tea. It answers questions from a knowledge base of help articles, looks up orders, issues refunds, sends email, and calls one outside tool server. It runs on Python with FastAPI and a small local language model (`qwen3:1.7b`) in Ollama. It is the companion code for the Sypher course "AI Security & Red Teaming".

The repository holds two copies of the app: `vulnerable/`, which is insecure on purpose so you can attack it lesson by lesson, and `fixed/`, the same app with every flaw fixed. Around them are the attack catalog and runner, a pretend attacker website, a deliberately compromised tool server, twelve security regression tests, a promptfoo configuration for automated red teaming, and a CI workflow.

## Read this first: safety

- The app in `vulnerable/` is **deliberately insecure**. It leaks its instructions, follows hidden instructions in documents, shows other customers' data, runs HTML from the model, builds SQL from model output, pays unlimited refunds and trusts any tool definition it is given. Treat it as a practice target, not as software.
- Every program in this repository binds to **127.0.0.1 only** (`config.BIND_HOST`), and the Docker containers publish their ports on 127.0.0.1 only. Only programs on your own computer can reach them. Do not change that, do not open the ports in a firewall, and never deploy either app.
- Point the attack scripts and promptfoo **only at the lab apps on your own machine**. Testing a system you do not own, without written permission, is illegal in most countries.
- All customers, orders, email addresses and phone numbers are fake. Email goes to Mailpit, a local mail catcher, and never leaves your computer. Addresses end in `.test`, a name reserved for testing.

## Set up your computer

You need Git, Python 3.12 or newer (the course was checked with 3.14), Docker, and Node.js 22.22 or newer for promptfoo in lesson 14. The local model needs about 2 GB of disk and runs on the CPU; a computer with 8 GB of free memory is enough.

On Windows, run the commands below in **Git Bash** (installed with Git). Where a command differs on Windows, both versions are shown.

| Tool | Windows | macOS | Ubuntu or Debian |
|---|---|---|---|
| Git | `winget install --id Git.Git -e` | `xcode-select --install` or `brew install git` | `sudo apt install -y git` |
| Python | `winget install Python.Python.3.14` | `brew install python@3.14` | `sudo apt install -y python3 python3-venv` |
| Docker | `winget install -e --id Docker.DockerDesktop` | `brew install --cask docker` | `curl -fsSL https://get.docker.com \| sh` |
| Node.js | `winget install OpenJS.NodeJS.LTS` | `brew install node` | install with nvm, then `nvm install --lts` |

Check them (`python` is `python3` on macOS and Linux):

```bash
git --version
python --version
docker version --format 'Docker Engine {{.Server.Version}}'
node --version
```

## Get the code and install

```bash
git clone <helpdesk-copilot-lab repository URL> helpdesk-copilot-lab
cd helpdesk-copilot-lab
python -m venv .venv
```

Activate the virtual environment and install the four dependencies:

```bash
source .venv/Scripts/activate      # Windows (Git Bash)
source .venv/bin/activate          # macOS and Linux
python -m pip install -r requirements.txt
```

## Run the app

1. Start the two containers and download the model (about 1.4 GB, once):

   ```bash
   bash scripts/start-services.sh
   ```

2. Start the outside tool server, then the vulnerable app, each in its own terminal (with the virtual environment active, from the repository root):

   ```bash
   python -m toolserver.server
   python -m vulnerable.server
   ```

   ```text
   Helpdesk Copilot (VULNERABLE practice app) on http://127.0.0.1:18920
   Never expose this app to a network.
   ```

3. Open `http://127.0.0.1:18920` in your browser and ask "Where is my order A-2002?". You are signed in as the fake customer Asha Rao.

4. For the fixed app, run `python -m fixed.server` and open `http://127.0.0.1:18921`.

| What | Address |
|---|---|
| Vulnerable app | `http://127.0.0.1:18920` |
| Fixed app | `http://127.0.0.1:18921` |
| Tool server (lesson 13) | `http://127.0.0.1:18925/mcp`, collected data at `/received` |
| Pretend attacker site (lesson 9), `python -m attacks.attacker_site` | `http://127.0.0.1:18926` |
| Ollama (the model) | `http://127.0.0.1:18930` |
| Mailpit (fake email) | web page `http://127.0.0.1:18932`, SMTP on 18931 |

## Run the attacks

Every attack the lessons use is one entry in `attacks/catalog.py`. Run one several times and see how often it works:

```bash
python -m attacks.run l06-prompt-leak --app vulnerable --tries 10
```

The model's answers vary between runs, so every lesson reports a success rate rather than a single result. Every answer is saved in `attacks/runs/`. To run the whole catalog against one app: `bash scripts/run-attacks.sh vulnerable 10`.

## Run the tests

The twelve security regression tests use a scripted fake model, so they need no Docker, no model and no network, and they give the same result every run.

```bash
python -m pytest tests --app fixed -q          # 12 passed
python -m pytest tests --app vulnerable -q     # 12 failed: the flaws are there
```

Each test name starts with the lesson that adds it (`L06` to `L16`), so `-k L12` runs one lesson's tests. The CI workflow in `.github/workflows/ci.yml` runs both commands on every pull request.

## Automated red teaming with promptfoo (lesson 14)

With both apps running, from the repository root (on Windows, use `$(pwd -W)` style paths only if promptfoo cannot find Python):

```bash
export PROMPTFOO_DISABLE_TELEMETRY=1 PROMPTFOO_DISABLE_UPDATE=1 PROMPTFOO_DISABLE_REMOTE_GENERATION=1
export PROMPTFOO_PYTHON="$(pwd)/.venv/Scripts/python"     # macOS and Linux: $(pwd)/.venv/bin/python
npx promptfoo@latest eval -c attacks/promptfoo/promptfooconfig.yaml --no-cache --no-share -j 1 -o promptfoo-results.html
```

The tests come from the attack catalog and are graded by `attacks/promptfoo/grade.py`, which reuses each attack's own check. Nothing is sent to an online service.

## The steps folders

`vulnerable/` is where the course starts and `fixed/` is where it ends. Lessons 15 and 16 build the defenses in two stages, and each stage is a full runnable copy:

| Folder | The fixed app at the end of | Tests it passes |
|---|---|---|
| `steps/15-checks-in-and-out/fixed` | lesson 15: input and output checks, escaping, page policy, untrusted articles, safe search | 5 of 12 |
| `steps/16-safer-design/fixed` | lesson 16: adds own-data-only tools, refunds waiting for approval, email to the customer only, pinned tool definitions, no secret in the prompt | 12 of 12 |
| `fixed/` | lesson 17 and the capstone: adds the security event log and `python -m fixed.report` | 12 of 12 |

Run a steps copy from its folder, so Python finds that copy of `fixed` first:

```bash
cd steps/16-safer-design
PYTHONPATH=../.. python -m fixed.server
```

## Project layout

```text
helpdesk-copilot-lab/
  common/              code both apps share: settings, model client, order store, mailer, search, chat page
    config.py          every port, limit and setting in one place
  knowledge/           the help articles; two of them carry planted hidden instructions
  vulnerable/          the deliberately insecure app (port 18920); each flaw has a FLAW comment
  fixed/               the same app with every flaw fixed (port 18921); fixes have FIX comments
    guards.py          checks on what goes into and comes out of the model
    events.py          the security event log; report.py summarises it
  toolserver/          the parcel partner's tool server, compromised for lesson 13
  attacks/
    catalog.py         every attack: lesson, OWASP id, message and how to tell it worked
    run.py             sends one attack several times and reports the success rate
    attacker_site.py   the pretend attacker website for lesson 9
    promptfoo/         lesson 14's promptfoo configuration, test generator and grader
  tests/               the twelve security regression tests
  findings/            TEMPLATE.md, the format for writing up a security finding (lesson 5)
  steps/               the fixed app at the end of lessons 15 and 16
  scripts/             start and stop the containers, run the whole attack catalog
  .github/workflows/   CI: the tests pass on fixed and fail on vulnerable
```

`diff -r vulnerable fixed` shows exactly what the course changes, and nothing else.

## Troubleshooting

- **`httpx.ConnectError` or "Connection refused" on port 18930.** Ollama is not running. Run `bash scripts/start-services.sh` and check `docker ps` shows `aisr-ollama`.
- **The first answer takes a minute.** Ollama loads the model into memory on the first request and unloads it after five idle minutes. Later answers take a few seconds to about 20 seconds on a laptop CPU.
- **"Tool server not reachable; continuing without remote tools."** Start `python -m toolserver.server` before the app, or restart the app after starting it. The app looks the tools up once.
- **`Address already in use` on 18920 or 18921.** Another copy is still running. Find it with `netstat -ano | grep 18920` (Windows) or `lsof -i :18920` (macOS, Linux) and stop it.
- **promptfoo says Python was not found.** Set `PROMPTFOO_PYTHON` to the full path of the virtual environment's Python, as shown above.
- **An attack works less often than the lesson says.** That is normal: the model varies between runs, and a newer Ollama or model build can change the rate. Run it with `--tries 10` and compare the rate, not one answer.

To remove everything afterwards: `bash scripts/stop-services.sh`, then `docker volume rm aisr-ollama-models` to delete the model.

## License

Copyright (C) 2026 SypherNext

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0). You may
use, study and change it. If you share a modified version, or run one as a website or service
that other people use, you must make your full modified source code available under the same
license. See [LICENSE](LICENSE) for the full terms.
