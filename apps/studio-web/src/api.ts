import type {
  EditorialReport, Issue, LoadedProject, ProjectDocument, ProjectSpec, ProjectSummary,
  StoryEditRequest, StoryEditResult,
} from "./contracts";

export class ApiError extends Error {
  constructor(public status: number, message: string, public issues: Issue[] = []) {
    super(message);
    this.name = "ApiError";
  }
}

export interface StudioApi {
  listProjects(signal?: AbortSignal): Promise<ProjectSummary[]>;
  getProject(id: string, signal?: AbortSignal): Promise<ProjectDocument>;
  getEditorial(id: string, signal?: AbortSignal): Promise<EditorialReport>;
  createProject(project: ProjectSpec, signal?: AbortSignal): Promise<ProjectDocument>;
  preview(id: string, edit: StoryEditRequest, signal?: AbortSignal): Promise<StoryEditResult>;
  apply(id: string, edit: StoryEditRequest, signal?: AbortSignal): Promise<StoryEditResult>;
}

export function createApi(origin: string, token: string, fetcher: typeof fetch = fetch): StudioApi {
  const url = new URL(origin);
  if (!["http:", "https:"].includes(url.protocol) || url.username || url.password ||
      url.pathname !== "/" || url.search || url.hash) {
    throw new Error("Nhập địa chỉ API dạng http://127.0.0.1:8765, không có đường dẫn.");
  }
  if (!token.trim()) throw new Error("Nhập token API để kết nối.");
  async function request<T>(path: string, method = "GET", body?: unknown, signal?: AbortSignal): Promise<T> {
    const response = await fetcher(`${url.origin}/api/v1${path}`, {
      method, signal, cache: "no-store", credentials: "omit",
      headers: { Authorization: `Bearer ${token}`, ...(body ? { "Content-Type": "application/json" } : {}) },
      ...(body ? { body: JSON.stringify(body) } : {}),
    });
    if (!response.ok) {
      const payload = await response.json().catch(() => ({}));
      const detail = payload.detail;
      const messages: Record<number, string> = {
        401: "Token không hợp lệ. Cập nhật token để kết nối lại; bản nháp vẫn được giữ.",
        404: "Không tìm thấy dự án.",
        409: "Dự án đã có bản mới. Bản nháp của bạn vẫn được giữ.",
        422: "Có thay đổi chưa hợp lệ. Xem lỗi cạnh shot hoặc câu thoại.",
      };
      throw new ApiError(response.status, messages[response.status] ?? "API chưa xử lý được yêu cầu. Hãy thử lại.",
        Array.isArray(detail?.issues) ? detail.issues : []);
    }
    return response.json() as Promise<T>;
  }
  return {
    listProjects: async signal => (await request<{ projects: ProjectSummary[] }>("/projects", "GET", undefined, signal)).projects,
    getProject: (id, signal) => request(`/projects/${id}`, "GET", undefined, signal),
    getEditorial: (id, signal) => request(`/projects/${id}/editorial`, "GET", undefined, signal),
    createProject: (project, signal) => request("/projects", "POST", { project }, signal),
    preview: (id, edit, signal) => request(`/projects/${id}/story-edits/preview`, "POST", edit, signal),
    apply: (id, edit, signal) => request(`/projects/${id}/story-edits`, "POST", edit, signal),
  };
}

export async function loadProject(api: StudioApi, id: string, signal?: AbortSignal): Promise<LoadedProject> {
  const document = await api.getProject(id, signal);
  const report = await api.getEditorial(id, signal);
  if (document.revision !== report.project_revision || document.project.project_id !== report.project_id) {
    throw new Error("Dự án đổi trong lúc tải. Bấm mở lại để nhận một bản đồng bộ.");
  }
  return { document, report };
}

export function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : "Không thể kết nối API. Bản nháp vẫn được giữ.";
}
