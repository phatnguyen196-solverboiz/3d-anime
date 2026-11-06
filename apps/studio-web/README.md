# AnimeFlow Story Editor

React/TypeScript editor for the revision-safe story endpoints. It uses the existing Studio dark CSS tokens and the generated ProjectSpec, StoryEditRequest, StoryEditResult and EditorialReport contracts. Only this focused editor is integrated; the broader UI-kit/studio mock draft remains separate.

## Run

Use Node 22.12+ or LTS 24. At the repository root:

```powershell
npm ci --ignore-scripts
npm run dev
```

Start the Python API using the root README, then open `http://127.0.0.1:5173`. Enter the API URL (default `http://127.0.0.1:8765`) and its bearer token. The token is only held in memory and sent in an authorization header. No browser storage or URL query contains it. The dev server binds to loopback.

For a production-build preview: `npm run build`, then `npm run preview --workspace @animeflow/studio-web`. To change the UI port, pass `-- --port 5174` to the workspace script and include that origin in `ANIMEFLOW_CORS_ORIGINS` on the backend.

The Vite 8 toolchain uses Rolldown/Oxc. Configuration loads natively from `.mjs`, avoiding a separate TypeScript config bundling step. This also avoids the esbuild ancestor-directory permission failure encountered in the Windows Codex sandbox.

## Behavior

- The bundled three-shot sample starts read-only. No project is silently created on the API. Create/open sample loads the existing project if present, preserving its saved edits.
- Drag/drop or Alt+ArrowUp/ArrowDown reorders within a scene. Plain arrows move selection; stable IDs retain selection/focus through reordering.
- Duration remains an integer frame count; voice slots/events remain shot-local. Timeline uses the API report's global ranges. Voice blocks are planned placements, not waveforms or playable audio.
- Editing text with linked audio defaults to reject. An explicit checkbox selects detach; the source asset is retained.
- Each draft change invalidates a completed preview and aborts a pending one. A late response is ignored even when the transport disregards abort. Apply sends the exact approved request and locks draft editing while saving.
- 422 errors map back to the affected shot/line, including project-index errors after reorder. 409 fetches the latest project/report while retaining the draft; overlapping field edits require a choice. Removed entities or changed scene membership require adopting that part of the remote version. Rebase is explicit and needs another preview.
- A changed audio take resets any earlier detach choice. A network failure during apply is treated as an unknown outcome and triggers readback, without an automatic save retry.
- Switching project/server is blocked while dirty or applying. Updating the token on the same server retains the draft. Project and report from mismatched revisions are rejected at load.
- Discard requires confirmation. Leaving a dirty tab requests a browser warning. Drafts and credentials are not persisted across reloads.

## Checks

```powershell
npm run typecheck
npm run build
npm run test:ui
```

Component tests cover stale responses, 422 mapping, explicit detach, 409/manual rebase, uncertain save readback, keyboard/drag reordering, discard and beforeunload. Pure tests cover command generation, permutations and deleted/new entities during rebase. API tests cover credentials and cross-revision loading.

A production-build browser run against a real disposable FastAPI/SQLite instance verified sample creation, editing, invalid duration rejection, non-persisting preview, an injected concurrent update causing 409, explicit merge/re-preview/apply to revision 3 and successful reopening after reload. Mobile layout at 430px was checked for page-wide overflow. No rendered video, generated speech or playback was exercised.

## Limits

No persistent draft recovery/undo, cross-scene moves, shot creation/deletion, J/L cuts, transitions, video/audio player or render controls. Impact is advisory; rebuild jobs/cache invalidation are not executed. The sample has no media. Images/audio/video remain separate pipeline work.
