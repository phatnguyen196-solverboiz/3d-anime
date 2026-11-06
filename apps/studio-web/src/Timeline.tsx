import type { EditorialReport, ProjectSpec } from "./contracts";

export function Timeline({ report, project, selected, onSelect, preview }: {
  report: EditorialReport | null; project: ProjectSpec; selected: string; onSelect: (id: string) => void; preview: boolean;
}) {
  return <section className="timeline-panel" aria-label="Timing bản dựng">
    <div className="section-heading"><div><span className="eyebrow">BẢN DỰNG</span><h2>Nhịp cảnh & vị trí thoại</h2></div>
      <span className={`badge ${preview ? "warning" : ""}`}>{preview ? "Phương án chưa lưu" : report ? `Timing bản ${report.project_revision}` : "Chưa có timing từ API"}</span></div>
    {!report ? <p className="muted">Kết nối và mở dự án để xem timing frame/sample. Bản mẫu chưa có hình hoặc audio phát lại.</p> : <>
      <p className="muted small">{report.duration_frames} frame · {report.duration_samples.toLocaleString("vi-VN")} sample · {report.fps.numerator}/{report.fps.denominator} fps. Các ô thoại là vị trí dự định, chưa phải waveform.</p>
      {report.shots.length === 0 ? <p>Chưa có shot.</p> : <div className="timeline-scroll"><div className="timeline-content">
        <div className="timeline-ruler"><span>0f</span><span>{report.duration_frames}f</span></div>
        <div className="picture-track">{report.shots.map((shot, index) => <button type="button" key={shot.shot_id}
          className={`timeline-shot ${selected === shot.shot_id ? "selected" : ""}`} onClick={() => onSelect(shot.shot_id)}
          style={{ left: `${shot.start_frame / report.duration_frames * 100}%`, width: `${shot.duration_frames / report.duration_frames * 100}%` }} aria-label={`Timeline: ${shot.title}`} aria-pressed={selected === shot.shot_id}>
          <span className="small">{String(index + 1).padStart(2, "0")}</span><strong>{shot.title}</strong><span className="small tabular-nums">{shot.start_frame}–{shot.end_frame_exclusive}f</span>
        </button>)}</div>
        {project.characters.filter(character => report.voice_lines.some(line => line.character_id === character.character_id)).map(character => <div key={character.character_id} className="voice-track" aria-label={`Vị trí thoại ${character.name}`}>
          {report.voice_lines.filter(line => line.character_id === character.character_id).map(line => <button type="button" key={line.voice_line_id}
            className={`voice-slot ${line.audio_linked ? "" : "unlinked"}`} title={`${character.name}: ${line.text}`}
            onClick={() => onSelect(line.shot_id)} style={{ left: `${line.start_frame / report.duration_frames * 100}%`, width: `${line.duration_frames / report.duration_frames * 100}%` }}>
            {character.name} · {line.start_frame}–{line.end_frame_exclusive}f
          </button>)}
        </div>)}
      </div></div>}
    </>}
  </section>;
}
