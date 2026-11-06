# Fixture story edit

Ba shot, hai scene, hai nhân vật; thời lượng dự định 264 frame tại 24000/1001 fps (11,011 giây). Chỉ có text và event, chưa có WAV hay hình/render.

Tạo project qua `POST /api/v1/projects` với `{ "project": <project.json> }`. Gửi `edit.json` tới `/api/v1/projects/ecb857be-8a30-4dba-9d5e-e2dc3bff7913/story-edits/preview`, xem report/impact, rồi gửi cùng request tới `/story-edits`. Các endpoint cần bearer token. Expected revision 1 chỉ đúng khi mới tạo project.

Bản edit là một phương án khác: bắt đầu bằng cận cảnh nhặt vé rồi mới thấy sân ga; rút shot sân ga xuống 48 frame và đổi câu hỏi của Linh. Tổng mới 240 frame (10,01 giây). Timing local của thoại/cue giữ nguyên; thứ tự ngữ nghĩa cần đạo diễn xem lại. Đây không phải đề xuất tự động về chất lượng kể chuyện.
