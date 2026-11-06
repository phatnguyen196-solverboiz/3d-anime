import type { Issue, ProjectDocument, ProjectSpec, Scene, StoryEditRequest } from "./contracts";

export type Operation = StoryEditRequest["operations"][number];
export interface Draft {
  orders: Record<string, string[]>;
  durations: Record<string, string>;
  texts: Record<string, string>;
  detach: Record<string, boolean>;
}
export interface DraftIssue { entityId: string; message: string }
export const emptyDraft = (): Draft => ({ orders: {}, durations: {}, texts: {}, detach: {} });
export const scenesOf = (project: ProjectSpec): Scene[] => project.sequences.flatMap(sequence => sequence.scenes);
export const shotsOf = (project: ProjectSpec) => scenesOf(project).flatMap(scene => scene.shots);
const equalOrder = (a: string[], b: string[]) => a.length === b.length && a.every((id, i) => id === b[i]);
const validDuration = (value: string) => /^\d+$/.test(value) && Number(value) >= 1 && Number(value) <= 100000000;

export function buildEdit(document: ProjectDocument, draft: Draft) {
  const operations: Operation[] = [];
  const issues: DraftIssue[] = [];
  for (const scene of scenesOf(document.project)) {
    const original = scene.shots.map(shot => shot.shot_id);
    const order = draft.orders[scene.scene_id];
    if (order && !equalOrder(order, original)) {
      if (order.length !== original.length || new Set(order).size !== order.length || order.some(id => !original.includes(id))) {
        issues.push({ entityId: scene.scene_id, message: "Danh sách shot đã đổi. Cần đối chiếu thứ tự mới." });
      } else operations.push({ op: "reorder_shots", scene_id: scene.scene_id, shot_ids: order });
    }
    for (const shot of scene.shots) {
      const value = draft.durations[shot.shot_id];
      if (value !== undefined && value !== String(shot.duration_frames)) {
        if (!validDuration(value)) issues.push({ entityId: shot.shot_id, message: "Thời lượng cần là số frame nguyên từ 1 đến 100.000.000." });
        else if (Number(value) !== shot.duration_frames) operations.push({ op: "set_shot_duration", shot_id: shot.shot_id, duration_frames: Number(value) });
      }
    }
  }
  for (const line of document.project.voice_lines) {
    const text = draft.texts[line.voice_line_id];
    if (text !== undefined && text !== line.text) {
      if (!text.trim() || text.length > 10000) issues.push({ entityId: line.voice_line_id, message: "Câu thoại cần có nội dung và tối đa 10.000 ký tự." });
      else operations.push({ op: "set_voice_text", voice_line_id: line.voice_line_id, text,
        audio_policy: draft.detach[line.voice_line_id] ? "detach" : "reject" });
    }
  }
  const request: StoryEditRequest | null = operations.length
    ? { expected_revision: document.revision, operations: operations as [Operation, ...Operation[]] } : null;
  if (operations.length > 100) issues.push({ entityId: document.project.project_id, message: "Mỗi lần lưu tối đa 100 thay đổi. Hãy chia thành các đợt nhỏ hơn." });
  return { request, issues, dirty: operations.length > 0 || issues.length > 0, fingerprint: JSON.stringify({ request, issues }) };
}

export function orderedScenes(project: ProjectSpec, draft: Draft): Scene[] {
  return scenesOf(project).map(scene => {
    const byId = new Map(scene.shots.map(shot => [shot.shot_id, shot]));
    return { ...scene, shots: (draft.orders[scene.scene_id] ?? scene.shots.map(shot => shot.shot_id))
      .map(id => byId.get(id)).filter(shot => shot !== undefined) };
  });
}

export function moveShot(project: ProjectSpec, draft: Draft, sceneId: string, shotId: string, to: number): Draft {
  const scene = orderedScenes(project, draft).find(value => value.scene_id === sceneId);
  if (!scene || to < 0 || to >= scene.shots.length) return draft;
  const order = scene.shots.map(shot => shot.shot_id);
  const index = order.indexOf(shotId);
  if (index < 0 || index === to) return draft;
  order.splice(index, 1);
  order.splice(to, 0, shotId);
  return { ...draft, orders: { ...draft.orders, [sceneId]: order } };
}

export function issueEntity(issue: Issue, project: ProjectSpec, draft: Draft, request: StoryEditRequest | null): string | undefined {
  const operationIndex = /^\/operations\/(\d+)/.exec(issue.path);
  if (operationIndex) {
    const operation = request?.operations[Number(operationIndex[1])];
    if (operation?.op === "reorder_shots") return operation.scene_id;
    if (operation?.op === "set_shot_duration") return operation.shot_id;
    if (operation?.op === "set_voice_text") return operation.voice_line_id;
  }
  const lineIndex = /^\/voice_lines\/(\d+)/.exec(issue.path);
  if (lineIndex) return project.voice_lines[Number(lineIndex[1])]?.voice_line_id;
  const shotIndex = /^\/sequences\/(\d+)\/scenes\/(\d+)\/shots\/(\d+)/.exec(issue.path);
  if (shotIndex) {
    const scene = project.sequences[Number(shotIndex[1])]?.scenes[Number(shotIndex[2])];
    return orderedScenes(project, draft).find(item => item.scene_id === scene?.scene_id)?.shots[Number(shotIndex[3])]?.shot_id;
  }
  return undefined;
}

export const issueText = (issue: Issue): string => ({
  event_out_of_shot: "Shot quá ngắn: có sự kiện nằm ngoài đoạn hình.",
  voice_line_out_of_shot: "Shot quá ngắn: câu thoại không còn nằm trọn trong shot.",
  linked_audio_requires_detach: "Câu đã đổi. Chọn tách audio cũ trước khi xem tác động.",
  invalid_blender_scene: "Keyframe hoặc scene Blender không còn phù hợp thời lượng này.",
  invalid_shot_order: "Thứ tự cần chứa đủ shot của cảnh, mỗi shot đúng một lần.",
}[issue.code] ?? issue.message);

interface ChangedField {
  key: string;
  kind: "order" | "duration" | "text";
  entityId: string;
  label: string;
  original: string;
  local: string;
  remote: string;
  canKeepLocal: boolean;
  conflict: boolean;
}
export type FieldConflict = ChangedField;
export type Resolutions = Record<string, "local" | "remote">;

function changedFields(base: ProjectSpec, latest: ProjectSpec, draft: Draft): ChangedField[] {
  const fields: ChangedField[] = [];
  for (const scene of scenesOf(base)) {
    const order = draft.orders[scene.scene_id];
    const original = scene.shots.map(shot => shot.shot_id);
    if (!order || equalOrder(order, original)) continue;
    const remoteScene = scenesOf(latest).find(value => value.scene_id === scene.scene_id);
    const remote = remoteScene?.shots.map(shot => shot.shot_id) ?? [];
    const sameMembers = order.length === remote.length && order.every(id => remote.includes(id));
    const names = new Map([...shotsOf(base), ...shotsOf(latest)].map(shot => [shot.shot_id, shot.title]));
    const label = (ids: string[]) => ids.map(id => names.get(id) ?? id).join(" → ") || "Đã xóa cảnh";
    fields.push({ key: `order:${scene.scene_id}`, kind: "order", entityId: scene.scene_id, label: `Thứ tự · ${scene.title}`,
      original: label(original), local: label(order), remote: label(remote), canKeepLocal: sameMembers,
      conflict: !sameMembers || (!equalOrder(original, remote) && !equalOrder(order, remote)) });
  }
  for (const shot of shotsOf(base)) {
    const local = draft.durations[shot.shot_id];
    if (local === undefined || local === String(shot.duration_frames)) continue;
    const remote = shotsOf(latest).find(value => value.shot_id === shot.shot_id);
    fields.push({ key: `duration:${shot.shot_id}`, kind: "duration", entityId: shot.shot_id, label: `Thời lượng · ${shot.title}`,
      original: String(shot.duration_frames), local, remote: remote ? String(remote.duration_frames) : "Shot đã bị xóa",
      canKeepLocal: !!remote, conflict: !remote || (remote.duration_frames !== shot.duration_frames && String(remote.duration_frames) !== local) });
  }
  for (const line of base.voice_lines) {
    const local = draft.texts[line.voice_line_id];
    if (local === undefined || local === line.text) continue;
    const remote = latest.voice_lines.find(value => value.voice_line_id === line.voice_line_id);
    fields.push({ key: `text:${line.voice_line_id}`, kind: "text", entityId: line.voice_line_id, label: "Câu thoại",
      original: line.text, local, remote: remote?.text ?? "Câu thoại đã bị xóa", canKeepLocal: !!remote,
      conflict: !remote || (remote.text !== line.text && remote.text !== local) });
  }
  return fields;
}

export function conflictFields(base: ProjectSpec, latest: ProjectSpec, draft: Draft): FieldConflict[] {
  return changedFields(base, latest, draft).filter(field => field.conflict);
}

export function rebaseDraft(base: ProjectSpec, latest: ProjectSpec, draft: Draft, resolutions: Resolutions): Draft {
  const next = emptyDraft();
  for (const field of changedFields(base, latest, draft)) {
    if (field.conflict && (!resolutions[field.key] || (resolutions[field.key] === "local" && !field.canKeepLocal))) {
      throw new Error("Cần chọn bản giữ lại cho từng mục xung đột.");
    }
    if (field.conflict && resolutions[field.key] === "remote") continue;
    if (field.kind === "order") next.orders[field.entityId] = [...draft.orders[field.entityId]!];
    if (field.kind === "duration") next.durations[field.entityId] = field.local;
    if (field.kind === "text") {
      next.texts[field.entityId] = field.local;
      const original = base.voice_lines.find(line => line.voice_line_id === field.entityId);
      const remote = latest.voice_lines.find(line => line.voice_line_id === field.entityId);
      next.detach[field.entityId] = !!draft.detach[field.entityId] && original?.audio_asset_id === remote?.audio_asset_id;
    }
  }
  return next;
}
