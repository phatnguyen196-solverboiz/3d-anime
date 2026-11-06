import { describe, expect, it, vi } from "vitest";
import { ApiError, createApi, loadProject } from "../src/api";
import { document, mockApi, sample } from "./data";

describe("API boundary", () => {
  it("sends credentials only in bearer headers and preserves UTF-8 JSON", async () => {
    const fetcher = vi.fn<typeof fetch>().mockResolvedValue(new Response(JSON.stringify(document), { status: 201 }));
    const api = createApi("http://127.0.0.1:8765", "test-token", fetcher);
    await api.createProject(sample);
    const [url, init] = fetcher.mock.calls[0]!;
    expect(url).toBe("http://127.0.0.1:8765/api/v1/projects");
    expect(init!.headers).toMatchObject({ Authorization: "Bearer test-token" });
    expect(init!.credentials).toBe("omit");
    expect(JSON.parse(init!.body as string).project.title).toBe("Chiếc vé bị đánh rơi");
  });
  it("rejects URLs with embedded credentials or paths", () => {
    expect(() => createApi("http://name:password@localhost:8765", "test")).toThrow();
    expect(() => createApi("http://localhost:8765/api", "test")).toThrow();
  });
  it("keeps 422 issues structured", async () => {
    const issues = [{ path: "/operations/0", code: "linked_audio_requires_detach", message: "Detach" }];
    const fetcher = vi.fn<typeof fetch>().mockResolvedValue(new Response(JSON.stringify({ detail: { issues } }), { status: 422 }));
    const api = createApi("http://localhost:8765", "test", fetcher);
    try { await api.listProjects(); throw new Error("must fail"); }
    catch (error) { expect(error).toBeInstanceOf(ApiError); expect((error as ApiError).issues).toEqual(issues); }
  });
  it("does not combine project and timing from different revisions", async () => {
    const api = mockApi(); api.getEditorial.mockResolvedValue({ ...(await api.getEditorial(sample.project_id)), project_revision: 2 });
    await expect(loadProject(api, sample.project_id)).rejects.toThrow("Dự án đổi trong lúc tải");
  });
});
