from naruto_agent.runtime.input.mock import MockInputBackend


class DryRunInputBackend(MockInputBackend):
    """Named production dry-run backend; records intent and never touches OS input."""

