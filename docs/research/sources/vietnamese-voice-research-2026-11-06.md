# Nghiên cứu bổ sung: giọng nói tiếng Việt cho AnimeFlow

Ngày kiểm tra: 06/11/2026. Nguồn là README/tài liệu chính thức của từng dự án; các số liệu hiệu năng là công bố của tác giả, chưa được benchmark trên máy này. Các repo dưới đây đang ở trạng thái nghiên cứu, chưa được cài, chạy hoặc tích hợp vào AnimeFlow.

| # | Repo | Có gì và luồng hoạt động | Vị trí dự kiến trong AnimeFlow |
|---:|---|---|---|
| 1 | [pnnbao97/VieNeu-TTS](https://github.com/pnnbao97/VieNeu-TTS) | SDK nhận văn bản tiếng Việt, chọn giọng có sẵn hoặc tham chiếu giọng, sinh waveform. README mô tả v3 Turbo 48 kHz qua ONNX CPU hoặc backend GPU; phiên bản/model khác có đặc tính khác. | Ứng viên TTS tiếng Việt đầu tiên: VoiceLine → audio WAV → alignment → lip-sync. Kiểm tra model/version và quyền giọng trước khi bật. |
| 2 | [zeroweight-ai/ZeroTTS](https://github.com/zeroweight-ai/ZeroTTS) | TTS tiếng Việt dùng ONNX, có luồng streaming; tài liệu mô tả reference voice/latents và giọng mẫu. Cần đọc kỹ quá trình tạo voice latents và quyền truy cập model trước khi hứa chạy hoàn toàn offline. | Ứng viên TTS CPU để so sánh khả năng bắt đầu nhanh, chất lượng và quy trình voice. |
| 3 | [dogenthq/KorvaTTS](https://github.com/dogenthq/KorvaTTS) | TTS ưu tiên tiếng Việt và câu pha tiếng Anh, dùng ONNX Runtime và các giọng có sẵn theo README. | Ứng viên TTS dự phòng cho giọng preset và code-switching; model license được công bố riêng với code. |
| 4 | [thinhlpg/vixtts-demo](https://github.com/thinhlpg/vixtts-demo) | Demo voice cloning tiếng Việt dựa trên XTTS fine-tune; cần runtime/dependencies và weights tương ứng. | Tham khảo tích hợp engine cloning; không coi demo là adapter sẵn sàng hoặc suy ra quyền weights từ license code. |
| 5 | [VinAIResearch/PhoWhisper](https://github.com/VinAIResearch/PhoWhisper) | Nhận dạng tiếng nói tiếng Việt thành văn bản bằng các checkpoint PhoWhisper. Đây là ASR, không tổng hợp giọng nói. | Kiểm tra transcript cho thoại thu sẵn; cần bước alignment riêng để có timestamp/cue phù hợp lip-sync. |
| 6 | [BsMediaVN/studio-agent](https://github.com/BsMediaVN/studio-agent) | Studio self-hosted ghép script/prompt, TTS nhiều nhân vật tiếng Việt dựa trên VieNeu và các pipeline video/talking head. | Tham khảo orchestration nhiều speaker và luồng từ thoại đến hình, không mặc định gộp toàn bộ ứng dụng. |
| 7 | [vuhai2002/vietnamese-tts-studio](https://github.com/vuhai2002/vietnamese-tts-studio) | Ứng dụng TTS/voice cloning local có CLI/UI, README mô tả chạy trên NVIDIA GPU với các model mà dự án hỗ trợ. | Tham khảo UX voice và thiết lập GPU; license báo NOASSERTION qua GitHub API nên cần kiểm tra trực tiếp trước khi dùng lại. |

## Luồng tích hợp đề xuất

1. Người dùng chọn text, language `vi-VN`, character và voice preset; hoặc đưa file thu âm có quyền sử dụng.
2. TTS adapter nhận request đã chuẩn hóa và trả file audio cùng sample rate, model revision, speaker/consent reference, thời lượng và hash. Không coi TTS là bộ căn phoneme.
3. Bộ alignment riêng tạo cue/timestamp, cho phép sửa tay; lip-sync chuyển cue đến mouth chart 2D hoặc viseme 3D.
4. Mixer phối thoại với SFX/ambience/music; timeline quy đổi frame ↔ sample bằng phép tính số nguyên.
5. Mỗi engine chạy trong môi trường riêng. Cần kiểm tra license của code, weights, reference voices và các phụ thuộc trước phân phối; không tải model tự động khi chưa có thiết lập.

## Phân công tiếp theo

Gemini nhận phần audio adapter theo kế hoạch nhóm. Bắt đầu bằng khảo sát có thể tái lập cho VieNeu: phiên bản/commit, model card, runtime Windows, kích thước weights, lệnh chạy, output WAV, failure modes và license; sau đó đưa đề xuất contract/PR. Adapter chỉ chuyển sang `supported` sau khi chạy thật trên môi trường đích và có ví dụ thoại tiếng Việt.
