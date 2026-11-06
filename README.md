# AnimeFlow Studio

Nền tảng local-first cho quy trình sản xuất video 2D/3D, hoạt hình bằng code, thoại và lồng tiếng. Đây là **bản nền móng** để các phần có thể được phát triển song song; [blueprint tiếng Việt](docs/animeflow-blueprint-vi.md) mô tả mục tiêu dài hạn.

## Hiện đã có

- JSON Schema cho project, artifact, job và adapter; TypeScript declarations được sinh từ schema.
- Project mẫu với shot, sự kiện và thoại tiếng Việt; phép quy đổi frame/sample dùng số nguyên.
- API local có bearer token, project lưu trong SQLite, revision chống ghi đè và validation các liên kết.
- Import/download asset theo project, băm SHA-256, giới hạn kích thước và kiểm tra file thiếu.
- Worker một tiến trình, job validation chạy nền với snapshot, hủy job, phục hồi sau khi dừng và event stream.
- Catalog có nguồn dẫn đến các báo cáo repo; nhóm ứng viên giọng tiếng Việt được ghi riêng.

Hiện **chưa có** studio UI, renderer 2D/3D, TTS, lip-sync, compositor hoặc xuất video. Repo nghiên cứu trong catalog chưa được tích hợp chỉ vì được liệt kê. Các phần đó có trong roadmap và sẽ được giao theo [hướng dẫn teamwork](docs/teamwork-vi.md).

## Chạy local trên Windows

Yêu cầu Python 3.11+, Node.js và npm cho việc sinh TypeScript contracts.

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

## Kiểm tra và tái sinh catalog

~~~powershell
python -m pytest -q
python -m ruff check packages services scripts tests
python -m ruff format --check packages services scripts tests
python scripts/build_research_catalog.py
npm run contracts:generate
~~~

Thư mục `docs/research/sources/` chứa các báo cáo làm nguồn; `packages/catalog/src/animeflow_catalog/data/repos.json` là catalog có thể sinh lại. Các mục chưa có URL được giữ trong `unresolved_names`, chưa được coi là repo đã tích hợp hoặc đã xác minh.

## Tài liệu

- [Kế hoạch, design system và kiến trúc](docs/animeflow-blueprint-vi.md)
- [Teamwork, API contract và ticket giao Gemini](docs/teamwork-vi.md)
- [Các nguồn giọng tiếng Việt](docs/research/sources/vietnamese-voice-research-2026-11-06.md)
- [Project fixture](fixtures/tiny-project/project.json)

Giấy phép của repo này chưa được chọn. Mỗi repo, model weights, giọng và asset bên ngoài cần kiểm tra điều kiện riêng trước khi tích hợp hoặc phân phối.
