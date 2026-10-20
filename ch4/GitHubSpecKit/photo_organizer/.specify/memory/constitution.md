<!--
SYNC IMPACT REPORT
==================
Version change: N/A (template) → 1.0.0 (initial ratification)
Bump rationale: MAJOR — first complete constitution authored from template placeholders.

Modified principles: N/A (initial creation)

Added sections:
  - Core Principles: I. Code Quality, II. Testing Standards,
    III. UX Consistency, IV. Performance Requirements
  - Quality Gates
  - Development Workflow
  - Governance

Removed sections: N/A

Template update status:
  - .specify/templates/plan-template.md  ✅ Constitution Check section already present;
    gate wording aligns with principles defined here.
  - .specify/templates/spec-template.md  ✅ Success Criteria + measurable outcomes
    pattern aligns with principle IV (Performance Requirements).
  - .specify/templates/tasks-template.md ✅ Phase structure (test-first, polish phase)
    aligns with principles I and II.
  - .specify/templates/constitution-template.md  ✅ Source template — no edits required.

Deferred TODOs: None. All placeholders resolved.
-->

# Photo Organizer Constitution

## Core Principles

### I. Code Quality

Every line of code MUST be readable, self-documenting, and idiomatic for the
language in use. No raw comments explaining *what* code does — only *why* where
a subtle constraint or invariant exists. Functions MUST have a single
responsibility; cyclomatic complexity MUST NOT exceed 10 per function.
Commented-out or dead code MUST be deleted, not retained. All public APIs MUST
carry explicit type signatures. Dependencies MUST be reviewed for known CVEs
before adoption and kept to the minimum necessary for the feature.

**Rationale**: Readable code is the primary artifact the team maintains. Opacity
and dead weight compound over time into unmaintainable systems; eliminating them
early is cheaper than refactoring later.

### II. Testing Standards

Test-Driven Development (TDD) is MANDATORY for all new feature work. Tests MUST
be written first, confirmed to fail, and only then followed by implementation
(Red → Green → Refactor). Unit tests MUST cover all business logic with ≥ 80%
line coverage. Integration tests MUST cover every cross-component boundary and
MUST NOT mock the file system, database, or OS-level photo APIs — use real
artifacts or test fixtures instead. Tests MUST be deterministic: no time
dependencies, no shared mutable state between cases. Each test MUST have a
single assertion focus and a name that reads as a specification sentence.

**Rationale**: Mocked integration tests have historically passed while real
integrations failed. Photo I/O and metadata parsing are the core risk surface —
real-file tests are non-negotiable.

### III. User Experience Consistency

All user-facing interactions MUST follow a single, predictable interaction
pattern documented in the UX guide. Error messages MUST be human-readable,
actionable, and free of stack traces or internal identifiers. Every operation
that takes longer than 200 ms MUST provide visible progress feedback. Visual
interfaces MUST satisfy WCAG 2.1 AA accessibility standards. Terminology for
concepts (album, collection, tag, event) MUST be consistent across UI, CLI
output, documentation, and error messages — no synonyms for the same concept.
CLI output MUST support both human-readable and `--json` machine-readable modes.

**Rationale**: Photo organizers handle personal, irreplaceable memories.
Confusing UX or ambiguous error messages erode user trust. Consistency across
surfaces removes the cognitive load of "what will happen if I press this."

### IV. Performance Requirements

Core single-photo operations (import, tag, move) MUST complete in ≤ 100 ms on
reference hardware (quad-core CPU, SSD). Batch operations MUST sustain
≥ 100 photos/second throughput. Search and filter queries over a 10 k-photo
collection MUST return results in ≤ 500 ms. Application memory MUST NOT exceed
256 MB resident for collections under 10 k photos. UI MUST remain responsive
(≤ 100 ms input latency) during background operations — long-running work MUST
run off the main thread. Every feature plan MUST include explicit performance
goals and a measurement strategy before implementation begins.

**Rationale**: Users abandon tools that feel slow. Photo libraries grow large;
performance that is not designed in from the start degrades as collections scale
and becomes exponentially harder to recover.

## Quality Gates

Every pull request MUST pass all gates before merge:

1. **Test gate**: All existing tests pass; new code has corresponding tests that
   fail before implementation and pass after.
2. **Coverage gate**: Line coverage MUST NOT decrease below 80%; new modules
   MUST meet the threshold at merge time.
3. **Complexity gate**: No function introduced or modified exceeds cyclomatic
   complexity 10 (enforced by linter).
4. **Performance gate**: Any change touching photo I/O, search, or batch
   processing MUST include a benchmark result showing compliance with
   principle IV thresholds.
5. **Accessibility gate**: UI changes MUST include an accessibility audit result
   (automated tool output is the minimum bar; manual review required for new
   interaction patterns).
6. **Constitution check**: Reviewer MUST confirm no principle is violated; if
   a violation is necessary, it MUST be recorded in the plan's Complexity
   Tracking table with justification.

## Development Workflow

- **Spec before code**: A `spec.md` MUST exist and be approved before any
  implementation task begins.
- **Plan before tasks**: A `plan.md` with a Constitution Check MUST be produced
  before `tasks.md` is generated.
- **One story at a time**: Implementation proceeds in user-story priority order
  (P1 → P2 → P3); each story MUST be independently testable and demo-able
  before the next begins.
- **Commit discipline**: Each commit MUST represent a single logical change
  (a test, a model, a service). Large "all in one" commits are prohibited.
- **No broken main**: The `main` branch MUST remain deployable at all times.
  Feature work lives on branches; merges require all quality gates to pass.
- **Changelog entries**: Every merged PR that adds or changes user-visible
  behavior MUST include a `CHANGELOG.md` entry under the appropriate version
  heading.

## Governance

This constitution supersedes all other informal practices. Amendments require:

1. A written proposal (issue or PR description) citing the specific section and
   reason for change.
2. Review and approval by at least one other team member.
3. A migration plan if the amendment introduces a breaking change to existing
   workflow or tests.
4. Version bump following semantic versioning rules defined in the constitution
   header (MAJOR / MINOR / PATCH).

All PRs and design reviews MUST verify compliance with the Core Principles and
Quality Gates. Complexity or performance violations are permissible only when
justified in the plan's Complexity Tracking table.

Refer to `.specify/memory/constitution.md` (this file) as the authoritative
runtime governance document. The constitution version line below is the
single source of truth for the current ratified version.

**Version**: 1.0.0 | **Ratified**: 2026-06-15 | **Last Amended**: 2026-06-15
