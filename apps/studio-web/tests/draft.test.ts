import { describe, expect, it } from "vitest";
import { buildEdit, conflictFields, emptyDraft, issueEntity, moveShot, rebaseDraft } from "../src/draft";
import { document, lineId, sample, sceneId, shotId } from "./data";

describe("draft commands and conflict resolution", () => {
  it("does not create operations for unchanged values or change the source project", () => {
    const draft = emptyDraft();
    draft.texts[lineId] = sample.voice_lines[0]!.text;
    draft.durations[shotId] = "96";
    expect(buildEdit(document, draft).request).toBeNull();
    const moved = moveShot(sample, draft, sceneId, shotId, 0);
    expect(buildEdit(document, moved).request!.operations[0]).toEqual({ op: "reorder_shots", scene_id: sceneId, shot_ids: [shotId, sample.sequences[0]!.scenes[0]!.shots[0]!.shot_id] });
    expect(sample.sequences[0]!.scenes[0]!.shots[1]!.shot_id).toBe(shotId);
  });
  it.each(["", "0", "1.5", "-2", "NaN", "100000001"])("rejects invalid duration %s before sending", value => {
    const draft = emptyDraft(); draft.durations[shotId] = value;
    expect(buildEdit(document, draft).issues[0]!.entityId).toBe(shotId);
  });
  it("keeps default audio policy explicit, requiring a real user choice to detach", () => {
    const draft = emptyDraft(); draft.texts[lineId] = "Mới";
    expect(buildEdit(document, draft).request!.operations[0]).toMatchObject({ audio_policy: "reject" });
    draft.detach[lineId] = true;
    expect(buildEdit(document, draft).request!.operations[0]).toMatchObject({ audio_policy: "detach" });
  });
  it("maps project-index errors after reordering to the correct shot ID", () => {
    const draft = moveShot(sample, emptyDraft(), sceneId, shotId, 0);
    expect(issueEntity({ path: "/sequences/0/scenes/0/shots/0/duration_frames", code: "error", message: "" }, sample, draft, buildEdit(document, draft).request)).toBe(shotId);
  });
  it("requires an explicit resolution when both parties edit a line", () => {
    const next = structuredClone(sample); next.voice_lines[0]!.text = "Lời của người khác";
    const draft = emptyDraft(); draft.texts[lineId] = "Lời của mình";
    expect(conflictFields(sample, next, draft)).toHaveLength(1);
    expect(() => rebaseDraft(sample, next, draft, {})).toThrow();
    expect(rebaseDraft(sample, next, draft, { [`text:${lineId}`]: "local" }).texts[lineId]).toBe("Lời của mình");
    expect(rebaseDraft(sample, next, draft, { [`text:${lineId}`]: "remote" }).texts[lineId]).toBeUndefined();
  });
  it("does not silently drop a new shot during rebase", () => {
    const draft = moveShot(sample, emptyDraft(), sceneId, shotId, 0);
    const next = structuredClone(sample);
    next.sequences[0]!.scenes[0]!.shots.push({ shot_id: "bc2f3d49-0547-48e4-aabf-9e6dcb9f0d34", title: "New", duration_frames: 24, events: [] });
    expect(conflictFields(sample, next, draft)[0]!.canKeepLocal).toBe(false);
    expect(() => rebaseDraft(sample, next, draft, { [`order:${sceneId}`]: "local" })).toThrow();
    expect(rebaseDraft(sample, next, draft, { [`order:${sceneId}`]: "remote" }).orders).toEqual({});
  });
  it("requires a fresh audio-detach choice when the linked take changes remotely", () => {
    const base = structuredClone(sample); base.voice_lines[0]!.audio_asset_id = "take-a";
    const next = structuredClone(base); next.voice_lines[0]!.audio_asset_id = "take-b";
    const draft = emptyDraft(); draft.texts[lineId] = "Mới"; draft.detach[lineId] = true;
    const rebased = rebaseDraft(base, next, draft, {});
    expect(rebased.texts[lineId]).toBe("Mới");
    expect(rebased.detach[lineId]).toBe(false);
  });
});
