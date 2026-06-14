# Homer MVP Specification

## Positioning

Homer is a novel project assistant for web-novel authors. It helps the author write, refine, and synchronize a single ongoing novel project. It is not a full web-novel toolbox, not a market research tool, and not a replacement for the author.

The author keeps creative control. Homer assists with drafting, polishing, context selection, chapter state management, and structured knowledge rebuilding after the author accepts chapters into canon.

## MVP Scope

Homer MVP has three business flows:

1. `homer-setup`
   - Initialize one book project.
   - Create `.homer/` infrastructure.
   - Create or update Codex adapter files using the same source/generated split as Trellis.
   - Scan existing chapters and establish `.homer/state/chapters.json`.
   - Confirm status for existing chapters during setup/import.

2. `homer-write`
   - Combine writing and polishing into one flow.
   - If a target draft exists, edit it in place.
   - If no target draft exists, create the chapter from the user's direction, outline, and selected context.
   - Directly edit files under `正文/`, so Git/IDE diff can show changes naturally when Git is available.
   - Do not automatically accept or synchronize the chapter.

3. `homer-sync`
   - Accept chapters into canon.
   - Rebuild public lore and tracking from all accepted chapters.
   - Rebuild author lore only when requested or when a task needs author-side settings indexed.
   - Do not modify author-owned freeform settings unless explicitly requested.

Out of scope for MVP:

- Ranking scans.
- Market/topic analysis.
- Book dissection/import as a full analysis product.
- Cover generation.
- Short-story/long-story dual workflow complexity.
- Multi-book switching.
- Publishing platform integration.
- Review as a separate author-facing workflow.
- Per-writing-task directories as a default flow.

## Project Model

One working directory is one book project.

Author-owned files are freeform:

```text
设定/     # Complete author-side settings and private truth. Freeform.
大纲/     # Outline, volume outline, chapter outline. Freeform.
正文/     # Chapter files.
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
    context-packs/
  scripts/
  adapters/
```

Codex/Trellis-style generated adapter layer:

```text
.agents/skills/    # Shared agent skills where applicable.
.codex/            # Codex-specific skills, hooks, agents, config.
```

`.homer/` is the canonical Homer infrastructure. `.agents/skills/` and `.codex/` are generated adapter outputs, not the source of truth.

## Chapter State

Chapter state is stored in `.homer/state/chapters.json`.

Only three chapter statuses exist:

- `planned`: planned but no accepted draft yet.
- `draft`: editable working chapter.
- `accepted`: accepted into canon, equivalent to published for Homer. It is not modified by default.

Example:

```json
{
  "schema_version": 1,
  "chapters": [
    {
      "number": 1,
      "title": "章名",
      "file": "正文/第001章_章名.md",
      "status": "accepted",
      "content_hash": "sha256:...",
      "knowledge_status": "current"
    },
    {
      "number": 29,
      "title": "章名",
      "file": "正文/第029章_章名.md",
      "status": "draft",
      "content_hash": "sha256:...",
      "knowledge_status": "none"
    }
  ]
}
```

`knowledge_status` values:

- `none`: not part of long-term knowledge, normally for `planned` or `draft`.
- `current`: accepted chapter hash matches generated knowledge.
- `stale`: accepted chapter changed after knowledge was generated.

Rules:

- `draft` chapters may be edited directly.
- `accepted` chapters are not modified by default.
- Modifying an accepted chapter is a canon revision and must mark generated knowledge stale until sync rebuilds it.
- A single unregistered chapter explicitly targeted by the user may be registered as `draft`.
- Batch-unregistered chapters must not be guessed; setup/import must confirm status.

Git is recommended but not required. If Git exists, file diffs are the normal review surface. If Git does not exist, Homer still works.

## Knowledge Layers

Homer uses JSON knowledge indexes for AI consumption. Author-facing Markdown remains freeform.

### Author Lore

Path: `.homer/knowledge/author-lore/`

Source: `设定/`

Purpose:

- Structured index of complete author-side settings.
- May include hidden truths, future reveals, real rules, and private plans.
- Used for planning and explicitly authorized reveal work.

Rules:

- `设定/` is the source author edits freely.
- Homer builds `author-lore` as a JSON index from `设定/`.
- MVP uses full rebuild rather than incremental indexing.
- Default extraction treats only explicit text as fact.
- Inferences, candidates, conflicts, and obsolete notes must be marked separately and must not be mixed into facts.

### Public Lore

Path: `.homer/knowledge/public-lore/`

Source: all `accepted` chapters.

Purpose:

- Reader-known story knowledge.
- Default lore source for writing new prose.
- Prevents accidental leakage of author-only settings.

Rules:

- MVP rebuilds public lore from all accepted chapters, ordered by chapter number.
- Draft chapters do not enter public lore.
- Public lore distinguishes:
  - `shown_fact`: explicitly shown or confirmed.
  - `reader_inference`: reader can infer it, but it is not confirmed.
  - `character_claim`: a character said or believes it.
  - `rumor`: social/public rumor.
  - `misdirection`: intentionally misleading information.
- Every item keeps evidence and source chapter references.

### Tracking

Path: `.homer/knowledge/tracking/`

Source: all `accepted` chapters.

Purpose:

- Current continuity state for the ongoing serial.
- Tracks what happened, where characters are, active foreshadowing, and unresolved patches.

Recommended files:

```text
context.json
timeline.json
character-state.json
foreshadowing.json
patches.json
```

Rules:

- MVP rebuilds tracking from all accepted chapters, ordered by chapter number.
- Tracking is not merely inferred from public lore; it is extracted directly from accepted chapters.
- Draft chapters are temporary context only and do not enter tracking.
- Accepted-chapter contradictions that should not be back-edited go into patches for future repair.

## Context Selection

Homer must select minimal context before writing or polishing.

Core rule:

```text
Only read what would cause this chapter to be wrong if omitted.
```

Default writing context:

- User's current instruction.
- Current chapter outline if available.
- Relevant public lore JSON.
- Relevant tracking JSON.
- Previous or directly related accepted chapter text when needed.
- Homer writing rules from `.homer/spec/`.

Default writing context excludes full `设定/` and full `author-lore`.

When hidden author settings are required, Homer reads only relevant `author-lore` slices. Example: if a chapter reveals a character's faction identity, read that character and faction, not all settings.

Context-selector output is normally transient. Save it under `.homer/cache/context-packs/` only for complex/debug cases.

## Writing And Polishing

`homer-write` handles both writing and polishing.

If target chapter exists and is `draft`:

- Edit `正文/` file in place.
- Interpret user intent:
  - polish/打磨/优化: refine existing draft.
  - 续写: continue from existing content.
  - 扩写: add detail and complete underwritten parts.
  - 重写: rewrite only when explicitly requested.
- If unclear, preserve the existing draft and improve/expand rather than replacing it.
- Update draft `content_hash` after edits.

If target chapter does not exist:

- Create the chapter under `正文/` using standard chapter naming conventions.
- Mark it `draft`.
- Use user direction, outlines, public lore, tracking, and minimal context.

If target chapter is `accepted`:

- Do not edit by default.
- Require explicit canon-revision intent to modify.
- Mark knowledge stale after modification.

Creative boundary:

- By default, Homer may improve expression, pacing, transitions, sensory detail, action, dialogue, and chapter hooks.
- Homer must not introduce canon-changing plot, important new characters, new world rules, relationship changes, or major foreshadowing unless the user authorizes it.

Default web-novel baseline:

- Long-form serialized web novel rhythm.
- Mobile-friendly paragraphs.
- Each chapter should advance events.
- Avoid pure atmosphere chapters, heavy exposition, and premature hidden-lore reveal.
- Default new-chapter length is 2000-3000 Chinese characters unless overridden by project config or user instruction.

After writing, Homer should not auto-sync. It should tell the user the chapter remains draft and can be accepted with `homer-sync` when ready.

## Sync

`homer-sync` means accepting chapters and rebuilding structured knowledge.

Default chapter sync:

1. Mark the target chapter `accepted`.
2. Record current content hash.
3. Rebuild `.homer/knowledge/public-lore/` from all accepted chapters.
4. Rebuild `.homer/knowledge/tracking/` from all accepted chapters.
5. Mark accepted chapter knowledge status current.

`homer-sync` does not modify `设定/` by default.

Author setting sync/index:

- Rebuild `.homer/knowledge/author-lore/` only when requested, during setup, or when a task explicitly needs author settings.
- Use full rebuild for MVP.
- Preserve source file, source quote, evidence, and extraction type.

## Setup And Import

Setup must establish chapter state.

If `正文/` is empty:

- Initialize empty `chapters.json`.

If one chapter exists:

- Ask whether it is draft or accepted unless the user instruction makes it clear.

If multiple chapters exist:

- Confirm status pattern, such as all accepted, first N accepted and later drafts, all drafts, or explicit custom status.

Imported completed/serialized works default to accepted unless the user says specific chapters are drafts.

After setup, if accepted chapters exist, generate public lore and tracking.

## Codex Adapter

Implement Codex support following Trellis conventions:

- Canonical Homer infrastructure lives under `.homer/`.
- Shared skills may be generated under `.agents/skills/`.
- Codex-specific skills, hooks, agents, and config may be generated under `.codex/`.
- Adapter files are generated from Homer templates/specs, not treated as the source of truth.
- Hooks are included following Trellis-style organization. Hooks must support the workflow but skills/scripts must still work if hooks are not enabled.

## Hard Rules

These rules belong in `.homer/spec/` and generated skill instructions:

- One project equals one book.
- `设定/`, `大纲/`, and `正文/` are author-owned.
- Author-owned settings are freeform and default not modified by Homer.
- AI-readable knowledge is JSON under `.homer/knowledge/`.
- `accepted` chapters are canon and default not editable.
- `draft` chapters are editable.
- Public lore and tracking are generated only from accepted chapters.
- Draft chapters are current-task context, not long-term public knowledge.
- Writing does not read full `设定/` by default.
- Hidden author settings may be read only as relevant `author-lore` slices.
- Inferences must never be mixed with explicit facts.
- After writing/polishing, Homer does not auto-accept or auto-sync.
