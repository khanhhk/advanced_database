---
name: drawio-project
version: 1.0.0
description: Create, edit and validate repository architecture and flow diagrams in native draw.io XML, with explicit connector ports and unambiguous routing.
license: MIT
homepage: https://github.com/Agents365-ai/drawio-skill
---

# Draw.io skill for this repository

Use this skill whenever creating, editing, validating or exporting a `.drawio`
file in this repository. It is a project-specific subset of the upstream
Agents365 draw.io skill.

## Required workflow

1. Read `.agents/memory/PROJECT_MEMORY.md` and inspect authoritative source code.
2. Read `references/diagram-types.md` when choosing an architecture/flow layout.
3. Before hand-writing XML, read `references/xml-authoring.md` completely.
4. Plan nodes, tiers, directions and routing corridors before editing XML.
5. Every connector must have valid source/target IDs, end on block boundaries,
   define explicit `exitX`, `exitY`, `entryX`, `entryY`, and use a separate
   waypoint corridor when auto-routing would stack or merge edges.
6. Keep a consistent flow direction. Prefer left-to-right for architecture and
   top-to-bottom inside a tier.
7. Validate after every material edit:

   ```bash
   python .agents/skills/drawio/scripts/validate.py diagram.drawio --score
   ```

8. Container/child overlap is expected only for intentional swimlanes. Fix
   dangling edges, duplicate IDs, crossings, stacked edges and routes through
   unrelated nodes.
9. Parse final XML and run `git diff --check`.
10. If draw.io CLI is unavailable, deliver editable XML or use
    `scripts/encode_drawio_url.py` for a browser editor URL.

## Large diagrams

For diagrams with more than about 15 connected nodes, prefer
`scripts/autolayout.py` after reading `references/autolayout.md`. Hand placement
is acceptable for swimlanes, but explicit connector ports remain mandatory.

## Export

```bash
drawio -x -f png --width 2000 -o preview.png diagram.drawio
drawio -x -f png -e -s 2 -o diagram.drawio.png diagram.drawio
python .agents/skills/drawio/scripts/repair_png.py diagram.drawio.png
```

Read `references/troubleshooting.md` when export fails. Do not install GUI or
system packages without user approval.

## Deliberately omitted

This project subset omits cloud/AI shape indexes, Terraform, Kubernetes, Docker,
OpenAPI, SQL ERD, sequence/C4 generators, PowerPoint, heatmaps, diffs and
timelapse tools. Reinstall upstream only when a future task explicitly needs one.
