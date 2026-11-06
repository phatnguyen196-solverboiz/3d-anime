# Working agreement for AnimeFlow

- Read the README and the relevant part of docs/teamwork-vi.md before changing a module.
- Coordinate ownership by path and use separate branches or worktrees when several contributors work in parallel. Never overwrite unrelated changes.
- JSON Schemas under packages/contracts are the source of truth. Update the schema and examples first, regenerate TypeScript declarations, and coordinate contract changes with the core owner.
- Treat the research catalog as evidence and candidates, not as a list of installed or supported integrations. Do not add weights, credentials, large media or third-party source code without an explicit integration and licensing decision.
- Keep unfinished capabilities visible as planned or unsupported; do not fabricate render, TTS, audio, or job results.
- Run the checks relevant to your change and document limitations in the handoff.
