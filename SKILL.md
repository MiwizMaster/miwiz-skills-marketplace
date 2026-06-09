---
name: miwiz-active5-conversation
description: >
  Biến MỘT đoạn hội thoại tiếng Anh (lượt A/B) thành 5 bộ flashcard Miwiz Active 5 +
  1 file audio cả bài hội thoại 2 giọng, rồi tự đẩy lên app Miwiz qua API.
  BẮT BUỘC dùng skill này bất cứ khi nào user dán/đưa một đoạn hội thoại tiếng Anh và muốn
  "tạo bộ thẻ", "làm flashcard hội thoại", "tạo thẻ Active 5", "làm bài hội thoại này",
  "tạo audio hội thoại", "đọc hội thoại 2 giọng", hoặc nói chung là muốn học một đoạn
  hội thoại theo phương pháp Miwiz Active 5 — kể cả khi user chỉ dán hội thoại kèm câu
  "làm cho anh bộ thẻ". Cũng dùng khi user nói: create Active 5 decks, make conversation
  flashcards, build 5 decks from this dialogue, generate two-voice dialogue audio.
  Skill tạo 5 deck RIÊNG (type 2/2/3/1/7), audio host VĨNH VIỄN trên GCS (không dùng TTS
  ký tạm của Miwiz vì link hết hạn), và 1 mp3 hội thoại 2 giọng.
  KHÔNG dùng cho đoạn văn xuôi ngắn (đó là Active 3) hay cho việc tạo thẻ lẻ.
---

# Miwiz Active 5 — Conversation → 5 decks + dialogue audio

## Skill này làm gì

Cho **1 đoạn hội thoại tiếng Anh** (có lượt A/B), skill tạo trọn gói trên Miwiz:

1. **5 deck flashcard riêng** theo phương pháp Active 5:

   | Bộ | Nội dung | Loại thẻ Miwiz | Mặt trước | Audio | Số thẻ |
   |---|---|---|---|---|---|
   | 1 | Trắc nghiệm nghĩa từ/cụm | `type 2` MCQ | tiếng Anh | — | 10–15 |
   | 2 | Trắc nghiệm tình huống | `type 2` MCQ | **tiếng Anh** | — | 8–15 |
   | 3 | Nghe & điền chỗ trống | `type 3` fill-blank | tiếng Anh | **CÓ** (`question_files`) | 8–15 |
   | 4 | Phản xạ nhanh tạo câu | `type 1` Nhớ-Quên | **tiếng Anh** | — | 8–15 |
   | 5 | Dịch Việt → Anh | `type 7` order-words | tiếng Việt | **CÓ** (`explanation.files`) | 5–10 |

2. **1 file mp3 cả bài hội thoại, 2 giọng** (A và B khác nhau).

> Đầu vào là **văn xuôi ngắn** (không phải đối thoại) → KHÔNG dùng skill này; đó là **Active 3** (3 deck). Nếu khó phân biệt, hỏi user 1 câu trước khi chạy.

## Quy trình (làm theo đúng thứ tự)

### Bước 0 — Đọc reference
Đọc `references/workflow.md` để nắm đúng payload từng loại thẻ, Miwiz API, và **pipeline audio vĩnh viễn** (phần quan trọng nhất — đừng dùng `/api/v2/audio/tts` của Miwiz vì nó trả link `Expires=` hết hạn).

### Bước 1 — Soạn nội dung
Copy `assets/lesson_template.py` thành `lesson.py` trong một thư mục làm việc mới (vd `<Topic>_decks/`) rồi điền:
- `TOPIC` (tên bài, dùng đặt tên deck + file audio)
- `TAGS`
- `BO1..BO5` — nội dung 5 bộ (xem comment trong template + ví dụ trong workflow)
- `DIALOGUE` — list `(speaker, text)` theo đúng thứ tự lượt; `VOICE = {"A": "Kore", "B": "Puck"}`

Nguyên tắc nội dung (Active 5): ưu tiên **cụm từ & mẫu câu** thật, distractor đủ gần để phải suy nghĩ, câu dịch tự nhiên như người bản ngữ, Bộ 4 buộc người học **tự tạo câu mới** chứ không lặp câu gốc.

### Bước 2 — Tạo 5 deck + audio
```bash
python3 scripts/build_decks.py <thư-mục-chứa-lesson.py>
```
Script tự: login → gen audio Bộ 3 & 5 bằng Gemini TTS → upload GCS (vĩnh viễn) → tạo 5 deck → push thẻ. **Resumable** (cache audio + state deck) — nếu sandbox timeout ~45s thì **chạy lại** cho tới khi đủ.

### Bước 3 — Tạo audio hội thoại 2 giọng
```bash
python3 scripts/make_dialogue.py <thư-mục-chứa-lesson.py>
```
Resumable theo từng lượt; chạy lại tới khi ghép xong `<Topic>_dialogue.mp3`.

### Bước 4 — Verify & báo cáo
- `GET /api/deck/<id>` từng deck: đúng số thẻ, đúng loại (1:type2, 2:type2, 3:type3, 4:type1, 5:type7).
- Bộ 3 & 5: mọi thẻ có audio, URL `storage.googleapis.com/miwiz/...`, **không** có `Expires=`, GET trả 200.
- Gửi user **5 link `miwiz.net`** + tóm tắt cụm từ vàng, và `present_files` file mp3 hội thoại.

## Cấu hình / credentials

Scripts đọc từ biến môi trường (nguồn chuẩn: file `.env` của user, vd `Miwiz Active/.miwiz-flc-config/.env`):
- `MIWIZ_IDENTIFIER`, `MIWIZ_PASSWORD` — login Miwiz
- `GEMINI_API_KEY` — Gemini TTS
- `MIWIZ_GCS_KEY` — đường dẫn tới service-account JSON của bucket `miwiz` (mặc định dò `.miwiz-flc-config/gcs-key.json`)

Trước khi chạy:
```bash
set -a; source "<đường dẫn>/.miwiz-flc-config/.env"; set +a
export MIWIZ_IDENTIFIER MIWIZ_PASSWORD GEMINI_API_KEY
export MIWIZ_GCS_KEY="<đường dẫn>/.miwiz-flc-config/gcs-key.json"
```
Cần `ffmpeg` (có sẵn) và `pip install google-cloud-storage --break-system-packages`.

## Lưu ý vận hành (sandbox)
- Mỗi lệnh bash timeout ~45s và tiến trình nền bị kill → **luôn dùng script resumable** ở trên, chạy lại nhiều lượt.
- Gemini TTS thi thoảng trả 500/503 → script đã có retry.
- `oauth2.googleapis.com` bị chặn → upload GCS bằng **signed URL ký cục bộ** (đã xử lý trong script). Bucket bật uniform access nên **không set ACL**.
- Link gửi user: `miwiz.net`. API call: `miwizapp.com`.

## Tham chiếu
- `references/workflow.md` — payload chi tiết từng loại thẻ + Miwiz API + pipeline audio vĩnh viễn.
- `assets/lesson_template.py` — khung nội dung để điền.
- `scripts/build_decks.py`, `scripts/make_dialogue.py` — thực thi.
