/* Generated from JSON Schema. Do not edit manually. */

export type Id = string;

/**
 * An ordered, atomic set of edits to a project revision. Preview and apply use the same request.
 */
export interface StoryEditRequest {
  expected_revision: number;
  /**
   * @minItems 1
   * @maxItems 100
   */
  operations: [ReorderShots | SetShotDuration | SetVoiceText, ...(ReorderShots | SetShotDuration | SetVoiceText)[]];
}
export interface ReorderShots {
  op: "reorder_shots";
  scene_id: Id;
  shot_ids: Id[];
}
export interface SetShotDuration {
  op: "set_shot_duration";
  shot_id: Id;
  duration_frames: number;
}
export interface SetVoiceText {
  op: "set_voice_text";
  voice_line_id: Id;
  text: string;
  /**
   * Changing text with linked audio requires explicit detach. The source asset is retained.
   */
  audio_policy?: "reject" | "detach";
}
