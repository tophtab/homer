---
name: homer-start
description: "Load Homer project state and workflow context in Codex. Use when starting work in a Homer novel project, when Codex hooks are unavailable, when the session was restarted, or when the assistant needs current Homer routing state before setup/write/sync work."
---

# Homer Start

Run:

```bash
python3 .homer/scripts/homer.py status
```

Then read:

- `.homer/workflow.md`
- `.homer/spec/hard-rules.md`
- `.homer/state/chapters.json`

Route the user's request:

- Setup, init, repair, import, adapter regeneration: `homer-setup`.
- Write, continue, expand, polish, revise: `homer-write`.
- Accept chapters, rebuild public lore/tracking, rebuild author-lore: `homer-sync`.

If `.homer/scripts/homer.py` is missing, initialize or repair with `homer-setup`.
