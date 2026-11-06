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
- `POST /api/v1/projects/{id}/jobs` nhận `{ "operation": "project.validate", "expected_revision": number }`; nhận job ID để theo dõi.
- `POST /api/v1/projects/{id}/assets` nhận multipart `file`, `kind` và `expected_revision`; mặc định tối đa 100 MiB/file. `GET /api/v1/projects/{id}/assets/{asset_id}` trả file với bearer header.
- `GET /api/v1/projects/{id}/events` là SSE, hỗ trợ `Last-Event-ID` hoặc `after_id`; dùng streaming `fetch` gửi bearer header vì `EventSource` của browser không cho set header tùy ý.
- `GET /api/v1/catalog/repos` trả catalog và danh sách tên chưa có URL. Mọi repo trong đó có trạng thái `cataloged`.

Contract đang ở **bản v1 khởi đầu**, chưa tuyên bố ổn định vĩnh viễn. Không giả lập render/TTS thành công; hiển thị nhãn chưa sẵn sàng. API chưa có timeline playback hoặc engine adapters.

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
Đầu vào: docs/research/sources/vietnamese-voice-research-2026-11-06.md và VoiceLine.
Khảo sát VieNeu-TTS trước: pin version/model, kiểm tra code/model/voice license,
Windows CPU/GPU, kích thước và quyền tải weights, rồi chạy một câu tiếng Việt.
Đề xuất adapter nhận text/language/voice, trả WAV, sample rate, duration, hash,
provenance và consent reference. Alignment/lip-sync là công đoạn riêng.
Giao báo cáo lỗi, lệnh tái lập, ví dụ audio nếu có quyền, và PR adapter độc lập.
Không commit model weights hoặc voice/reference media chưa được phép.
~~~

## Handoff mỗi ticket

Ghi branch, file đã đổi, contract sử dụng, cách chạy, bằng chứng kiểm tra, giới hạn và câu hỏi cần phối hợp. Không đánh dấu một capability đã xong nếu mới chỉ có manifest, fixture hoặc mock.
