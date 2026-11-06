import { vi } from "vitest";
import project from "../../../fixtures/story-edit-project/project.json";
import timing from "./fixtures/editorial.json";
import type { StudioApi } from "../src/api";
import type { EditorialReport, ProjectDocument, ProjectSpec, StoryEditResult } from "../src/contracts";

export const sample = project as ProjectSpec;
export const report = timing as EditorialReport;
export const document: ProjectDocument = { project: sample, revision: 1 };
export const sceneId = sample.sequences[0]!.scenes[0]!.scene_id;
export const shotId = sample.sequences[0]!.scenes[0]!.shots[1]!.shot_id;
export const lineId = sample.voice_lines[0]!.voice_line_id;
export function result(text = "Lời đã chỉnh", revision = 1, apply = false): StoryEditResult {
  const candidate = structuredClone(sample);
  candidate.voice_lines[0]!.text = text;
  const nextReport = structuredClone(report);
  nextReport.voice_lines[0]!.text = text;
  nextReport.project_revision = revision + (apply ? 1 : 0);
  return {
    mode: apply ? "apply" : "preview", base_revision: revision, revision: revision + (apply ? 1 : 0), changed: true,
    project: candidate, report: nextReport,
    impact: { dependency_tracking: "advisory", repositioned_shot_ids: [], resized_shot_ids: [],
      edited_voice_line_ids: [lineId], detached_audio_line_ids: [], render_review_shot_ids: [shotId],
      rebuild_candidates: ["voice", "alignment", "lip_sync", "subtitles", "audio_mix", "video_mux"], extensions_require_review: false },
  };
}
export function mockApi() {
  return {
    listProjects: vi.fn<StudioApi["listProjects"]>().mockResolvedValue([{ project_id: sample.project_id, title: sample.title, revision: 1 }]),
    getProject: vi.fn<StudioApi["getProject"]>().mockResolvedValue(structuredClone(document)),
    getEditorial: vi.fn<StudioApi["getEditorial"]>().mockResolvedValue(structuredClone(report)),
    createProject: vi.fn<StudioApi["createProject"]>().mockResolvedValue(structuredClone(document)),
    preview: vi.fn<StudioApi["preview"]>().mockResolvedValue(result()),
    apply: vi.fn<StudioApi["apply"]>().mockResolvedValue(result("Lời đã chỉnh", 1, true)),
  };
}
