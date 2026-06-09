# Workflow chi tiết — Active 5 (hội thoại → 5 deck + audio)

## 1. Payload từng loại thẻ

`audio_file(url)` = `{"url": url, "type": "audio", "file_name": <basename>, "file_path": url}`

### Bộ 1 — MCQ nghĩa (type 2)
- `question`: `What is the meaning of: "<phrase>"?`
- `answers`: 1 đúng + 3 distractor (định nghĩa tiếng Anh), mỗi row `{"answer_text","is_correct","order_index","answer_files":{"files":[]}}`. Type 2 không cần audio cho answer.
- `explanation.text`: `"<icon> Example: <câu ví dụ Anh>\n🇻🇳 Nghĩa: <nghĩa Việt>"`

### Bộ 2 — MCQ tình huống (type 2), MẶT TRƯỚC TIẾNG ANH
- `question`: `Situation: <tình huống tiếng Anh>\nChoose the most appropriate response:`
- `answers`: 1 câu tiếng Anh đúng nhất + 3 sai.
- `explanation.text`: `"<icon> <giải thích ngắn vì sao hợp tình huống>"`

### Bộ 3 — Fill in the blank (type 3) + AUDIO
- `question`: `Fill in the blank:\n<câu có ______>` (khuyết 1 từ/cụm key).
- `question_files.files = [audio_file(url)]` — audio đọc **cả câu đầy đủ**.
- `answers`: đúng 1 row = từ/cụm còn thiếu.
- `explanation.text`: `"<icon> Full sentence:\n➡️ <câu đầy đủ>\n🇻🇳 <nghĩa Việt>"`

### Bộ 4 — Phản xạ nhanh (type 1, Nhớ-Quên), MẶT TRƯỚC TIẾNG ANH
- `question` (cue): `Use "<phrase>" to <ràng buộc tình huống bằng tiếng Anh>.`
- `answers`: đúng 1 row, `answer_text` = mặt sau lật ra: `"<icon> <câu mẫu>\n🔁 Variation: <biến thể>"`.
- `explanation.text`: `""`.
- Mục tiêu: buộc người học tự bật câu MỚI, không lặp câu gốc.

### Bộ 5 — Dịch Việt → Anh (type 7) + AUDIO
- `question`: `Translate this sentence into English:\n\n🇻🇳 <nghĩa tiếng Việt>`
- `answers`: **CHÍNH XÁC 1 row**, `answer_text` = nguyên câu tiếng Anh, **KHÔNG dấu chấm cuối** (UI tự tách & xáo từ).
- `explanation.text = ""`, `explanation.files = [audio_file(url)]` — audio đọc câu tiếng Anh.

## 2. Miwiz API (đã verify)

- **API host:** `https://miwizapp.com` · **Link cho user:** `https://miwiz.net/flashcard/deck/<id>`
- **Login:** `POST /api/v2/auth/login` body `{"identifier","password"}` → `data.access_token`. (Field `identifier`, KHÔNG phải `email`.)
- **Tạo deck:** `POST /api/deck` body `{"title","description","is_public":false,"price":0,"test_time":20,"tags":[...]}` → `data.deck.id`
- **Tạo thẻ:** `POST /api/flashcard` body `{deck_id,type,question,question_files,explanation,answers,order_index}`
- **Sửa thẻ (partial):** `PUT /api/flashcard/<id>` — chỉ field muốn đổi; gửi `answers` thì REPLACE hết answer rows.
- **Xoá thẻ:** `DELETE /api/flashcard/<id>`
- **Lấy deck + thẻ:** `GET /api/deck/<id>` → `data.deck.flashcards[]`, `data.deck.flashcard_count`
- `order_index` tuần tự 1,2,3,…

## 3. Audio PHẢI vĩnh viễn (bài học cốt lõi)

❌ **KHÔNG dùng** `POST /api/v2/audio/tts` của Miwiz: trả **signed URL có `Expires=`**, hết hạn sau ~1 giờ → thẻ mất tiếng.

✅ **Pipeline đúng** (đã code sẵn trong `scripts/build_decks.py`):
1. **Gemini TTS** — `POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key=<GEMINI_API_KEY>`, body responseModalities `["AUDIO"]`, voice `Leda`. Trả base64 PCM trong `candidates[0].content.parts[0].inlineData.data` (mimeType chứa `rate=`).
2. **PCM → mp3**: `ffmpeg -f s16le -ar <rate> -ac 1 -i pipe:0 -f mp3 pipe:1`.
3. **Upload GCS** (oauth2.googleapis.com bị chặn → ký URL cục bộ bằng private key trong gcs-key.json):
   ```python
   blob = client.bucket("miwiz").blob(name)
   signed = blob.generate_signed_url(version="v4", expiration=timedelta(minutes=15),
                                     method="PUT", content_type="audio/mpeg")  # KHÔNG headers ACL
   # PUT bytes tới signed với Content-Type: audio/mpeg
   ```
   Bucket bật **uniform bucket-level access** → object tự public, KHÔNG set `x-goog-acl` (sẽ lỗi 400).
4. URL công khai cuối: `https://storage.googleapis.com/miwiz/<name>` (không có `Expires` → vĩnh viễn). Verify GET 200 `audio/mpeg`.

Prefix khuyến nghị: `flashcard/audio/<topic-slug>/<md5>.mp3`.

## 4. File audio hội thoại 2 giọng (`scripts/make_dialogue.py`)
- Tách theo từng lượt A/B. Gán giọng `A = Kore`, `B = Puck`.
- Mỗi lượt: Gemini TTS giọng tương ứng → mp3 chunk.
- Ghép theo thứ tự, chèn 0.45s im lặng giữa lượt (`anullsrc`), encode `libmp3lame -q:a 4`.
- Xuất `<Topic>_dialogue.mp3` rồi `present_files` cho user.

## 5. Checklist hoàn thành
- [ ] 5 deck đủ thẻ, đúng loại (1:type2, 2:type2, 3:type3, 4:type1, 5:type7).
- [ ] Bộ 2 & Bộ 4 mặt trước tiếng Anh.
- [ ] Bộ 3 & 5: mọi thẻ có audio `storage.googleapis.com/miwiz/...`, KHÔNG `Expires`, GET 200.
- [ ] File audio hội thoại 2 giọng đã tạo + `present_files`.
- [ ] Gửi 5 link `miwiz.net` + cụm từ vàng.

## 6. Ví dụ nội dung mẫu (1 thẻ mỗi bộ)
- Bộ 1: phrase `"let it go"` → correct "to stop thinking about something and stop being upset about it"; distractors gần nghĩa; vi "buông bỏ"; example từ hội thoại.
- Bộ 2: `Situation: You've just gotten angry and want to say it's hard to calm down.` → đúng: "Once I get angry, it's hard for me to let it go."
- Bộ 3: `Fill in the blank:\nWhen anger ______, I keep thinking about it.` → answer `kicks in`; audio đọc cả câu.
- Bộ 4: `Use "clear my head" to say you need a walk before deciding.` → sample "I need a walk to clear my head before deciding."
- Bộ 5: `Translate ...\n🇻🇳 Tôi tin đó là kỹ năng phát triển theo thời gian.` → answer "I believe it's a skill that develops over time" (không dấu chấm); audio mặt sau.
