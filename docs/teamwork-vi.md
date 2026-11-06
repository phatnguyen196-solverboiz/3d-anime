# Hướng dẫn phối hợp Gemini và Codex

## Ownership ban đầu

| Phần | Owner gợi ý | Thư mục |
|---|---|---|
| Contract, ProjectSpec, API, persistence và worker | Codex | `packages/contracts/`, `packages/project-spec/`, `services/` |
| Design tokens, UI kit, Studio Web | Gemini | `packages/design-tokens/`, `packages/ui-kit/`, `apps/studio-web/` |
| Audio/TTS và khảo sát giọng Việt | Gemini | `adapters/audio/`, tài liệu audio liên quan |
| Catalog nền và provenance nghiên cứu | Codex | `packages/catalog/`, `scripts/build_research_catalog.py`, `docs/research/` |

Tách branch/worktree; không sửa file người khác đang làm. Root `package.json` hiện phục vụ sinh types; nếu UI cần workspace package manager, phối hợp trước khi thay scripts/lockfile. Thay đổi contract cần ví dụ và review của owner core; file trong `packages/contracts/generated/` được sinh lại, không sửa tay.

## Contract đang có

- Schema canonical: `packages/contracts/src/animeflow_contracts/schemas/`.
- TypeScript declarations: `packages/contracts/generated/`.
- Dữ liệu mẫu: `fixtures/tiny-project/project.json`.
- FPS là phân số, shot duration và voice-line position là số frame nguyên; voice line tính theo shot.
- Sequences/scenes/shots hiện được nối tuần tự; chưa có transition/overlap hoặc media playback.
- `POST /api/v1/projects` nhận `{ "project": ProjectSpec }`; `GET` trả project kèm `revision`.
- `PUT /api/v1/projects/{id}` nhận `{ "project": ProjectSpec, "expected_revision": number }`; revision cũ trả 409.
- `GET /api/v1/projects/{id}/editorial` trả report timing dự định của assembly cut nối tiếp, kèm revision; không phải kết quả đo media.
- `POST /api/v1/projects/{id}/story-edits/preview` và `/story-edits` dùng `StoryEditRequest`: `{ expected_revision, operations }`. Preview không ghi; apply kiểm revision và lưu cả batch, no-op không tăng revision. Ba op: `reorder_shots` trong scene, `set_shot_duration`, `set_voice_text`. Contract/schema và phạm vi ở [nghiên cứu story edit](research/story-edit-video-verified-2026-11-06.md).
- `POST /api/v1/projects/{id}/jobs` nhận `{ "operation": "project.validate", "expected_revision": number }` hoặc job Blender `{ "operation": "render.shot.blender", "expected_revision": number, "shot_id": UUID, "frame_start": number, "frame_end_exclusive": number }`; nhận job ID để theo dõi.
- `POST /api/v1/projects/{id}/assets` nhận multipart `file`, `kind` và `expected_revision`; mặc định tối đa 100 MiB/file. `GET /api/v1/projects/{id}/assets/{asset_id}` trả file với bearer header.
- `GET /api/v1/projects/{id}/events` là SSE, hỗ trợ `Last-Event-ID` hoặc `after_id`; dùng streaming `fetch` gửi bearer header vì `EventSource` của browser không cho set header tùy ý.
- `GET /api/v1/catalog/repos` trả catalog và danh sách tên chưa có URL. Mọi repo trong đó có trạng thái `cataloged`.

Contract đang ở **bản v1 khởi đầu**, chưa tuyên bố ổn định vĩnh viễn. Adapter Blender primitive có trạng thái `experimental`, thiếu binary trả lỗi rõ ràng; không giả lập render/TTS thành công. API chưa có timeline playback hay audio adapter.

## Handoff renderer 3D cho Gemini UI

- Scene mẫu: `fixtures/blender-primitive-project/project.json`; cấu trúc scene ở `shot.extensions['animeflow.blender.scene.v1']`. Keyframe là số frame cục bộ của shot.
- `GET /api/v1/adapters/blender` (bearer) trả `status: binary_detected | missing_binary` và `probe: executable_path_only`. Việc thấy binary chưa chứng minh render chạy được; UI hiển thị trạng thái này trước khi bật nút render.
- Job render dùng range nửa mở `[frame_start, frame_end_exclusive)`, tùy chọn bỏ `frame_end_exclusive` để render cả shot. `GET /api/v1/jobs/{job_id}` trả trạng thái và `result` theo `RenderResult` khi thành công; `GET /api/v1/jobs/{job_id}/frames/{index}` trả `image/png` có bearer. Lỗi render nằm ở `job.error.code`, ví dụ `blender_missing`, `invalid_scene`, `blender_failed`, `render_timeout`.
- UI không dùng `frames[].path` làm file URL trực tiếp; đó là đường dẫn lưu trữ tương đối. Dùng endpoint frame có xác thực. Trong browser, lấy blob bằng `fetch` với bearer rồi tạo object URL, thu hồi URL khi đổi frame.
- Không coi adapter `experimental` là video hoàn chỉnh. Hiện chưa có mux tiếng Việt, compositor hoặc 2D renderer. Bằng chứng/caveat ở `docs/research/blender-render-verified-2026-11-06.md`.

## Ticket cho Gemini: AF-UI-01

~~~text
Owner: Gemini
Phạm vi: packages/design-tokens/**, packages/ui-kit/**, apps/studio-web/**
Đầu vào: ProjectSpec và Job types đã generate; fixtures/tiny-project/project.json.
Giao: Studio shell có project rail, shot list, preview placeholder, timeline,
inspector, job dock; hỗ trợ trạng thái lỗi/chưa có adapter; dùng token qua cấu hình local.
Không sửa: schema, API, worker hoặc package.json gốc nếu chưa thống nhất.
Tiêu chí: UI đọc đúng fixture, không tự thêm trường bắt buộc; keyboard/focus rõ;
API errors và revision conflicts được hiển thị; ghi cách chạy và giới hạn.
~~~

## Ticket cho Gemini: AF-AUDIO-VI-01

~~~text
Owner: Gemini
Đầu vào: docs/research/vietnamese-voice-verified-2026-11-06.md và VoiceLine.
Làm VieNeu v3 Turbo trước trong adapters/audio/**: pin SDK/model revision,
kiểm quyền code/weights/preset/reference; smoke test Windows CPU bằng câu Việt.
Adapter nhận text gốc, spoken text/normalizer mode, engine/voice, seed,
trả WAV mono, native/target sample rates, sample counts, SHA-256 của từng bản,
model/voice provenance và consent reference. Không giả định duration_frames bằng
thời lượng audio; báo overflow slot. Alignment/lip-sync là công đoạn riêng.
Giao lệnh tái lập, WAV ví dụ nếu có quyền, kết quả nghe/kiểm transcript, mã lỗi,
license và PR adapter độc lập. Không ghi model/clip giọng vào Git.
Không commit model weights hoặc voice/reference media chưa được phép.
~~~

## Handoff mỗi ticket

### AF-STORY-UI-01 — đã triển khai

Codex đã thực hiện cả phần UI của ticket này: `apps/studio-web/**`, dùng CSS tokens snapshot và generated contracts. Có draft → preview → apply, error mapping/409, đối chiếu field conflicts, explicit audio detach, keyboard/drag reorder và giữ selection theo ID. Chỉ dùng global timing từ API report. Xem [Studio README](../apps/studio-web/README.md) để chạy và biết giới hạn. Bộ UI-kit/studio mock còn ở workspace riêng, chưa được gộp vào ứng dụng này. Chưa có persistent undo/player/multi-track.

Ghi branch, file đã đổi, contract sử dụng, cách chạy, bằng chứng kiểm tra, giới hạn và câu hỏi cần phối hợp. Không đánh dấu một capability đã xong nếu mới chỉ có manifest, fixture hoặc mock.
