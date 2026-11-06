import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiError } from "../src/api";
import { StoryEditor } from "../src/StoryEditor";
import type { StoryEditResult } from "../src/contracts";
import { document, lineId, mockApi, report, result, sample, shotId } from "./data";

const button = (name: string) => screen.getByRole("button", { name }) as HTMLButtonElement;
const textarea = () => screen.getByRole("textbox", { name: "Thoại của Linh" }) as HTMLTextAreaElement;
function editLine(text = "Lời đã chỉnh") {
  fireEvent.click(button("Chọn shot: Linh nhặt vé"));
  fireEvent.change(textarea(), { target: { value: text } });
}
describe("story editing workflow", () => {
  it("warns before leaving an unsaved draft, and clears the warning after discarding", () => {
    render(<StoryEditor initialDocument={document} initialReport={report} api={mockApi()} />);
    const clean = new Event("beforeunload", { cancelable: true }); window.dispatchEvent(clean);
    expect(clean.defaultPrevented).toBe(false);
    editLine();
    const dirty = new Event("beforeunload", { cancelable: true }); window.dispatchEvent(dirty);
    expect(dirty.defaultPrevented).toBe(true);
    fireEvent.click(button("Bỏ bản nháp")); fireEvent.click(button("Xác nhận bỏ nháp"));
    const discarded = new Event("beforeunload", { cancelable: true }); window.dispatchEvent(discarded);
    expect(discarded.defaultPrevented).toBe(false);
  });
  it("shows the sample read-only when no API document is open", () => {
    render(<StoryEditor initialDocument={document} initialReport={null} api={null} />);
    fireEvent.click(button("Chọn shot: Linh nhặt vé"));
    expect(textarea().disabled).toBe(true);
    expect(button("Xem tác động").disabled).toBe(true);
    expect(screen.queryByRole("button", { name: /phát video/i })).toBeNull();
  });
  it("keeps selection and keyboard focus stable when moving by keyboard or drag", async () => {
    render(<StoryEditor initialDocument={document} initialReport={report} api={mockApi()} />);
    const reaction = button("Chọn shot: Linh nhặt vé");
    fireEvent.keyDown(reaction, { altKey: true, key: "ArrowUp" });
    expect(screen.getAllByRole("button", { name: /Chọn shot:/ })[0]).toBe(reaction);
    expect(reaction.getAttribute("aria-current")).toBe("true");
    await waitFor(() => expect(window.document.activeElement).toBe(reaction));
    const opening = button("Chọn shot: Tấm vé dưới chân");
    fireEvent.dragStart(reaction.closest("li")!, { dataTransfer: { setData() {}, effectAllowed: "none" } });
    fireEvent.drop(opening.closest("li")!);
    expect(screen.getAllByRole("button", { name: /Chọn shot:/ })[1]).toBe(reaction);
    expect(reaction.getAttribute("aria-current")).toBe("true");
  });
  it("previews without saving, then applies the exact approved request", async () => {
    const api = mockApi();
    render(<StoryEditor initialDocument={document} initialReport={report} api={api} />);
    editLine();
    expect(button("Lưu thay đổi").disabled).toBe(true);
    fireEvent.click(button("Xem tác động"));
    await screen.findByText("Phương án chưa lưu");
    expect(api.apply).not.toHaveBeenCalled();
    fireEvent.click(button("Lưu thay đổi"));
    await screen.findByText("Đã lưu bản 2.");
    expect(api.apply.mock.calls[0]![1]).toEqual(api.preview.mock.calls[0]![1]);
    expect(screen.getByText("Bản đã lưu 2")).toBeTruthy();
    expect(button("Lưu thay đổi").disabled).toBe(true);
    expect(textarea().value).toBe("Lời đã chỉnh");
  });
  it("ignores a preview that finishes after a new edit even if the transport ignores abort", async () => {
    let finish!: (value: StoryEditResult) => void;
    const api = mockApi(); api.preview.mockReturnValue(new Promise(resolve => { finish = resolve; }));
    render(<StoryEditor initialDocument={document} initialReport={report} api={api} />);
    editLine("Câu cũ đang chờ"); fireEvent.click(button("Xem tác động"));
    fireEvent.change(textarea(), { target: { value: "Câu vừa sửa tiếp" } });
    await act(async () => { finish(result("Câu cũ đang chờ")); });
    expect(screen.queryByText("Phương án chưa lưu")).toBeNull();
    expect(button("Lưu thay đổi").disabled).toBe(true);
    expect(textarea().value).toBe("Câu vừa sửa tiếp");
    expect(api.preview.mock.calls[0]![2]!.aborted).toBe(true);
  });
  it("disables saving when the draft changes after a completed preview", async () => {
    render(<StoryEditor initialDocument={document} initialReport={report} api={mockApi()} />);
    editLine(); fireEvent.click(button("Xem tác động")); await screen.findByText("Phương án chưa lưu");
    fireEvent.change(textarea(), { target: { value: "Một câu khác" } });
    expect(button("Lưu thay đổi").disabled).toBe(true);
    expect(screen.queryByText("Phương án chưa lưu")).toBeNull();
  });
  it("links a backend timing error to the right shot after reordering", async () => {
    const api = mockApi(); api.preview.mockRejectedValue(new ApiError(422, "Có lỗi", [{
      path: "/sequences/0/scenes/0/shots/0/extensions/animeflow.blender.scene.v1/objects/0/keyframes/0/frame",
      code: "invalid_blender_scene", message: "Keyframe invalid",
    }]));
    render(<StoryEditor initialDocument={document} initialReport={report} api={api} />);
    fireEvent.click(button("Đưa Linh nhặt vé lên"));
    fireEvent.change(screen.getByLabelText(/Thời lượng shot/), { target: { value: "30" } });
    fireEvent.click(button("Xem tác động"));
    await screen.findByRole("alert");
    expect(screen.getByLabelText(/Thời lượng shot/).getAttribute("aria-invalid")).toBe("true");
    expect(button("Chọn shot: Linh nhặt vé").getAttribute("aria-current")).toBe("true");
    expect(button("Lưu thay đổi").disabled).toBe(true);
  });
  it("requires a checkbox choice before detaching a linked take", async () => {
    const linked = structuredClone(document); linked.project.voice_lines[0]!.audio_asset_id = "audio-test";
    const api = mockApi(); api.preview.mockRejectedValueOnce(new ApiError(422, "Cần tách audio", [{ path: "/operations/0", code: "linked_audio_requires_detach", message: "Detach" }]));
    render(<StoryEditor initialDocument={linked} initialReport={report} api={api} />);
    editLine(); fireEvent.click(button("Xem tác động")); await screen.findByRole("alert");
    expect(api.preview.mock.calls[0]![1].operations[0]).toMatchObject({ audio_policy: "reject" });
    fireEvent.click(screen.getByRole("checkbox", { name: /Tách audio cũ/ }));
    fireEvent.click(button("Xem tác động")); await screen.findByText("Phương án chưa lưu");
    expect(api.preview.mock.calls[1]![1].operations[0]).toMatchObject({ audio_policy: "detach" });
  });
  it("keeps the draft on 409, fetches the latest and requires explicit conflict resolution and re-preview", async () => {
    const api = mockApi();
    api.apply.mockRejectedValueOnce(new ApiError(409, "Dự án đã có bản mới."));
    const latest = structuredClone(document); latest.revision = 2; latest.project.voice_lines[0]!.text = "Nội dung của người khác";
    api.getProject.mockResolvedValue(latest);
    api.getEditorial.mockResolvedValue({ ...structuredClone(report), project_revision: 2 });
    render(<StoryEditor initialDocument={document} initialReport={report} api={api} />);
    editLine(); fireEvent.click(button("Xem tác động")); await screen.findByText("Phương án chưa lưu");
    fireEvent.click(button("Lưu thay đổi"));
    await screen.findByText("Nội dung của người khác");
    expect(textarea().value).toBe("Lời đã chỉnh");
    expect(button("Tiếp tục trên bản mới").disabled).toBe(true);
    expect(button("Lưu thay đổi").disabled).toBe(true);
    fireEvent.click(screen.getByLabelText("Giữ bản nháp · Câu thoại"));
    fireEvent.click(button("Tiếp tục trên bản mới"));
    expect(textarea().value).toBe("Lời đã chỉnh");
    expect(screen.getByText("Bản đã lưu 2")).toBeTruthy();
    expect(button("Lưu thay đổi").disabled).toBe(true);
    expect(api.apply).toHaveBeenCalledTimes(1);
    api.preview.mockResolvedValue(result("Lời đã chỉnh", 2));
    fireEvent.click(button("Xem tác động")); await screen.findByText("Phương án chưa lưu");
    expect(api.preview.mock.calls[1]![1].expected_revision).toBe(2);
  });
  it("handles an unknown network save outcome by reading back, preserving draft and avoiding an automatic retry", async () => {
    const api = mockApi(); api.apply.mockRejectedValue(new TypeError("Failed to fetch"));
    api.getProject.mockResolvedValue({ project: result().project, revision: 2 });
    api.getEditorial.mockResolvedValue({ ...result().report, project_revision: 2 });
    render(<StoryEditor initialDocument={document} initialReport={report} api={api} />);
    editLine(); fireEvent.click(button("Xem tác động")); await screen.findByText("Phương án chưa lưu");
    fireEvent.click(button("Lưu thay đổi"));
    await waitFor(() => expect(button("Tiếp tục trên bản mới").disabled).toBe(false));
    expect(textarea().value).toBe("Lời đã chỉnh");
    fireEvent.click(button("Tiếp tục trên bản mới"));
    expect(button("Xem tác động").disabled).toBe(true);
    expect(api.apply).toHaveBeenCalledTimes(1);
  });
  it("does not discard a draft until explicitly confirmed", () => {
    render(<StoryEditor initialDocument={document} initialReport={report} api={mockApi()} />);
    editLine(); fireEvent.click(button("Bỏ bản nháp"));
    expect(textarea().value).toBe("Lời đã chỉnh");
    fireEvent.click(button("Xác nhận bỏ nháp"));
    expect(textarea().value).toBe(sample.voice_lines.find(line => line.voice_line_id === lineId)!.text);
    expect(button("Xem tác động").disabled).toBe(true);
  });
  it("blocks empty duration locally and does not call the API", () => {
    const api = mockApi(); render(<StoryEditor initialDocument={document} initialReport={report} api={api} />);
    fireEvent.click(button("Chọn shot: Linh nhặt vé"));
    fireEvent.change(screen.getByLabelText(/Thời lượng shot/), { target: { value: "" } });
    expect(button("Xem tác động").disabled).toBe(true);
    expect(api.preview).not.toHaveBeenCalled();
    expect(screen.getByLabelText(/Thời lượng shot/).getAttribute("aria-invalid")).toBe("true");
    expect(screen.getByLabelText(/Thời lượng shot/).id).toBe(`edit-${shotId}`);
  });
});
