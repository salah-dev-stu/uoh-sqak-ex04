# OOP Structure Plan (R2 — no duplication)

> Planned class design for `graphguide`, factoring shared behavior into base classes/mixins/Template Method so logic is written once. The rendered class diagram (`oop_diagram.*`) is produced in Phase 7; this is the design intent it must reflect.

## Shared abstractions (avoid duplication)

- **`ExternalCall` (via `ApiGatekeeper`)** — Template Method: every external call (LLM, subprocess, file read) flows through `ApiGatekeeper.call(kind, fn)`. Subtypes differ only in how tokens/units are counted; the pre-call (budget/rate) and post-call (record) steps are written once.
- **`BaseInvestigator`** — abstract base for the two agent modes. Defines the Template Method `investigate()` (setup → loop → diagnose → result) and the shared success bar + trace recording. `GraphGuidedInvestigator` and `NaiveInvestigator` override only the step strategy (graph-first vs raw-files). No duplicated orchestration.
- **`VaultPage`** — base renderer for Markdown pages; `IndexPage`/`HotPage`/`LogPage`/`SuspectPage`/`FixPage` override only their body section. Front-matter, wikilink, and tag emission live in the base.
- **`GraphArtifact` models** — `Node`/`Edge` share a `from_dict` mixin; `Confidence` is a single enum reused by loader, centrality, and extensions.
- **`Extension`** — small protocol (`run(graph, vault) -> Artifact`) implemented by `SuspectRanker` and `KnowledgeDiff`, so the SDK treats extensions uniformly.

## Composition (not inheritance) where it fits
- `GraphGuide` (SDK façade) **composes** `GraphifyRunner`, `VaultBuilder`, the investigators, the extensions, and the `ApiGatekeeper` — it owns no business logic itself, only orchestration.
- Investigators **hold** a `Gatekeeper` + `LLMClient` + `GraphLoader` rather than subclassing them.

## Why this satisfies R2
- One orchestration path (`BaseInvestigator.investigate`) → mode logic isn't copy-pasted.
- One metering path (`ApiGatekeeper.call`) → no per-call-site duplication.
- One page-rendering path (`VaultPage`) → consistent wikilinks/tags.
- The OOP diagram in Phase 7 will show these base/subclass + composition relationships extracted from the code.
