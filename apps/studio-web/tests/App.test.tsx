import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import { App } from "../src/App";
import { document, report, sample } from "./data";

function router(empty = false) {
  return vi.fn<typeof fetch>().mockImplementation(async input => {
    const url = String(input);
    if (url.endsWith("/editorial")) return Response.json(report);
    if (url.endsWith(`/projects/${sample.project_id}`)) return Response.json(document);
    if (url.endsWith("/projects")) return Response.json({ projects: empty ? [] : [{ project_id: sample.project_id, title: sample.title, revision: 1 }] });
    return new Response("not found", { status: 404 });
  });
}
it("waits for explicit sample creation and keeps the token out of browser storage", async () => {
  const fetcher = router(true); vi.stubGlobal("fetch", fetcher);
  render(<App />);
  fireEvent.change(screen.getByLabelText("Token cục bộ"), { target: { value: "test-token" } });
  fireEvent.click(screen.getByRole("button", { name: "Kết nối API" }));
  await screen.findByText("API đã kết nối");
  expect(fetcher).toHaveBeenCalledTimes(1);
  expect(fetcher.mock.calls[0]![1]!.method).toBe("GET");
  expect(window.localStorage.length).toBe(0);
  expect(window.sessionStorage.length).toBe(0);
  expect((screen.getByRole("button", { name: "Tạo / mở dự án mẫu" }) as HTMLButtonElement).disabled).toBe(false);
});
it("binds a dirty draft to its API origin even if settings were edited before the draft", async () => {
  const fetcher = router(); vi.stubGlobal("fetch", fetcher);
  render(<App />);
  fireEvent.change(screen.getByLabelText("Token cục bộ"), { target: { value: "test-token" } });
  fireEvent.click(screen.getByRole("button", { name: "Kết nối API" }));
  await screen.findByText("Bản đã lưu 1");
  fireEvent.click(screen.getByRole("button", { name: "Kết nối" }));
  fireEvent.change(screen.getByLabelText("Địa chỉ API"), { target: { value: "http://127.0.0.1:9999" } });
  fireEvent.click(screen.getByRole("button", { name: "Chọn shot: Linh nhặt vé" }));
  fireEvent.change(screen.getByRole("textbox", { name: "Thoại của Linh" }), { target: { value: "Bản nháp cần giữ" } });
  fireEvent.click(screen.getByRole("button", { name: "Cập nhật kết nối" }));
  await screen.findByRole("alert");
  expect((screen.getByRole("textbox", { name: "Thoại của Linh" }) as HTMLTextAreaElement).value).toBe("Bản nháp cần giữ");
  expect((screen.getByLabelText("Địa chỉ API") as HTMLInputElement).value).toBe("http://127.0.0.1:8765");
  expect(fetcher.mock.calls.every(([url]) => !String(url).includes(":9999"))).toBe(true);
  await waitFor(() => expect((screen.getByRole("combobox") as HTMLSelectElement).disabled).toBe(true));
});
