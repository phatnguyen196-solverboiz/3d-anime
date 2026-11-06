# 100 repo bổ sung về animation tạo bằng code

**Nghiên cứu ngày:** 2026-11-06<br>
**Danh sách gốc đối chiếu:** `all-repos-researched-2026-11-06.md`<br>
**Phạm vi:** 100 repo GitHub khác với các đường dẫn repo đã có trong danh sách gốc. Tập trung vào tạo hình/animation theo frame, render video bằng code, motion graphics, Manim và procedural animation. Các repo tương tác trực tiếp trên canvas hoặc trong game engine cũng được giữ lại nhưng ghi rõ nếu mặc định không xuất MP4.

> Đây là 100 repo đã được sàng lọc và đọc README/mô tả/cấu trúc công khai ở mức nghiên cứu tài liệu. Mình chưa clone, cài hoặc chạy cả 100 repo; vì thế ghi chú mô tả cách repo tự công bố hoạt động, không phải kết quả kiểm thử độc lập. GitHub có hàng nghìn repo theo các nhãn creative-coding/animation nên danh sách này là tập bổ sung có giới hạn, không thể khẳng định là toàn bộ repo tồn tại.

## Cách đọc nhãn

- **Rất sát:** repo tạo scene/frame/video bằng code hoặc chứa code scene có thể render.
- **Sát:** thư viện/template/tool giúp dựng animation bằng code; thường phải tích hợp vào project khác.
- **Liên quan:** animation tương tác/procedural chạy trong browser/game engine; thường không phải pipeline xuất video sẵn.
- **Hỗ trợ:** workflow, ví dụ học tập hoặc danh mục khám phá; không phải renderer độc lập.

Số lượng: **35** repo Remotion/video-as-code, **21** repo Manim/toán học, **25** repo creative coding 2D/3D, **19** repo procedural/3D/character animation.

## A. Video và motion graphics bằng code — Remotion ecosystem (35)

| # | Repo | Có gì và hoạt động như thế nào | Độ sát |
|---:|---|---|---|
| 1 | [remotion-dev/template-audiogram](https://github.com/remotion-dev/template-audiogram) | Template video podcast: đặt audio, waveform, lời nói/nhãn và các lớp hình vào composition React; Remotion tính từng frame rồi render clip. | Rất sát |
| 2 | [remotion-dev/template-music-visualization](https://github.com/remotion-dev/template-music-visualization) | Template biến đoạn nhạc thành video mạng xã hội; thay nhạc và thông số composition để dựng visualizer đồng bộ audio. | Rất sát |
| 3 | [remotion-dev/template-tiktok](https://github.com/remotion-dev/template-tiktok) | Dựng caption TikTok theo từng từ; Whisper.cpp tạo/transcribe lời, còn composition Remotion quyết định vị trí, màu, nhịp hiện chữ và render video. | Rất sát |
| 4 | [remotion-dev/template-code-hike](https://github.com/remotion-dev/template-code-hike) | Template hoạt họa code snippet: trình bày đoạn mã và trạng thái highlight theo thời gian để làm video giải thích code. | Rất sát |
| 5 | [remotion-dev/template-three](https://github.com/remotion-dev/template-three) | Boilerplate Remotion + React Three Fiber; dựng scene 3D bằng component React, lấy frame của Remotion làm thời gian để render video ổn định. | Rất sát |
| 6 | [remotion-dev/template-skia](https://github.com/remotion-dev/template-skia) | Starter Remotion có React Native Skia; vẽ đồ họa trên canvas Skia theo frame, hữu ích khi muốn nhiều shape/particle hơn DOM/CSS. | Sát |
| 7 | [remotion-dev/template-prompt-to-video](https://github.com/remotion-dev/template-prompt-to-video) | Pipeline prompt → câu chuyện, hình ảnh và voiceover → chuỗi scene Remotion; cần dịch vụ/credential cho phần tạo media, sau đó render bằng code. | Rất sát |
| 8 | [remotion-dev/template-prompt-to-motion-graphics-saas](https://github.com/remotion-dev/template-prompt-to-motion-graphics-saas) | Starter SaaS cho ứng dụng tạo motion graphic theo prompt; phần web nhận cấu hình, Remotion composition biến cấu hình thành scene và video. | Sát |
| 9 | [remotion-dev/github-unwrapped](https://github.com/remotion-dev/github-unwrapped) | Tạo video tổng kết năm của GitHub từ dữ liệu hoạt động lập trình; dữ liệu đầu vào được đưa vào các component/charts theo timeline Remotion. | Rất sát |
| 10 | [remotion-dev/remotion-three-gltf-example](https://github.com/remotion-dev/remotion-three-gltf-example) | Demo nạp mô hình GLTF bằng `useGLTF`, đặt vào scene 3D rồi render khung hình qua Remotion; phù hợp product shot 3D. | Rất sát |
| 11 | [remotion-dev/glb-example](https://github.com/remotion-dev/glb-example) | Ví dụ khác về hoạt họa asset `.glb` với React Three Fiber; model và camera được điều khiển trong scene, Remotion xuất thành MP4. | Rất sát |
| 12 | [remotion-dev/three-particles](https://github.com/remotion-dev/three-particles) | Chuyển demo hạt 3D sang Remotion; vị trí/hình dạng particle thay đổi theo thời gian scene, phù hợp mở đầu hoặc background video. | Rất sát |
| 13 | [remotion-dev/morph-text](https://github.com/remotion-dev/morph-text) | Demo biến đổi hình dạng chữ theo timeline Remotion; hữu ích để học morphing typography và tái sử dụng effect trong composition. | Rất sát |
| 14 | [remotion-dev/text-warping](https://github.com/remotion-dev/text-warping) | Demo uốn chữ theo path bằng API `warpPath`; mã xác định hình học và frame, phù hợp logo/title động. | Rất sát |
| 15 | [remotion-dev/anime-example](https://github.com/remotion-dev/anime-example) | Ví dụ ghép Anime.js vào composition Remotion; cho thấy cách dùng timeline/animation API khác trong môi trường render theo frame. | Sát |
| 16 | [remotion-dev/mapbox-example](https://github.com/remotion-dev/mapbox-example) | Dựng bản đồ/camera Mapbox bên trong video; điều khiển góc nhìn và trạng thái bản đồ bằng thời gian scene. | Rất sát |
| 17 | [remotion-dev/d3-example](https://github.com/remotion-dev/d3-example) | Dùng D3 để tạo đồ họa dữ liệu trong Remotion; dữ liệu và trạng thái chart được ghép thành các frame video. | Rất sát |
| 18 | [remotion-dev/remotion-gl-transitions](https://github.com/remotion-dev/remotion-gl-transitions) | Bộ ví dụ chuyển cảnh OpenGL/shader cho Remotion; shader trộn hai hình theo tiến độ transition và được render thành video. | Sát |
| 19 | [remotion-dev/light-leak-example](https://github.com/remotion-dev/light-leak-example) | Một transition light-leak tạo bằng code; xem cách dùng lớp sáng, alpha và timing để nối hai shot. | Sát |
| 20 | [remotion-dev/tone-js-example](https://github.com/remotion-dev/tone-js-example) | Demo tạo một bài nhạc nhỏ với Tone.js trong project Remotion; ghép âm thanh và hình theo cùng timeline render. | Sát |
| 21 | [calesthio/OpenMontage](https://github.com/calesthio/OpenMontage) | Hệ thống sản xuất video theo workflow agent: phân tích brief, viết kịch bản, gọi công cụ/tạo asset rồi dựng composition; gồm nhiều pipeline và skill, bản thân nó là orchestrator chứ không phải một animation engine đơn lẻ. | Hỗ trợ |
| 22 | [JonnyBurger/spring-loaded](https://github.com/JonnyBurger/spring-loaded) | Mã nguồn animation logo sự kiện Apple “Spring Loaded”; có thể đọc scene Remotion để học easing, scale và timing cho logo reveal. | Rất sát |
| 23 | [JonnyBurger/wavy-meme](https://github.com/JonnyBurger/wavy-meme) | Hiệu ứng chữ/hình gợn sóng kiểu TikTok được dựng trong Remotion; điều chỉnh tham số theo frame rồi render clip. | Rất sát |
| 24 | [JonnyBurger/ledevevent-stinger](https://github.com/JonnyBurger/ledevevent-stinger) | Stinger chuyển cảnh cho livestream/Twitch; scene ngắn được tạo bằng code và render thành asset video trong suốt/transition. | Rất sát |
| 25 | [JonnyBurger/react-summit-talk](https://github.com/JonnyBurger/react-summit-talk) | Source của một bài nói React Summit được biên tập bằng React/Remotion; cho thấy cách dựng slide, nội dung và nhịp video từ component. | Rất sát |
| 26 | [Thedurancode/locomotion-templates](https://github.com/Thedurancode/locomotion-templates) | Bộ template Remotion độc lập (data viz, text, intro, SaaS/property tour); mỗi template là composition có props, thay nội dung rồi render. | Rất sát |
| 27 | [RenderComp/free-remotion-templates](https://github.com/RenderComp/free-remotion-templates) | Kho 50 template MIT cho Remotion, mỗi mẫu là file TSX có props mặc định; mở studio để xem/chỉnh rồi render từng composition. | Rất sát |
| 28 | [zz41354899/SwiftClip](https://github.com/zz41354899/SwiftClip) | Template production-ready và workflow storyboard cho Claude Code; agent tạo/chỉnh cấu trúc shot, Remotion components lo layout, motion và render. | Sát |
| 29 | [AleBrito124356/remotion-video-templates](https://github.com/AleBrito124356/remotion-video-templates) | Sáu mẫu gồm logo intro, lower third, kinetic type, chart, caption và promo; thay props để sinh video lặp lại theo nội dung. | Rất sát |
| 30 | [calcuforge/remotion-video-template](https://github.com/calcuforge/remotion-video-template) | Template explainer/doc/product/news với 14 component; YAML khai báo từng section và dữ liệu, schema Zod đưa cấu hình vào Studio, rồi Remotion render các định dạng ngang/dọc/4K. | Rất sát |
| 31 | [nrwl/remotion-template](https://github.com/nrwl/remotion-template) | Monorepo Nx chứa composition React dùng lại giữa website/player và video mạng xã hội; Nx điều phối studio, render MP4 và task/cache. | Sát |
| 32 | [sambowenhughes/a-react-video-editor](https://github.com/sambowenhughes/a-react-video-editor) | Nền tảng editor Next.js + Remotion; timeline UI tạo/chỉnh cấu trúc clip rồi chuyển thành composition render được. Đây là editor mẫu hơn là thư viện animation. | Sát |
| 33 | [Ashref-dev/openmotion](https://github.com/Ashref-dev/openmotion) | Chuyển screenshot thành video giới thiệu có chuyển động; chọn một trong các template, cung cấp ảnh/thông tin và Remotion dựng các shot. | Rất sát |
| 34 | [Remocn/remocn](https://github.com/Remocn/remocn) | Thư viện animation, transition, background và scene cho Remotion; cài component vào project rồi điều chỉnh props/timing. | Sát |
| 35 | [av/remotion-bits](https://github.com/av/remotion-bits) | Các component làm sẵn cho chart, text reveal, transition và motion graphics; lắp vào composition thay vì bắt đầu từ hình học trống. | Sát |

## B. Manim, toán học và video giải thích (21)

| # | Repo | Có gì và hoạt động như thế nào | Độ sát |
|---:|---|---|---|
| 36 | [3b1b/manim](https://github.com/3b1b/manim) | Bản ManimGL gốc của 3Blue1Brown: Python mô tả mobject, camera và các thao tác theo thời gian; renderer dựng scene thành frame/video giải thích. Khác Manim Community dù cùng họ. | Rất sát |
| 37 | [3b1b/videos](https://github.com/3b1b/videos) | Mã scene thật dùng trong video 3Blue1Brown; xem cách chia scene, dựng hình/toán, camera và animation trên ManimGL. Đây là kho project video, không phải thư viện độc lập. | Rất sát |
| 38 | [Matheart/manim-physics](https://github.com/Matheart/manim-physics) | Plugin mô phỏng các nhánh vật lý trong Manim; định nghĩa đối tượng/đại lượng và cập nhật trạng thái rồi render thành cảnh động. | Sát |
| 39 | [ManimCommunity/manim-voiceover](https://github.com/ManimCommunity/manim-voiceover) | Plugin đồng bộ narration với scene Manim; đánh dấu mốc lời thoại để các animation chờ/đi theo âm thanh, rồi xuất video giải thích có voiceover. | Sát |
| 40 | [jeertmans/manim-slides](https://github.com/jeertmans/manim-slides) | Lớp trình chiếu cho scene Manim; chia scene thành slide/đoạn, điều khiển chuyển tiếp trực tiếp để dùng bài giảng vừa live vừa xuất video. | Sát |
| 41 | [ManimCommunity/manim_editor](https://github.com/ManimCommunity/manim_editor) | Web presenter/editor cho animation Manim; dùng scene đã render để xem và trình bày nội dung theo thứ tự. Hữu ích khâu phát lại, không thay renderer scene. | Hỗ trợ |
| 42 | [helblazer811/ManimML](https://github.com/helblazer811/ManimML) | Bộ scene minh họa neural network và khái niệm machine learning; mã Python dùng Manim Community để vẽ layer, neuron và luồng dữ liệu theo từng bước. | Rất sát |
| 43 | [TIGER-AI-Lab/TheoremExplainAgent](https://github.com/TIGER-AI-Lab/TheoremExplainAgent) | Repo nghiên cứu giải thích định lý bằng video đa phương thức; kết hợp xử lý theorem/agent với scene Manim để biến giải thích thành hoạt họa. | Sát |
| 44 | [marcelo-earth/generative-manim](https://github.com/marcelo-earth/generative-manim) | Prototype web/Streamlit nhận prompt và dùng GPT để soạn code Manim; sau đó chạy renderer tạo video 2D. Phần sinh mã phụ thuộc model/API. | Sát |
| 45 | [manim-kindergarten/manim_sandbox](https://github.com/manim-kindergarten/manim_sandbox) | Kho scene cộng đồng Manim, có code thử nghiệm/animation mẫu; chọn file/scene phù hợp rồi chạy bằng phiên bản Manim tương thích. | Hỗ trợ |
| 46 | [ManimCommunity/awesome-manim](https://github.com/ManimCommunity/awesome-manim) | Danh mục creator, nội dung, plugin và tài liệu Manim; dùng để tìm thêm scene/repo, không tạo animation khi chạy riêng. | Hỗ trợ |
| 47 | [cai-hust/manim-tutorial-CN](https://github.com/cai-hust/manim-tutorial-CN) | Hướng dẫn tiếng Trung và ví dụ scene từ cơ bản đến nâng cao; học cú pháp rồi render từng file bằng Manim. | Hỗ trợ |
| 48 | [malhotra5/Manim-Tutorial](https://github.com/malhotra5/Manim-Tutorial) | Tutorial ManimGL với các scene nhỏ; minh họa cách biến hình học/toán thành lớp đối tượng và lệnh animation. Cần để ý phiên bản Manim cũ/mới. | Hỗ trợ |
| 49 | [cigar666/my_manim_projects](https://github.com/cigar666/my_manim_projects) | Bộ project Manim cá nhân; đọc scene Python để tham khảo cách làm hiệu ứng/toán và sửa nội dung cho video mới. | Rất sát |
| 50 | [vivek3141/dl-visualization](https://github.com/vivek3141/dl-visualization) | Source animation cho series “Visualizing Deep Learning”; scene Manim mô tả mạng/thuật toán theo nhịp giải thích. | Rất sát |
| 51 | [emhayki/Animated-Mathematics](https://github.com/emhayki/Animated-Mathematics) | Tập hợp visualization hàm số, fractal, đường cong và giải thích thuật toán bằng Manim Community; README hướng dẫn render scene bằng CLI `manim`. | Rất sát |
| 52 | [initialcommit-com/git-sim](https://github.com/initialcommit-com/git-sim) | Mô phỏng và phát lại thao tác Git bằng visual layer/Manim; biến lịch sử lệnh và trạng thái repository thành video/animation giải thích. | Sát |
| 53 | [jkjkil4/JAnim](https://github.com/jkjkil4/JAnim) | Engine animation lập trình hướng Manim, có phản hồi preview gần thời gian thực; viết scene bằng API của JAnim để xem/chỉnh nhanh trước khi xuất. | Rất sát |
| 54 | [yongkyuns/noon](https://github.com/yongkyuns/noon) | Engine 2D lấy cảm hứng Manim: Python/Rust author scene → semantic scene model → compile → đánh giá frame xác định → render WGPU; hỗ trợ seek/rewind. | Rất sát |
| 55 | [AzurIce/ranim](https://github.com/AzurIce/ranim) | Engine animation Rust dùng wgpu, lấy cảm hứng từ Manim/JAnim; tác giả scene bằng Rust rồi render đồ họa GPU. Còn nhỏ hơn hệ Manim lâu đời. | Rất sát |
| 56 | [academa-labs/manimgx](https://github.com/academa-labs/manimgx) | Engine GPU dùng lõi Rust/wgpu nhưng giữ API Python kiểu Manim; preview scene trực tiếp rồi render math/3D video, nhắm giảm vòng lặp chờ render. | Rất sát |

## C. Creative coding, generative art và animation tương tác (25)

| # | Repo | Có gì và hoạt động như thế nào | Độ sát |
|---:|---|---|---|
| 57 | [DECK6/dexa-gen-lab](https://github.com/DECK6/dexa-gen-lab) | Gallery 500 sketch có code (400 p5.js, 100 Three.js, gồm shader); mỗi sketch nhận seed/context chung để chạy animation có thể tái lập và tạo thumbnail. | Rất sát |
| 58 | [rberenguel/sketches](https://github.com/rberenguel/sketches) | Sổ tay generative art p5.js: particle flow, noise, synthwave và hình học; code/seed tạo lại artwork, một số sketch có chuyển động và có thể dùng làm nền tảng loop. | Sát |
| 59 | [jkhuhnke11/generative-art-processing](https://github.com/jkhuhnke11/generative-art-processing) | Nhiều tác phẩm thuật toán bằng Processing, Python và p5.js, gồm sóng động, noise và hiệu ứng; mở/chạy sketch riêng để xem mã sinh hình. | Sát |
| 60 | [yurigo/p5.js-sketches](https://github.com/yurigo/p5.js-sketches) | Bộ bài/sketch p5.js như Bezier, particle, double pendulum, noise field và bouncing balls; mỗi thư mục là ví dụ chạy trong browser bằng vòng `draw()`. | Sát |
| 61 | [bkmashiro/creative-lab](https://github.com/bkmashiro/creative-lab) | Gallery demo HTML tự chứa: particles, fluid, fractal, waves, typographic motion và shader; mỗi file dùng Canvas/WebGL/CSS với cập nhật theo thời gian, không cần build. | Sát |
| 62 | [Mark5484/vibe-lab](https://github.com/Mark5484/vibe-lab) | Bộ sketch Python/Pygame có animated spiral, grid waves và particle motion; chạy menu hoặc từng script, cập nhật vị trí theo frame và có phím điều khiển. | Sát |
| 63 | [CWen001/art-code](https://github.com/CWen001/art-code) | Đưa ảnh tĩnh vào pipeline: trích vùng màu/cạnh/flow hint, sau đó shader GLSL advect texture có feedback và ghép lại; tạo chuyển động cục bộ bám cấu trúc ảnh. | Rất sát |
| 64 | [purzbeats/gen-art-playground](https://github.com/purzbeats/gen-art-playground) | Playground React cho sketch p5.js 2D và Three.js 3D; API animation cung cấp time/frame toàn cục để tạo chuyển động, có công cụ xem và xuất ảnh. | Sát |
| 65 | [Meskh/PerlinNoiseFlowField2D](https://github.com/Meskh/PerlinNoiseFlowField2D) | Lưới vector lấy hướng từ Perlin noise thay đổi theo thời gian; hàng nghìn particle đi theo hướng và để lại vệt trên canvas p5.js. | Rất sát |
| 66 | [leonlaser/p5js-particle-flowfield](https://github.com/leonlaser/p5js-particle-flowfield) | Demo flow-field p5.js có cấu hình kích thước ô, tốc độ field, số particle và độ dài vệt; mỗi frame lấy vector ô hiện tại để cập nhật hạt. | Rất sát |
| 67 | [ricedust/p5-inkweaver](https://github.com/ricedust/p5-inkweaver) | Tool tạo line art bằng p5.js; particle đi theo flow field và tích lũy nét để sinh bố cục kiểu mực/organic. | Sát |
| 68 | [WilsonsPage/driftfield](https://github.com/WilsonsPage/driftfield) | Thư viện/CLI và browser playground cho tranh flow-field xác định theo seed; seed giống nhau cho kết quả giống nhau, dễ làm series/biến thể. | Sát |
| 69 | [evoluteur/flow-fields](https://github.com/evoluteur/flow-fields) | Canvas tương tác cho hàng nghìn particle theo Perlin/curl noise, xoáy và sóng; người dùng chỉnh màu/zoom rồi tải ảnh, mặc định thiên về artwork hơn MP4. | Liên quan |
| 70 | [GregoryKogan/particle-flow](https://github.com/GregoryKogan/particle-flow) | Sketch p5.js cho particle flow; vector field điều khiển chuyển động và các hạt lưu vệt thành họa tiết. Repo nhỏ, phù hợp đọc thuật toán. | Sát |
| 71 | [mikeascendx/aether](https://github.com/mikeascendx/aether) | Canvas vanilla JS cho curl-noise flow field; thêm kaleidoscope/mirror, tương tác chuột và chia sẻ tham số bằng URL. Chạy realtime, không phải timeline MP4. | Liên quan |
| 72 | [Scenes3D/particles-flow-field](https://github.com/Scenes3D/particles-flow-field) | Hệ particle 3D chạy Three.js WebGPU/TSL; compute shader cập nhật hạt theo curl noise và phản ứng vị trí chuột. Mạnh về realtime visual, cần browser hỗ trợ WebGPU. | Sát |
| 73 | [chloe4ai/three-visits](https://github.com/chloe4ai/three-visits) | Animatic lịch sử vẽ từng frame bằng code trên canvas; timeline/shot code quyết định chuyển động và repo xuất file video thực. | Rất sát |
| 74 | [chloe4ai/qishan](https://github.com/chloe4ai/qishan) | Animatic chiến dịch Gia Cát Lượng: nhân vật/bối cảnh được vẽ theo thuật toán từng frame, sau đó mã hóa thành video; tham khảo tốt cho storytelling không dùng video model. | Rất sát |
| 75 | [wazabaki/isometric-spider](https://github.com/wazabaki/isometric-spider) | Nhện isometric đi theo cursor; JavaScript tính vị trí chân bằng 2-bone inverse kinematics rồi canvas vẽ mỗi frame. Demo procedural character motion nhỏ, dễ đọc. | Sát |
| 76 | [sardistic/Procedural-Pond](https://github.com/sardistic/Procedural-Pond) | Ecosystem pixel-art chạy trên browser: động vật tăng trưởng, sinh sản, săn mồi và di chuyển; agent/state simulation cập nhật liên tục rồi renderer vẽ lại. | Sát |
| 77 | [addce/generative-art](https://github.com/addce/generative-art) | Vườn số p5.js dùng L-system tạo cây; click trồng cây, quy tắc fractal tạo nhánh và growth animation tiến theo thời gian, mùa được nội suy bằng slider. | Rất sát |
| 78 | [michaelkolesidis/perlin-landscape](https://github.com/michaelkolesidis/perlin-landscape) | Cảnh địa hình được tạo từ Perlin noise trong p5.js; thay noise/seed/tham số để sinh landscape, hữu ích làm nền procedural hơn là pipeline phim hoàn chỉnh. | Liên quan |
| 79 | [johnnyawesome/ConnectedParticles](https://github.com/johnnyawesome/ConnectedParticles) | Particle effect p5.js: điểm chuyển động, tránh vật cản/chuột và nối các hạt gần nhau để hình thành mạng chuyển động. | Sát |
| 80 | [johnnyawesome/MatrixRain](https://github.com/johnnyawesome/MatrixRain) | Hiệu ứng Matrix Rain bằng JavaScript/p5.js; từng cột ký tự rơi, đổi ký tự và độ sáng theo frame. Có thể tái dùng như background loop. | Rất sát |
| 81 | [Koalhack/PerlinASCII](https://github.com/Koalhack/PerlinASCII) | Animation ASCII procedural: Perlin noise điều khiển giá trị/ký tự, tạo chuyển động liên tục thay vì clip sprite có sẵn. | Sát |

## D. Blender, procedural 3D và chuyển động nhân vật (19)

| # | Repo | Có gì và hoạt động như thế nào | Độ sát |
|---:|---|---|---|
| 82 | [JacquesLucke/animation_nodes](https://github.com/JacquesLucke/animation_nodes) | Hệ node visual scripting cho motion graphics Blender; nối node để sinh/biến đổi data, geometry và thuộc tính theo thời gian thay vì viết từng keyframe tay. | Sát |
| 83 | [cepko33/Pr3tz](https://github.com/cepko33/Pr3tz) | Script/add-on Blender tạo torus knot procedural và animation; tham số curve/đường đi tạo geometry, keyframe/Action API điều khiển thời gian, có bước bake/export scene. | Rất sát |
| 84 | [faarisaahmed/festival-star](https://github.com/faarisaahmed/festival-star) | Short 3D khoảng 5 phút được dựng bằng Python `bpy`: script tạo môi trường, ánh sáng, thời tiết, chuyển động nhân vật và camera rồi render; model được mang vào riêng. | Rất sát |
| 85 | [njanakiev/blender-scripting](https://github.com/njanakiev/blender-scripting) | Bài tập/script Blender Python từ đơn giản đến phức tạp; chạy script trong Blender/background để tạo scene và render frame, có ví dụ animation handler. | Sát |
| 86 | [gokayfem/video-to-blender](https://github.com/gokayfem/video-to-blender) | Skill cho coding agent chuyển video/ảnh/ý tưởng thành Blender Geometry/Shader/compositor node graph có thể chỉnh sửa; agent sinh node/script, người dùng kiểm tra output và render. | Hỗ trợ |
| 87 | [MeroVinggen/Godot-Spider-Procedural-Animation](https://github.com/MeroVinggen/Godot-Spider-Procedural-Animation) | Spider procedural trong Godot; script/shader điều khiển gait và bước chân, thay vì phát sprite sheet có sẵn. Dùng làm mẫu locomotion cho character. | Sát |
| 88 | [jerejoensuu/procedural-animation](https://github.com/jerejoensuu/procedural-animation) | Demo Unity về creature locomotion; inverse kinematics và vị trí địa hình quyết định nơi đặt từng chân khi nhân vật di chuyển. | Sát |
| 89 | [VivianMenard/boids](https://github.com/VivianMenard/boids) | Mô phỏng flocking 3D realtime trong Unity; mỗi agent áp dụng quy tắc tách/đồng hướng/kết đàn rồi graphics vẽ chuyển động nhóm. | Liên quan |
| 90 | [StefanPetrick/animartrix](https://github.com/StefanPetrick/animartrix) | Bộ công thức LED animation độ phân giải cao cho Teensy/ESP32; C++ tính màu/chuyển động mỗi frame và xuất giá trị ra ma trận LED, không phải MP4. | Liên quan |
| 91 | [MinaPecheux/UnityTutorials-ProceduralAnimations](https://github.com/MinaPecheux/UnityTutorials-ProceduralAnimations) | Mã và bài hướng dẫn tạo procedural animation bằng Unity Animation Rigging; rig constraints điều khiển bones/pose theo logic C#. | Sát |
| 92 | [gerlogu/ProceduralFPSAnimationsPlugin](https://github.com/gerlogu/ProceduralFPSAnimationsPlugin) | Plugin Unreal Engine 4/5 cho FPS; curves và thay đổi giá trị runtime tạo recoil/weapon motion thay vì chỉ chạy animation clip cứng. | Sát |
| 93 | [Saurav56295/creepy-crawly-kinematics](https://github.com/Saurav56295/creepy-crawly-kinematics) | Sinh sinh vật bò tương tác bằng Canvas 2D/JavaScript; IK tính chân và thân theo mục tiêu, renderer vẽ pose mới theo frame. | Rất sát |
| 94 | [rohit-sagar256/noise-wave-flow](https://github.com/rohit-sagar256/noise-wave-flow) | Canvas animation trường noise với hiệu ứng gió theo cursor; có React hook để gắn vào UI, còn cách vẽ cốt lõi framework-agnostic. | Sát |
| 95 | [maikramer/AiGameKit — Animator3D](https://github.com/maikramer/AiGameKit/tree/main/Animator3D) | Thư mục Animator3D cung cấp CLI procedural animation qua Blender Python API; script tạo/chỉnh scene/pose rồi dùng Blender dựng frame. Nằm trong repo AI/game asset lớn hơn. | Rất sát |
| 96 | [cpduncan/blender-shapekey-bakery](https://github.com/cpduncan/blender-shapekey-bakery) | Script bake geometry-node animation thành shape keys qua các frame để chuyển animation procedural của Blender sang engine/framework khác như Unity. | Sát |
| 97 | [GraphiteEditor/Graphite](https://github.com/GraphiteEditor/Graphite) | Ứng dụng đồ họa node-based với engine procedural 2D và motion graphics realtime; tạo/chỉnh đồ họa trong graph, phù hợp thử nghiệm animation tương tác hơn là render video theo timeline. | Liên quan |
| 98 | [shader-park/shader-park-core](https://github.com/shader-park/shader-park-core) | DSL JavaScript → shader realtime 2D/3D; thời gian đưa vào shader uniforms để sinh hình chuyển động trên GPU. Dùng để tạo visual/scene, cần ghép exporter riêng nếu cần MP4. | Sát |
| 99 | [mattdesl/canvas-sketch](https://github.com/mattdesl/canvas-sketch) | Framework JavaScript/browser cho generative artwork; sketch trả về draw/update callback, tool cung cấp seed/preview/render-export. Phù hợp viết animation/loop riêng. | Sát |
| 100 | [processing/processing4](https://github.com/processing/processing4) | Source Processing IDE/core; sketch Java thường có `setup()` + `draw()` chạy theo frame, tạo hình động trong cửa sổ sketch và có thể ghi/xuất frame bằng thư viện phù hợp. | Sát |

## Đọc sâu: pipeline nào thực sự diễn ra?

### 1. Video theo timeline — Remotion

Trong các repo Remotion, mã React mô tả composition và thời lượng. Khi render, Remotion chạy composition ở từng frame; component đọc số frame/thời gian để tính vị trí, opacity, scale, text, audio và các lớp hình. Ví dụ `template-audiogram`, `template-code-hike`, `gl-transitions`, `mapbox-example` khác nhau ở nội dung scene nhưng chung cơ chế frame-by-frame. Đây là hướng gần nhất nếu mục tiêu là **sinh MP4 có thể sửa bằng code**.

### 2. Toán/giải thích — Manim

Một scene Python tạo mobject (text, shape, graph, vector), rồi xếp các phép `Create`/`Transform`/camera theo thời gian. Renderer lấy trạng thái scene tại từng mốc và xuất frame/video. `3b1b/videos`, `ManimML` và `Animated-Mathematics` là ví dụ đọc được về cách scene code được tổ chức quanh một lời giải thích.

### 3. Sinh hình/animation realtime — p5.js, Canvas, Processing

Sketch giữ state (particle, vị trí, vận tốc, noise seed); vòng `draw()`/`requestAnimationFrame` cập nhật state rồi vẽ canvas mỗi frame. Các project flow-field dùng noise để tạo vector field, đưa hạt qua field và để lại trail. Chúng rất phù hợp làm interactive loop/background; mặc định nhiều repo chỉ chạy realtime hoặc xuất ảnh, chưa có pipeline MP4 hoàn chỉnh.

### 4. Hình ảnh tĩnh “biết chuyển động” — `CWen001/art-code`

Repo phân tích ảnh gốc thành masks/edges/flow hints. Shader GPU dùng các tín hiệu này để đẩy texture cục bộ qua nhiều frame rồi composite lại với ảnh nền. Ý chính là chuyển động bị ràng buộc bởi cấu trúc ảnh; không phải mô hình video diffusion.

### 5. Procedural 3D — Blender Python/Geometry Nodes

Script `bpy` hoặc node graph tạo scene, geometry, camera, đèn và keyframe. Blender tính mỗi frame rồi render. `festival-star` là ví dụ đầu-cuối dạng short; `Pr3tz` là một hiệu ứng animation có thể điều chỉnh; `blender-scripting` là tập ví dụ học cách gọi API. `video-to-blender` thêm coding agent để sinh node graph từ reference, nhưng phần review/render vẫn chạy trong Blender.

### 6. Chân tay/nhân vật procedural — Unity/Godot/Canvas

Thay vì phát clip keyframe dựng trước, code giải bài toán pose ở từng frame. IK tính chân phải đặt ở đâu dựa trên vị trí thân/địa hình; curves/noise/physics bổ sung chuyển động. `isometric-spider`, `creepy-crawly-kinematics`, `Godot-Spider-Procedural-Animation` và Unity demo là các ví dụ cụ thể.

## Repo nên mở đầu tiên theo mục tiêu

| Mục tiêu | Nên đọc trước | Vì sao |
|---|---|---|
| Tạo video marketing/short bằng React code | `template-code-hike`, `template-audiogram`, `template-tiktok`, `calcuforge/remotion-video-template` | Có composition/timeline và mẫu đầu ra; dễ thay text, data, audio rồi render. |
| Học cách dựng math explainer | `3b1b/videos`, `ManimML`, `Animated-Mathematics` | Có scene thực tế, từ khái niệm đến animation step-by-step. |
| Generative art/loop trên web | `dexa-gen-lab`, `p5.js-sketches`, `creative-lab`, `canvas-sketch` | Có sketch runnable và thuật toán noise/particle/shader. |
| Làm ảnh/scene procedural thành short 3D | `festival-star`, `Pr3tz`, `blender-scripting` | Cho thấy Python `bpy` tạo scene và chuyển động rồi Blender render. |
| Tạo animation từ prompt/reference bằng agent | `template-prompt-to-video`, `OpenMontage`, `video-to-blender`, `generative-manim` | Có bước agent/model sinh cấu hình hoặc code; cần xem dependency/credential và review output. |
| Procedural character motion | `Godot-Spider-Procedural-Animation`, `procedural-animation`, `isometric-spider`, `creepy-crawly-kinematics` | Mã tính gait/IK theo trạng thái thay vì chỉ dùng clip dựng sẵn. |

## Kết luận nghiên cứu

- Nếu đầu ra cần là **video hoàn chỉnh, timeline rõ, dễ render hàng loạt**, Remotion và Manim là hai nhánh rõ nhất trong 100 repo này.
- Nếu muốn tạo **visual loop/animation tương tác**, p5.js/Canvas/Processing và shader/Three.js linh hoạt hơn nhưng cần tự làm bước quay frame/encode nếu muốn MP4.
- Nếu muốn **hoạt cảnh 3D có scene, camera, nhân vật**, Blender Python và Geometry Nodes là nhánh đáng đọc; repo mẫu có thể đòi model/asset ngoài.
- Một phần repo là template, plugin hay tài liệu học, không phải sản phẩm tự tạo video ngay sau một lệnh. Cột “độ sát” giúp nhận ra điều đó.
- Remotion có điều kiện license theo tình huống sử dụng; kiểm tra license upstream trước khi đưa vào dự án thương mại. Các repo Rust Manim mới như Noon/Ranim/ManimGX nên xem như lựa chọn thử nghiệm cho tới khi xác nhận tương thích và chất lượng đầu ra trong project của bạn.

## Nguồn khám phá và xác minh

- [Remotion — official resource index](https://github.com/remotion-dev/remotion/blob/main/packages/docs/docs/resources.mdx): templates, examples, full projects, component libraries và tooling.
- [GitHub topic: remotion-video](https://github.com/topics/remotion-video): tìm thêm repo gắn nhãn Remotion/video.
- [GitHub topic: manim](https://github.com/topics/manim): plugin, tutorials, project scene và engine liên quan Manim.
- [GitHub topic: p5js-animation](https://github.com/topics/p5js-animation): project/sketch animation p5.js.
- [GitHub topic: procedural-animation](https://github.com/topics/procedural-animation): animation chân tay/creature và procedural motion.
- [Awesome Code Video](https://github.com/imjszhang/awesome-code-video): danh mục discovery cho template, scene, shot recipe và workflow code-video; từng repo trong danh sách trên được link về nguồn GitHub riêng.
