# AGENTS.md — Agent-first guide for this repository

This file provides a concise, agent-focused entry point. Keep it small; delegate details to docs-agent/.

## 1) Project overview (for agents)
- Process-engineering is modularized: rules are tiny and persistent; workflows are injected on-demand.
- Always prefer minimal context: 1 workflow at a time; add a quality gate only when checking.
- Use Source Mapping in workflows to reference theory with tiny excerpts only.

## 2) Process mode (Autonomous Mode)
- Baseline: docs-agent/core-rules.md (includes autonomous operation guidelines)
- Workflow self-selection: docs-agent/workflows/meta-workflow-orchestrator.md
- Minimal context policy: docs-agent/workflows/context-management-protocol.md

Quick rules:
- Determine current STEP from existing deliverables
- Inject exactly 1 workflow; when finishing, inject exactly 1 quality gate
- Never load docs-theory/theory fully; cite only the referenced section

## 3) Workflow index
- Steps
  - STEP0 Goal: docs-agent/workflows/step0-goal-definition.md
  - STEP1 Requirements: docs-agent/workflows/step1-requirements.md
  - STEP2 System Design: docs-agent/workflows/step2-system-design.md
  - STEP3 Detailed Design: docs-agent/workflows/step3-detailed-design.md
  - STEP4 Test Design: docs-agent/workflows/step4-test-design.md
  - STEP5 Implementation Planning: docs-agent/workflows/step5-implementation-planning.md
  - STEP7 Coding Execution: docs-agent/workflows/step7-coding-execution.md
- Quality gates
  - Requirements: docs-agent/workflows/quality-gate-requirements.md
  - Architecture: docs-agent/workflows/quality-gate-architecture.md
  - Design: docs-agent/workflows/quality-gate-design.md
  - Test Design: docs-agent/workflows/quality-gate-test-design.md
  - Implementation Planning: docs-agent/workflows/quality-gate-implementation-planning.md
- Meta / Protocol
  - Meta Orchestrator: docs-agent/workflows/meta-workflow-orchestrator.md
  - Context Protocol: docs-agent/workflows/context-management-protocol.md

## 4) Context policy (must follow)
- Persistent: load only the essence of docs-agent/core-rules.md
- During execution: inject 1 workflow file only
- During checking: inject 1 quality gate file only
- Theory: use Source Mapping to copy a small, relevant excerpt (≤ 200 tokens)
- Do not inject multiple workflows simultaneously; do not read docs-theory/theory in full

## 5) Testing / checks (safe-by-default)
- Prefer running safe, local checks if available (unit tests, static analysis) without modifying environment
- Do NOT install dependencies, run migrations, deploy, call paid/external services, or perform destructive operations without explicit permission
- After edits, update/add tests relevant to the change and ensure they pass

Examples (conditional; only if config exists):
- Node.js: if package.json has "test" → `npm test` or `pnpm test`; linters → `npm run lint`; type-check → `npm run type-check`
- Python: if pytest config and tests/ present → `pytest -q`; linters → `ruff`/`flake8` if configured
- Rust: if Cargo.toml → `cargo test --all`
- Docs: if markdownlint/yamllint config present → run them
- Otherwise: skip checks; never install deps automatically

## 6) Safety & permissions
- Always requires explicit permission:
  - Dependency installs/updates; database changes; deployments; external paid APIs; long-running resource-heavy jobs
- Allowed by default (if available in-repo):
  - Local unit tests; linters; type-checkers; building docs; non-destructive static tools

## 7) Monorepo note
- If subprojects appear, place an AGENTS.md inside each package. Agents should prefer the closest AGENTS.md to the edited files (nearness precedence).

## 8) Tooling integration (optional hints)
- If using Cline, .clinerules/ is provided for fast workflow injection
- Canonical docs live in docs-agent/; .clinerules contains wrappers/compressed guidance

