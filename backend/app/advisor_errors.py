"""Error types for the AI Advisor, independent of any specific LLM provider.

Kept in their own module (rather than app.advisor or a provider module) so
app.advisor and app.llm_provider can both import them without creating a
circular import - this is what lets the LLM provider be swapped out later
without touching app.advisor or app.routes.advisor.
"""


class AdvisorConfigError(Exception):
    """The Advisor cannot run because of missing/invalid server configuration."""


class AdvisorProviderError(Exception):
    """The LLM provider failed, timed out, or returned something unusable."""


class AdvisorNotFoundError(Exception):
    """A caller-supplied scholarship/application context ID is invalid."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
