# Homer

Homer is a Codex skill set for single-book web-novel projects.

It helps authors draft, polish, accept, and synchronize one ongoing novel project. It is intentionally not a full web-novel toolbox: no market scanning, no ranking analysis, no publishing platform integration, and no multi-book workspace. The author keeps creative control; Homer manages project state, writing workflow, and AI-readable knowledge indexes.

## What Homer Provides

- `homer-setup`: initialize or repair a one-book project.
- `homer-write`: write, continue, expand, polish, or revise draft chapters.
- `homer-sync`: accept chapters into canon and rebuild structured knowledge.
- `homer-start`: Codex helper for loading current Homer state after a restart or when hooks are unavailable.

## Project Model

One working directory is one book.

Author-owned files are freeform:

```text
设定/     # Author-side settings, private truth, future reveals
大纲/     # Outline files
正文/     # Chapter files
```

Homer-owned infrastructure is structured:

```text
.homer/
  workflow.md
  spec/
  state/
    chapters.json
  knowledge/
    author-lore/
    public-lore/
    tracking/
  cache/
  scripts/
  adapters/
```

Generated adapter files:

```text
.agents/skills/    # Shared skill definitions
.codex/            # Codex-specific skill and hook adapter
```

`.homer/` is the source of truth. `.agents/` and `.codex/` are generated adapter outputs.

## Chapter State

Chapter state lives in `.homer/state/chapters.json`.

Only three chapter statuses exist:

- `planned`: planned but not accepted canon.
- `draft`: editable working chapter.
- `accepted`: accepted into canon. Homer does not edit it by default.

Knowledge status:

- `none`: not part of generated long-term knowledge.
- `current`: accepted chapter hash matches generated knowledge.
- `stale`: accepted chapter changed after knowledge was generated.

## Knowledge Layers

Homer keeps AI-readable JSON under `.homer/knowledge/`.

- `author-lore/`: structured index from `设定/`; may include hidden truths and private plans.
- `public-lore/`: reader-known story knowledge from accepted chapters only.
- `tracking/`: continuity state from accepted chapters only, including timeline, character state, foreshadowing, and future patches.

Default writing uses public lore and tracking. It does not read full `设定/` or full `author-lore` unless the task requires relevant hidden settings.

## Basic Usage

Initialize or repair a project:

```bash
python3 .homer/scripts/homer.py init --scan
```

Show current state:

```bash
python3 .homer/scripts/homer.py status
```

Regenerate `.agents/` and `.codex/` adapter files from `.homer/adapters/`:

```bash
python3 .homer/scripts/homer.py generate-adapters
```

After editing draft chapters:

```bash
python3 .homer/scripts/homer.py check
```

Accept a chapter mechanically:

```bash
python3 .homer/scripts/homer.py accept 1
```

After `homer-sync` rebuilds public lore and tracking:

```bash
python3 .homer/scripts/homer.py mark-current
```

## Codex Workflow

Use these skills in Codex:

- `$homer-start` when beginning a session or after context loss.
- `$homer-setup` to initialize or scan a book project.
- `$homer-write` to edit or create draft chapter files under `正文/`.
- `$homer-sync` to accept chapters and rebuild knowledge JSON.

The Codex hook in `.codex/hooks/inject-homer-state.py` emits a compact state block, but the scripts and skills still work when hooks are disabled.

## Hard Rules

- One project equals one book.
- `设定/`, `大纲/`, and `正文/` are author-owned.
- Author-owned settings are freeform and are not modified by default.
- `accepted` chapters are canon and are not edited by default.
- `draft` chapters are editable.
- Public lore and tracking are generated only from accepted chapters.
- Draft chapters are current-task context, not long-term public knowledge.
- Writing does not read full `设定/` by default.
- Inferences must never be mixed with explicit facts.
- After writing or polishing, Homer does not auto-accept or auto-sync.

## Repository Contents

- `HOMER_MVP_SPEC.md`: design specification.
- `.homer/`: canonical Homer workflow, specs, state, scripts, and adapter templates.
- `.agents/skills/`: generated shared skill definitions.
- `.codex/`: generated Codex-specific skill and hook files.
- `.gitignore`: ignores runtime cache, local Python artifacts, local reference repos, and private author manuscript directories.

## Status

MVP skill scaffold. The current implementation provides the workflow, skills, adapter generation, chapter state management, and mechanical sync helpers. Semantic prose writing and knowledge extraction are performed by Codex through the Homer skills.
