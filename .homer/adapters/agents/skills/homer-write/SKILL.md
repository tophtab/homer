---
name: homer-write
description: "Write, continue, expand, polish, or revise web-novel chapters in a Homer project. Use when the user provides a chapter draft, asks for prose improvement, asks to continue or expand a chapter, gives direction for a new chapter, or wants direct edits under 正文/."
---

# Homer Write

Writing and polishing are one business flow. Edit target files directly under `正文/`.

## Required Checks

Read before editing:

- `.homer/workflow.md`
- `.homer/spec/hard-rules.md`
- `.homer/spec/write.md`
- `.homer/state/chapters.json`

Identify the target chapter and file.

- If target chapter is `accepted`, do not edit unless the user explicitly asks for canon revision.
- If target chapter is `draft`, edit the file directly.
- If target chapter is missing, create it under `正文/` and register it as `draft`.

## Context Selection

Use minimal context:

- Current user instruction.
- Current chapter outline in `大纲/` when relevant.
- Relevant `.homer/knowledge/public-lore/*.json`.
- Relevant `.homer/knowledge/tracking/*.json`.
- Previous or directly related accepted chapter text only when needed.
- `.homer/spec/` rules.

Do not read full `设定/` by default. If hidden author settings are required, read only relevant `.homer/knowledge/author-lore/` slices.

## Editing Semantics

- Polish, `打磨`, `优化`: refine existing material.
- `续写`: continue from existing material.
- `扩写`: add detail and complete underwritten parts.
- `重写`: replace only when explicitly requested.

If unclear, preserve and improve or expand instead of replacing.

Do not introduce canon-changing plot, important new characters, new world rules, relationship changes, or major foreshadowing unless authorized.

## Finish

Run after editing:

```bash
python3 .homer/scripts/homer.py check
```

Do not auto-accept or sync. Tell the user the chapter remains draft and can be accepted with `homer-sync`.
