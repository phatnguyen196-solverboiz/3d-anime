# AnimeFlow Studio

Nền tảng local-first cho quy trình sản xuất video 2D/3D, hoạt hình bằng code, thoại và lồng tiếng. Đây là **bản nền móng** để các phần có thể được phát triển song song; [blueprint tiếng Việt](docs/animeflow-blueprint-vi.md) mô tả mục tiêu dài hạn.

## Hiện đã có

- JSON Schema cho project, artifact, job và adapter; TypeScript declarations được sinh từ schema.
- Project mẫu với shot, sự kiện và thoại tiếng Việt; phép quy đổi frame/sample dùng số nguyên.
- Story edit core: báo cáo timeline cut, preview/apply đảo shot, sửa thời lượng/thoại theo revision; chặn cue tràn shot và giữ rõ tác động của audio cũ.
- Studio Web story editor tiếng Việt: sửa draft, kéo thả/bàn phím reorder, xem tác động, lưu qua API và đối chiếu conflict; token chỉ giữ trong phiên.
- API local có bearer token, project lưu trong SQLite, revision chống ghi đè và validation các liên kết.
- Import/download asset theo project, băm SHA-256, giới hạn kích thước và kiểm tra file thiếu.
- Worker một tiến trình, job validation chạy nền với snapshot, hủy job, phục hồi sau khi dừng và event stream.
- Adapter Blender **experimental**: scene primitive/keyframe/rigid body dạng JSON có schema; job xuất PNG từng frame, kiểm kích thước, số frame và SHA-256, trả manifest qua API. Cần Blender executable riêng.
- Catalog có nguồn dẫn đến các báo cáo repo; nhóm ứng viên giọng tiếng Việt được ghi riêng.

Studio Web hiện tập trung vào story edit, chưa có player hình/audio, renderer 2D, TTS, lip-sync, compositor hoặc xuất video hoàn chỉnh. Blender adapter mới ở mức thử nghiệm và chưa chạy render thật trên máy phát triển này; các repo khác trong catalog chưa được tích hợp chỉ vì được liệt kê. Các phần đó có trong roadmap và [hướng dẫn teamwork](docs/teamwork-vi.md).

## Chạy local trên Windows

Yêu cầu Python 3.11+, Node.js 22.12+ hoặc bản LTS 24 và npm cho frontend/contracts.

~~~powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -c requirements-constraints.txt -e ".[dev]"
npm ci
npm run contracts:generate
~~~

Tạo token cục bộ mới và khởi chạy một API worker, chỉ bind vào loopback:

~~~powershell
$env:ANIMEFLOW_API_TOKEN = python -c "import secrets; print(secrets.token_urlsafe(32))"
# Sao chép giá trị này vào terminal thứ hai và giữ bí mật:
$env:ANIMEFLOW_API_TOKEN
python -m uvicorn animeflow_api.app:create_app --factory --host 127.0.0.1 --port 8765
~~~

Giữ token trong môi trường cục bộ, không commit token. Vì server chiếm terminal đầu tiên, mở terminal thứ hai và đặt cùng token nếu gọi API từ đó. Mặc định dữ liệu ghi trong `.animeflow-data/` ở thư mục hiện hành; có thể đổi bằng `ANIMEFLOW_DATA_DIR`. Chỉ chạy một API worker trên mỗi thư mục dữ liệu.

Sau khi đặt cùng token trong terminal thứ hai, tạo project mẫu:

~~~powershell
$project = Get-Content -Raw -Encoding utf8 fixtures/tiny-project/project.json | ConvertFrom-Json
$body = @{ project = $project } | ConvertTo-Json -Depth 30
$headers = @{ Authorization = "Bearer $env:ANIMEFLOW_API_TOKEN" }
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8765/api/v1/projects -Headers $headers -ContentType "application/json; charset=utf-8" -Body ([Text.Encoding]::UTF8.GetBytes($body))
~~~

API docs: `http://127.0.0.1:8765/docs`. Tất cả endpoint dữ liệu cần header `Authorization: Bearer <token>`; health check công khai trên loopback. CORS cho localhost port 5173, cấu hình qua `ANIMEFLOW_CORS_ORIGINS` nếu cần.

## Mở story editor

Sau khi API chạy, mở terminal khác tại repo và chạy `npm ci --ignore-scripts` rồi `npm run dev`. Mở `http://127.0.0.1:5173`, nhập địa chỉ API và cùng token đã đặt cho backend. Chọn dự án hoặc bấm **Tạo / mở dự án mẫu**; thao tác này mở bản đã có nếu ID mẫu tồn tại, không ghi đè nó.

Sửa thoại/thời lượng hoặc đổi thứ tự shot trong cảnh, bấm **Xem tác động** rồi **Lưu thay đổi**. Khi có bản lưu mới từ người khác, draft được giữ để đối chiếu và chọn nội dung cần giữ; phải preview lại trước khi lưu tiếp. Có thể đổi thứ tự bằng kéo thả, nút ↑/↓ hoặc Alt+↑/↓ trên shot; phím ↑/↓ thường chuyển selection.

Token và draft chỉ giữ trong bộ nhớ tab. Trình duyệt được yêu cầu cảnh báo khi rời trang có draft chưa lưu, nhưng chưa có khôi phục draft/undo bền vững. Chi tiết chạy, kiểm tra và giới hạn ở [Studio Web README](apps/studio-web/README.md).

## Render shot 3D bằng Blender

Cài Blender 4.5 LTS trên máy riêng và đặt đường dẫn binary trước khi chạy API. Worker chạy Blender ở chế độ background/offline, Cycles CPU. `GET /api/v1/adapters/blender` chỉ kiểm tra đường dẫn binary (`binary_detected` hoặc `missing_binary`); nếu thiếu, render job trả lỗi `blender_missing`.

~~~powershell
$env:ANIMEFLOW_BLENDER_BIN = 'C:\Program Files\Blender Foundation\Blender 4.5\blender.exe'
$project = Get-Content -Raw -Encoding utf8 fixtures/blender-primitive-project/project.json | ConvertFrom-Json
$headers = @{ Authorization = "Bearer $env:ANIMEFLOW_API_TOKEN" }
$body = @{ project = $project } | ConvertTo-Json -Depth 40
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8765/api/v1/projects -Headers $headers -ContentType 'application/json; charset=utf-8' -Body ([Text.Encoding]::UTF8.GetBytes($body))
$jobBody = @{ operation = 'render.shot.blender'; expected_revision = 1; shot_id = '2673bbee-bcbc-4591-8bc6-795fc5463c17'; frame_start = 0; frame_end_exclusive = 3 } | ConvertTo-Json
$job = Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8765/api/v1/projects/ea07e191-d192-41d1-ae43-34b78e2e7447/jobs' -Headers $headers -ContentType 'application/json' -Body $jobBody
Invoke-RestMethod -Uri "http://127.0.0.1:8765/api/v1/jobs/$($job.job_id)" -Headers $headers
~~~

Job thành công trả `render-result` gồm `frames[].index/path/sha256/width/height`; tải một ảnh qua `GET /api/v1/jobs/{job_id}/frames/{frame_index}` với bearer token. Range dùng `[frame_start, frame_end_exclusive)`, tính theo shot. Scene đặt ở `shot.extensions['animeflow.blender.scene.v1']`; chỉ hỗ trợ primitive, material, keyframe transform và rigid body đơn giản. Chi tiết và giới hạn ở [nghiên cứu Blender](docs/research/blender-render-verified-2026-11-06.md).

## Kiểm tra và tái sinh catalog

~~~powershell
python -m pytest -q
python -m ruff check adapters packages services scripts tests
python -m ruff format --check adapters packages services scripts tests
python scripts/build_research_catalog.py
npm run contracts:generate
npm run typecheck
npm run build
npm run test:ui
~~~

Thư mục `docs/research/sources/` chứa các báo cáo làm nguồn; `packages/catalog/src/animeflow_catalog/data/repos.json` là catalog có thể sinh lại. Các mục chưa có URL được giữ trong `unresolved_names`, chưa được coi là repo đã tích hợp hoặc đã xác minh.

## Tài liệu

- [Kế hoạch, design system và kiến trúc](docs/animeflow-blueprint-vi.md)
- [Teamwork, API contract và ticket giao Gemini](docs/teamwork-vi.md)
- [Các nguồn giọng tiếng Việt](docs/research/sources/vietnamese-voice-research-2026-11-06.md)
- [Đối chiếu kỹ thuật giọng Việt và handoff Gemini](docs/research/vietnamese-voice-verified-2026-11-06.md)
- [Nghiên cứu story editor, vấn đề video và API mới](docs/research/story-edit-video-verified-2026-11-06.md)
- [Project fixture](fixtures/tiny-project/project.json)

Giấy phép của repo này chưa được chọn. Mỗi repo, model weights, giọng và asset bên ngoài cần kiểm tra điều kiện riêng trước khi tích hợp hoặc phân phối.
