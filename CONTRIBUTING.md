# Contributing to Zephyr MCP

Thank you for your interest in contributing to this project! This document outlines the guidelines for contributing.

## Getting Started

1. **Fork** the repository
2. **Clone** your fork locally
3. **Create a branch** from `main` for your changes

```bash
git clone https://github.com/<your-username>/zephyr-mcp.git
cd zephyr-mcp
git checkout -b feature/your-feature-name
```

## Development Setup

```bash
# Install dependencies
task install

# Or manually
uv venv
uv pip install -e ".[dev]"
```

## Code Standards

### Formatting & Linting

All code must pass **ruff** checks before merge:

```bash
# Format code
task format

# Lint and auto-fix
task check
```

### Testing

- All new code **must** have unit tests with **≥ 90% coverage**
- Tests must pass on Python 3.11, 3.12, and 3.13
- Use **Test-Driven Development (TDD)** — write tests before implementation when possible

```bash
# Run tests
task test

# Run tests with coverage
task test-cov
```

### Code Style

- Use **ruff** for formatting and linting (line length: 150)
- Keep comments short and only on internal functions
- No emojis in code unless explicitly requested
- Follow existing patterns in the codebase

## Pull Request Process

1. **Ensure CI passes** — all lint, format, and test checks must be green
2. **One PR per feature/fix** — keep changes focused and reviewable
3. **Write a clear PR title and description** explaining what changed and why
4. **Update documentation** if your change affects:
   - README.md (new env vars, tools, config options)
   - docs/architecture.md (structural changes)
5. **Update tests** — never delete or weaken existing tests without justification

### PR Review & Approval

> **All pull requests require approval from [@dloiacono](https://github.com/dloiacono) before merging.**
>
> No PRs will be merged without explicit approval from the project maintainer.

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(scope): add new feature
fix(scope): fix a bug
docs(scope): update documentation
test(scope): add or update tests
refactor(scope): code refactoring without behavior change
ci(scope): CI/CD changes
```

Examples:
- `feat(squad): add PAT authentication support`
- `fix(config): handle missing env var gracefully`
- `docs: update README with new configuration options`

## Reporting Issues

- Use GitHub Issues to report bugs or request features
- Include steps to reproduce for bugs
- Include your Python version and OS

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.
