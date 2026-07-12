# Agent instructions

Before working on this repository, read `.agents/memory/PROJECT_MEMORY.md`.

Treat that file as a compact, version-controlled project briefing. Source code and
the original documents remain authoritative. If a source document listed in
`.agents/memory/SOURCES.sha256` changes, refresh the memory before relying on it.

When implementation decisions materially change the architecture, scope, data
model, API, evaluation plan, or reproducibility workflow, update the project
memory in the same change.

## Project skills

Repository-local skills live under `.agents/skills/`. Before creating, editing,
validating, or exporting a draw.io diagram, read and follow
`.agents/skills/drawio/SKILL.md`. Resolve referenced files relative to that skill
directory and prefer its bundled validators/layout tools over hand-checking XML.
