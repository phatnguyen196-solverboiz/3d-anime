import { useEffect, useRef, useState, type DragEvent } from "react";
import type { StudioApi } from "./api";
import type { EditorialReport, ProjectDocument } from "./contracts";
import { issueEntity, issueText, moveShot, orderedScenes, shotsOf } from "./draft";
import { Timeline } from "./Timeline";
import { useStoryEditor } from "./useStoryEditor";

const stepNames: Record<string, string> = {
  animatic: "Animatic", subtitles: "Phụ đề", audio_mix: "Bản mix", video_mux: "Video cuối",
  voice: "Thu / tạo thoại", alignment: "Căn lời", lip_sync: "Khẩu hình", shot_render: "Hình của shot",
};
export function StoryEditor({ initialDocument, initialReport, api, onDirtyChange, onBusyChange }: {
  initialDocument: ProjectDocument; initialReport: EditorialReport | null; api: StudioApi | null;
  onDirtyChange?: (dirty: boolean) => void; onBusyChange?: (busy: boolean) => void;
}) {
  const editor = useStoryEditor(initialDocument, initialReport, api);
  const { document, draft, built, preview } = editor;
  const scenes = orderedScenes(document.project, draft);
  const allShots = scenes.flatMap(scene => scene.shots);
  const [selectedId, setSelectedId] = useState(allShots[0]?.shot_id ?? "");
  const [confirmDiscard, setConfirmDiscard] = useState(false);
  const buttons = useRef(new Map<string, HTMLButtonElement>());
  const dragged = useRef<{ shotId: string; sceneId: string } | null>(null);
  const shot = allShots.find(value => value.shot_id === selectedId);
  const scene = scenes.find(value => value.shots.some(item => item.shot_id === selectedId));
  const lines = document.project.voice_lines.filter(line => line.shot_id === selectedId);
  const editable = !!api && !editor.applying;
  const mappedIssues = [...built.issues, ...editor.issues.map(issue => ({
    entityId: issueEntity(issue, document.project, draft, built.request) ?? document.project.project_id,
    message: issueText(issue),
  }))];
  const errorsFor = (id: string) => mappedIssues.filter(issue => issue.entityId === id);
  const timeline = preview?.result.report ?? editor.report;
  const impact = preview?.result.impact;
  const seconds = (frames: number) => (frames * document.project.canvas.fps.denominator / document.project.canvas.fps.numerator).toLocaleString("vi-VN", { maximumFractionDigits: 3 });
  const shotName = (id: string) => allShots.find(item => item.shot_id === id)?.title ?? id;

  useEffect(() => { onDirtyChange?.(built.dirty || editor.conflicted); }, [built.dirty, editor.conflicted, onDirtyChange]);
  useEffect(() => { onBusyChange?.(editor.applying); }, [editor.applying, onBusyChange]);
  useEffect(() => {
    if (!shotsOf(document.project).some(item => item.shot_id === selectedId)) setSelectedId(shotsOf(document.project)[0]?.shot_id ?? "");
  }, [document, selectedId]);

  function reorder(sceneId: string, id: string, to: number) {
    if (!editable) return;
    editor.change(current => moveShot(document.project, current, sceneId, id, to));
    setSelectedId(id);
    requestAnimationFrame(() => buttons.current.get(id)?.focus());
  }
  function drop(event: DragEvent, sceneId: string, target: number) {
    event.preventDefault();
    if (dragged.current?.sceneId === sceneId) reorder(sceneId, dragged.current.shotId, target);
    dragged.current = null;
  }
  function selectIssue(id: string) {
    const line = document.project.voice_lines.find(item => item.voice_line_id === id);
    const targetScene = scenes.find(item => item.scene_id === id);
    const target = line?.shot_id ?? targetScene?.shots[0]?.shot_id ?? id;
    setSelectedId(target);
    requestAnimationFrame(() => {
      const field = window.document.getElementById(`edit-${id}`);
      if (field) field.focus(); else buttons.current.get(target)?.focus();
    });
  }

  return <div className="editor-shell">
    <header className="project-heading">
      <div><span className="eyebrow">KỊCH BẢN / STORY EDIT</span><h1>{document.project.title}</h1>
        <p className="muted">{scenes.length} cảnh · {allShots.length} shot · {document.project.voice_lines.length} câu thoại</p></div>
      <div className="project-state"><span className="badge">{api ? `Bản đã lưu ${document.revision}` : "Bản mẫu · chỉ xem"}</span>
        {built.dirty && <span className="badge warning">Bản nháp chưa lưu</span>}</div>
    </header>

    <div className="workspace-grid">
      <nav className="shot-rail panel" aria-label="Cảnh và shot">
        <div className="rail-heading"><h2>Mạch truyện</h2><span className="muted small">ALT + ↑ / ↓ để đổi thứ tự</span></div>
        {scenes.length === 0 && <p className="muted">Dự án chưa có cảnh.</p>}
        {scenes.map((item, sceneIndex) => <section key={item.scene_id} className="scene-group" aria-label={`Cảnh ${item.title}`}>
          <h3><span className="scene-number">{String(sceneIndex + 1).padStart(2, "0")}</span>{item.title}</h3>
          {errorsFor(item.scene_id).map((issue, i) => <p key={i} className="field-error">{issue.message}</p>)}
          {!item.shots.length && <p className="muted small">Chưa có shot.</p>}
          <ol>{item.shots.map((value, index) => <li key={value.shot_id}
            className={`shot-card ${selectedId === value.shot_id ? "active" : ""} ${errorsFor(value.shot_id).length ? "has-error" : ""}`}
            draggable={editable} onDragStart={event => { dragged.current = { sceneId: item.scene_id, shotId: value.shot_id }; event.dataTransfer.setData("text/plain", value.shot_id); event.dataTransfer.effectAllowed = "move"; }}
            onDragEnd={() => { dragged.current = null; }} onDragOver={event => { if (editable && dragged.current?.sceneId === item.scene_id) event.preventDefault(); }}
            onDrop={event => drop(event, item.scene_id, index)}>
            <button type="button" className="shot-select" ref={node => { if (node) buttons.current.set(value.shot_id, node); else buttons.current.delete(value.shot_id); }}
              onClick={() => setSelectedId(value.shot_id)} aria-current={selectedId === value.shot_id ? "true" : undefined}
              aria-label={`Chọn shot: ${value.title}`} onKeyDown={event => {
                if (event.altKey && (event.key === "ArrowUp" || event.key === "ArrowDown")) {
                  event.preventDefault(); reorder(item.scene_id, value.shot_id, index + (event.key === "ArrowUp" ? -1 : 1));
                } else if (!event.altKey && (event.key === "ArrowUp" || event.key === "ArrowDown")) {
                  event.preventDefault(); const next = allShots[allShots.findIndex(s => s.shot_id === value.shot_id) + (event.key === "ArrowUp" ? -1 : 1)];
                  if (next) { setSelectedId(next.shot_id); buttons.current.get(next.shot_id)?.focus(); }
                }
              }}>
              <span className="shot-thumb" aria-hidden="true">{String(index + 1).padStart(2, "0")}</span>
              <span className="shot-label"><strong>{value.title}</strong><span className="muted small">{draft.durations[value.shot_id] ?? value.duration_frames} frame</span></span>
            </button>
            <div className="shot-move"><button type="button" title="Di chuyển lên" aria-label={`Đưa ${value.title} lên`} disabled={!editable || index === 0} onClick={() => reorder(item.scene_id, value.shot_id, index - 1)}>↑</button>
              <button type="button" title="Di chuyển xuống" aria-label={`Đưa ${value.title} xuống`} disabled={!editable || index === item.shots.length - 1} onClick={() => reorder(item.scene_id, value.shot_id, index + 1)}>↓</button></div>
          </li>)}</ol>
        </section>)}
      </nav>

      <main className="story-sheet panel" aria-label="Biên tập shot">
        {!shot ? <p className="muted">Chọn một shot để xem nội dung.</p> : <>
          <div className="shot-heading"><span className="eyebrow">{scene?.title}</span><h2>{shot.title}</h2><span className="badge subtle">Nội dung & thoại</span></div>
          {shot.description && <div className="action-description"><span className="eyebrow">HÀNH ĐỘNG</span><p>{shot.description}</p></div>}
          <div className="timing-editor"><label htmlFor={`edit-${shot.shot_id}`}>Thời lượng shot <span className="muted small">(frame)</span></label>
            <div className="inline"><input id={`edit-${shot.shot_id}`} className="duration-input tabular-nums" inputMode="numeric" type="text" disabled={!editable}
              value={draft.durations[shot.shot_id] ?? String(shot.duration_frames)} aria-invalid={errorsFor(shot.shot_id).length > 0}
              aria-describedby={`errors-${shot.shot_id}`} onChange={event => { const value = event.target.value; editor.change(current => ({ ...current, durations: { ...current.durations, [shot.shot_id]: value } })); }} />
              <span className="muted small">Đã lưu: {shot.duration_frames}f · {seconds(shot.duration_frames)} giây</span></div>
            <div id={`errors-${shot.shot_id}`}>{errorsFor(shot.shot_id).map((issue, i) => <p className="field-error" key={i}>{issue.message}</p>)}</div>
          </div>
          <div className="section-heading"><h3>Đối thoại</h3><span className="muted small">{lines.length} câu</span></div>
          {lines.length === 0 && <div className="empty-dialogue"><span aria-hidden="true">◌</span><p>Shot này chưa có thoại.</p></div>}
          {lines.map(line => {
            const text = draft.texts[line.voice_line_id] ?? line.text;
            const changed = text !== line.text;
            const character = document.project.characters.find(value => value.character_id === line.character_id);
            return <article key={line.voice_line_id} className="dialogue-card">
              <div className="dialogue-heading"><span className="avatar" aria-hidden="true">{character?.name.slice(0, 1) ?? "?"}</span><label htmlFor={`edit-${line.voice_line_id}`}><strong>{character?.name ?? "Nhân vật"}</strong><span className="muted small">{line.language} · {line.start_frame}–{line.start_frame + line.duration_frames}f trong shot</span></label>
                <span className={`badge ${line.audio_asset_id ? "success" : "subtle"}`}>{line.audio_asset_id ? "Có liên kết audio" : "Chưa gắn audio"}</span></div>
              <textarea id={`edit-${line.voice_line_id}`} aria-label={`Thoại của ${character?.name ?? "nhân vật"}`} rows={3} disabled={!editable}
                aria-invalid={errorsFor(line.voice_line_id).length > 0} aria-describedby={`errors-${line.voice_line_id}`} value={text}
                onChange={event => { const value = event.target.value; editor.change(current => ({ ...current, texts: { ...current.texts, [line.voice_line_id]: value },
                  detach: { ...current.detach, [line.voice_line_id]: value === line.text ? false : !!current.detach[line.voice_line_id] } })); }} />
              <div className="dialogue-footer"><span className="muted small">{text.length.toLocaleString("vi-VN")} / 10.000 ký tự</span>{changed && <span className="small accent">Đã sửa lời</span>}</div>
              {changed && line.audio_asset_id && <label className="detach-choice"><input type="checkbox" checked={!!draft.detach[line.voice_line_id]} disabled={!editable}
                onChange={event => { const checked = event.target.checked; editor.change(current => ({ ...current, detach: { ...current.detach, [line.voice_line_id]: checked } })); }} />
                <span>Tách audio cũ khỏi câu thoại này<small>File nguồn vẫn giữ trong dự án. Cần thu hoặc tạo lại câu đã sửa.</small></span></label>}
              <div id={`errors-${line.voice_line_id}`}>{errorsFor(line.voice_line_id).map((issue, i) => <p key={i} className="field-error">{issue.message}</p>)}</div>
            </article>;
          })}
          {shot.events.length > 0 && <div className="events-note"><h3>Cue trong shot</h3>{shot.events.map(event => <span key={event.event_id} className="cue"><span aria-hidden="true">◆</span> {event.type} <strong>{event.frame}f</strong></span>)}</div>}
        </>}
      </main>

      <aside className="review-panel panel" aria-label="Kiểm tra thay đổi">
        <span className="eyebrow">TRƯỚC KHI LƯU</span><h2>Xem tác động</h2>
        <div className="draft-summary"><span className={`status-dot ${built.dirty ? "warning-dot" : ""}`} />{built.dirty ? `${(built.request?.operations.length ?? 0) + built.issues.length} thay đổi trong bản nháp` : "Chưa có thay đổi"}</div>
        {editor.error && <div className="error-banner" role="alert">{editor.error}</div>}
        <div role="status" aria-live="polite" className={editor.notice ? "success-banner" : "sr-only"}>{editor.notice}</div>
        {mappedIssues.length > 0 && <ul className="issue-list">{mappedIssues.map((issue, i) => <li key={i}><button type="button" onClick={() => selectIssue(issue.entityId)}>{issue.message}</button></li>)}</ul>}
        {!preview && <p className="muted">Xem trước để kiểm tra thời lượng, vị trí thoại và các phần cần làm lại. Thay đổi vẫn ở bản nháp cho đến khi bạn bấm lưu.</p>}
        {preview && impact && <div className="impact-details">
          <div className="duration-comparison"><span>Tổng thời lượng</span><strong>{editor.report?.duration_frames ?? "—"}f <span aria-hidden="true">→</span> {preview.result.report.duration_frames}f</strong><small>{seconds(preview.result.report.duration_frames)} giây ở FPS của dự án</small></div>
          <p><strong>{impact.repositioned_shot_ids.length}</strong> shot đổi vị trí trên bản dựng.</p>
          {impact.repositioned_shot_ids.length > 0 && <ul>{impact.repositioned_shot_ids.map(id => <li key={id}>{shotName(id)}</li>)}</ul>}
          {impact.detached_audio_line_ids.length > 0 && <p className="warning-text">{impact.detached_audio_line_ids.length} câu sẽ tách audio cũ. File nguồn được giữ.</p>}
          <h3>Cần xem lại</h3><div className="step-tags">{impact.rebuild_candidates.map(step => <span className="badge subtle" key={step}>{stepNames[step] ?? step}</span>)}</div>
          {impact.extensions_require_review && <p className="small warning-text">Dữ liệu mở rộng được giữ nguyên; cần kiểm tra các cue hoặc animation phụ thuộc.</p>}
          <p className="muted small">Đây là danh sách cần kiểm tra. Các phần này chưa tự chạy lại.</p>
        </div>}
        <div className="editor-actions"><button type="button" className="button secondary" disabled={!api || !built.dirty || !!built.issues.length || editor.previewing || editor.applying || editor.conflicted} onClick={() => void editor.previewDraft()}>
          {editor.previewing ? "Đang kiểm tra…" : "Xem tác động"}</button>
          <button type="button" className="button primary" disabled={!preview || !api || editor.applying || editor.conflicted} onClick={() => void editor.applyDraft()}>{editor.applying ? "Đang lưu…" : "Lưu thay đổi"}</button>
          <button type="button" className="button quiet" disabled={(!built.dirty && !editor.conflicted) || editor.applying} onClick={() => setConfirmDiscard(true)}>Bỏ bản nháp</button>
        </div>
        {confirmDiscard && <div className="confirm-box" role="alertdialog" aria-label="Xác nhận bỏ bản nháp"><p>Các thay đổi chưa lưu sẽ được bỏ.</p><button type="button" className="button danger" onClick={() => { editor.discard(); setConfirmDiscard(false); }}>Xác nhận bỏ nháp</button><button type="button" className="button quiet" onClick={() => setConfirmDiscard(false)}>Giữ lại</button></div>}
        <p className="small muted">Chưa có hình hoặc audio phát lại trong màn hình này. Timing hiển thị là kế hoạch dựng.</p>
      </aside>
    </div>

    {editor.conflicted && <section className="conflict-panel" aria-label="Đối chiếu bản mới">
      <div className="section-heading"><div><span className="eyebrow">BẢN NHÁP ĐƯỢC GIỮ</span><h2>Đối chiếu trước khi tiếp tục</h2></div><button type="button" className="button secondary" disabled={editor.loadingLatest} onClick={() => void editor.refreshLatest()}>{editor.loadingLatest ? "Đang tải bản mới…" : "Tải bản mới để đối chiếu"}</button></div>
      {editor.latest && <><p>Bạn sửa từ bản {document.revision}; trên API hiện là bản {editor.latest.document.revision}. Chọn nội dung giữ lại ở những mục cùng thay đổi.</p>
        {editor.conflicts.length === 0 && <p className="muted">Chưa thấy xung đột trên các mục bạn đang sửa. Bản nháp sẽ được ghép lên bản mới khi bạn chọn tiếp tục.</p>}
        {editor.conflicts.map(field => <fieldset key={field.key} className="conflict-field"><legend>{field.label}</legend><div className="comparison-columns"><div><small>Trước khi sửa</small><p>{field.original}</p></div><div><small>Bản nháp của bạn</small><p>{field.local}</p></div><div><small>Bản đã lưu mới</small><p>{field.remote}</p></div></div>
          {field.canKeepLocal && <label><input type="radio" name={field.key} value="local" checked={editor.resolutions[field.key] === "local"} onChange={() => editor.setResolutions(current => ({ ...current, [field.key]: "local" }))} />Giữ bản nháp · {field.label}</label>}
          <label><input type="radio" name={field.key} value="remote" checked={editor.resolutions[field.key] === "remote"} onChange={() => editor.setResolutions(current => ({ ...current, [field.key]: "remote" }))} />Dùng bản mới · {field.label}</label>
          {!field.canKeepLocal && <p className="small warning-text">Đối tượng hoặc danh sách shot đã thay đổi. Dùng bản mới rồi sửa lại mục này.</p>}
        </fieldset>)}
        <button type="button" className="button primary" disabled={editor.applying || editor.loadingLatest || editor.conflicts.some(field => !editor.resolutions[field.key])} onClick={editor.useLatest}>Tiếp tục trên bản mới</button><span className="small muted"> Cần xem tác động lại trước khi lưu.</span>
      </>}
    </section>}
    <Timeline report={timeline} project={preview?.result.project ?? document.project} selected={selectedId} onSelect={setSelectedId} preview={!!preview} />
  </div>;
}
