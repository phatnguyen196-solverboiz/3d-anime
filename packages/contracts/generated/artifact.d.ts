/* Generated from JSON Schema. Do not edit manually. */

export interface Artifact {
  artifact_id: string;
  job_id: string;
  uri: string;
  media_type: string;
  sha256: string;
  width?: number;
  height?: number;
  duration_frames?: number;
  metadata?: {
    [k: string]: unknown;
  };
}
