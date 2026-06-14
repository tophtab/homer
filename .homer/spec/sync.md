# Homer Sync

Use this flow to accept chapters and rebuild structured knowledge.

## Chapter Acceptance

1. Run `python3 .homer/scripts/homer.py accept <chapter>`.
2. Read `.homer/state/chapters.json`.
3. Read all `accepted` chapters ordered by chapter number.
4. Rebuild `.homer/knowledge/public-lore/` from accepted chapter text.
5. Rebuild `.homer/knowledge/tracking/` from accepted chapter text.
6. Run `python3 .homer/scripts/homer.py mark-current`.

## Public Lore

Public lore is reader-known knowledge only. Store items with source chapter and evidence.

Separate item types:

- `shown_fact`
- `reader_inference`
- `character_claim`
- `rumor`
- `misdirection`

## Tracking

Tracking stores current serial continuity extracted directly from accepted chapters:

- Current story context.
- Timeline.
- Character state and location.
- Active foreshadowing.
- Patches for accepted-canon issues that should be repaired later.

Recommended files:

- `.homer/knowledge/tracking/context.json`
- `.homer/knowledge/tracking/timeline.json`
- `.homer/knowledge/tracking/character-state.json`
- `.homer/knowledge/tracking/foreshadowing.json`
- `.homer/knowledge/tracking/patches.json`

## Author Lore

Rebuild `.homer/knowledge/author-lore/` only when requested, during setup, or when the task needs author settings.

Source is `设定/`. Keep explicit facts separate from inferences, candidates, conflicts, and obsolete notes. Do not modify `设定/` unless explicitly requested.
