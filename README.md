# Homebrain-ai Backend

### Local Dev workflow

```bash
# Clone repo
git clone git@github.com:Homebrain-ai/backend.git

# Setup dev env
uv sync --frozen --group dev

# Run locally
uv run uvicorn app.main:app --reload --port 8001

# Linter
uv run ruff check .
uv run ruff format .

# Testing
uv run pytest
```

## Architecture

```bash
START
  ↓
ingest_message  (normalize input, append to messages)
  ↓
router          (classify route + confidence + “needs review?”)
  ├─→ personal_react_agent
  ├─→ projects_react_agent
  ├─→ homelab_react_agent   (tools + RAG + approvals)
  └─→ general_react_agent
  ↓
finalize        (format answer + redact/deny sensitive requests)
  ↓
END
```

# Working on

- [ ] unit tests
- [ ] FastAPI optimization (streaming, error handling, division of layers)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).