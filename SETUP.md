# Setup Guide — Phase 0

Step-by-step setup for the Algo Trading Platform foundation. Commands are shown
for Windows (PowerShell); Mac/Linux differences are noted inline.

## Prerequisites (install once)

- **Python 3.12 or newer** (you have 3.14 — that's fine). From python.org; tick
  "Add Python to PATH" during install.
- **Git** — from git-scm.com.
- **VS Code** — your editor.
- **GitHub account** — for hosting the repo.
- *(Optional)* **Docker Desktop** — only for the local stack step.

## 1. Open the project

Copy the `algo-trading-platform` folder somewhere like `C:\Projects\`, open it in
VS Code, then open the integrated terminal (Terminal -> New Terminal).

## 2. Create a virtual environment

```powershell
python --version           # expect 3.14.x (or use: py -3.14 -m venv .venv)
python -m venv .venv
.venv\Scripts\Activate.ps1   # Mac/Linux: source .venv/bin/activate
```
Your prompt should now show `(.venv)`.

## 3. Install the project + tooling

```powershell
pip install -e ".[dev]"
pre-commit install
```

## 4. Run the quality gate (confirm green)

```powershell
ruff check .
ruff format --check .
mypy services libs
pytest --cov --cov-report=term-missing
```
The last command should end with `3 passed` and `100%` coverage.
(Mac/Linux shortcut for all of the above: `make check`.)

## 5. Run the template service

```powershell
uvicorn app.main:app --reload --app-dir services/health-service
```
Open http://localhost:8000/health (and http://localhost:8000/docs). `Ctrl+C` to stop.

## 6. (Optional) Run the full local stack

```powershell
docker compose up --build      # service + TimescaleDB + Redis
docker compose down            # stop
```

## 7. Push to GitHub

```powershell
git init
git add .
git commit -m "chore: Phase 0 foundation"
git branch -M main
git remote add origin https://github.com/<your-username>/algo-trading-platform.git
git push -u origin main
```
Create the empty repo on github.com first (no README/.gitignore — this project
already has them). After pushing, watch CI run under the **Actions** tab.

## 8. Protect main

Repo **Settings -> Branches -> Add branch ruleset**: require status checks to pass
and at least one review before merging to `main`.

## CI runs on every push

The pipeline tests on Python **3.12 and 3.14**, then runs lint, format, type
check, complexity, security (Bandit), dependency scan (pip-audit), secret scan
(Gitleaks), and builds + scans the Docker image.

## Troubleshooting

- **`Activate.ps1 cannot be loaded` (execution policy):** run
  `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` then retry.
- **A package fails to install on 3.14:** tell Claude the error — occasionally a
  brand-new Python version needs a slightly newer package pin.
- **`ruff`/`pytest` not found:** make sure the venv is active (`(.venv)` in prompt).
