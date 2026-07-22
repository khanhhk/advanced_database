# Repository memory

This directory is committed project context for coding agents and new
contributors. `PROJECT_MEMORY.md` is the entry point. `SOURCES.sha256` records
the exact source versions used to prepare it.

The root `AGENTS.md` makes loading this memory explicit. The `.agents/memory/`
directory alone is not guaranteed to be discovered automatically by every AI
tool.

Refresh procedure:

1. Run `sha256sum -c .agents/memory/SOURCES.sha256`.
2. Review changed documents and update `PROJECT_MEMORY.md`.
3. Replace the recorded checksums for the files that changed.

Do not store secrets, raw datasets, transient task state, or generated Office
text dumps here.
