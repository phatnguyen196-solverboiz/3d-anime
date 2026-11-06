/* Generated from JSON Schema. Do not edit manually. */

/**
 * Verified PNG frame result of a single Blender shot job. Frame end is exclusive.
 */
export interface RenderResult {
  adapter_id: "animeflow.blender.primitives";
  adapter_version: string;
  backend_version: string;
  project_id: string;
  shot_id: string;
  job_id: string;
  frame_start: number;
  frame_end_exclusive: number;
  fps: {
    numerator: number;
    denominator: number;
  };
  width: number;
  height: number;
  source_sha256: string;
  seed: number;
  /**
   * @minItems 1
   */
  frames: [
    {
      index: number;
      path: string;
      sha256: string;
      width: number;
      height: number;
    },
    ...{
      index: number;
      path: string;
      sha256: string;
      width: number;
      height: number;
    }[]
  ];
  warnings: string[];
}
