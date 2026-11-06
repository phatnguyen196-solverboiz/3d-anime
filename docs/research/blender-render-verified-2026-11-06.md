# Khảo sát renderer 3D cho AnimeFlow — 06/11/2026

## Phạm vi và mức độ xác nhận

Tài liệu này kiểm tra **đường đi từ mô tả shot đến chuỗi frame 3D** bằng tài liệu chính thức của Blender, mã/tài liệu upstream của BlenderProc và tài liệu Godot. Các lệnh và API dưới đây là khả năng của công cụ upstream, **chưa phải tính năng đã tích hợp vào AnimeFlow**. Trong phiên khảo sát này, `Get-Command blender,blender.exe,godot,godot.exe` không tìm thấy executable trên `PATH` của Windows local; chưa có lần render Blender hay Godot thực tế, chưa có số liệu tốc độ hoặc kết quả hình ảnh được kiểm chứng tại máy này.

`ProjectSpec` của repo đã có FPS dạng phân số, shot có `duration_frames`, còn `Artifact` và `AdapterManifest` có schema riêng. Sau khảo sát này, nhánh `codex/scene-render-pipeline` đã thêm schema cảnh primitive và job Blender thử nghiệm; các mục bên dưới ghi bằng chứng upstream và quyết định thiết kế tại thời điểm khảo sát, không phải kết quả render đã được nghiệm thu. [Project schema](../../packages/contracts/src/animeflow_contracts/schemas/project.schema.json), [render result schema](../../packages/contracts/src/animeflow_contracts/schemas/render-result.schema.json), [adapter schema](../../packages/contracts/src/animeflow_contracts/schemas/adapter-manifest.schema.json).

## Kết luận kỹ thuật

| Hướng | Entry point và đầu ra đã xác nhận | Điểm phù hợp và giới hạn |
|---|---|---|
| **Blender Python native — ưu tiên đầu tiên** | `blender --background ... --python render_shot.py`; Python `bpy` dựng scene rồi gọi `bpy.ops.render.render(animation=True)` để tạo chuỗi PNG. Blender CLI hỗ trợ frame đầu/cuối, định dạng PNG và mẫu tên có `#` để đệm số frame. [Blender CLI 4.5](https://docs.blender.org/manual/es/4.5/advanced/command_line/arguments.html), [Blender CLI 4.3](https://docs.blender.org/manual/en/4.3/advanced/command_line/arguments.html), [ví dụ blender-scripting](https://github.com/njanakiev/blender-scripting). | Ít tầng phụ thuộc nhất để làm thử một shot 3D thật trên Windows. Có thể bắt đầu bằng scene tự tạo, Cycles CPU, không cần model weights hay tải asset. Chất lượng và thời gian render phải đo trên máy đã cài Blender. |
| **BlenderProc — adapter sau** | `blenderproc run <script>` chạy script trong Python của Blender. `bproc.init()`, đặt camera, `bproc.renderer.render()` trả dictionary các mảng ảnh; `bproc.writer.write_hdf5("output/", data)` ghi HDF5 theo frame, ví dụ `output/0.hdf5`. [README upstream](https://github.com/DLR-RM/BlenderProc/blob/main/README.md), [renderer](https://github.com/DLR-RM/BlenderProc/blob/main/docs/tutorials/renderer.md), [writer](https://github.com/DLR-RM/BlenderProc/blob/main/docs/tutorials/writer.md). | Hợp với RGB, depth, normals, semantic/object segmentation và dữ liệu huấn luyện. HDF5 không phải chuỗi PNG có thể đưa thẳng vào compositor/video; cần bước trích xuất/đổi định dạng. Không cần cho bản render shot đầu tiên. |
| **Godot Movie Maker — adapter tương tác sau** | `godot --path PROJECT --write-movie shot.png --fixed-fps 24 --quit-after 48` ghi PNG 8 chữ số từ 0 và WAV cùng tên gốc; hỗ trợ scene 2D/3D cùng âm thanh trong project. [Godot Movie Maker](https://docs.godotengine.org/en/stable/tutorials/animation/creating_movies.html), [CLI](https://docs.godotengine.org/en/stable/tutorials/editor/command_line_tutorial.html). | Có giá trị cho chuyển động tương tác, simulation và cutscene. **Không dùng `--headless` để render movie**: tài liệu `RenderingServer` xác nhận chế độ đó tắt toàn bộ rendering/window management. Cần môi trường có graphics driver/display phù hợp, và kiểm tra trên Windows thực tế. [RenderingServer](https://docs.godotengine.org/en/stable/classes/class_renderingserver.html). |
| **OpenUSD `usdrecord` — nghiên cứu sau** | CLI `usdrecord` đọc USD stage và xuất ảnh/chuỗi ảnh theo `--frames`; dự án upstream nói hỗ trợ Windows. [USD Toolset](https://openusd.org/release/toolset.html), [OpenUSD README](https://github.com/PixarAnimationStudios/OpenUSD). | Phù hợp làm định dạng trao đổi scene nhiều DCC/render delegate. Không tự giải bài toán tạo nhân vật, diễn xuất, physics hay lồng tiếng; tăng chi phí đóng gói nên chưa chọn làm renderer đầu tiên. |

### Ranh giới frame phải thống nhất

Chọn quy ước nội bộ **nửa mở** `[frame_start, frame_end_exclusive)`, trong đó `frame_end_exclusive - frame_start` bằng đúng số frame cần render. Shot 24 frame có thể dùng `[0, 24)` và phải tạo đúng frame 0–23. Quy ước này phù hợp với `duration_frames` nguyên trong `ProjectSpec` và tránh cộng/trừ một frame khi ghép shot.

Blender CLI `-a` / `--render-anim` render từ frame đầu đến frame cuối **bao gồm frame cuối**. Adapter thử nghiệm hiện dùng `bpy.ops.render.render(write_still=True)` cho từng frame và ánh xạ frame nội bộ 0 thành Blender frame 1; nhờ vậy file `frame_000000.png` ứng với frame 0 của shot. Nếu chuyển sang `animation=True` với cùng offset này, phải đặt `scene.frame_start = frame_start + 1` và `scene.frame_end = frame_end_exclusive`. Ngược lại, tài liệu BlenderProc định nghĩa vùng render `[frame_start, frame_end - 1]`, tức tham số `frame_end` của BlenderProc đã là đầu cuối **loại trừ**. [Blender CLI](https://docs.blender.org/manual/en/4.3/advanced/command_line/arguments.html), [BlenderProc renderer](https://github.com/DLR-RM/BlenderProc/blob/main/docs/tutorials/renderer.md), [BlenderProc keyframes](https://github.com/DLR-RM/BlenderProc/blob/main/docs/tutorials/key_frames.md).

FPS của project là phân số `numerator/denominator`; số frame và thứ tự frame là dữ liệu chuẩn để ghép video/voice. Adapter phải giữ lại phân số này trong manifest. Khi backend cần FPS dạng khác, phép ánh xạ phải được kiểm tra, đặc biệt với 24000/1001. Không suy ra thời lượng chuẩn bằng cách làm tròn FPS thành số nguyên trong bước mux audio.

### Cách gọi Blender native đề xuất

Ví dụ lệnh truyền **mảng tham số** từ Python `subprocess`, không ghép chuỗi shell; `BLENDER_EXE` là đường dẫn `blender.exe` do người vận hành cấu hình:

```python
argv = [
    BLENDER_EXE,
    "--background",
    "--factory-startup",
    "--offline-mode",
    "--python-exit-code", "1",
    "--python", RENDER_SCRIPT,
    "--", REQUEST_JSON,
]
```

`--background` chạy không UI; `--python` chạy script trong môi trường Blender; `--` chuyển phần còn lại nguyên vẹn cho `sys.argv`; `--python-exit-code 1` báo lỗi khi script Python ném exception. `--offline-mode` cấm truy cập mạng của Blender, phù hợp với job render offline sau khi asset đã được nhập. Tài liệu CLI nêu rõ **thứ tự đối số có tác dụng**: nếu dùng `.blend` đầu vào thì tải file trước khi đặt output và phát lệnh render, vì tải `.blend` có thể ghi đè setting trước đó. Đặt toàn bộ render settings trong script giúp kiểm soát thứ tự. [Blender CLI 4.5](https://docs.blender.org/manual/es/4.5/advanced/command_line/arguments.html).

Script tối thiểu cần đọc JSON request đã kiểm tra schema từ trước; tạo scene; cấu hình camera, vật thể, vật liệu, đèn, engine, resolution, frame range và đường dẫn xuất trong thư mục job; gọi render từng frame; sau đó process điều phối kiểm tra mã thoát **và** tất cả file PNG. Adapter thử nghiệm đặt tên `frame_000000.png` đến `frame_000023.png` trực tiếp và kiểm tra đủ 24 file. Tên path được xử lý bằng `pathlib`/đối số process, kể cả đường dẫn Windows có khoảng trắng và tiếng Việt. Blender cũng hỗ trợ mẫu `#` nếu về sau chuyển sang render animation liền mạch. [Blender CLI 4.3](https://docs.blender.org/manual/en/4.3/advanced/command_line/arguments.html).

Đề xuất chạy Cycles CPU với sample thấp và độ phân giải nhỏ cho phép thử đầu tiên; đây là **quyết định triển khai**, không phải số liệu tương thích/hiệu năng đã đo. Dùng một thư mục riêng theo job; adapter hiện kiểm tra đủ frame, kích thước, cấu trúc chunk/CRC PNG và SHA-256 trước khi công bố manifest. Chưa tích hợp bộ giải mã pixel PNG độc lập. Không chạy Python tùy ý từ project người dùng trong Blender. Mọi file `.blend`, model hoặc texture bên ngoài phải qua nhập asset, kiểm tra hash và quyền dùng trước khi mở.

### Physics và tính lặp lại

Với rigid body/physics của Blender, bake cache trước khi render để có thể phát lại cùng simulation và tránh sai khác khi seek frame. Blender có `bpy.ops.ptcache.bake_all(bake=True)`; tài liệu chính thức khuyên bake trước rendering, và disk cache cần lưu `.blend` trước để tạo `blendcache_[filename]` bên cạnh file. Bước physics nên tạo artifact cache riêng rồi renderer đọc cache đã khóa; không chia nhiều worker render frame rời trước khi bake. [Blender Python API ptcache](https://docs.blender.org/api/main/bpy.ops.ptcache.html), [Blender 4.5 Baking Physics](https://docs.blender.org/manual/id/4.5/physics/baking.html).

BlenderProc có hai API rất khác mục đích: `bproc.object.simulate_physics_and_fix_final_poses(...)` chỉ giữ tư thế nghỉ cuối cùng và bỏ diễn tiến; muốn render chuyển động phải dùng `bproc.object.simulate_physics(...)` rồi mở rộng khoảng keyframe bằng `bproc.utility.set_keyframe_render_interval(frame_end=N)`. Tài liệu upstream cũng chỉ rõ convex decomposition bằng V-HACD trong ví dụ chỉ hỗ trợ Linux; issue Windows còn mở. [Physics tutorial](https://github.com/DLR-RM/BlenderProc/blob/main/docs/tutorials/physics.md), [ví dụ convex decomposition](https://github.com/DLR-RM/BlenderProc/blob/main/examples/README.md), [issue Windows](https://github.com/DLR-RM/BlenderProc/issues/1223).

Đối với capability manifest, chưa có bằng chứng để cam kết hash pixel giống hệt trên mọi máy/driver/phiên bản. Nên ghi `determinism: "seeded"` hoặc `"unknown"` đúng với backend cụ thể; giữ seed, phiên bản engine, thiết bị render, cấu hình sample, hash asset và cache trong provenance. Chuyển động keyframe của bản thử đầu tiên **không được gọi là physics**.

### License và asset

Blender là phần mềm GPL; Blender Foundation xác nhận ảnh, movie và `.blend` do người dùng tạo thuộc quyền của người dùng, đồng thời lưu ý Python add-on/script dùng API Blender khi phân phối cần tương thích GPL theo cách diễn giải của họ. BlenderProc có [LICENSE GPL-3.0](https://github.com/DLR-RM/BlenderProc/blob/main/LICENSE); Godot dùng [MIT](https://godotengine.org/license/). Các model, texture, giọng nói và dữ liệu huấn luyện có điều kiện riêng; license của engine không cấp quyền dùng những asset đó. Do repo AnimeFlow chưa chọn license, quyết định phân phối script `bpy` hay tích hợp mã BlenderProc cần review riêng trước khi copy/vendoring. [Blender license](https://www.blender.org/about/license/).

## Hợp đồng adapter đề xuất cho bước triển khai

Đây là contract kỹ thuật đã dùng để thiết kế adapter v1. Nhánh triển khai có JSON Schema cảnh primitive và render result; các trường như `source_asset_ids` và pass bổ sung vẫn là đề xuất cho bước sau:

```text
render_frames(
  request = {
    shot_id, frame_start, frame_end_exclusive,
    fps: {numerator, denominator}, width, height,
    scene_spec_version, scene_spec,
    source_asset_ids, seed, render_quality
  },
  isolated_workspace
) -> frame_sequence_manifest
```

`scene_spec` bản đầu chỉ cần camera, background/world, một đèn, mesh/primitive, vật liệu và keyframe transform; kiểu vật thể hoặc hiệu ứng ngoài tập này phải trả lỗi `unsupported`, không giả lập thành render thành công. Frame index là tọa độ **trong shot**; khi nối scene/sequence, scheduler mới chuyển sang frame global. Giữ `source_asset_ids` thay cho đường dẫn tùy ý do người dùng đưa vào; core giải `asset://` thành file đã xác minh hash.

Manifest kết quả nên chứa `adapter_id`, `adapter_version`, `backend_version`, cấu hình render, FPS phân số, range nửa mở, hash đầu vào và danh sách `{frame_index, relative_path, sha256, width, height}`. Có thể đăng ký chính file manifest thành một `Artifact` theo schema hiện tại (`artifact_id`, `job_id`, `asset://` URI, media type, SHA-256), còn thiết kế lưu/serve nhiều frame sẽ do owner artifact quyết định. Không dùng một đường dẫn tuyệt đối máy render làm URI công khai. Kết quả thất bại/hủy phải giữ log và trạng thái lỗi, không tạo artifact hoàn thành.

**Lát cắt đã viết:** fixture một shot 24 frame ở 320×180, camera cố định, nền/đèn và vật thể có keyframe; API tạo job và worker gọi Blender để xuất PNG, kiểm số frame, kích thước và SHA-256. Kiểm thử Python dùng process giả để kiểm hợp đồng điều phối và mã lỗi khi Blender thiếu. **Chưa chạy render thực tế** vì Windows local không có Blender trên PATH và tải binary chính thức từ shell bị HTTP 403. Cần chạy smoke test với Blender đã cài trước khi nâng adapter khỏi `experimental`; audio, thoại Việt, lip-sync và xuất video hoàn chỉnh là các pipeline tiếp theo.
