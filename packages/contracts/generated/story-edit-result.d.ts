/* Generated from JSON Schema. Do not edit manually. */

export interface StoryEditResult {
  mode: "preview" | "apply";
  base_revision: number;
  revision: number;
  changed: boolean;
  project: ProjectSpec;
  report: EditorialReport;
  impact: {
    dependency_tracking: "advisory";
    repositioned_shot_ids: string[];
    resized_shot_ids: string[];
    edited_voice_line_ids: string[];
    detached_audio_line_ids: string[];
    render_review_shot_ids: string[];
    rebuild_candidates: (
      "animatic" | "subtitles" | "audio_mix" | "video_mux" | "voice" | "alignment" | "lip_sync" | "shot_render"
    )[];
    extensions_require_review: boolean;
  };
}
/**
 * Renderer-independent source project. All video positions are whole frames.
 */
export interface ProjectSpec {
  schema_version: "1.0.0";
  project_id: string;
  title: string;
  locale: string;
  canvas: Canvas;
  assets: Asset[];
  characters: Character[];
  sequences: Sequence[];
  voice_lines: VoiceLine[];
  extensions?: Extensions;
}
export interface Canvas {
  width: number;
  height: number;
  fps: {
    numerator: number;
    denominator: number;
  };
  audio_sample_rate: number;
}
export interface Asset {
  asset_id: string;
  kind: "image" | "video" | "audio" | "model" | "other";
  uri: string;
  path: string;
  sha256: string;
  source_name?: string;
  media_type?: string;
  extensions?: Extensions;
}
/**
 * Namespaced, optional application extensions.
 */
export interface Extensions {
  [k: string]: unknown;
}
export interface Character {
  character_id: string;
  name: string;
  asset_ids: string[];
  extensions?: Extensions;
}
export interface Sequence {
  sequence_id: string;
  title: string;
  scenes: Scene[];
  extensions?: Extensions;
}
export interface Scene {
  scene_id: string;
  title: string;
  shots: Shot[];
  extensions?: Extensions;
}
export interface Shot {
  shot_id: string;
  title: string;
  duration_frames: number;
  description?: string;
  events: ShotEvent[];
  extensions?: Extensions;
}
export interface ShotEvent {
  event_id: string;
  type: string;
  frame: number;
  intensity?: number;
  payload?: {
    [k: string]: unknown;
  };
}
export interface VoiceLine {
  voice_line_id: string;
  shot_id: string;
  character_id: string;
  text: string;
  language: string;
  start_frame: number;
  duration_frames: number;
  audio_asset_id?: string;
  extensions?: Extensions;
}
/**
 * Intended sequential cut timing, not measured media or rendered output.
 */
export interface EditorialReport {
  schema_version: "1.0.0";
  project_id: string;
  project_revision: number;
  assembly: "sequential_cuts";
  fps: {
    numerator: number;
    denominator: number;
  };
  audio_sample_rate: number;
  duration_frames: number;
  duration_samples: number;
  shots: {
    shot_id: string;
    scene_id: string;
    sequence_id: string;
    title: string;
    description: string;
    start_frame: number;
    end_frame_exclusive: number;
    duration_frames: number;
    start_sample: number;
    end_sample_exclusive: number;
    duration_samples: number;
    voice_line_ids: string[];
    events: {
      event_id: string;
      type: string;
      local_frame: number;
      frame: number;
    }[];
  }[];
  voice_lines: {
    voice_line_id: string;
    shot_id: string;
    character_id: string;
    text: string;
    language: string;
    local_start_frame: number;
    audio_linked: boolean;
    start_frame: number;
    end_frame_exclusive: number;
    duration_frames: number;
    start_sample: number;
    end_sample_exclusive: number;
    duration_samples: number;
  }[];
  warnings: {
    code: "empty_scene" | "voice_audio_unlinked" | "same_speaker_overlap";
    entity_id: string;
    related_entity_id?: string;
  }[];
}
