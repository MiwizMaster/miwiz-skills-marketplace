# Miwiz Active 3 — workflow & payload reference

Phương pháp Active 3 (TS. Hán Minh Cường): từ **1 bài đọc văn xuôi ngắn** → 3 deck
(từ/cụm + nghe + dịch) + 2 file audio (đọc cả bài, shadowing). Đầu vào là **hội thoại** →
dùng Active 5, không dùng skill này.

## 1. Ba deck

| Deck | type | Mặt trước | Audio | Tối thiểu |
|---|---|---|---|---|
| Active 1 | 2 (MCQ 1 đúng) | `What is the meaning of: "<cụm>"?` | — | ≥15 |
| Active 2 | 3 (fill blank) | `Fill in the blank:\n<câu có ______>` | **CÓ** ở `question_files` (đọc cả câu) | ≥12 |
| Active 3 | 7 (order words) | `Translate this sentence into English:\n\n🇻🇳 <vi>` | **CÓ** ở `explanation.files` (đọc câu Anh) | ≥10 |

**Active 1 — MCQ nghĩa cụm (type 2):** 4 đáp án = định nghĩa tiếng Anh, 1 đúng + 3 distractor
đủ gần. Mặt sau: `"<icon> Example: <ví dụ Anh>\n🇻🇳 Nghĩa: <nghĩa Việt>"`. KHÔNG cần `answer_files`.

**Active 2 — Fill blank (type 3) + audio:**
- ⚠️ **Khoét trống CẢ CỤM / collocation, KHÔNG khoét từ đơn.** Chỗ trống là một chunk có
  nghĩa (vd `cleaner production`, `material and energy flows`), **ưu tiên trùng cụm đã dạy ở
  Active 1** để 3 deck logic với nhau.
- `question_files.files = [audio_file(url)]` đọc **cả câu đầy đủ**.
- `answers` = 1 row = nguyên cụm còn thiếu (đúng hoa/thường như trong câu).
- Mặt sau: `"<icon> Full sentence:\n➡️ <câu đầy đủ>\n🇻🇳 <nghĩa Việt>"`.

**Active 3 — Dịch Việt → Anh (type 7) + audio:**
- `question`: `Translate this sentence into English:\n\n🇻🇳 <nghĩa Việt>` (KHÔNG dùng "Arrange the words").
- `answers` = **CHÍNH XÁC 1 row** = nguyên câu tiếng Anh, **KHÔNG dấu chấm cuối** (UI tự xáo từ).
- `explanation.files = [audio_file(url)]` đọc câu Anh.

## 2. Miwiz API (đã verify)
- Host API: `https://miwizapp.com` · Link gửi user: `https://miwiz.net/flashcard/deck/<id>`.
- Login: `POST /api/v2/auth/login` body `{"identifier","password"}` → `data.access_token`
  (field là **identifier**, không phải email/username).
- Tạo deck: `POST /api/deck` `{title,description,is_public:false,price:0,test_time:20,tags}` → `data.deck.id`.
- Tạo thẻ: `POST /api/flashcard` `{deck_id,type,question,question_files,explanation,answers,order_index}`.
- Lấy deck: `GET /api/deck/<id>` → `data.deck.flashcards[]`, `data.deck.flashcard_count`.
- `http()` nên **retry** lỗi tạm thời (Cloudflare 5xx/521) để push không gãy giữa chừng.

**audio_file(url)** = `{"url":url,"type":"audio","file_name":<basename>,"file_path":url}`
(`type` literal `"audio"`, KHÔNG phải `"mp3"`).

## 3. Audio PHẢI vĩnh viễn (bài học quan trọng nhất)
❌ KHÔNG dùng `/api/v2/audio/tts` của Miwiz: trả signed URL có `Expires=`, hết hạn ~1h → thẻ mất tiếng.
✅ Pipeline: **Gemini TTS → mp3 → upload bucket `gs://miwiz` (public vĩnh viễn) → gắn URL vào thẻ.**
- Gemini: model `gemini-2.5-flash-preview-tts`, trả base64 PCM (rate trong `mimeType`),
  đổi mp3 bằng `ffmpeg -f s16le -ar <rate> -ac 1 -i pipe:0 -f mp3 pipe:1`.
- GCS: bucket bật uniform access → **KHÔNG set ACL**. Ký **signed URL method=PUT** cục bộ bằng
  `gcs-key.json` rồi PUT bytes; URL công khai `https://storage.googleapis.com/miwiz/<blob>`
  (không có `Expires` → vĩnh viễn). Verify GET phải `200 audio/mpeg`.
- Giọng flashcard: **Leda**. Prefix: `flashcard/audio/<slug>/...`.

## 4. Hai file audio kèm theo
- **Đọc cả bài** (`make_reading.py`): giọng **Leda**, 1x. Tách bài theo câu/đoạn
  (`READING_CHUNKS`), gen từng chunk, chèn ~0.4s lặng giữa các chunk, nối + encode 1 lần.
- **Shadowing 10 câu** (`make_shadowing.py`): mỗi câu →
  1. nghĩa **tiếng Việt** (voice **Kore**) 1x → nghỉ **5s**;
  2. tiếng Anh **1.2x** → nghỉ **2–4s**;
  3. tiếng Anh **1x** → nghỉ **2–4s**;
  4. tiếng Anh **0.85x**.
  Giữa 2 câu nghỉ **5s**. Nghỉ giữa các lần đọc: `p = max(2, min(4, round(dur_1x * 0.4)))`.
  Đổi tốc độ bằng `ffmpeg atempo=1.2 / 0.85` (gen EN 1 lần ở 1x rồi đổi tốc độ → giữ cùng giọng).
  Giọng Anh = **Leda**, giọng Việt = **Kore**.

## 5. Mẹo pipeline (rút kinh nghiệm)
- Background process bị kill giữa các lần gọi tool → mọi script gen audio **resumable**:
  cache mỗi clip PCM/URL ra đĩa, chạy lại bỏ qua clip đã xong. Sandbox hay timeout ~45s →
  cứ chạy lại script tới khi in `DONE`.
- `build_decks.py` lưu `perm_cache.json` (text→URL audio) + `state.json` (deck_id + số thẻ đã
  push) → chạy lại không tạo trùng deck, không push trùng thẻ.

## 6. Lệnh chạy
```bash
python3 scripts/build_decks.py    <Topic>_decks    # 3 deck + audio thẻ (Active 2 & 3)
python3 scripts/make_reading.py   <Topic>_decks    # file đọc cả bài
python3 scripts/make_shadowing.py <Topic>_decks    # file shadowing 10 câu
```
Env: `MIWIZ_IDENTIFIER`, `MIWIZ_PASSWORD`, `GEMINI_API_KEY`; GCS key tự dò ở
`<Topic>_decks/../.miwiz-flc-config/gcs-key.json` hoặc đặt `MIWIZ_GCS_KEY`.
