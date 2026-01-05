# backend/tests/unit/fakes.py



class FakeStructuredRouter:
    """Minimal fake that mimics structured_router.invoke(prompt)."""

    def __init__(self, decision: RouteDecision | None = None, exc: Exception | None = None):
        self._decision = decision
        self._exc = exc
        self.last_prompt: str | None = None

    def invoke(self, prompt: str) -> RouteDecision:
        self.last_prompt = prompt
        if self._exc:
            raise self._exc
        assert self._decision is not None
        return self._decision


class FakeLLM:
    """Minimal fake that supports llm.with_structured_output(RouteDecision)."""

    def __init__(self, structured_router: FakeStructuredRouter):
        self._structured_router = structured_router

    def with_structured_output(self, _schema):  # _schema is RouteDecision
        return self._structured_router
