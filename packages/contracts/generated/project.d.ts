/* Generated from JSON Schema. Do not edit manually. */

export type Id = string;

/**
 * Renderer-independent source project. All video positions are whole frames.
 */
export interface ProjectSpec {
  schema_version: "1.0.0";
  project_id: Id;
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
  asset_id: Id;
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
  character_id: Id;
  name: string;
  asset_ids: Id[];
  extensions?: Extensions;
}
export interface Sequence {
  sequence_id: Id;
  title: string;
  scenes: Scene[];
  extensions?: Extensions;
}
export interface Scene {
  scene_id: Id;
  title: string;
  shots: Shot[];
  extensions?: Extensions;
}
export interface Shot {
  shot_id: Id;
  title: string;
  duration_frames: number;
  description?: string;
  events: ShotEvent[];
  extensions?: Extensions;
}
export interface ShotEvent {
  event_id: Id;
  type: string;
  frame: number;
  intensity?: number;
  payload?: {
    [k: string]: unknown;
  };
}
export interface VoiceLine {
  voice_line_id: Id;
  shot_id: Id;
  character_id: Id;
  text: string;
  language: string;
  start_frame: number;
  duration_frames: number;
  audio_asset_id?: Id;
  extensions?: Extensions;
}
