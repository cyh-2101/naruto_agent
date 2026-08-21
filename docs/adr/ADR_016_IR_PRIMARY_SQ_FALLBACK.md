# ADR-016 — IR Primary with SQ Fallback; Remove IQ

- Status: accepted
- Date: 2026-08-22
- Scope: observation views and future routing/training behavior

## Context

ADR-015 introduced IR, SQ, and IQ as identity-information variants and selected SQ as the default.
The Product Owner clarified that the project objective is the strongest lawful screen-only agent,
not an identity-limited deployment policy.

If identity information is accurate, fresh, legally screen-derived, and all other conditions are
equal, removing it cannot improve the theoretical optimal policy. A reduced view can outperform a
poorly trained full-information model only because of finite-data overfitting, shortcut learning,
model capacity, or identity errors. Those are training and robustness problems, not benefits of
information loss.

## Decision

Support exactly two policy views:

- IR (`identity_rich`) is primary. It uses self and opponent identity only when the estimates are
  fresh and sufficiently confident.
- SQ (`self_qualified`) is the fallback when opponent identity is unknown, stale, low-confidence,
  or conflicting. It always retains configured self identity so character-specific execution
  remains possible.

Remove IQ from the current enum, builder, tests, architecture, work order, and forward-looking
documentation.

Future learning may use SQ as opponent-identity dropout while sharing the same backbone and weights
as IR. This encourages behavior understanding without reducing the maximum-information runtime path.
Evaluation must include identity available, missing, stale, corrupted, familiar-opponent, and
unfamiliar-opponent conditions.

## Runtime intent

```text
fresh + confident opponent identity -> IR
unknown/stale/low-confidence/conflicting identity -> SQ
```

The current builder can construct IR or SQ explicitly. Automatic selection is not implemented by
this decision because no passive identity estimator has measured calibration or freshness evidence.
That resolver belongs to an explicitly authorized Work Order 002 and must record its reason.

## Consequences

- Reliable visible information is used for maximum performance.
- Missing or bad identity does not block the policy; it degrades to SQ.
- IR and SQ must use one state, one shared backbone, and one character-conditioning architecture.
- Training robustness comes from identity dropout and corrupted-identity evaluation, not an IQ
  deployment mode.
- No learning, perception, generated input, or character mechanics are authorized by this decision.

## Rejected alternative: retain IQ as an ablation

Rejected because SQ already tests opponent-identity removal while preserving the self identity
required for character-specific action. Removing self identity does not match the intended runtime,
adds schema/test/experiment surface, and does not increase the strongest policy's information ceiling.
