# Homebrain-ai Backend

This repo builds and publishes the Homebrain backend Docker image to GitHub Container Registry (GHCR).

* Stable: deploys specific release `:v1.2.3`
* Dev: always deploy `:latest`

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

## Working on

- [ ] unit tests
- [ ] FastAPI optimization (streaming, error handling, division of layers)


## 🏷️ What gets published

Every push/merge to `main` publishes:

- `:latest` — **dev** tag
- `:sha-<commit>` — points to a specific commit

Only when you explicitly cut a release (see below), it also publishes:

- `:vX.Y.Z` — **stable** release tag

## ✨ Releasing

To cut a **stable release** include `#release` in the merge commit message (or squash commit title) for `main`.

### Bump options

* `#major`
* `#minor`
* `#patch`

If none is provided, the workflow bumps **patch**.

When a release is cut:

* git tag like `v1.2.3` is created.
* a **GitHub Release** is created from that tag (with notes)
* Docker image `:v1.2.3` is published to GHCR

Examples:

* `feat: add RAG ingestion #release #minor`
* `fix: handle disconnected SSE clients #release` (defaults to patch)

## Using the image 🐳

Normally deploy from the [infra repo](https://github.com/Homebrain-ai/infra#), but these are the two modes.

### Dev

Use the floating tag
```env
BACKEND_IMAGE=ghcr.io/<org-or-user>/homebrain-backend
BACKEND_TAG=latest
```

### Stable

```bash
# Pin version
BACKEND_IMAGE=ghcr.io/<org-or-user>/homebrain-backend
BACKEND_TAG=v1.2.3

# Then deploy from infra repo/directory
docker compose pull backend
docker compose up -d
```

## Local Dev

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


## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).
