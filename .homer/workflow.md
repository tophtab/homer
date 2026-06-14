# Homer Workflow

Homer is a single-book web-novel assistant. One working directory equals one book project.

## Business Flows

1. `homer-setup`
   - Initialize `.homer/` infrastructure.
   - Create `设定/`, `大纲/`, and `正文/` if missing.
   - Scan existing chapter files and establish `.homer/state/chapters.json`.
   - Generate or refresh agent adapter files from `.homer` source.

2. `homer-write`
   - Write, continue, expand, polish, or revise draft chapters.
   - Edit files directly under `正文/`.
   - Keep edited chapters as `draft`.
   - Do not accept chapters or rebuild long-term knowledge automatically.

3. `homer-sync`
   - Accept chapters into canon.
   - Rebuild `.homer/knowledge/public-lore/` from all accepted chapters.
   - Rebuild `.homer/knowledge/tracking/` from all accepted chapters.
   - Rebuild `.homer/knowledge/author-lore/` only when requested or needed.

## State Model

Chapter state lives in `.homer/state/chapters.json`.

Statuses:

- `planned`: planned but not accepted canon.
- `draft`: editable working chapter.
- `accepted`: canon. Do not edit by default.

Knowledge status:

- `none`: not part of generated long-term knowledge.
- `current`: accepted chapter hash matches generated knowledge.
- `stale`: accepted chapter changed after knowledge was generated.

## Context Rule

Only read what would cause the target chapter to be wrong if omitted.

Default writing context includes current instruction, relevant outline, public lore, tracking, and nearby accepted chapters when needed. Default writing context excludes full `设定/` and full `author-lore`.

## Workflow State Breadcrumbs

[workflow-state:no_project]
No initialized Homer project. If the user wants setup, initialization, writing, chapter sync, or knowledge rebuild, load `homer-setup` and run setup first.
[/workflow-state:no_project]

[workflow-state:ready]
Homer project is initialized. Route setup/import/repair to `homer-setup`; writing, polishing, continuation, expansion, or revision to `homer-write`; accepting chapters, rebuilding public lore/tracking, or rebuilding author-lore indexes to `homer-sync`.
[/workflow-state:ready]
