---
name: miwiz-active3-reading
description: >
  Biến MỘT bài đọc tiếng Anh (văn xuôi ngắn, không phải hội thoại) thành 3 bộ flashcard
  Miwiz Active 3 + 2 file audio (đọc cả bài & shadowing 10 câu), rồi tự đẩy 3 deck lên app
  Miwiz qua API. BẮT BUỘC dùng skill này bất cứ khi nào user dán/đưa một đoạn văn xuôi
  tiếng Anh và muốn "tạo bộ thẻ", "làm flashcard bài đọc", "tạo thẻ Active 3", "làm bài
  đọc này", "tạo audio đọc cả bài", "tạo file shadowing", hoặc nói chung muốn học một bài
  đọc theo phương pháp Miwiz Active 3 — kể cả khi user chỉ dán bài đọc kèm câu "làm cho anh
  bộ thẻ". Cũng dùng khi user nói: create Active 3 decks, make reading flashcards, build 3
  decks from this passage, generate full-reading audio, make shadowing audio. Skill tạo 3
  deck RIÊNG (type 2/3/7), audio host VĨNH VIỄN trên GCS (KHÔNG dùng TTS ký tạm của Miwiz
  vì link hết hạn), 1 mp3 đọc cả bài và 1 mp3 shadowing 10 câu.
  KHÔNG dùng cho hội thoại (lượt A/B) — đó là Active 5; cũng không dùng để tạo thẻ lẻ.
---

# Miwiz Active 3 — Reading passage → 3 decks + reading & shadowing audio

## Skill này làm gì

Cho **1 bài đọc tiếng Anh** (văn xuôi ngắn), skill tạo trọn gói:

1. **3 deck flashcard riêng** theo phương pháp Active 3:

   | Deck | Nội dung | Loại thẻ Miwiz | Mặt trước | Audio | Số thẻ |
   |---|---|---|---|---|---|
   | Active 1 | Trắc nghiệm nghĩa cụm từ | `type 2` MCQ | tiếng Anh | — | ≥15 |
   | Active 2 | Nghe & điền **cụm từ** vào chỗ trống | `type 3` fill-blank | tiếng Anh | **CÓ** (`question_files`) | ≥12 |
   | Active 3 | Dịch Việt → Anh | `type 7` order-words | tiếng Việt | **CÓ** (`explanation.files`) | ≥10 |

2. **1 file mp3 đọc cả bài** (giọng Leda, 1x).
3. **1 file mp3 shadowing 10 câu** quan trọng (VI → EN 1.2x → EN 1x → EN 0.85x).

> Đầu vào là **hội thoại** (có lượt A/B) → KHÔNG dùng skill này; đó là **Active 5**.
> Nếu khó phân biệt văn xuôi vs hội thoại, hỏi user 1 câu trước khi chạy.

## Quy trình (làm theo đúng thứ tự)

### Bước 0 — Đọc reference
Đọc `references/workflow.md` để nắm payload từng loại thẻ, Miwiz API, **pipeline audio
vĩnh viễn** (phần quan trọng nhất — đừng dùng `/api/v2/audio/tts` của Miwiz vì nó trả link
`Expires=` hết hạn ~1h), và spec 2 file audio.

### Bước 1 — Soạn nội dung
Copy `assets/lesson_template.py` thành `lesson.py` trong một thư mục làm việc mới
(vd `<Topic>_decks/`) rồi điền:
- `TOPIC` (tên bài — dùng đặt tên deck + file audio) và `TAGS`
- `ACTIVE1` — MCQ nghĩa **cụm từ** (≥15)
- `ACTIVE2` — câu khoét trống, **chỗ trống là CẢ CỤM/collocation** (≥12), ưu tiên trùng
  cụm đã dạy ở Active 1 để 3 deck logic với nhau
- `ACTIVE3` — câu dịch Việt → Anh (≥10), câu Anh tự nhiên, KHÔNG dấu chấm cuối
- `READING_CHUNKS` — bài đọc tách theo câu/đoạn để gen audio đọc cả bài
- `SHADOW` — 10 câu cốt lõi (mỗi câu `en` + `vi`) cho file shadowing

Nguyên tắc nội dung (Active 3): ưu tiên **cụm từ & collocation** thật, distractor đủ gần
để phải suy nghĩ, câu dịch tự nhiên như người bản ngữ. **Active 2 KHÔNG khoét từ đơn.**

### Bước 2 — Tạo 3 deck + audio thẻ
```bash
python3 scripts/build_decks.py <thư-mục-chứa-lesson.py>
```
Script tự: login → gen audio Active 2 & 3 bằng Gemini TTS → upload GCS (vĩnh viễn) → tạo 3
deck → push thẻ. **Resumable** (cache `perm_cache.json` + `state.json`) — nếu sandbox
timeout ~45s thì **chạy lại** cho tới khi đủ.

### Bước 3 — Tạo file đọc cả bài
```bash
python3 scripts/make_reading.py <thư-mục-chứa-lesson.py>
```

### Bước 4 — Tạo file shadowing 10 câu
```bash
python3 scripts/make_shadowing.py <thư-mục-chứa-lesson.py>
```
Cả 2 script audio cũng **resumable** (cache PCM từng chunk) → chạy lại nếu timeout.

### Bước 5 — Báo cáo
Gửi user: 3 link deck `https://miwiz.net/flashcard/deck/<id>` + 2 file mp3 (đường dẫn local
và link public GCS).

## Môi trường cần
- Env: `MIWIZ_IDENTIFIER`, `MIWIZ_PASSWORD`, `GEMINI_API_KEY`; GCS key tự dò ở
  `../.miwiz-flc-config/gcs-key.json` (hoặc đặt `MIWIZ_GCS_KEY`).
- Cần `ffmpeg`; `pip install google-cloud-storage`.
