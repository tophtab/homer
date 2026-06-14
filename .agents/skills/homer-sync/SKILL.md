---
name: homer-sync
description: "Accept Homer chapters into canon and rebuild structured knowledge. Use when the user says to accept/采纳 a chapter, sync after writing, rebuild public lore, rebuild tracking, mark accepted chapters current after knowledge rebuild, or rebuild the author-lore JSON index from freeform 设定/."
---

# Homer Sync

Use sync to accept chapters and rebuild structured JSON knowledge.

Read before syncing:

- `.homer/workflow.md`
- `.homer/spec/hard-rules.md`
- `.homer/spec/sync.md`
- `.homer/state/chapters.json`

## Chapter Acceptance

When the user asks to accept a chapter:

```bash
python3 .homer/scripts/homer.py accept <chapter>
```

Then:

1. Read all `accepted` chapters from `.homer/state/chapters.json`, ordered by chapter number.
2. Rebuild `.homer/knowledge/public-lore/` from accepted chapter text.
3. Rebuild `.homer/knowledge/tracking/` from accepted chapter text.
4. Run:

```bash
python3 .homer/scripts/homer.py mark-current
```

## Public Lore

Public lore stores reader-known knowledge only. Each item must include source chapter and evidence.

Separate:

- `shown_fact`
- `reader_inference`
- `character_claim`
- `rumor`
- `misdirection`

## Tracking

Tracking stores current serial state extracted directly from accepted chapters:

- context
- timeline
- character state
- foreshadowing
- patches for accepted-canon issues that should be repaired later

## Author Lore

Rebuild `.homer/knowledge/author-lore/` only when requested, during setup, or when a task needs author settings. Extract explicit facts separately from inferences, candidates, conflicts, and obsolete notes.

Do not modify `设定/` unless the user explicitly asks.
