---
name: homer-setup
description: "Initialize or repair a Homer single-book novel project. Use when setting up .homer infrastructure, scanning existing chapter files, creating or fixing .homer/state/chapters.json, confirming imported chapter statuses, or generating .agents/.codex adapter files from Homer sources."
---

# Homer Setup

Initialize or repair the current directory as one Homer book project.

## Steps

1. Read `HOMER_MVP_SPEC.md` if present.
2. Read `.homer/spec/setup.md` and `.homer/spec/hard-rules.md` if present.
3. Ensure `设定/`, `大纲/`, `正文/`, and `.homer/` infrastructure exist.
4. Run:

```bash
python3 .homer/scripts/homer.py init --scan
```

5. Inspect `.homer/state/chapters.json`.
6. If existing chapter status is uncertain, ask before changing status.
7. Generate adapters:

```bash
python3 .homer/scripts/homer.py generate-adapters
```

## Existing Chapter Status

- Empty `正文/`: initialize empty state.
- One existing chapter: ask whether it is `draft` or `accepted` unless the user made it clear.
- Multiple existing chapters: confirm all accepted, all draft, first N accepted, or a custom pattern.
- Imported completed or serialized works may be marked accepted only when the user says they are completed/published.

Do not guess batch chapter status.

## After Setup

Run:

```bash
python3 .homer/scripts/homer.py status
```

If accepted chapters exist, use `homer-sync` to rebuild public lore and tracking.
