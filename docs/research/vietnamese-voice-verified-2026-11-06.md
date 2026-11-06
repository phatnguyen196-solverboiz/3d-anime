# Xác minh các thành phần giọng tiếng Việt cho AnimeFlow

Ngày đối chiếu nguồn: 06/11/2026. Tài liệu này ghi kết quả đọc README, mã nguồn, model card và giấy phép do chính các dự án công bố. **Chưa cài model, tải weights, tạo audio hoặc benchmark trên máy Windows của dự án.** Các số liệu tốc độ là kết quả tự công bố của upstream; không phải kết quả nghiệm thu AnimeFlow. Repo trong bảng vẫn là **ứng viên**, chưa là adapter `supported`.

## Đính chính cần áp dụng ngay

- **ZeroTTS mã nguồn mở không clone giọng mới trực tiếp từ file âm thanh.** Gói hiện phát hành có 8 giọng preset và có thể *đọc* speaker latents. Voice encoder tạo latents từ clip chưa được công bố. Muốn dùng một giọng mới theo hướng dẫn upstream, người dùng tải clip lên nền tảng ZeroWeight, nhận ZIP chứa latents rồi import vào gói local. Không mô tả thao tác này là voice cloning hoàn toàn offline. [README ZeroTTS](https://github.com/zeroweight-ai/ZeroTTS#voices--and-voice-cloning), [model card](https://huggingface.co/zeroweight-ai/ZeroTTS#voices-and-voice-cloning).
- **VieNeu v3 Turbo là bản nguồn mở mới nhất trong repo; v4 chỉ có qua API độc quyền.** Các tính năng Dubbing/Lecture/TikTok của ứng dụng hosted không đồng nghĩa với tính năng dựng video có sẵn trong SDK GitHub. [README VieNeu](https://github.com/pnnbao97/VieNeu-TTS).
- **PhoWhisper là ASR, không phải TTS hay forced aligner.** Kết quả transcript không có đủ thông tin để đặt chính xác từng viseme. [README PhoWhisper](https://github.com/VinAIResearch/PhoWhisper).
- **Rhubarb mặc định dùng recognizer chỉ nhận tiếng Anh.** Audio tiếng Việt cần `-r phonetic`; upstream cảnh báo chế độ này thường kém chính xác hơn. Cue cần preview và chỉnh tay khi chất lượng không đạt. [README Rhubarb](https://github.com/DanielSWolf/rhubarb-lip-sync#recognizers).

## Ma trận kỹ thuật và quyền sử dụng

| Thành phần | API/đầu ra xác minh | Runtime và giới hạn | Mã nguồn, weights, giọng |
|---|---|---|---|
| [VieNeu-TTS v3 Turbo](https://github.com/pnnbao97/VieNeu-TTS) | `Vieneu().infer(text, voice=...)` trả waveform; `save(audio, "out.wav")`; `infer_stream` trả chunk `float32` **48 kHz**; clone từ `ref_audio` **3–8 giây**, kể cả CPU ONNX. | README hướng dẫn Windows. Cài CPU tối thiểu dùng ONNX và không cần PyTorch; GPU CUDA dùng backend PyTorch. Chế độ `precision="int8"` đòi CPU có VNNI, nếu không có thể ra audio lỗi. `style` của v3 Turbo bị bỏ qua. Preset thay đổi giữa phiên bản; gọi `list_preset_voices()` lúc chạy. | Repo và [model card v3 Turbo](https://huggingface.co/pnnbao-ump/VieNeu-TTS-v3-Turbo#-usage-rights--licensing-faq) nêu Apache-2.0 cho code, weights, ONNX và preset assets; model card xác nhận preset được phép dùng cho video thương mại. Quyền đó **không** thay thế sự đồng ý của người có giọng trong clip clone. Codec MOSS là Apache-2.0; [SEA-G2P](https://github.com/pnnbao97/sea-g2p) là Apache-2.0. |
| [ZeroTTS](https://github.com/zeroweight-ai/ZeroTTS) | `ZeroTTS.from_pretrained("zeroweight-ai/ZeroTTS").synthesize(text, voice="maichi")`; `save_audio(audio, "out.wav")`. Stream chunk `float32` mono **48 kHz**; WAV qua API lưu file. | ONNX CPU, không cần torch cho inference; lần đầu lấy khoảng **900 MB** weights từ Hugging Face. `synthesize()` **không tự gọi** `normalize_vi_text()`; CLI/Web UI thì có. Nên chia văn bản dài thành đoạn ngắn, ví dụ `chunk_text(..., max_chunk_sec=15)`. Upstream không có xác nhận Windows riêng trong README; cần smoke test trên Windows. | [README](https://github.com/zeroweight-ai/ZeroTTS#license) và [model card](https://huggingface.co/zeroweight-ai/ZeroTTS#license) nêu code/weights MIT, codec MOSS đi kèm Apache-2.0. Model card mô tả preset voices dành cho evaluation/demo; cần xác minh phạm vi sử dụng giọng preset khi phát hành sản phẩm. Bộ benchmark ZeroBench-TTS CC-BY-NC-4.0 là giấy phép **riêng cho benchmark**, không áp cho weights ZeroTTS. |
| [KorvaTTS](https://github.com/dogenthq/KorvaTTS) | `TTS().synthesize(text, voice="khanh_vy", lang="vi")` trả `(waveform, duration_seconds)`; `save_audio(waveform, "out.wav")`; WAV **44,1 kHz**. Có 10 preset (5 nữ, 5 nam). | Python ≥3.10, ONNX Runtime CPU, GPU tùy chọn; model tải ở lần đầu, có `assets_dir`/`KORVATTS_ASSETS_DIR` cho assets local. Hỗ trợ đọc câu pha tiếng Anh. Chưa phát hành clone giọng. `pyproject.toml` khai OS Independent nhưng vẫn cần smoke test Windows. | [README](https://github.com/dogenthq/KorvaTTS#licenses) và [MODEL_LICENSE.md](https://github.com/dogenthq/KorvaTTS/blob/main/MODEL_LICENSE.md) nêu Apache-2.0 cho code, weights và voice styles. Tập dữ liệu pha Việt–Anh tự thu là private, không được phát hành. |
| [PhoWhisper](https://github.com/VinAIResearch/PhoWhisper) | `pipeline("automatic-speech-recognition", model="vinai/PhoWhisper-small")(audio_16k)["text"]` trả transcript. Input ví dụ là **16 kHz**, nên audio TTS phải được resample cho bước kiểm transcript. | Transformers/PyTorch; `small` là 244M tham số theo README. Dùng để so lại lời đã thu hoặc TTS; không suy ra tự động timestamp từ transcript text. | Repo BSD-3-Clause; [model card small](https://huggingface.co/vinai/PhoWhisper-small) cũng khai BSD-3-Clause. |
| [Rhubarb Lip Sync](https://github.com/DanielSWolf/rhubarb-lip-sync) | CLI nhận WAV/Ogg, xuất JSON/TSV/XML các mouth cue `start`, `end` tính bằng **giây**, `value` thuộc A–H/X. `rhubarb -r phonetic -f json -o cues.json voice.wav`. | Bản phát hành Windows/macOS/Linux. Phonetic nhận ngôn ngữ ngoài tiếng Anh nhưng kém chính xác hơn PocketSphinx tiếng Anh; 2D mouth chart có thể ánh xạ thô sang 3D viseme, chưa phải căn phoneme tiếng Việt chuẩn. | [LICENSE.md](https://github.com/DanielSWolf/rhubarb-lip-sync/blob/master/LICENSE.md) nêu MIT cho công cụ; dữ liệu lip-sync do người chạy tạo thuộc về họ. |

### Xử lý văn bản tiếng Việt thực tế

- VieNeu dùng [SEA-G2P](https://github.com/pnnbao97/sea-g2p) để chuẩn hóa và chuyển chữ sang âm vị Việt/Anh. Giữ **text gốc** trong ProjectSpec; nếu cần bản đọc kiểm duyệt, lưu riêng `spoken_text` và phiên bản normalizer. Không chạy một bộ mở rộng số/ngày bên ngoài rồi lại giả định SDK không xử lý lần nữa.
- ZeroTTS công bố `normalize_vi_text()` mở rộng ngày, giờ, phân số, số và chữ viết tắt; gọi tường minh trước `synthesize()` hoặc dùng CLI có bật mặc định. Không áp quy tắc tiếng Việt lên một đoạn tiếng Anh thuần. [Ví dụ normalizer và chunking](https://github.com/zeroweight-ai/ZeroTTS#usage).
- [Mã `text_processor.py` của KorvaTTS](https://github.com/dogenthq/KorvaTTS/blob/main/korvatts/text_processor.py) chuẩn hóa Unicode NFKD, loại emoji, thay một số dấu/ký tự, gắn language tag và chia câu tối đa 300 ký tự. Mã này **không thể hiện** bước đọc số/ngày đầy đủ thành lời Việt. Trong bản thoại cần QA thủ công các chuỗi như `23/8/2026`, `1.250.000`, tên người, thương hiệu và đoạn pha tiếng Anh. [Mã `tts.py`](https://github.com/dogenthq/KorvaTTS/blob/main/korvatts/tts.py) ghép các chunk với khoảng lặng mặc định 0,3 giây và nhận `seed`.

## API tối thiểu để Gemini kiểm thử trong môi trường riêng

Các đoạn sau là **ví dụ upstream để dựng smoke test**, chưa phải script đã chạy trong AnimeFlow. Mỗi engine cần venv/lockfile và cache weights riêng; pin bản SDK và revision model trước khi dùng cho job. Không cài chồng các gói model vào venv API/core.

```python
# VieNeu v3 Turbo; CPU mặc định ONNX, output native 48 kHz.
from vieneu import Vieneu

tts = Vieneu(mode="v3turbo", backend="onnx")
audio = tts.infer("Xin chào, đây là một câu thoại tiếng Việt.", voice="Hải Đăng")
tts.save(audio, "vieneu-vi.wav")
# Clone có quyền: tts.infer(text, ref_audio="consented-reference.wav", denoise=True)
```

```python
# ZeroTTS; output native 48 kHz, chỉ dùng preset hoặc latent đã có.
from zerotts import ZeroTTS, normalize_vi_text

tts = ZeroTTS.from_pretrained("zeroweight-ai/ZeroTTS")
spoken = normalize_vi_text("Ngày 23/8/2026, chúng ta bắt đầu.")
audio = tts.synthesize(spoken, voice="maichi")
tts.save_audio(audio, "zerotts-vi.wav")
```

```python
# KorvaTTS; output native 44,1 kHz.
from korvatts import TTS

tts = TTS()
audio, duration_seconds = tts.synthesize(
    "Hôm nay team mình làm video hoạt hình.", voice="khanh_vy", lang="vi", seed=42
)
tts.save_audio(audio, "korvatts-vi.wav")
```

```python
# PhoWhisper chỉ kiểm transcript, không tạo audio/cue. Input phải 16 kHz.
from transformers import pipeline

asr = pipeline("automatic-speech-recognition", model="vinai/PhoWhisper-small")
transcript = asr("speech-resampled-16k.wav")["text"]
```

```powershell
# Rhubarb cho audio tiếng Việt. Cần binary đã tải từ release chính thức.
rhubarb -r phonetic -f json -o cues.json voice.wav
```

## Pin phiên bản và provenance trước khi bật adapter

| Engine | Mốc upstream đã đọc | Pin bắt buộc trong nghiệm thu Gemini |
|---|---|---|
| VieNeu | [Model card](https://huggingface.co/pnnbao-ump/VieNeu-TTS-v3-Turbo) ghi SDK **v3.7.1**, model ID `pnnbao-ump/VieNeu-TTS-v3-Turbo`. README repo và model card hiện lệch số preset (25 so với 23). | Chốt version PyPI/commit SDK, **SHA revision Hugging Face** của weights và codec, backend/precision, roster từ `list_preset_voices()`, SHA của output test. Không coi version trong model card là pin thực tế của repo này khi chưa cài. |
| ZeroTTS | [`pyproject.toml`](https://github.com/zeroweight-ai/ZeroTTS/blob/main/pyproject.toml) ghi **0.1.5**, model ID `zeroweight-ai/ZeroTTS`. | Pin package version và SHA revision weights/voice pack; ghi cache path, voice ID, mode chuẩn hóa, SHA output. Không chọn `voice=None` vì README nêu giọng unconditional không ổn định qua các lần chạy. |
| KorvaTTS | [`pyproject.toml`](https://github.com/dogenthq/KorvaTTS/blob/main/pyproject.toml) ghi **0.1.3**, model ID `dogenthq/KorvaTTS`. | Pin package version, SHA revision `onnx/` và `voice_styles/`, `seed`, `total_steps`, `speed`, silence giữa chunk, SHA output. |
| PhoWhisper | Model ID ví dụ `vinai/PhoWhisper-small`. | Pin revision model/processor và bản Transformers/PyTorch nếu đưa vào kiểm transcript. |
| Rhubarb | Có binary release theo OS. | Pin release version và SHA binary; lưu recognizer `phonetic`, file JSON và phiên bản mapping mouth chart. |

**Chưa chốt SHA revision cho model nào** vì chưa tải hoặc chạy chúng trong môi trường đích. Không dùng nhánh `main`/`latest` làm pin của một job có thể tái lập. Khi nghiệm thu, ghi khóa cụ thể vào manifest/lockfile và metadata artifact; không commit weights, ZIP giọng cá nhân, clip tham chiếu hay dữ liệu có bản quyền vào Git.

## Contract đề xuất cho AF-AUDIO-VI-01 và ranh giới ownership

Đây là **đề xuất giao tiếp**, chưa là JSON Schema canonical. `ProjectSpec` hiện có `voice_line_id`, `shot_id`, `character_id`, `text`, `language`, `start_frame`, `duration_frames`, tùy chọn `audio_asset_id`, và `canvas.audio_sample_rate`. Contract/schema thực tế thuộc core owner; Gemini gửi đề xuất và fixture trước khi đổi schema. Không thêm trường bắt buộc trực tiếp vào `project.schema.json` từ adapter. [Schema ProjectSpec](../../packages/contracts/src/animeflow_contracts/schemas/project.schema.json), [hướng dẫn teamwork](../teamwork-vi.md).

| Request `TtsRequestV1` | Ý nghĩa |
|---|---|
| `request_id`, `project_id`, `voice_line_id` | Liên kết job với snapshot ProjectSpec; retry dùng cùng ID nhưng không âm thầm ghi đè artifact. |
| `text`, `language` | Text UTF-8 nguyên gốc và locale (`vi-VN` ở ProjectSpec, ánh xạ sang `vi` nếu engine yêu cầu). |
| `spoken_text_override`, `normalization_mode` | Văn bản đọc đã duyệt (nếu có); một trong `engine`, `vi-explicit`, `none`, ghi phiên bản normalizer. |
| `engine_id`, `package_version`, `model_id`, `model_revision`, `backend` | Pin runtime/model và chọn CPU/GPU có chủ đích. Không tải weights ngoài cache khi policy offline. |
| `voice` | `kind` là `preset`, `reference` hoặc `latent`; ID giọng hoặc `reference_audio_asset_id`/latent asset; nguồn và consent reference cho giọng clone. Mỗi engine khai rõ loại hỗ trợ. |
| `target_audio_sample_rate`, `output_format`, `seed` | Lấy sample rate từ canvas; output trao đổi đề xuất WAV PCM mono; seed nếu engine hỗ trợ. |

| Result `TtsResultV1` | Ý nghĩa |
|---|---|
| `status`, `error_code`, `message` | `completed` hoặc lỗi có mã; không trả thành công giả khi engine/model chưa có. |
| `native_audio` và `project_audio` | Asset ID, SHA-256, WAV subtype, channels, sample rate và số sample nguyên cho file gốc và file đã resample. Không suy ra sample rate từ phần mở rộng `.wav`. |
| `original_text`, `spoken_text`, `normalizer_version` | Cho phép tái lập, kiểm đọc số/ngày, so transcript. |
| `engine_id`, `package_version`, `model_id`, `model_revision`, `voice_id`, `seed` | Provenance thật của lượt chạy, không chỉ cấu hình dự định. |
| `duration_samples`, `warnings`, `consent_reference` | Thời lượng kiểm bằng sample count; cảnh báo thoại tràn slot, chữ đọc sai hoặc thiếu quyền giọng. |

Pipeline: `VoiceLine → normalizer có ghi provenance → TTS ở venv riêng → lưu WAV native → resample về canvas.audio_sample_rate → kiểm transcript tùy chọn → alignment/cue → lip-sync → mix thoại/SFX/nhạc → mux video`. TTS không được tự tuyên bố có phoneme timestamps. Rhubarb xuất cue tính bằng giây; chuyển về **sample index nguyên** tại sample rate canonical rồi mới ánh xạ sang frame. Với FPS `numerator/denominator`, tính vị trí sample của frame `f` bằng `round(f × sample_rate × denominator / numerator)` với một quy tắc làm tròn cố định; không cộng dồn số giây thực. Korva 44.100 → project 48.000 Hz có tỉ lệ resample chính xác **160/147**. Giữ checksum native và derived riêng.

`duration_frames` là slot kịch bản, không chắc bằng thời lượng audio thật. Nếu audio tràn slot, trả cảnh báo/lỗi hoặc xin chính sách fit cụ thể; không cắt hay kéo giãn âm thanh im lặng. `audio_asset_id` chỉ được cập nhật trong ProjectSpec sau khi core đã lưu artifact và kiểm revision project. Mapping mouth chart A–H/X của Rhubarb sang 3D viseme là bước downstream và cần QA hình ảnh, nhất là tiếng Việt.

Gemini sở hữu `adapters/audio/**`, venv/lockfile riêng, smoke test và báo cáo tiếng Việt theo ticket `AF-AUDIO-VI-01`; Codex sở hữu schema, API, persistence và phép quy đổi timeline. Handoff tối thiểu: version/package/model revision đã pin, danh sách file đổi, license code/weights/preset/reference, lệnh chạy Windows CPU, file WAV ngắn kèm sample rate/channels/subtype/hash, transcript nghe kiểm, lỗi/failure mode và đề xuất contract. Chỉ nâng trạng thái adapter lên `supported` sau khi có test thật trên Windows đích và fixture thoại tiếng Việt chạy được.
