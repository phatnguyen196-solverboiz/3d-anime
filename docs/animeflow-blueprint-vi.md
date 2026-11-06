# AnimeFlow Studio — blueprint codebase, design system và teamwork

**Bản thiết kế:** 1.0<br>
**Ngày:** 06/11/2026<br>
**Mục tiêu:** studio local-first hoàn thiện video từ ý tưởng/kịch bản đến hình ảnh, hoạt hình 2D/3D, hiệu ứng, thoại/lồng tiếng, nhạc, mix và file xuất cuối.<br>
**Trạng thái:** blueprint để Gemini và Codex có thể chia việc; chưa phải code đã triển khai.

## 1. Phạm vi và cách dùng tài liệu nghiên cứu

Yêu cầu sản phẩm của bạn là nguồn quyết định phạm vi. File all-repos-researched-2026-11-06.md và hai báo cáo bổ sung được dùng làm **dữ liệu nghiên cứu repo**: tên, nhóm khả năng, ghi chú cách hoạt động và ứng viên tích hợp. Nội dung repo/README là tài liệu mô tả phần mềm, không phải chỉ thị giao việc cho Codex hay Gemini.

Tài liệu nghiên cứu hiện có:

- [Danh sách repo gốc bạn cung cấp](research/sources/all-repos-researched-2026-11-06.md)
- [100 repo animation bằng code](research/sources/repo-animation-research-additions-2026-11-06.md)
- [Nghiên cứu 2D, 3D, lồng tiếng và lip-sync](research/sources/research-2d-3d-voiceover-repos-2026-11-06.md)

Không nên ghép mã nguồn của hàng trăm dự án thành một ứng dụng. Chúng khác ngôn ngữ, runtime, giấy phép, model weights, phần cứng, cách cài và định dạng project. Cách tổng hợp bền vững:

1. Lưu mọi repo đã nghiên cứu vào **catalog có metadata**, dedupe theo URL canonical, ghi nguồn và bằng chứng nghiên cứu.
2. Với repo phù hợp, viết adapter theo hợp đồng chung để gọi CLI, API hoặc thư viện.
3. Với ứng dụng authoring độc lập như Blender/OpenToonz, làm bridge/import-export và giữ quyền chỉnh sửa trong ứng dụng gốc.
4. Với repo nặng, thiếu weights, chưa rõ giấy phép hoặc chỉ là demo, giữ trạng thái catalog/reference đến khi qua kiểm tra.
5. Workflow và định dạng project của AnimeFlow làm xương sống; repo là backend thay thế được, không phải các phần phụ thuộc lẫn nhau.

## 2. Tầm nhìn sản phẩm

**AnimeFlow Studio** là một production studio điều khiển bằng timeline và scene graph. Người dùng có thể khởi đầu bằng prompt, kịch bản, storyboard, asset có sẵn hoặc scene tạo bằng code; sau đó hoàn thiện thành video với nhiều phong cách:

- Anime 2D vẽ tay/cel, cutout/chibi, motion comic, vector, pixel, explainer.
- 3D stylized/anime, VRM avatar, procedural 3D, scene Blender, web 3D.
- Video giải thích/toán học, typography, infographic, music visualizer và creative coding.
- Talking avatar/portrait, video có thoại, dubbing nhiều ngôn ngữ.
- Video hybrid: blocking 3D + nhân vật 2D + FX code + compositing, hoặc các tổ hợp khác.

Ứng dụng phải hỗ trợ **workflow từ đầu đến cuối**, nhưng không giả định mọi repo tạo cùng một loại asset. Adapter phải khai báo đầu vào, đầu ra, khả năng chỉnh sửa tiếp, thời gian chạy, phần cứng, model/weights và giấy phép.

### Thành phẩm người dùng cần có

Project mở lại được, chứa kịch bản, shot list, character bible, assets, timeline, audio, subtitle, cache, provenance và job state. Có preview/proxy trước final, khôi phục job lỗi, và xuất tối thiểu MP4 H.264/AAC cùng project/source manifest. Khi engine hỗ trợ, giữ frame sequence/layer passes để compositing hoặc render lại shot.

## 3. Ý tưởng mới tổng hợp từ các nhóm repo

Đây là thiết kế sản phẩm mới rút ra từ những cách làm đã nghiên cứu, không phải tuyên bố một repo nào đã có toàn bộ chức năng.

| Ý tưởng | Kết hợp bài học từ nhóm repo | Chức năng AnimeFlow |
|---|---|---|
| **Story-to-Shot Production Graph** | Prompt/script-to-video, Remotion compositions, Manim scenes, Blender procedural scenes | Kịch bản thành beat graph → scene → shot → task graph. Mỗi node do người dùng hoặc adapter thực hiện; output liên kết về đúng shot/version. |
| **Một shot, nhiều renderer** | Remotion/HyperFrames theo frame; Three.js/Babylon; Blender offline | Shot lưu ý định hình ảnh, camera, thời lượng, asset và cue. Chọn renderer code, web 3D hay Blender mà không đổi kịch bản/timeline. Không hứa pixel giống hệt giữa engine; giữ shot ID, thời gian và cue. |
| **2.5D Anime Stage** | Blender/Geometry Nodes, 2D authoring, parallax/canvas, code motion | Dựng camera/blocking 3D; render nhân vật/line art/background/FX thành lớp; compositing 2D giữ nét cel nhưng vẫn đổi góc máy. |
| **Event-to-FX Choreography** | Animation tương tác/physics, creative coding, game engine, audio synthesis | Bước chân, va chạm, rơi vật, mở cửa, impact thành event có timestamp. Event phát FX, camera shake, particle, foley/SFX, subtitle cue hoặc nhịp nhạc; từng phản hồi có thể sửa/bake/tắt. |
| **Voice Director và Lip-sync Relay** | TTS, ASR/alignment, Rhubarb/Papagayo, VRM blendshape, talking portrait | VoiceLine có speaker, take, cảm xúc, ngôn ngữ và time range. Cue chuẩn chuyển thành mouth chart 2D, viseme/blendshape 3D hoặc input audio cho portrait-video model; sửa cue tay được. |
| **Look Bible dạng dữ liệu** | Code-driven design systems, template videos, procedural materials | Character/style/environment bible có palette, silhouette, outline, lens, lighting, texture, FX rules và ví dụ. Backend không hỗ trợ thuộc tính nào thì app báo rõ, không âm thầm bỏ qua. |
| **Render Ledger có thể tiếp tục** | Frame-based render, offline 3D, media pipeline | Mỗi frame/pass ghi renderer version, input hash, seed, color settings và trạng thái. Render lại frame/shot lỗi; sửa voice chỉ invalidate nhánh audio/lip-sync/final mix liên quan. |
| **Story-aware Revisions** | Timeline editor, script-to-video, localization/dubbing | Sửa câu thoại đánh dấu alignment, lip-sync, subtitle, mix và các render node phụ thuộc là stale. Scene không liên quan giữ cache; đồ thị cho biết phần nào phải làm lại. |
| **Hybrid Manual/AI Production** | Repo authoring thủ công, generative media, scriptable renderers | Thay TTS bằng thu âm, AI image bằng tranh vẽ, motion synthesis bằng keyframe mà vẫn giữ timeline/shot graph. Không khóa project vào AI hoặc một dịch vụ cloud. |

## 4. Workflow sản xuất video hoàn chỉnh

Xương sống: **Project → Sequence → Scene → Shot → Layer/Track → Artifact**. Script và timeline liên kết bằng ID ổn định. Mọi bước có thể quay lại sửa, tạo version mới và xác định bước sau nào phải tính lại.

### A. Khởi tạo và định hướng

1. Tạo project; chọn ngôn ngữ, tỷ lệ khung hình, độ phân giải, frame rate dạng phân số, sample rate, profile màu và mục tiêu xuất.
2. Chọn recipe: anime 2D, 2.5D, anime 3D, explainer, music visualizer, talking avatar, dubbing hoặc hybrid.
3. Nhập brief, tài liệu tham khảo, assets có sẵn hoặc kịch bản.
4. Tạo thư viện style/character/environment/prop và ghi nguồn/quyền sử dụng media.

**Cổng duyệt:** chốt format, style bible, nhân vật và giới hạn thời lượng trước khi sản xuất nhiều asset.

### B. Kịch bản, nhịp truyện và storyboard

1. Từ brief tạo logline, premise, outline và beat sheet.
2. Chia scene theo địa điểm, thời gian, nhân vật và mục đích cảm xúc.
3. Viết narration/đối thoại theo speaker, giữ ID cho từng line.
4. Tạo shot list: cỡ cảnh, camera, chủ thể, hành động, thời lượng, thoại, âm thanh và transition.
5. Tạo storyboard tĩnh hoặc animatic; nhạc guide/temporary voice đặt nhịp.
6. Tạo animatic có timecode để kiểm tra nhịp trước khi dựng chi tiết.

**Cổng duyệt:** chốt cấu trúc truyện/thời lượng. Có thể sửa sau đó, nhưng hệ thống chỉ rõ shot, thoại và render nào bị ảnh hưởng.

### C. Tạo asset và bối cảnh

1. **Character bible:** ID, turn-around, biểu cảm, palette, rig/viseme, costume variant, scale, nguồn asset.
2. **Environment bible:** layout, landmarks, ánh sáng theo thời gian, foreground/midground/background, collision surfaces.
3. **Prop bible:** kích thước, pivot, vật liệu, khả năng tương tác, trạng thái mở/đóng/vỡ.
4. **2D asset:** layer, vector/path, mouth chart, pose sheet, FX cel, background plates.
5. **3D asset:** mesh, material, skeleton/rig, shape keys/blendshapes, camera markers, collision proxy, animation clips.
6. Import PSD/PNG/SVG/EXR/GLB/VRM/WAV/FLAC hoặc project bridge được hỗ trợ. Fingerprint và lưu source path cho từng import.

Không bắt buộc mọi nhân vật do AI sinh: có thể dùng tranh vẽ, model tự dựng, asset có sẵn, ảnh chân dung hoặc placeholder tùy quyền sử dụng/chất lượng.

### D. Blocking, chuyển động và tương tác

1. Dựng layout bối cảnh và camera từng shot.
2. Gắn nhân vật/prop vào shot; chọn clip hoặc tạo keyframe.
3. Dùng 3D blocking để đặt staging/camera/timing, rồi render passes sang compositing 2D nếu cần.
4. Hỗ trợ frame-by-frame, cutout, keyframe/tween, rig/retarget, procedural/code, motion capture hoặc audio-driven portrait.
5. Physics có thể là rigid body, cloth/soft-body, particles, destruction hoặc physics stylized. Chạy fixed timestep, bake cache, lưu seed/version; không để final render thay đổi ngẫu nhiên.
6. Chuẩn hóa event: contact, impact, footstep, prop pickup, landing, facial beat. Mỗi event có frame/time, entity IDs, intensity và type.
7. Event điều khiển camera shake, particles, line burst, dust, hit flash, foley, SFX, light pulse hoặc nhịp nhạc.
8. Scrub timeline và preview proxy; báo animation/cache/weights còn thiếu.

**Cổng duyệt:** chốt camera/blocking/nhịp trước final render; physics phải bake hoặc gắn nhãn realtime/nondeterministic.

### E. Render hình theo frame và compositing

1. Adapter khai báo cách nhận scene/timeline. Core gửi JSON manifest, không ghép shell command từ input người dùng.
2. Render theo shot và frame range; hỗ trợ preview resolution, final resolution, seed, samples/quality.
3. Nếu backend hỗ trợ, giữ passes: beauty, alpha, line/art, depth, normal, shadow, emission, object/character matte và motion/vector.
4. Lưu image sequence theo shot/render version; kiểm tra số frame, kích thước, alpha, profile màu và file lỗi.
5. Compositor ghép layer, background, outline, glow, FX, transition, title, caption và color treatment.
6. Xuất image sequence sang editor khác được hỗ trợ; giữ shot ID/time range để round-trip.
7. Khi mọi shot đạt, tạo picture lock rồi final render/encode.

### F. Thoại, lồng tiếng và âm thanh

1. Chốt text; gán speaker/voice actor; quản lý take, emotion, delivery, language và pronunciation dictionary.
2. Nạp file thu thật hoặc gọi TTS adapter. Voice clone chỉ chạy khi có quyền/consent được ghi nhận.
3. Căn transcript/line với audio thành word/phoneme timestamps nếu engine cung cấp; nếu không, sửa marker bằng tay.
4. Lip-sync relay:
   - **2D:** mouth chart/viseme theo frame, sửa được từng cue.
   - **3D:** viseme/phoneme → blendshape hoặc rig channel; emotion/eye/brow là lớp riêng.
   - **Portrait video:** audio + portrait input cho adapter video; khai báo rõ output là video tổng hợp, không phải rig chỉnh xương.
5. Dựng track thoại, ADR, room tone, ambience, foley, SFX, music, narration và silence; hỗ trợ mute/solo, gain, pan, fades, ducking.
6. Subtitle/caption theo ngôn ngữ, speaker và accessibility; cue độc lập với hình để dễ dịch.
7. Mix/master theo delivery profile; phát hiện clipping, missing audio và silence bất thường.
8. Đổi một line tạo version và invalidate dependency liên quan; hỗ trợ picture lock hoặc mix lock.

### G. Review, QC và phát hành

- Xem toàn timeline/shot, so A/B giữa các version.
- Kiểm tra frame gap/duplicate, frame đen, aspect/crop sai, audio drift, clipping, silent track, subtitle tràn, lip-sync lệch và asset thiếu.
- Preview proxy hiển thị sớm; final QC kiểm trên file encode, không chỉ canvas preview.
- Xuất MP4, WAV/stems, VTT/SRT, image sequence tùy chọn, project bundle và provenance manifest.
- Package handoff có asset license metadata, engine/adapter versions, render settings, voice source/consent reference và hashes.

## 5. Kiến trúc kỹ thuật

### Quyết định baseline

| Vùng | Baseline | Lý do |
|---|---|---|
| Studio UI | React + TypeScript + Vite | Phù hợp editor/timeline và hệ sinh thái Remotion/Three.js; tách UI khỏi worker. |
| Local API | Python + FastAPI + Pydantic | Hợp adapter AI/media, subprocess, file assets và GPU libraries. |
| Orchestration | Python worker service, SQLite-backed queue ban đầu | Một nguồn điều phối local; có thể thay queue mà không đổi UI contract. |
| Shared contracts | JSON Schema + generated TypeScript/Python types | API, project spec và adapter manifest không bị định nghĩa lệch. |
| Project metadata | SQLite + migrations | Project local; media vẫn lưu trên filesystem. |
| Editorial interchange | OpenTimelineIO adapter | Trao đổi timeline, không thay toàn bộ story/character/generation metadata. |
| Media | FFmpeg adapter + capability probe | Encode/mux/convert; cần ghi cấu hình build/licensing. |
| Adapter runtime | Mỗi adapter có environment/version pin riêng | Tránh dependency va chạm; tắt riêng GPU/model-heavy adapter được. |
| Packaging | Dev launcher trước, desktop packaging sau MVP | Chốt project/adapter contract trước khi đầu tư đóng gói. |

OpenTimelineIO mô tả cấu trúc editorial timeline và tham chiếu media; nó không chứa bản thân media hay toàn bộ metadata nghiệp vụ. Xem [tài liệu kiến trúc OpenTimelineIO](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/blob/main/docs/tutorials/architecture.md).

### Sơ đồ hệ thống

~~~mermaid
flowchart LR
    U[User] --> UI[React Studio]
    UI --> API[Local FastAPI]
    API --> DB[(SQLite project metadata)]
    API --> ORCH[Workflow Orchestrator]
    ORCH --> Q[Job Queue]
    Q --> W[Worker Manager]
    W --> A1[Code Video Adapters]
    W --> A2[2D Animation Bridges]
    W --> A3[3D and Physics Adapters]
    W --> A4[Voice and Lip Sync Adapters]
    W --> A5[FFmpeg and Compositor]
    A1 --> FS[(Project Assets and Render Cache)]
    A2 --> FS
    A3 --> FS
    A4 --> FS
    A5 --> FS
    W --> EV[Progress Events / SSE]
    EV --> UI
    CAT[Repository Catalog] --> API
    OTIO[OTIO Import and Export] <--> API
~~~

### Monorepo layout

~~~text
animeflow-studio/
  apps/
    studio-web/                 # React: project, script, storyboard, timeline, preview
    local-launcher/             # dev/start scripts; desktop shell after MVP
  services/
    api/                        # FastAPI, project/job/catalog endpoints
    orchestrator/               # dependency graph, invalidation, job lifecycle
    worker-manager/             # process isolation, resource limits, logs, cancel
  packages/
    contracts/
      schemas/                  # ProjectSpec, AdapterManifest, Job, Artifact, VoiceLine
      generated/                # generated TS/Python types; do not edit manually
    project-spec/               # migration, validation, project IO
    timeline/                   # time math, frame/sample conversion, OTIO bridge
    adapter-sdk/                # manifest, process protocol, result validation
    design-tokens/              # CSS variables, themes, spacing, typography
    ui-kit/                     # reusable editor components
    media-utils/                # ffprobe, waveform, thumbnail, hash, proxy
    style-profiles/             # capability-aware output looks and templates
  adapters/
    code-video/{remotion,hyperframes,motion-canvas,manim,creative-canvas}/
    animation-2d/{opentoonz-bridge,synfig,vector-animation,lipsync-cues}/
    animation-3d/{blender,three-web,babylon,vrm,physics}/
    portrait-video/{sadtalker,musetalk,echomimic,liveportrait}/
    audio/{tts,asr-alignment,voice-conversion,separation,music-sfx,dubbing}/
    media/{ffmpeg,compositor}/
  catalog/
    repos.json                  # canonical URL, category, evidence, status, license
    schemas/
  templates/
    anime-cel-2d/  2-5d-stage/  anime-vrm-3d/  motion-comic/
    explainer/     talking-avatar/  dubbed-series/  audio-visualizer/
  docs/
    architecture/  decisions/  adapter-guides/  research/
    TEAM_WORKFLOW.md  RELEASE_CHECKLIST.md
  fixtures/
    tiny-project/  sample-character/  audio-short/
  scripts/
  .github/
    CODEOWNERS  PULL_REQUEST_TEMPLATE.md  ISSUE_TEMPLATE/
~~~

Không cần bật mọi adapter ngay. Adapter chưa sẵn sàng có trạng thái disabled/experimental, không làm hỏng core project.

## 6. Dữ liệu chuẩn và hợp đồng module

### 6.1 ProjectSpec

ProjectSpec là nguồn dữ liệu chính. JSON Schema ở packages/contracts/schemas; TS/Python types được generate từ schema.

~~~text
Project
  schema_version, project_id, title, locale, delivery_profile
  style_profiles[]
  characters[], environments[], assets[]
  sequences[]
    scenes[]
      shots[]
        shot_id, duration, camera, renderer_intent
        entities[], actions[], events[]
        tracks[]
          dialogue | animation | video | audio | subtitle | effect
  voice_cast[], render_profiles[], provenance{}
~~~

Mỗi entity/shot/asset/line có ID ổn định và version. Đổi tên không mất liên kết. Media dùng `asset://<asset_id>` trong spec; bảng asset trỏ tới relative path, external path hoặc cache URI. Không lưu secret/token trong project JSON.

### 6.2 Timebase chính xác

- Video lưu frame rate dạng rational numerator/denominator, không tích lũy float.
- Cue animation/video lưu frame index và timebase sequence/shot.
- Audio lưu sample index và sample rate tường minh; baseline production là 48 kHz nhưng phải đọc rate khác.
- UI có thể hiển thị timecode/giây; phép tính nội bộ dùng integer frame, rational fps và integer audio samples.
- Quy tắc rounding tập trung trong timeline package, không tự tính lại ở từng adapter.
- Import OTIO/FCPXML/CSV giữ giá trị gốc và normalized position để kiểm tra round-trip.

### 6.3 AdapterManifest

Mỗi adapter khai báo:

~~~text
id, display_name, adapter_version, contract_version
category, capabilities[], input_schema, output_schema
entrypoint, runtime, install_state, health_check
supported_os[], cpu/gpu requirements, memory/vram estimate
model_files[], model_license_refs[], code_license_ref
network_requirement, privacy_mode, deterministic_level
estimated_duration, cancellation_behavior, docs_url
~~~

Adapter phải mô tả operation cụ thể như `render.frames`, `import.scene`, `animate.vrm_from_audio`, `generate.portrait_video`, `align.phonemes` hoặc `mix.stems`, không chỉ gắn nhãn “3D animation”.

### 6.4 Chu trình adapter

~~~text
inspect()       -> capabilities + versions + installed models
validate(input) -> errors/warnings + resource estimate
prepare(input)  -> normalized input and temp workspace
execute(job)    -> progress events + output paths
cancel(job_id)  -> cooperative cancellation where supported
collect(job)    -> validated ResultManifest
cleanup(job)    -> temp/cache cleanup policy
~~~

Worker gọi executable bằng argument array, không ghép shell command từ prompt/input. Adapter có environment riêng, temp directory riêng và output path giới hạn trong workspace/cache được cấp. Giới hạn log stdout/stderr và loại credential/token.

ResultManifest gồm output asset IDs, MIME, dimensions, duration/timebase, hashes, warnings, source job, renderer/adapter/model versions, seed và sidecars. Core validate manifest rồi mới cho artifact dùng được.

### 6.5 Workflow graph, cache và invalidation

Mỗi bước là node trong DAG: script parse → voice generation/alignment → lip-sync cues → shot render → composite → final audio mix → encode. Node ghi input hashes, parameter hash, tool versions và dependency IDs.

- Đổi màu subtitle không invalid physics simulation.
- Đổi audio take invalid alignment/lip-sync/mix/final encode của shot liên quan.
- Đổi mesh/rig invalid render của shot dùng character đó.
- Cùng input/version/seed có thể reuse cache nếu adapter deterministic và hash khớp.
- Adapter realtime/nondeterministic phải gắn nhãn; yêu cầu bake/freeze trước khi giả định cache.

## 7. Job system và API

### Job lifecycle

`queued → validating → preparing → running → collecting → succeeded`

Nhánh kết thúc: `failed`, `cancel_requested → cancelled`, `blocked` (thiếu binary/model/license acceptance), `stale` (input đã đổi). Job có progress, phase, log reference, resource estimate, cancel policy, outputs và lỗi có thể xử lý. UI không chờ render đồng bộ.

### API v1 sơ khởi

~~~text
GET    /api/v1/health
GET    /api/v1/catalog/repos
GET    /api/v1/adapters
GET    /api/v1/adapters/{id}/health
POST   /api/v1/projects
GET    /api/v1/projects/{project_id}
PATCH  /api/v1/projects/{project_id}
POST   /api/v1/projects/{project_id}/validate
POST   /api/v1/projects/{project_id}/assets/import
POST   /api/v1/projects/{project_id}/jobs
GET    /api/v1/jobs/{job_id}
POST   /api/v1/jobs/{job_id}/cancel
GET    /api/v1/projects/{project_id}/events   # SSE progress/update stream
POST   /api/v1/projects/{project_id}/timeline/import
POST   /api/v1/projects/{project_id}/timeline/export
~~~

API nhận project/shot IDs và typed options, không nhận arbitrary shell script. FastAPI OpenAPI tạo client; JSON Schema project/adapter là contract versioned riêng.

## 8. Repository catalog và ưu tiên tích hợp

### Catalog record

~~~text
repo_id, canonical_url, display_name, category[], capability_tags[]
research_summary, evidence_links[], last_checked_at
repo_commit_or_release, language, runtime, install_notes
license_spdx_or_unknown, model_license, asset_license
maintenance_signal, platform_support, hardware_requirements
integration_mode, integration_status, confidence, open_questions
~~~

Dedupe theo canonical origin URL. Trạng thái: `researched → candidate → spike → adapter_alpha → supported → deprecated`; hoặc `reference_only`, `blocked_license`, `unverified`, `archived`. “Đã nghiên cứu” không đồng nghĩa “đã tích hợp”. Repo bổ sung cần mô tả pipeline hoạt động, ngày và nguồn.

### Nhóm ứng viên theo vai trò

- **Code video/motion:** Remotion, HyperFrames, Motion Canvas/Revideo, Manim, template/code motion projects, creative coding. Chọn một renderer chính cho MVP.
- **2D authoring/motion:** OpenToonz/Tahoma2D, Synfig, vector/canvas animation; bridge cho desktop app, adapter cho CLI/library tự động hóa được.
- **3D/web/procedural:** Blender/BlenderProc, Three.js/React Three Fiber, Babylon.js, PlayCanvas, glTF/VRM, Theatre.js. Phân biệt offline render, realtime preview và asset viewer.
- **Physics/interaction:** physics libraries/game engines/procedural effects; contract riêng với fixed timestep/bake/cache.
- **Voice/audio:** TTS, ASR/alignment, voice conversion/separation, SFX/music, dubbing; tách generation khỏi alignment, lip-sync và mix.
- **Portrait video:** SadTalker, MuseTalk, EchoMimic, LivePortrait là video-output adapters, không mặc định là mesh/rig editor.
- **Media editorial:** FFmpeg, OTIO, subtitle/waveform helpers, editors và handoff.

### Chấm điểm adapter

Chấm 0–5 cho: chất lượng output, tự động hóa, kiểm soát frame/timing, batch/headless, Windows support, VRAM/CPU, độ rõ license của code/weights, maintenance, và giá trị so với adapter đang có. Ghi score cùng bằng chứng; xem score là quyết định ưu tiên chứ không phải sự thật khách quan.

Review tách code license, pretrained weights, sample assets, fonts, voice data và output terms. Remotion có điều kiện cấp phép theo loại/kích cỡ tổ chức; xem [license Remotion](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md). FFmpeg có cấu hình LGPL/GPL khác nhau tùy build/component; xem [legal information FFmpeg](https://ffmpeg.org/legal.html). Adapter chỉ bật khi đã ghi rõ trạng thái kiểm tra code và weights.

## 9. Design system của studio

Design system này là giao diện **ứng dụng AnimeFlow**, tách biệt với style bible tạo ra hình ảnh. Output được đa dạng; UI giữ các quy tắc điều khiển nhất quán.

### Nguyên tắc

- Dark editing room mặc định, tương phản tốt, có theme sáng tùy chọn.
- Trạng thái rõ: ready, rendering, stale, missing asset, setup/license required, failed.
- Preview cạnh timeline; inspector thay nội dung theo lựa chọn.
- Không giấu lỗi render/model/voice trong log chung.
- Người mới dùng wizard/recipe; người nâng cao mở scene graph, parameters, node status và paths.
- Thao tác quan trọng dùng bàn phím; focus ring, tooltip và label/icon; không phân biệt trạng thái chỉ bằng màu.

### Token nền tảng

~~~css
:root {
  --color-bg: #101218;
  --color-surface: #191d27;
  --color-panel: #202633;
  --color-border: #343c4c;
  --color-text: #f3f5fa;
  --color-muted: #a8b0c0;
  --color-accent: #8b7cff;
  --color-accent-2: #45c6b0;
  --color-warning: #ffc36b;
  --color-danger: #ff6d7a;
  --color-success: #59d39a;
  --space-1: 4px; --space-2: 8px; --space-3: 12px;
  --space-4: 16px; --space-6: 24px; --space-8: 32px;
  --radius-sm: 6px; --radius-md: 10px; --radius-lg: 14px;
}
~~~

Token là điểm bắt đầu, phải kiểm contrast trong UI. Font UI sans dễ đọc; timecode/parameters dùng tabular numerals. Timeline có mật độ compact/comfortable.

### Workspace layout

1. **Project rail:** projects, sequences, assets, characters, environments.
2. **Production navigator:** script, storyboard, shots, audio, render graph, catalog/adapters.
3. **Preview canvas:** shot/camera, safe areas, overlays, proxy/final indicator, playback/scrub.
4. **Timeline:** ruler, scene/shot bands, video/animation/audio/subtitle/FX lanes, markers, waveform, snap, zoom, mute/solo/lock.
5. **Inspector:** transform, renderer settings, style, character rig/voice, cue/event list.
6. **Job dock:** render queue, GPU/VRAM estimate, progress, logs, retry/cancel, missing setup.

### Components dùng chung

`AppShell`, `ProjectSwitcher`, `AssetBrowser`, `CharacterCard`, `EnvironmentCard`, `ShotList`, `StoryboardBoard`, `PreviewCanvas`, `TimelineRuler`, `TrackHeader`, `ClipBlock`, `WaveformLane`, `VoiceLineCard`, `VisemeEditor`, `EventMarker`, `StyleProfilePicker`, `AdapterCard`, `CapabilityBadge`, `ResourceEstimate`, `RenderQueue`, `JobLogDrawer`, `MissingDependencyBanner`, `ExportDialog`.

### Output style profiles

`anime-cel-2d`, `chibi-cutout`, `motion-comic`, `vector-explainer`, `pixel-animation`, `2-5d-anime-stage`, `anime-vrm-3d`, `procedural-3d`, `talking-avatar`, `portrait-dub`, `music-visualizer`, `stop-motion`. Mỗi profile mô tả palette/material/line/camera/lighting/compositing/audio treatment và adapter cần thiết; backend thiếu khả năng thì báo và chỉ ra pass/postprocess thay thế.

## 10. Tổ chức project/artifact

~~~text
MyFilm.animeflow/
  project.json
  project.db
  scripts/
  storyboard/
  assets/
    characters/ environments/ props/ audio/ imported/
  shots/
    seq01_sc01_sh010/
      shot.json
      cache/
      renders/
        preview/ final/ passes/
  audio/
    dialogue/ music/ sfx/ stems/ subtitles/
  exports/
  provenance/
    jobs/ manifests/
~~~

Asset nội bộ dùng relative paths để project di chuyển được. Asset ngoài có chế độ link/copy-in; UI báo file nào chỉ có trên máy này. Cache xóa/rebuild được; source/project spec/final exports không bị xem là cache. Hash file lớn tính nền để không khóa UI.

## 11. Vận hành an toàn và tái lập

- Adapter chạy bằng user hiện tại, temp folder riêng, timeout/resource limits và quyền rõ.
- Không tự cài repo/weights âm thầm; setup nêu size, nguồn, license và hardware trước khi tải.
- Không upload media nếu user chưa bật cloud adapter tương ứng.
- Không log API key, voice credentials hay nội dung nhạy cảm.
- Version project/schema/adapter/tool; migration tạo backup.
- Pin commit/release và lock dependencies; kiểm tra update tường minh.
- Voice có provenance/permission/speaker attribution; voice clone cần consent record; thay/xóa voice cho phép render lại dependencies.
- Manifest ghi seed, model revision, color settings, fps, sample rate và hashes.

## 12. Teamwork Gemini + Codex

Nguyên tắc: **một owner cho mỗi thư mục và schema; module kết nối qua contract đã chốt.** Nếu dùng chung repo/worktree, không sửa cùng file đồng thời; dùng branch/worktree riêng và tích hợp theo PR/patch.

| Workstream | Owner gợi ý | Paths sở hữu | Bàn giao |
|---|---|---|---|
| Product spec, story/shot model, API, orchestration | Codex | services/api/, services/orchestrator/, packages/project-spec/, packages/contracts/ | JSON Schema, OpenAPI, API examples, migration |
| UI shell, tokens, component kit, editor panels | Gemini | apps/studio-web/, packages/design-tokens/, packages/ui-kit/ | UI dùng generated types; fixture screen; interaction notes |
| Code-video adapter spike | Codex | adapters/code-video/ và SDK consumer | AdapterManifest + vertical render flow nhỏ |
| 2D bridge spike và catalog audit | Gemini | adapters/animation-2d/, catalog/, docs/research/ | setup/license evidence, import/export sample, gaps |
| Voice/transcript/cue integration | Gemini | adapters/audio/, voice cue UI nếu được giao | VoiceLine/Alignment contract; sample audio manifest |
| 3D/physics adapter và artifact pipeline | Codex | adapters/animation-3d/, packages/media-utils/ | frame/pass manifest, resource estimate, deterministic notes |
| Full-stack integration/release | Codex + Gemini theo ticket nhỏ | paths theo PR; không share ownership | demo project, changelog, known limitations |
| Product/style/sample rights | User | docs/product/ hoặc issue review | ngôn ngữ, style ban đầu, hardware, quyền, priority |

Đổi owner trong task packet trước khi làm. Gemini không đổi canonical schema ngoài schema PR đã thống nhất; Codex không sửa UI files Gemini đang sở hữu nếu chưa chuyển owner. Module owner review thay đổi trong thư mục của họ.

### Quy trình

1. **M0 contract freeze:** chốt IDs, time model, ArtifactRef, AdapterManifest, Job events, conventions; lưu ADR và JSON examples.
2. Mỗi ticket nêu một mục tiêu, ownership, contract I/O, acceptance, fixture, câu lệnh chạy và out-of-scope.
3. Branch `feat/<ticket>-<short-name>`; mỗi PR một module; không commit weights, media lớn hay secrets.
4. Schema PR kèm examples và migration/versioning notes. Generated files không sửa tay.
5. Trước merge, owner rà contract, error handling, provenance và Windows run path. Các kiểm tra dự án sẽ được chạy khi implementation tồn tại; blueprint này chưa thêm hoặc chạy test.
6. Tích hợp trên demo project nhỏ; chạy adapter thật bằng manifest; chốt demo có hình, tiếng và export trước khi mở scope.
7. Lệch plan thì ghi ADR: bối cảnh, lựa chọn, lý do, ảnh hưởng và cách quay lại.

### Task packet giao cho Gemini

~~~text
Ticket: AF-UI-01 — Build the Studio shell from the approved architecture
Owner: Gemini
Allowed paths: apps/studio-web/**, packages/design-tokens/**, packages/ui-kit/**
Do not edit: packages/contracts/schemas/**, services/**, adapters/**
Inputs: approved ProjectSummary, ShotSummary, JobSummary JSON examples in docs/contracts/
Deliver: responsive dark editor shell with project rail, preview canvas, timeline lanes,
inspector, job dock; design tokens; keyboard/focus behavior; one fixture-backed screen.
Acceptance: uses generated contracts; missing adapter and failed job states are visible;
no fake API assumptions beyond fixtures; list changed files and commands to run.
If a contract is missing, propose the smallest schema change; do not invent a second schema.
~~~

### Task packet giao cho Codex

~~~text
Ticket: AF-CORE-01 — Implement the project/job API contract
Owner: Codex
Allowed paths: services/api/**, services/orchestrator/**, packages/project-spec/**
Shared contract owner: packages/contracts/schemas/** changes only through an ADR/schema PR.
Inputs: approved JSON Schemas and tiny-project fixture.
Deliver: project create/read/validate, job enqueue/status/cancel, SSE events, migration plan.
Acceptance: typed errors; job state transitions; paths restricted to project workspace;
API examples documented for UI owner; no UI edits.
~~~

### Handoff note cho mọi ticket

~~~text
Ticket/branch:
Files changed:
Contracts relied on:
What works:
How to run/open:
Known gaps:
Evidence/demo artifact:
Next dependency or question:
~~~

## 13. Roadmap theo phase

Thứ tự/phạm vi, không phải cam kết lịch. Mỗi phase kết thúc bằng vertical slice dùng được.

### M0 — Product + contracts

- Dedupe catalog; chốt project tree, IDs, timebase, artifact/job contracts.
- ADR cho storage, adapter process boundary, offline mode, license metadata.
- Tiny project: 1 scene, 1 placeholder character, 1 voice line.

**Exit:** Gemini và Codex cùng đọc/validate fixture; chỉ có một canonical schema.

### M1 — Studio shell + project core

- UI project/asset/shot navigator, preview placeholder, frame/sample math.
- API project CRUD/validation, SQLite migration, events/job queue.
- Import asset, probe metadata, backup.

**Exit:** tạo/mở project, sửa shot timing, xem job progress trên Windows local.

### M2 — First complete video slice (code + audio + export)

- Chọn một code renderer đã qua spike/license/setup review.
- Title/scene template, voice/audio track, caption hoặc visualizer.
- Render preview, waveform/cue timeline, mux bằng FFmpeg, xuất MP4.
- Manifest và QC cơ bản.

**Exit:** project fixture thành video có hình/tiếng; sửa text/audio và render lại.

### M3 — Storyboard, script, voice and dubbing

- Script/beat/shot editor, storyboard/animatic.
- VoiceLine/take manager, file thoại/TTS, alignment, subtitles, lip-sync cue editor.
- Tách thoại/ambience/music và mix profile.

**Exit:** scene hội thoại nhiều speaker, sửa cue tay, subtitle/mix đúng timebase.

### M4 — 2D pipeline

- Bridge cho 2D authoring được chọn; mouth chart; layer/pass ingestion.
- Batch cue → mouth animation → render shot.
- 2D compositing, camera moves, FX layers.

**Exit:** shot thoại 2D đi từ voice cue qua hình, comp và encode.

### M5 — 3D, camera, character and physics

- Một 3D renderer offline và một preview path.
- Import scene/character, rig metadata, clips, camera, material/look profile.
- Physics events, simulation bake, particles/FX hook, render passes và frame resume.

**Exit:** shot 3D có bối cảnh, nhân vật, camera, physics event, thoại/viseme; xuất sequence và video.

### M6 — Hybrid studio and editorial interchange

- 2.5D stage, multi-pass compositing, timeline interchange.
- Shot dependency graph, selective invalidation, render ledger, retries.
- Thêm renderer thứ hai theo capability mà không đổi core spec.

**Exit:** một scene spec qua hai backend khác scope; shot IDs/time/audio được giữ.

### M7 — Portrait video, localization and quality

- Portrait-video adapters theo GPU/weights/license; worker resource isolation.
- Multi-language voice/subtitle, voice provenance, dubbing QA.
- Quality dashboard, export profiles, packaging.

**Exit:** localization chỉ render lại dependency liên quan, giữ asset khác.

### M8 — Catalog mở rộng và đóng gói

- Đánh giá catalog và thêm adapter có lợi ích rõ.
- Installer/dev launcher, self-diagnostics, backup/recovery, portable project.
- Xem xét desktop shell/remote workers khi local workflow ổn định.

**Exit:** cài mới, mở project mẫu, self-check, tạo và xuất video.

## 14. Definition of Done cho workflow hoàn chỉnh

Một demo project tái lập được:

- Story/scene/shot, character/environment/assets và timeline lưu trong project.
- Ít nhất một đường hình ảnh đến MP4, có preview và final profile.
- Frame rate/audio timebase rõ; không drift giữa các stage.
- Có thoại/audio track, cue hoặc subtitle, mix và mux trong output.
- Ít nhất một phương thức animation 2D hoặc 3D hoạt động; thêm adapter không đổi ProjectSpec.
- Job có progress, lỗi đọc được, cancel/retry, provenance và output manifest.
- Sample media nhỏ xác nhận hình/audio/timestamp; license/model/setup status hiển thị trước khi chạy.
- Project đóng/mở lại được; assets resolve hoặc báo missing; cache rebuild được.
- Có duyệt storyboard, blocking, voice, picture lock, final QC.
- Output cuối được probe/playback; preview canvas không tính là bằng chứng file video hoàn tất.

## 15. Rủi ro và cách giảm thiểu

| Rủi ro | Thiết kế giảm thiểu |
|---|---|
| Tích hợp hàng trăm repo cùng lúc làm vỡ lịch | Dedupe/catalog; chọn theo score và vertical slice; reference-only vẫn tra cứu được. |
| License code/weights/assets khác nhau | Metadata tách theo loại; review trước khi bật adapter/phân phối. |
| GPU/VRAM không đủ | Preflight resource estimate; GPU queue tuần tự mặc định; proxy/CPU nếu hỗ trợ. |
| Render/physics khác giữa lần chạy | Fixed timestep, bake, seed/version tracking và deterministic level. |
| Audio/video lệch timecode | Timeline package chuẩn; frames và samples là integer; conversion tập trung. |
| Adapter dùng định dạng riêng | Converter cô lập; không nhét logic engine vào ProjectSpec. |
| Gemini/Codex sửa chồng schema/UI/API | Path ownership, schema owner, branch riêng, handoff và contract freeze. |
| Upstream đổi/ngừng duy trì | Pin commit/release, last checked, health check và deprecation. |
| Nhầm portrait video với rig 3D | Khai báo output type: video synthesis hay mesh/rig animation. |
| Voice clone/upload thiếu quyền | Consent/provenance, local-first, cloud opt-in, không log secrets. |

## 16. Nguồn kỹ thuật chính

- [OpenTimelineIO architecture tutorial](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/blob/main/docs/tutorials/architecture.md) — editorial interchange.
- [Remotion license](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md) — điều kiện sử dụng cần rà theo mô hình tổ chức.
- [FFmpeg legal information](https://ffmpeg.org/legal.html) — cấu hình build và thành phần LGPL/GPL.
- [OpenToonz ToonzScript](https://github.com/opentoonz/opentoonz_docs/blob/master/source/toonzscript.rst) — automation/bridge 2D.
- [Rhubarb Lip Sync](https://github.com/DanielSWolf/rhubarb-lip-sync) — cue khẩu hình từ thoại.
- [TalkingHead](https://github.com/met4citizen/TalkingHead) và [HeadTTS](https://github.com/met4citizen/HeadTTS) — TTS/audio timing với avatar web.
- [Blender](https://github.com/blender/blender), [Babylon.js](https://github.com/BabylonJS/Babylon.js), [Three.js](https://github.com/mrdoob/three.js), [Manim Community](https://github.com/ManimCommunity/manim) — nhóm renderer/code animation trong tập nghiên cứu.
- Chi tiết các repo và ghi chú hoạt động: ba tài liệu research tại mục 1.

**Bước triển khai đầu tiên:** M0 contracts/fixture và catalog dedup; Gemini dựng UI shell trên fixture, Codex dựng ProjectSpec/API. Khi cả hai cùng đọc một fixture, nối renderer/audio adapter đầu tiên.
