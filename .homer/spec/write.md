# Homer Write

Use this flow for drafting, continuing, expanding, polishing, or revising chapters.

## Required Checks

1. Read `.homer/workflow.md`.
2. Read `.homer/spec/hard-rules.md`.
3. Read `.homer/state/chapters.json`.
4. Identify the target chapter and its file under `正文/`.
5. If the target is `accepted`, do not edit unless the user explicitly asks for a canon revision.
6. If the target is `draft`, edit that file directly.
7. If the target is missing, create it under `正文/` and register it as `draft`.

## Context Selection

Read minimal context:

- User's current instruction.
- Relevant chapter outline from `大纲/`.
- Relevant public lore JSON.
- Relevant tracking JSON.
- Previous or directly related accepted chapter text only when needed.
- Relevant Homer spec rules.

Do not read full `设定/` by default. When hidden author settings are needed, read only relevant `.homer/knowledge/author-lore/` slices.

## Editing Semantics

- `polish`, `打磨`, `优化`: refine existing draft while preserving intent.
- `续写`: continue from existing material.
- `扩写`: add detail and complete underwritten parts.
- `重写`: replace only when explicitly requested.

If intent is unclear, preserve and improve or expand rather than replacing.

## Creative Boundary

By default, Homer may improve expression, pacing, transitions, sensory detail, action, dialogue, and chapter hooks.

Do not introduce canon-changing plot, important new characters, new world rules, relationship changes, or major foreshadowing unless the user authorizes it.

## Baseline Style

- Long-form serialized web novel rhythm.
- Mobile-friendly paragraphs.
- Each chapter should advance events.
- Avoid pure atmosphere chapters, heavy exposition, and premature hidden-lore reveal.
- Default new chapter length is 2000-3000 Chinese characters unless overridden.

After editing, run `python3 .homer/scripts/homer.py check` so hashes and stale knowledge markers update. Tell the user the chapter remains draft.
