export type { ProjectSpec, Shot, Scene, VoiceLine } from "../../../packages/contracts/generated/project";
export type { StoryEditRequest } from "../../../packages/contracts/generated/story-edit";
export type { StoryEditResult } from "../../../packages/contracts/generated/story-edit-result";
export type { EditorialReport } from "../../../packages/contracts/generated/editorial-report";

import type { ProjectSpec } from "../../../packages/contracts/generated/project";
import type { EditorialReport } from "../../../packages/contracts/generated/editorial-report";
export interface ProjectDocument { project: ProjectSpec; revision: number }
export interface LoadedProject { document: ProjectDocument; report: EditorialReport }
export interface ProjectSummary { project_id: string; title: string; revision: number }
export interface Issue { path: string; code: string; message: string }
