# Contributing

## Workflow (trunk-based)

1. Branch off `main`: `git checkout -b feat/<short-name>`.
2. Make changes. Keep commits small and use [Conventional Commits](https://www.conventionalcommits.org)
   (`feat:`, `fix:`, `chore:`, `test:`, `docs:`, `refactor:`).
3. Run `make check` — it must pass before you push.
4. Open a pull request. CI must be green and at least one review is required.
5. Squash-merge to `main`. Direct pushes to `main` are blocked.

## Quality bar (enforced in CI)

- Ruff lint + format clean
- mypy type-checks with no errors
- Cyclomatic complexity within limits (Radon / Ruff mccabe)
- Bandit + Semgrep find no high-severity issues
- Tests pass with coverage ≥ 85% (≥ 90% on risk/OMS code)
- No known-vulnerable dependencies (pip-audit) and no committed secrets (Gitleaks)

## Adding a new service

Copy `services/health-service/` as a template, rename the package, and add the
service to `docker-compose.yml` and the CI test matrix.
