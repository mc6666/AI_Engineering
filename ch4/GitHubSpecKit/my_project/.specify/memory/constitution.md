<!-- SYNC IMPACT REPORT
Version change: N/A (initial) → 1.0.0
Added sections:
  - Core Principles (4 principles: Code Quality, Test-First Development, UX Consistency, Performance)
  - Development Workflow
  - Quality Gates & Review Process
  - Governance
Modified principles: none (initial constitution)
Removed sections: none (initial constitution)
Templates requiring updates:
  - .specify/templates/plan-template.md ✅ compatible (Constitution Check placeholder resolved dynamically at plan time)
  - .specify/templates/spec-template.md ✅ compatible (Success Criteria covers performance targets; User Scenarios covers UX acceptance)
  - .specify/templates/tasks-template.md ✅ compatible (Polish phase includes performance optimization; Setup includes linting)
  - .specify/templates/commands/ ⚠️ no command files found — no updates required
Follow-up TODOs: none (all fields resolved)
-->

# My Project Constitution

## Core Principles

### I. Code Quality

All code MUST be clean, readable, and maintainable. Code MUST pass linting and formatting checks
before merge. Functions MUST have a single responsibility. Complexity MUST be justified — if a
simpler alternative exists, it MUST be used. Dead code, unused imports, and debug artifacts MUST
NOT be committed. Code reviews MUST verify adherence to these standards before approval.

**Rationale**: Unmanaged complexity compounds over time and makes every future change more expensive.
Enforcing quality at the gate prevents entropy rather than fighting it retroactively.

### II. Test-First Development

Tests MUST be written before implementation (TDD). The Red-Green-Refactor cycle MUST be strictly
followed: tests written → tests fail → implementation → tests pass → refactor. Unit tests MUST
cover all business logic. Integration tests MUST cover all inter-component contracts. Test coverage
MUST NOT drop below the project-defined threshold for any merge. No feature is considered complete
until its tests pass in CI.

**Rationale**: Tests written after implementation validate what was built, not what was intended.
Writing tests first forces requirement clarity and prevents regression from future changes.

### III. User Experience Consistency

All user-facing interactions MUST follow a consistent design language. Error messages MUST be
human-readable and actionable — never raw stack traces or internal codes. Response formats MUST be
uniform across all entry points (same field names, same error shapes, same status conventions). UI
components MUST reuse shared primitives; parallel implementations of the same pattern are prohibited.
New UX patterns MUST be reviewed and approved before implementation.

**Rationale**: Inconsistent UX erodes user trust and multiplies support burden. Consistency is a
first-class feature, not an aesthetic preference.

### IV. Performance Requirements

All features MUST meet defined performance targets before release. Response time and throughput
targets MUST be documented in the feature spec's Success Criteria section before implementation
begins. Performance tests MUST be included when a feature introduces a latency-sensitive path.
Regressions against established baselines MUST block merge. Targets are feature-specific and
MUST be documented per spec — vague goals such as "should be fast" are not acceptable.

**Rationale**: Performance problems discovered post-release are expensive to fix and cause direct
user harm. Defining measurable targets upfront makes them testable and prevents acceptance-criteria
drift.

## Development Workflow

Features MUST follow the spec-driven workflow: specify → plan → tasks → implement. Each phase
produces a durable artifact (`spec.md`, `plan.md`, `tasks.md`). Implementation MUST NOT begin
before `plan.md` has passed the Constitution Check gate. Task lists MUST be organized by user
story to enable independent delivery and testing of each increment.

Branch naming MUST follow the pattern `###-feature-name`. Commits MUST be atomic — one logical
change per commit. All merges require a passing CI pipeline.

## Quality Gates & Review Process

The following gates MUST pass before any merge:

- **Constitution Check**: Plan passes all applicable principle gates
- **Tests green**: All tests pass (unit, integration, contract)
- **Linting clean**: Zero lint or formatting errors
- **Performance baseline**: No regression against documented targets
- **Code review**: At least one peer approval
- **Spec alignment**: Implementation matches the accepted spec and plan

Bypassing any gate MUST be documented with written justification in the PR description and
acknowledged by a maintainer. Undocumented bypasses are grounds for revert.

## Governance

This constitution supersedes all other development practices. Amendments require:

1. A written proposal explaining the change and its rationale.
2. Review and approval by project maintainers.
3. A migration plan for existing artifacts if principle semantics change.
4. Version increment per the versioning policy below.

**Versioning policy**:
- MAJOR: Backward-incompatible principle removal or redefinition.
- MINOR: New principle or section added, or materially expanded guidance.
- PATCH: Clarification, wording fix, or non-semantic refinement.

All PRs and reviews MUST verify compliance with this constitution. For runtime agent development
guidance see `CLAUDE.md`.

**Version**: 1.0.0 | **Ratified**: 2026-06-14 | **Last Amended**: 2026-06-14
