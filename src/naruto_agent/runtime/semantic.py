from __future__ import annotations

from dataclasses import dataclass

from naruto_agent.core.actions import ActionCapabilities, CapabilityDecision, SemanticAction
from naruto_agent.core.interfaces import CharacterActionAdapter
from naruto_agent.runtime.safety import ActionScheduler, DispatchResult, SafetySnapshot


@dataclass(frozen=True, slots=True)
class SemanticDispatchResult:
    capability: CapabilityDecision
    dispatch: DispatchResult | None


class SemanticActionDispatcher:
    """Only V2 route: capabilities -> adapter -> scheduler -> SafetyGate -> backend."""

    def __init__(self, *, adapter: CharacterActionAdapter, scheduler: ActionScheduler) -> None:
        self._adapter = adapter
        self._scheduler = scheduler

    def dispatch(
        self,
        action: SemanticAction,
        capabilities: ActionCapabilities,
        safety: SafetySnapshot,
        *,
        at_ns: int,
    ) -> SemanticDispatchResult:
        decision = capabilities.evaluate(action, at_ns=at_ns)
        if not decision.allowed:
            return SemanticDispatchResult(capability=decision, dispatch=None)
        command = self._adapter.to_control_command(action)
        return SemanticDispatchResult(
            capability=decision,
            dispatch=self._scheduler.dispatch(command, safety),
        )
