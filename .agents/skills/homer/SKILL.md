---
name: homer
description: "Route Homer novel-assistant requests inside a single-book project. Use when Codex needs to initialize a Homer project, write or polish chapters, accept chapters into canon, rebuild public lore/tracking, rebuild author-lore indexes, or decide which Homer workflow applies."
---

# Homer Router

Load Homer state before acting:

```bash
python3 .homer/scripts/homer.py status
```

Read:

- `.homer/workflow.md`
- `.homer/spec/hard-rules.md`
- `.homer/state/chapters.json`

## Route

- Setup, init, repair, or import existing chapters: use `homer-setup`.
- Write, continue, expand, polish, or revise chapters: use `homer-write`.
- Accept chapters, rebuild public lore/tracking, or rebuild author-lore indexes: use `homer-sync`.

If `.homer/` is missing or `.homer/scripts/homer.py` is unavailable and the user wants Homer behavior, route to `homer-setup`.

## Boundaries

- One project is one book.
- `设定/`, `大纲/`, and `正文/` are author-owned freeform files.
- Default writing does not read full `设定/`.
- `accepted` chapters are canon and are not edited by default.
- `draft` chapters are editable.
- Public lore and tracking are generated only from accepted chapters.
- After writing, do not auto-accept or auto-sync.
