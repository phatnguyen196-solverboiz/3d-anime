import { useEffect, useRef, useState, type FormEvent } from "react";
import fixture from "../../../fixtures/story-edit-project/project.json";
import { ApiError, createApi, errorMessage, loadProject, type StudioApi } from "./api";
import type { EditorialReport, LoadedProject, ProjectDocument, ProjectSpec, ProjectSummary } from "./contracts";
import { StoryEditor } from "./StoryEditor";

const sample = fixture as ProjectSpec;
export function App() {
  const [origin, setOrigin] = useState("http://127.0.0.1:8765");
  const [token, setToken] = useState("");
  const [api, setApi] = useState<StudioApi | null>(null);
  const [boundOrigin, setBoundOrigin] = useState("");
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [chosen, setChosen] = useState("");
  const [loaded, setLoaded] = useState<{ document: ProjectDocument; report: EditorialReport | null }>({ document: { project: sample, revision: 1 }, report: null });
  const [remote, setRemote] = useState(false);
  const [generation, setGeneration] = useState(0);
  const [dirty, setDirty] = useState(false);
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(true);
  const [error, setError] = useState("");
  const pending = useRef<AbortController | null>(null);
  const ticket = useRef(0);
  useEffect(() => () => { ticket.current++; pending.current?.abort(); }, []);

  function accept(value: LoadedProject) {
    setLoaded(value); setRemote(true); setChosen(value.document.project.project_id);
    setGeneration(current => current + 1); setDirty(false);
  }
  async function perform(action: (signal: AbortSignal, id: number) => Promise<void>) {
    if (busy || loading) return;
    pending.current?.abort();
    const controller = new AbortController(); pending.current = controller;
    const id = ++ticket.current;
    setLoading(true); setError("");
    try { await action(controller.signal, id); }
    catch (cause) { if (!controller.signal.aborted && id === ticket.current) setError(cause instanceof TypeError ? "Không kết nối được API. Hãy khởi chạy server và kiểm tra địa chỉ." : errorMessage(cause)); }
    finally { if (!controller.signal.aborted && id === ticket.current) setLoading(false); }
  }
  function connect(event: FormEvent) {
    event.preventDefault();
    void perform(async (signal, id) => {
      const client = createApi(origin.trim(), token);
      const endpoint = new URL(origin.trim()).origin;
      if (dirty && boundOrigin && endpoint !== boundOrigin) {
        setOrigin(boundOrigin);
        throw new Error("Bản nháp thuộc API đang mở. Địa chỉ đã trở về server đó; lưu hoặc bỏ nháp trước khi đổi server.");
      }
      const list = await client.listProjects(signal);
      const shouldOpen = (!remote || boundOrigin !== endpoint) && !dirty;
      const first = shouldOpen && list[0] ? await loadProject(client, list[0].project_id, signal) : null;
      if (signal.aborted || id !== ticket.current) return;
      setApi(client); setBoundOrigin(endpoint); setProjects(list); setSettingsOpen(false);
      if (first) accept(first);
      else if (shouldOpen && !list.length) {
        setRemote(false); setChosen(""); setLoaded({ document: { project: sample, revision: 1 }, report: null }); setGeneration(current => current + 1);
      }
    });
  }
  function openProject() {
    if (!api || !chosen || dirty) return;
    void perform(async (signal, id) => {
      const value = await loadProject(api, chosen, signal);
      if (!signal.aborted && id === ticket.current) accept(value);
    });
  }
  function createSample() {
    if (!api || dirty) return;
    void perform(async (signal, id) => {
      try { await api.getProject(sample.project_id, signal); }
      catch (cause) {
        if (!(cause instanceof ApiError) || cause.status !== 404) throw cause;
        try { await api.createProject(sample, signal); }
        catch (conflict) { if (!(conflict instanceof ApiError) || conflict.status !== 409) throw conflict; }
      }
      const value = await loadProject(api, sample.project_id, signal);
      const list = await api.listProjects(signal);
      if (!signal.aborted && id === ticket.current) { setProjects(list); accept(value); }
    });
  }
  return <>
    <header className="app-header"><a className="brand" href="#story-workspace"><span className="brand-mark" aria-hidden="true">✦</span><span>ANIMEFLOW<small>STORY WORKSPACE</small></span></a>
      <div className="header-right"><span className="badge"><span className={`status-dot ${api ? "" : "offline-dot"}`} />{api ? "API đã kết nối" : "Chưa kết nối API"}</span>
        <button type="button" className="button secondary small-button" aria-expanded={settingsOpen} aria-controls="connection-panel" onClick={() => setSettingsOpen(value => !value)}>Kết nối</button></div></header>
    {settingsOpen && <form id="connection-panel" className="connection-panel" onSubmit={connect} aria-label="Kết nối API">
      <label>Địa chỉ API<input type="url" value={origin} onChange={event => setOrigin(event.target.value)} disabled={dirty || busy || loading} required spellCheck={false} /></label>
      <label>Token cục bộ<input type="password" value={token} onChange={event => setToken(event.target.value)} disabled={busy || loading} required autoComplete="off" spellCheck={false} /></label>
      <button className="button primary" type="submit" disabled={busy || loading}>{loading ? "Đang kết nối…" : api ? "Cập nhật kết nối" : "Kết nối API"}</button>
      <p className="muted small">Token chỉ giữ trong phiên này. API mặc định chạy tại cổng 8765.</p>
    </form>}
    <div className="project-bar"><div className="inline"><label htmlFor="project-select" className="muted small">DỰ ÁN</label><select id="project-select" value={chosen} disabled={!api || dirty || busy || loading} onChange={event => setChosen(event.target.value)}>
      <option value="">{api ? "Chọn dự án" : "Bản mẫu chưa lưu"}</option>{projects.map(project => <option value={project.project_id} key={project.project_id}>{project.title}</option>)}
    </select><button type="button" className="button secondary small-button" disabled={!api || !chosen || dirty || busy || loading} onClick={openProject}>Mở dự án</button></div>
      <button type="button" className="button quiet small-button" disabled={!api || dirty || busy || loading} onClick={createSample}>Tạo / mở dự án mẫu</button></div>
    {error && <div className="app-error" role="alert">{error}</div>}
    {!remote && <div className="sample-banner">Bạn đang xem kịch bản mẫu. Kết nối API, rồi tạo hoặc mở dự án để bắt đầu sửa và lưu.</div>}
    <div id="story-workspace"><StoryEditor key={generation} api={remote ? api : null} initialDocument={loaded.document} initialReport={loaded.report}
      onDirtyChange={setDirty} onBusyChange={setBusy} /></div>
    <footer className="app-footer">AnimeFlow Studio <span>Kịch bản → shot → bản dựng</span><span>Hình và âm thanh được sản xuất ở các bước tiếp theo.</span></footer>
  </>;
}
