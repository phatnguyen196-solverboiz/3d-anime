/* Generated from JSON Schema. Do not edit manually. */

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
