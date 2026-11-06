/* Generated from JSON Schema. Do not edit manually. */

export interface Job {
  job_id: string;
  project_id: string;
  project_revision: number;
  operation: "project.validate" | "render.shot.blender";
  state: "queued" | "running" | "cancel_requested" | "cancelled" | "succeeded" | "failed";
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
  result: {
    [k: string]: unknown;
  } | null;
  error: {
    [k: string]: unknown;
  } | null;
}
