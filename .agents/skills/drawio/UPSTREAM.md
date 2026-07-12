# Upstream provenance

- Repository: https://github.com/Agents365-ai/drawio-skill
- Installed path: `skills/drawio-skill`
- Upstream version used as the source: `1.28.2`
- Local subset version: `1.0.0`
- Installed on: `2026-07-13`
- License declared by `SKILL.md`: MIT

This directory intentionally contains only the files needed by this project.
To update, install upstream into a temporary directory, review changes to the
retained files, then copy only the equivalent subset:

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo Agents365-ai/drawio-skill \
  --path skills/drawio-skill \
  --dest /tmp/drawio-skill-update \
  --name drawio
```

Do not replace the local folder wholesale; that would restore unrelated tools.
