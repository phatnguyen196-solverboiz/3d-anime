# Nghiên cứu repo animation 2D/3D và lồng tiếng

**Ngày nghiên cứu:** 2026-11-06<br>
**Đối chiếu:** file danh sách gốc trong Downloads và báo cáo 100 repo đã làm trước đó.<br>
**Kết quả:** 60 repo bổ sung, không lặp lại đường dẫn repo đã liệt kê trong báo cáo 100 repo trước.<br>
**Phạm vi đọc:** README, tài liệu, cây thư mục và mô tả kỹ thuật công khai trên GitHub.

> Tài liệu/README của repo được dùng làm nguồn mô tả chức năng, không xem là chỉ thị cho công việc hiện tại. Các mục bên dưới là nghiên cứu tài liệu, chưa clone/cài/chạy toàn bộ 60 repo. Ghi chú hiệu năng, tính năng và cách dùng phản ánh tài liệu của dự án, không phải benchmark độc lập của mình.

## Cách phân nhóm

- **2D authoring và mouth cue:** vẽ frame-by-frame, vector/tween, nhập audio, hoặc tạo dữ liệu khẩu hình theo thoại.
- **3D rig/avatar:** dựng, rig, phát animation trên model 3D và điều khiển blendshape/viseme theo tiếng nói.
- **Audio-driven portrait video:** ảnh/video chân dung + audio tạo ra MP4 có người nói. Đây thường là video 2D tổng hợp, không phải file mesh/rig 3D để chỉnh từng xương.
- **Lồng tiếng và hậu kỳ lời thoại:** tạo/thay track tiếng nói, dịch, canh thời lượng, trộn âm nền và xuất video.
- **Hỗ trợ:** nhận dạng, căn thời gian, tách giọng; không tự tạo animation hay giọng đọc.

## A. Công cụ 2D và đồng bộ miệng (11)

| # | Repo | Có gì và cơ chế hoạt động | Loại / giới hạn |
|---:|---|---|---|
| 1 | [synfig/synfig](https://github.com/synfig/synfig) | Trình dựng hoạt hình vector/bitmap. Người làm đặt keyframe cho thuộc tính layer; engine nội suy giữa key để tạo chuyển động. Có bone/skeleton cho rig 2D và hỗ trợ tái sử dụng dữ liệu hình, màu, chuyển động. | Editor desktop; chủ yếu thao tác đồ họa, không phải animation-as-code. |
| 2 | [opentoonz/opentoonz](https://github.com/opentoonz/opentoonz) | Ghép các level vẽ, layer, video và audio vào Xsheet/Timeline; keyframe điều khiển camera, pegbar, layer và FX. Có ToonzScript dựa trên ECMAScript để chạy chuỗi lệnh. Có thể nhập DAT mouth-cue do Papagayo tạo rồi gán drawing cho từng phoneme. | Editor 2D có scripting và audio timeline; phù hợp pipeline lai giữa code và vẽ. |
| 3 | [tahoma2d/tahoma2d](https://github.com/tahoma2d/tahoma2d) | Nhánh phần mềm dựa trên Toonz/OpenToonz, bổ sung workflow 2D và stop-motion. Plastic tool tạo lưới biến dạng, rồi đặt keyframe cho các điểm để làm cutout/deformation. | Editor desktop; hợp rig/cutout và stop-motion, không tự tổng hợp giọng. |
| 4 | [pencil2d/pencil](https://github.com/pencil2d/pencil) | Vẽ từng frame bằng bitmap hoặc vector, xếp frame trên timeline/layer rồi preview chuỗi hình. Tập trung vào hoạt hình vẽ tay và thử chuyển động, không có pipeline TTS hoặc tự sinh cảnh. | Editor 2D frame-by-frame; dễ thử nghiệm nhưng phải tự dựng từng frame. |
| 5 | [KDE/krita](https://github.com/KDE/krita) | Tạo raster animation bằng animated layer và timeline; mỗi drawing được giữ ở frame tương ứng. Khi xuất, Krita render ảnh tuần tự rồi gọi FFmpeg để đóng thành GIF/MP4/MKV. Tài liệu lưu ý Krita không phải công cụ dựng audio/video nhiều track. | Vẽ frame-by-frame; nên ghép voiceover ở editor/video pipeline khác. |
| 6 | [KDE/glaxnimate](https://github.com/KDE/glaxnimate) | Dựng shape vector và keyframe trên timeline, chỉnh đường cong/easing rồi xuất SVG animation, Lottie hoặc video. Có Python scripting/plugin và khả năng render frame/headless. | Hợp motion graphic vector. Repo GitHub này ghi upstream chính chuyển sang GitLab. |
| 7 | [morevnaproject-org/papagayo-ng](https://github.com/morevnaproject-org/papagayo-ng) | Nhập bản ghi thoại và script, đặt từ/phoneme lên waveform rồi chỉnh thời điểm khẩu hình. Xuất cue tương thích OpenToonz để mỗi mouth shape xuất hiện đúng frame. | Công cụ căn thoại/khẩu hình; không tạo TTS hay hình nhân vật. |
| 8 | [DanielSWolf/rhubarb-lip-sync](https://github.com/DanielSWolf/rhubarb-lip-sync) | CLI đọc WAV/Ogg, nhận dạng lời hoặc phoneme rồi sinh danh sách mouth-shape cùng timestamp ở TSV/XML/JSON/DAT. Có tích hợp với OpenToonz, Moho, Spine và After Effects. | Cách tự động tạo cue cho nhân vật 2D; kết quả vẫn cần bộ hình miệng và mapping. |
| 9 | [OpenAnimationLibrary/opentoonz-headless](https://github.com/OpenAnimationLibrary/opentoonz-headless) | Bản OpenToonz chạy không GUI, phơi chức năng vẽ qua JSON-RPC trên stdin/stdout để chương trình ngoài gọi. Có thể dùng làm cầu nối agent/script → hình vẽ/render. Tài liệu nêu sound column trên Xsheet chưa hỗ trợ headless. | Fork thử nghiệm, mức độ adoption thấp; kiểm tra API và trạng thái trước khi chọn làm nền tảng. |
| 10 | [Rai220/talking-circle](https://github.com/Rai220/talking-circle) | Lấy bốn ảnh trạng thái miệng/mắt và audio. Với mỗi frame, tính RMS theo cửa sổ ngắn để chọn miệng đóng/hơi mở/mở rộng; thêm blink theo chu kỳ rồi dựng video vòng tròn. Có bước gọi TTS ngoài để tạo thoại từ text. | Cách 2D rất nhẹ và dễ hiểu; sync theo âm lượng nên không chính xác từng âm vị. |
| 11 | [HH1st/hoho-avatar](https://github.com/HH1st/hoho-avatar) | Đọc PCM từ mic/file/TTS, đo tín hiệu rồi điều khiển năm mouth states và blink; cùng engine có renderer Canvas 2D và adapter Three.js/Live2D. Nhận audio trực tiếp hoặc dùng KittenTTS trong trình duyệt. | SDK/demo realtime; không phải renderer video tổng quát, không phân tích phoneme. |

## B. Rig, avatar và animation 3D có tiếng nói (16)

| # | Repo | Có gì và cơ chế hoạt động | Loại / giới hạn |
|---:|---|---|---|
| 12 | [ekza-space/ekza-studio](https://github.com/ekza-space/ekza-studio) | Studio 3D chạy trên trình duyệt cho GLB/VRM: tạo rig, điều khiển xương/IK, đặt key, chỉnh Dope Sheet và Graph Editor, rồi bake/export VRMA hoặc animation-only GLB. | Có đường làm animation 3D thật trên model; hiện repo tự ghi trạng thái alpha, chưa phải voiceover/TTS. |
| 13 | [vrm-c/UniVRM](https://github.com/vrm-c/UniVRM) | Bộ Unity đọc/ghi VRM 0.x/1.0, glTF/GLB và VRMA ở editor lẫn runtime. App Unity có thể load avatar, phát clip/VRMA và nối script của mình vào expression/blendshape. | Nền tảng tích hợp avatar/animation; bản thân không dựng thoại hay TTS. |
| 14 | [met4citizen/TalkingHead](https://github.com/met4citizen/TalkingHead) | JavaScript/Three.js nạp avatar GLB và animation FBX. speakText tạo audio bằng TTS cấu hình sẵn, dùng word timing/viseme để animate miệng; speakAudio nhận audio ngoài và dữ liệu viseme/blendshape. Có callback subtitle. | Một trong các đường gần end-to-end nhất cho avatar 3D nói; cần model có rig và blendshape phù hợp. |
| 15 | [met4citizen/HeadTTS](https://github.com/met4citizen/HeadTTS) | TTS neural dựa trên Kokoro, chạy WebGPU/WASM trong browser hoặc Node. Ngoài audio, trả timestamp từ và viseme để avatar có thể animate khớp lời. | Lớp tạo voice + dữ liệu đồng bộ; cần renderer avatar khác. |
| 16 | [vlapky/three-vrm-lip-sync](https://github.com/vlapky/three-vrm-lip-sync) | Nhận audio file, AudioBuffer, mic hoặc MediaStream; AudioWorklet tính đặc trưng MFCC và phân loại âm vowel, sau đó đặt năm VRM expressions aa/ih/ou/ee/oh. Không cần ASR. | Runtime nhẹ cho avatar VRM web; sync theo phân loại audio, không sinh speech. |
| 17 | [s-soltys/LipSync](https://github.com/s-soltys/LipSync) | TypeScript/Three.js chia audio thành cửa sổ ngắn, trích hệ số LPC rồi neural net phân lớp thành viseme; các giá trị viseme lái morph target trên model GLB. | Demo/app nghiên cứu 3D face lipsync; không tạo giọng nói. |
| 18 | [hecomi/uLipSync](https://github.com/hecomi/uLipSync) | Unity dùng MFCC và profile phoneme đã hiệu chỉnh theo giọng/model. Chạy realtime hoặc bake trước; baked data đưa vào Unity Timeline hay chuyển thành AnimationClip/blendshape. Có VRM và texture switching cho kiểu 2D. | Tốt cho pipeline 3D/Unity có kiểm soát và render lặp lại; cần hiệu chỉnh profile. |
| 19 | [NVIDIA/Audio2Face-3D-Samples](https://github.com/NVIDIA/Audio2Face-3D-Samples) | Sample client/service chuyển audio thành ARKit facial blendshapes để phát trên avatar. Quick-start triển khai container Audio2Face-3D NIM, client stream audio rồi nhận dữ liệu weight theo frame. | Phụ thuộc NVIDIA NIM/container, GPU và NGC key; không phải TTS engine độc lập. |
| 20 | [NVIDIA/Audio2Face-3D-SDK](https://github.com/NVIDIA/Audio2Face-3D-SDK) | SDK C++ mẫu cho pipeline streaming: audio accumulator nhận các chunk PCM, executor xử lý Audio2Face/Audio2Emotion và trả biểu cảm/face curves theo thời gian. | Tích hợp cấp ứng dụng 3D; cần kiểm tra SDK/model access và môi trường NVIDIA. |
| 21 | [nirholas/voice](https://github.com/nirholas/voice) | Client JavaScript nối ba endpoint: ASR audio→text, TTS text→audio và Audio2Face audio→ARKit blendshape frames. Có thể chuyển frame vào avatar GLB theo current audio time. | Lớp API cho nền tảng three.ws; phụ thuộc dịch vụ/credential cấu hình, không phải xử lý offline hoàn chỉnh. |
| 22 | [sl33pyC01E/neural-avatar-pipeline](https://github.com/sl33pyC01E/neural-avatar-pipeline) | Pipeline Windows ghép PocketTTS, nhận diện emotion, tạo facial motion và body motion cho VRM trên một timeline, rồi xuất MP4. Track mặt/thân có thể phát cùng audio trong một project. | Nghiên cứu phù hợp để xem cách ghép các model; model/checkpoint lớn không được đóng gói sẵn trong repo. |
| 23 | [BsMediaVN/studio-agent](https://github.com/BsMediaVN/studio-agent) | Studio self-hosted ưu tiên tiếng Việt: script/prompt → TTS nhiều nhân vật dựa trên VieNeu → video. Mode hoạt họa tạo character motion/caption qua HyperFrames; mode chân dung dùng SadTalker để lip-sync. | Ví dụ gần workflow thoại tiếng Việt → animation; TTS và dựng video được tích hợp, nhưng hai mode dùng backend khác nhau. |
| 24 | [xanguera/aicompanion](https://github.com/xanguera/aicompanion) | Pipeline voice tương tác dùng Whisper local nhận mic, Kokoro TTS phát từng câu và TalkingHead/Three.js animate avatar theo audio/timestamp. Câu tiếp theo được tổng hợp song song lúc câu trước đang phát. | Mẫu kiến trúc realtime; LLM có thể gọi từ xa, đây là app hội thoại chứ không phải editor xuất animation MP4. |
| 25 | [anjaydo/vroid-ai-companion](https://github.com/anjaydo/vroid-ai-companion) | Next.js/Three.js load VRM, backend sinh trả lời và audio bằng Gemini TTS; frontend phân tích audio theo frame để điều khiển mouth blendshape, đồng thời retarget clip Mixamo lên VRM. | Mẫu đầy đủ có TTS, lip-sync và body motion; cần API/backend, thiên về avatar chat realtime. |
| 26 | [sungbongju/VRM-Avatar-Bot](https://github.com/sungbongju/VRM-Avatar-Bot) | Starter React/Three.js cho VRM: streaming chat, sentence-level TTS queue, auto lip-sync kiểu RMS→aa, blink/idle/breath và chế độ mic/voice/text. | Starter kit để học cách nối các thành phần; lip-sync cơ bản, không phải phoneme alignment hay video batch renderer. |
| 27 | [mfais473/Virtual-Interactive-Assistant-3D](https://github.com/mfais473/Virtual-Interactive-Assistant-3D) | Electron + Three.js hiển thị VRM desktop avatar; Gemini xử lý voice conversation/TTS, Web Audio đo âm lượng để mở miệng; tag cảm xúc/gesture điều khiển expression và clip VRMA. | Demo tương tác trên desktop; không phù hợp làm renderer video không người dùng. |

## C. Audio-driven portrait và visual dubbing (16)

Các repo nhóm này nhận audio để làm chân dung/video có miệng chuyển động. Kết quả thường là video 2D đã tổng hợp; không tạo rig 3D có thể chỉnh xương như Ekza/UniVRM.

| # | Repo | Có gì và cơ chế hoạt động | Loại / giới hạn |
|---:|---|---|---|
| 28 | [Rudrabha/Wav2Lip](https://github.com/Rudrabha/Wav2Lip) | Nhận video/ảnh mặt và audio mới, crop vùng mặt theo frame rồi mô hình sinh lại phần miệng để khớp lời. CLI xuất MP4; không tự viết hoặc tổng hợp câu thoại. | Cổ điển và có nhiều integration; code/model weights có điều khoản riêng, cần xem kỹ trước khi dùng thương mại. |
| 29 | [OpenTalker/SadTalker](https://github.com/OpenTalker/SadTalker) | Ảnh chân dung + driving audio → ước lượng motion coefficients/pose → sinh chuyển động đầu/mặt và video. Có CLI/WebUI, full-image/still mode và enhancer; TTS phải tạo audio ở bước riêng. | Làm một ảnh thành talking-head MP4; không trả về mesh/rig 3D để tiếp tục keyframe. |
| 30 | [TMElyralab/MuseTalk](https://github.com/TMElyralab/MuseTalk) | Nhận ảnh/video mặt và audio; mã hóa audio bằng Whisper-tiny, mã hóa vùng mặt vào latent, rồi UNet inpaint phần mặt theo audio để xuất frame. Tài liệu nêu chạy 30fps+ trên V100 cho cấu hình của họ. | Thích hợp lip-sync từ audio có sẵn; cần model weights/GPU và xử lý crop mặt cẩn thận. |
| 31 | [antgroup/echomimic](https://github.com/antgroup/echomimic) | Ảnh portrait + audio tạo animation; có thể thêm selected landmarks/pose để kiểm soát. Dùng audio embedding và diffusion video pipeline, cho phép tạo mặt/đầu chuyển động kèm khẩu hình. | Mô hình nghiên cứu nặng; hướng dẫn kiểm thử A100/4090/V100, không phải editor timeline nhẹ. |
| 32 | [antgroup/echomimic_v2](https://github.com/antgroup/echomimic_v2) | Mở rộng từ talking-head sang semi-body: ảnh + audio + tùy chọn pose → video nửa người; model có pose encoder, motion module và audio processor. | Khung hình có thể chứa thân và gesture nhiều hơn bản V1; vẫn là video tổng hợp, yêu cầu GPU/weights đáng kể. |
| 33 | [Zejun-Yang/AniPortrait](https://github.com/Zejun-Yang/AniPortrait) | Từ chân dung và audio, audio2pose/audio2mesh tạo chuyển động mặt/pose, sau đó pipeline diffusion sinh video. Hỗ trợ cả face reenactment từ video điều khiển. | Mô hình audio-to-portrait có code và weight; cần cài CUDA và tải nhiều checkpoint. |
| 34 | [fudan-generative-vision/hallo](https://github.com/fudan-generative-vision/hallo) | Ảnh vuông + audio WAV làm đầu vào; Wav2Vec/Whisper audio feature và motion module điều khiển latent video diffusion để tạo portrait animation. README bản này yêu cầu audio tiếng Anh và GPU mạnh. | Phù hợp thử ảnh + voiceover thành talking-head; không tạo giọng và chưa phải mesh 3D. |
| 35 | [fudan-generative-vision/hallo2](https://github.com/fudan-generative-vision/hallo2) | Nâng cấp Hallo cho video dài/độ phân giải cao: inference_long đọc ảnh + audio, sinh theo cấu hình dài rồi có bước super-resolution. Repo minh họa clip dài nhiều phút đến khoảng một giờ. | Dùng khi cần bài giảng/narration dài; yêu cầu A100 trong hướng dẫn, phần upscale có điều khoản phụ thuộc CodeFormer. |
| 36 | [OpenTalker/video-retalking](https://github.com/OpenTalker/video-retalking) | Nhận video talking-head và audio khác; lần lượt chuẩn hóa expression, chạy audio lip-sync, rồi face enhancement. Có tham số chọn expression, inference script và MP4 đầu ra. | Hợp lồng tiếng lại một video người đang nói; không sinh TTS, có giới hạn với góc mặt cực đoan. |
| 37 | [KlingAIResearch/LivePortrait](https://github.com/KlingAIResearch/LivePortrait) | Ảnh/video nguồn + video chuyển động → trích motion, retarget/stitch lên portrait và tạo video. Có crop tự động, motion template và video-to-video. | Animation portrait dựa trên video lái, không tự đồng bộ theo lời thoại; có thể phối với Wav2Lip/MuseTalk. |
| 38 | [TaoLiveAIGC/TBDub](https://github.com/TaoLiveAIGC/TBDub) | Visual dubbing cho video có sẵn: detect/crop/align mặt 512×512, encode latent chuyển động, dùng audio mới sinh latent đã đồng bộ rồi ghép lại vào video gốc. Tài liệu nhấn mạnh giữ appearance, motion và background. | Code Apache-2.0 theo README; checkpoint lớn và cần GPU mạnh, TTS/translation phải làm trước. |
| 39 | [fudan-generative-vision/Hallo-Live](https://github.com/fudan-generative-vision/Hallo-Live) | Từ text prompt sinh đồng thời luồng audio và video avatar bằng dual-stream DiT có attention liên-modal và KV cache, cho phản hồi streaming. Ví dụ gồm người thật và nhân vật anime. | Khác với audio-driven lip-sync: issue của maintainer ghi hiện chỉ hỗ trợ text-to-audio-video, chưa nhận ảnh/audio tùy ý; demo báo cáo 2×H200. |
| 40 | [neosapience/TA2.0](https://github.com/neosapience/TA2.0) | Ảnh tham chiếu + giọng nói + prompt tùy chọn → avatar video biểu cảm. Inference script nạp model/config, chuẩn hóa ảnh và đóng audio vào MP4; release dùng safetensors và manifest kiểm tra hash. | Repo có inference runtime; yêu cầu CUDA/model weights lớn. Dùng ảnh/giọng có quyền và xem riêng điều khoản model/dataset. |
| 41 | [SkyworkAI/SkyReels-A1](https://github.com/SkyworkAI/SkyReels-A1) | Framework video diffusion cho portrait animation; bản audio-driven nhận reference image và driving audio để animate mặt/đầu, ngoài ra có motion/video modes trong họ SkyReels. | Nghiên cứu, cần tải checkpoints và GPU; phân biệt pipeline audio portrait với framework text-to-video của SkyReels khác. |
| 42 | [chanjing-ai/Chanjing-Avatar](https://github.com/chanjing-ai/Chanjing-Avatar) | Chanjing-Avatar 14B nhận ảnh tham chiếu, audio và prompt để tạo talking-avatar 720p. Repo công bố thêm nhánh V2V 5B/1.3B để dùng video nguồn và giữ motion khi tái tạo mặt. | Code tập trung vào model family lớn; dùng inference locally cần GPU/RAM phù hợp, không phải app TTS nhẹ. |
| 43 | [BQ-Wang0511/PC-Talk](https://github.com/BQ-Wang0511/PC-Talk) | Điều khiển talking-face theo style nói, mức khẩu hình và emotion; LAC tạo articulation/style signal, EMC điều khiển cảm xúc, LivePortrait dựng portrait video. | Hữu ích khi cần điều khiển biểu cảm cụ thể thay vì chỉ mở miệng; nhận audio có sẵn, không làm voice cloning. |

## D. Lồng tiếng, voiceover và dựng track lời thoại (13)

| # | Repo | Có gì và cơ chế hoạt động | Loại / giới hạn |
|---:|---|---|---|
| 44 | [krillinai/OpenCreator](https://github.com/krillinai/OpenCreator) | Ứng dụng workflow cho dịch video, sinh TTS từ subtitle, render ngang/dọc và có quy trình stick-figure animation gồm script, narration, timing, storyboard, captions và video. Các model giọng/hình/video được chọn từ provider cấu hình. | Có thể dùng làm app/workflow tổng hợp; không mặc định bundle mô hình local hoặc TTS miễn phí. |
| 45 | [langswap-app/langswap](https://github.com/langswap-app/langswap) | Docker pipeline local: ASR → dịch → voice-cloned TTS → fit audio vào khoảng thời gian → mux video và SRT. Hỗ trợ thuật toán speedup/stretch và nhiều backend TTS. | Hợp local GPU và dubbing video có sẵn; không tự làm animation/scene 2D/3D. |
| 46 | [estebanstifli/OpenDub](https://github.com/estebanstifli/OpenDub) | Desktop app tách thoại khỏi nhạc/SFX, nhận dạng và diarize speaker, căn từ, dịch, sinh từng đoạn giọng có tham chiếu emotion/voice, cho sửa/preview từng line rồi xuất MP4/audio/SRT. | Mạnh về kiểm soát từng đoạn và mix; phải tải nhiều model, phần mềm vẫn đang phát triển. |
| 47 | [stronghamjji/PersoDub](https://github.com/stronghamjji/PersoDub) | App dubbing local: nhận video, transcription, translation, voice cloning, subtitle và xuất social video. Có editor sửa từng câu, chỉ regenerate line đã đổi và chủ động fit speech vào timing. | Ưu tiên xử lý local; một số mode/API dùng dịch vụ ngoài, cần chọn engine và điều khoản model rõ ràng. |
| 48 | [timoncool/dub-studio](https://github.com/timoncool/dub-studio) | Windows app Rust/C++/CUDA cho dubbing/voice clone/subtitle và OCR chữ trên video; có tách vocal, diarization, dịch, TTS, editor và render. Cho phép chọn track gốc/dub/voiceover và burn-in captions. | Repo ghi workflow local cần NVIDIA là cấu hình được kiểm thử; cloud provider là tùy chọn. |
| 49 | [himanishpuri/PolyDub](https://github.com/himanishpuri/PolyDub) | Python pipeline video → Whisper transcript → Argos Translate → XTTS voice cloning → fit/mix → video/subtitle. Có cache theo audio fingerprint; tùy chọn Demucs tách nhạc nền để giữ soundtrack. | README roadmap còn nêu multi-speaker diarization/lip-sync là phần sau; cần kiểm tra giới hạn này trước khi chọn. |
| 50 | [dalsoop/voiceclonedub](https://github.com/dalsoop/voiceclonedub) | Nhắm lồng tiếng video đúng khoảng thời gian gốc: transcription/translation, clone voice, đặt line theo mốc, kiểm tra drift/overlap/pacing và lưu versioned output. | Tập trung độ khớp timeline và tái lập; không tạo hình/animation nhân vật. |
| 51 | [akshinmrv/Voxa](https://github.com/akshinmrv/Voxa) | CLI Python nhận file/video, nhận dạng, tùy chọn chia speaker, dịch và tạo track speech bằng engine được chọn; sau đó mux audio với video. Có đường chạy local/offline và một số backend online. | Hữu ích để script/batch dubbing; không sinh lip movement và voice clone phụ thuộc backend. |
| 52 | [jsfan3/autodub-local](https://github.com/jsfan3/autodub-local) | Dành cho webinar, talk, interview dài: trích mono audio, ASR, diarization, dịch, synthesize từng đoạn và mux thành MP4. Tập trung giữ duration/pause gần source thay vì mouth-level lip-sync. | Lựa chọn voiceover/translation cho video dài; repo nêu perfect lip-sync không phải mục tiêu. |
| 53 | [cezarc1/podcast_dub](https://github.com/cezarc1/podcast_dub) | Pipeline speaker-aware: extract audio → Qwen ASR/forced alignment → diarize → lấy voice reference → dịch → Qwen3-TTS clone → căn/mix audio → MP4. Có chống drift và kiểm tra output. | Phù hợp hội thoại nhiều người; phụ thuộc model lớn và cấu hình local inference. |
| 54 | [salihavcioglu/sesly](https://github.com/salihavcioglu/sesly) | Local voice studio vừa clone/design voice, vừa tạo audiobook theo chapter/character và dubbing theo speaker; script được tách thành đoạn để sửa, cast voice và render/mix. | Bao phủ narration dài và translation; engine/model có license khác nhau, README phân loại rõ một số non-commercial model. |
| 55 | [estebanstifli/LocalText2Voice](https://github.com/estebanstifli/LocalText2Voice) | Script/book → TTS theo segment → review/edit và audio mix → storyboard hình/clip → timeline → MP4 dài. Có offline engines lẫn cloud APIs tùy lựa chọn. | Nối trực tiếp voiceover với storyboard/video; kiểm tra cấu hình provider nếu cần thuần local. |
| 56 | [zast57/ZastTranslate](https://github.com/zast57/ZastTranslate) | Video/local audio/URL → WhisperX word alignment → dịch/voice clone → subtitle và video. Có batch tạo Shorts 9:16 với karaoke captions, nhiều ngôn ngữ và metadata. | Tác giả ghi đã thử trên Windows; cần xác nhận phần cứng/model/license và độ ổn định trên máy của mình. |

## E. Thành phần hỗ trợ voiceover (4)

| # | Repo | Có gì và cơ chế hoạt động | Dùng ở bước nào |
|---:|---|---|---|
| 57 | [m-bain/whisperX](https://github.com/m-bain/whisperX) | ASR batched, forced alignment bằng wav2vec2 và tùy chọn pyannote diarization; xuất mốc từng từ và speaker label. | Tạo transcript/mốc từ để gán subtitle, chia lời thoại và fit TTS vào timeline. Không tự dịch/TTS. |
| 58 | [pyannote/pyannote-audio](https://github.com/pyannote/pyannote-audio) | Bộ model phát hiện speech, đổi lượt nói, overlap, voice activity và speaker embedding; pipeline trả start/end theo speaker. | Chia vai cho voiceover hội thoại nhiều nhân vật; model community yêu cầu chấp nhận điều khoản/token Hugging Face. |
| 59 | [facebookresearch/demucs](https://github.com/facebookresearch/demucs) | Tách stem vocal khỏi accompaniment bằng Hybrid Transformer Demucs, để thay lời thoại mà giữ nhạc nền/SFX. | Tiền xử lý trước dubbing; README của repo gốc nói dự án không còn được maintain, có chỉ tới fork duy trì. |
| 60 | [jianfch/stable-ts](https://github.com/jianfch/stable-ts) | Bản mở rộng Whisper sửa mốc từ bằng VAD/silence suppression, regroup theo dấu câu và có bước refine timestamp. | Có ích khi cần SRT/word timing; maintainer ghi phát triển repo đã tạm dừng vô thời hạn, xem như lựa chọn cũ/đối chiếu. |

## Luồng ghép phù hợp theo mục tiêu

### 1. Hoạt hình 2D có lời thoại

**Tạo/thu TTS hoặc voice actor → WhisperX/Rhubarb/Papagayo tạo cue → OpenToonz/Tahoma2D đặt frame miệng theo cue → ghép track voiceover/nhạc và render.**

- Muốn tự động hóa mạnh: Rhubarb tạo DAT/JSON cue; OpenToonz có thể script tác vụ lặp lại.
- Muốn sửa tay cho biểu cảm tốt: Papagayo-NG hoặc timeline của OpenToonz.
- Muốn làm bằng code end-to-end: dùng renderer video/code trong danh sách trước, rồi dùng audio timestamp/viseme làm animation input.

### 2. Avatar 3D có giọng nói đồng bộ

**Script → TTS có word timing/viseme → TalkingHead hoặc VRM renderer phát audio → blendshape/viseme chạy theo audio clock → render/capture video.**

- Web nhanh: TalkingHead + HeadTTS + GLB rigged có các blendshape cần thiết.
- Unity: UniVRM để load model, uLipSync để phân tích/bake mouth animation.
- Cần mặt chi tiết từ audio: Audio2Face-3D SDK/Samples tạo blendshape track, sau đó apply vào rig.
- Ekza Studio thiên về keyframe/rig thủ công; dùng để soạn motion clip chứ không tự tạo voiceover.

### 3. Một ảnh/video chân dung thành talking video

**Tạo voiceover trước → SadTalker/Hallo/MuseTalk/EchoMimic nhận ảnh và audio → xuất MP4 → ghép captions/nhạc.**

- Ảnh + audio có sẵn: MuseTalk, Hallo, SadTalker, EchoMimic.
- Video có sẵn, thay giọng: VideoReTalking hoặc TBDub.
- Cần nửa người/gesture: EchoMimicV2, AniPortrait, Chanjing-Avatar.
- Các repo này tạo frame/video; thường không cho xuất một rig 3D chỉnh được.

### 4. Dịch/lồng tiếng video dài

**Tách vocal → ASR + diarization → dịch từng đoạn → tạo voice per-speaker → fit vào timeline → giữ/ghép nền → xuất MP4 + subtitle.**

- Muốn sửa từng câu trên UI: OpenDub, PersoDub, Dub Studio.
- Muốn pipeline local bằng code/CLI: Langswap, PolyDub, Voxa, podcast_dub.
- Muốn script/narration rồi thêm storyboard thành video: LocalText2Voice hoặc OpenCreator.
- Với video dài, WhisperX/pyannote giúp phân đoạn speaker/timing; Demucs giúp giữ nhạc khi thay thoại.

## Nhận định thực dụng

1. **Combo 2D voiceover dễ kiểm soát nhất:** Papagayo-NG hoặc Rhubarb + OpenToonz/Tahoma2D. Dễ chỉnh cue và giữ nhân vật ổn định; đổi lại cần có bộ mouth shape.
2. **Combo 3D realtime linh hoạt nhất:** TalkingHead + HeadTTS + avatar GLB/VRM rigged. Có audio, subtitle timing và viseme trong một stack web.
3. **Combo 3D Unity có thể bake:** UniVRM + uLipSync. Có thể đưa khẩu hình thành AnimationClip trên timeline và phối với body animation.
4. **Tạo video chân dung nói từ audio có sẵn:** MuseTalk hoặc VideoReTalking cho lip-sync; SadTalker/Hallo/EchoMimic khi bắt đầu từ ảnh tĩnh và muốn head motion rõ hơn. Đây là tạo video 2D, không phải asset 3D.
5. **Tiếng Việt + nhân vật hoạt họa:** BsMediaVN/studio-agent là repo nên đọc sâu trước vì đã ghép multi-character TTS tiếng Việt với hai kiểu video: motion graphics và talking-head.
6. **Dịch voiceover video dài:** OpenDub/PersoDub nếu cần chỉnh line và mix; podcast_dub/autodub-local nếu muốn xem pipeline code và timeline placement.
7. **Repo hỗ trợ không đồng nghĩa có cùng license:** code, model weights, voice clone, sample avatar và dataset có thể có điều khoản khác nhau. README của Hallo2, TA2.0, Wav2Lip và các tool dubbing cần được kiểm tra riêng trước khi dùng trong sản phẩm.

## Nguồn tài liệu kỹ thuật đã dùng

- [OpenToonz ToonzScript](https://github.com/opentoonz/opentoonz_docs/blob/master/source/toonzscript.rst) và [Xsheet/Timeline](https://github.com/opentoonz/opentoonz_docs/blob/master/source/working_in_xsheet.rst).
- [Rhubarb Lip Sync](https://github.com/DanielSWolf/rhubarb-lip-sync) và [Papagayo-NG](https://github.com/morevnaproject-org/papagayo-ng) về audio → mouth cue cho 2D.
- [TalkingHead](https://github.com/met4citizen/TalkingHead), [HeadTTS](https://github.com/met4citizen/HeadTTS), [uLipSync](https://github.com/hecomi/uLipSync) và [Audio2Face-3D-Samples](https://github.com/NVIDIA/Audio2Face-3D-Samples) về TTS/viseme/blendshape cho avatar 3D.
- [MuseTalk](https://github.com/TMElyralab/MuseTalk), [Hallo2](https://github.com/fudan-generative-vision/hallo2), [TBDub](https://github.com/TaoLiveAIGC/TBDub) và [TA2.0](https://github.com/neosapience/TA2.0) về audio-driven portrait/lip-sync.
- [WhisperX](https://github.com/m-bain/whisperX), [pyannote-audio](https://github.com/pyannote/pyannote-audio) và [Demucs](https://github.com/facebookresearch/demucs) về căn lời, chia speaker và tách nền âm thanh.
