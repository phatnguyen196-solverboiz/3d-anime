import { useEffect, useMemo, useRef, useState } from "react";
import { ApiError, errorMessage, loadProject, type StudioApi } from "./api";
import type { EditorialReport, Issue, LoadedProject, ProjectDocument, StoryEditRequest, StoryEditResult } from "./contracts";
import { buildEdit, conflictFields, emptyDraft, rebaseDraft, type Draft, type Resolutions } from "./draft";

interface Preview { request: StoryEditRequest; result: StoryEditResult; fingerprint: string }
export function useStoryEditor(initialDocument: ProjectDocument, initialReport: EditorialReport | null, api: StudioApi | null) {
  const [document, setDocument] = useState(initialDocument);
  const [report, setReport] = useState(initialReport);
  const [draft, setDraft] = useState(emptyDraft);
  const [preview, setPreview] = useState<Preview | null>(null);
  const [issues, setIssues] = useState<Issue[]>([]);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [previewing, setPreviewing] = useState(false);
  const [applying, setApplying] = useState(false);
  const [conflicted, setConflicted] = useState(false);
  const [latest, setLatest] = useState<LoadedProject | null>(null);
  const [loadingLatest, setLoadingLatest] = useState(false);
  const [resolutions, setResolutions] = useState<Resolutions>({});
  const epoch = useRef(0);
  const mounted = useRef(true);
  const previewAbort = useRef<AbortController | null>(null);
  const applyAbort = useRef<AbortController | null>(null);
  const applyLock = useRef(false);
  const latestAbort = useRef<AbortController | null>(null);
  const built = useMemo(() => buildEdit(document, draft), [document, draft]);
  const freshPreview = preview?.fingerprint === built.fingerprint ? preview : null;
  const conflicts = useMemo(() => latest ? conflictFields(document.project, latest.document.project, draft) : [], [document, latest, draft]);

  useEffect(() => {
    if (!built.dirty) return;
    const warn = (event: BeforeUnloadEvent) => { event.preventDefault(); event.returnValue = ""; };
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, [built.dirty]);

  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
      epoch.current++;
      previewAbort.current?.abort(); applyAbort.current?.abort(); latestAbort.current?.abort();
    };
  }, []);
  useEffect(() => {
    epoch.current++;
    previewAbort.current?.abort();
    setPreview(null); setPreviewing(false);
  }, [api]);

  function invalidate() {
    epoch.current++;
    previewAbort.current?.abort();
    setPreview(null); setPreviewing(false); setIssues([]); setError(""); setNotice("");
  }
  function change(update: (current: Draft) => Draft) {
    if (applying || !api) return;
    invalidate();
    setDraft(update);
  }
  async function refreshLatest() {
    if (!api) return;
    latestAbort.current?.abort();
    const controller = new AbortController();
    latestAbort.current = controller;
    setLoadingLatest(true);
    try {
      const loaded = await loadProject(api, document.project.project_id, controller.signal);
      if (!mounted.current || controller.signal.aborted) return;
      setLatest(loaded); setResolutions({});
    } catch (cause) {
      if (mounted.current && !controller.signal.aborted) setError(errorMessage(cause));
    } finally {
      if (mounted.current && !controller.signal.aborted) setLoadingLatest(false);
    }
  }
  function failed(cause: unknown, saveAttempt = false) {
    setError(cause instanceof TypeError
      ? (saveAttempt ? "Chưa xác định được kết quả lưu. Tải bản đã lưu để đối chiếu; bản nháp vẫn giữ." : "Chưa kết nối được API. Kiểm tra địa chỉ và server; bản nháp vẫn giữ.")
      : errorMessage(cause));
    setIssues(cause instanceof ApiError ? cause.issues : []);
    if ((cause instanceof ApiError && cause.status === 409) || (saveAttempt && !(cause instanceof ApiError))) {
      setConflicted(true);
      void refreshLatest();
    }
  }
  async function previewDraft() {
    if (!api || !built.request || built.issues.length || applying || conflicted) return;
    invalidate();
    const ticket = epoch.current;
    const controller = new AbortController();
    previewAbort.current = controller;
    setPreviewing(true);
    try {
      const result = await api.preview(document.project.project_id, built.request, controller.signal);
      if (!mounted.current || controller.signal.aborted || ticket !== epoch.current) return;
      setPreview({ request: built.request, result, fingerprint: built.fingerprint });
    } catch (cause) {
      if (mounted.current && !controller.signal.aborted && ticket === epoch.current) failed(cause);
    } finally {
      if (mounted.current && ticket === epoch.current) setPreviewing(false);
    }
  }
  async function applyDraft() {
    if (!api || !freshPreview || applyLock.current || conflicted || built.issues.length) return;
    applyLock.current = true;
    const approved = freshPreview;
    epoch.current++;
    const controller = new AbortController();
    applyAbort.current = controller;
    setApplying(true); setError(""); setNotice("");
    try {
      const result = await api.apply(document.project.project_id, approved.request, controller.signal);
      if (!mounted.current || controller.signal.aborted) return;
      setDocument({ project: result.project, revision: result.revision });
      setReport(result.report); setDraft(emptyDraft()); setPreview(null); setIssues([]);
      setNotice(result.changed ? `Đã lưu bản ${result.revision}.` : "Nội dung đã trùng bản lưu; không tạo bản mới.");
    } catch (cause) {
      if (mounted.current && !controller.signal.aborted) failed(cause, true);
    } finally {
      applyLock.current = false;
      if (mounted.current) setApplying(false);
    }
  }
  function useLatest() {
    if (!latest || applying) return;
    try {
      const rebased = rebaseDraft(document.project, latest.document.project, draft, resolutions);
      invalidate();
      setDocument(latest.document); setReport(latest.report); setDraft(rebased);
      setLatest(null); setConflicted(false); setResolutions({});
      setNotice("Đã ghép lựa chọn lên bản mới. Xem tác động lại trước khi lưu.");
    } catch (cause) { setError(errorMessage(cause)); }
  }
  function discard() {
    if (applying) return;
    invalidate(); setDraft(emptyDraft());
    if (latest) { setDocument(latest.document); setReport(latest.report); }
    setConflicted(false); setLatest(null); setResolutions({});
    setNotice("Đã bỏ các thay đổi trong bản nháp.");
  }
  return {
    document, report, draft, built, preview: freshPreview, issues, error, notice, previewing, applying,
    conflicted, latest, loadingLatest, conflicts, resolutions, setResolutions,
    change, previewDraft, applyDraft, refreshLatest, useLatest, discard,
  };
}
