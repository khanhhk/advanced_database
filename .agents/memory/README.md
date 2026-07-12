# Repository memory

This directory is committed project context for coding agents and new
contributors. `PROJECT_MEMORY.md` is the entry point. `SOURCES.sha256` records
the exact source versions used to prepare it.

The root `AGENTS.md` makes loading this memory explicit. The `.agents/memory/`
directory alone is not guaranteed to be discovered automatically by every AI
tool.

Refresh procedure:

1. Run `python scripts/extract_office.py` to extract searchable text to `/tmp`.
2. Run `sha256sum docs/sources/*.pptx docs/sources/*.docx README.md docs/*.md`
   and compare the result with `SOURCES.sha256`.
3. Review changed documents and update `PROJECT_MEMORY.md`.
4. Replace the recorded checksums.

Do not store secrets, raw datasets, transient task state, or generated Office
text dumps here.
