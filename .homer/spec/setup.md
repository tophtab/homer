# Homer Setup

Use setup to initialize or repair a single-book Homer project.

## Required Outputs

- `设定/`
- `大纲/`
- `正文/`
- `.homer/workflow.md`
- `.homer/spec/`
- `.homer/state/chapters.json`
- `.homer/knowledge/author-lore/`
- `.homer/knowledge/public-lore/`
- `.homer/knowledge/tracking/`
- `.homer/cache/context-packs/`
- `.homer/scripts/`
- `.homer/adapters/`
- generated `.agents/skills/` and `.codex/` adapter files when applicable

## Existing Chapters

- Empty `正文/`: initialize an empty chapter list.
- One chapter: ask whether it is `draft` or `accepted` unless the user has already said.
- Multiple chapters: confirm the status pattern before marking them accepted.
- Imported completed or serialized works may default to `accepted` only when the user says the import is completed/published.

Do not guess batch chapter status.

## After Setup

Run `python3 .homer/scripts/homer.py status`.

If accepted chapters exist, use `homer-sync` to rebuild public lore and tracking.
