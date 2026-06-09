# -*- coding: utf-8 -*-
"""LESSON TEMPLATE — copy this to <Topic>_decks/lesson.py and fill in.
Then run:  python3 scripts/build_decks.py <Topic>_decks
           python3 scripts/make_dialogue.py <Topic>_decks
See references/workflow.md for payload rules."""

TOPIC = "My Conversation Topic"          # dùng đặt tên deck + file audio
TAGS = ["English", "Conversation", "Active 5"]
VOICE = {"A": "Kore", "B": "Puck"}        # 2 giọng khác nhau cho file audio hội thoại

# ── BỘ 1 — MCQ nghĩa từ/cụm (type 2). 10–15 thẻ ──
# Mỗi thẻ: phrase, icon, correct (định nghĩa Anh đúng), distractors (3 cái gần nghĩa),
#          vi (nghĩa Việt ngắn), example (câu ví dụ Anh, nên lấy từ hội thoại).
BO1 = [
    {"phrase": "", "icon": "💡", "correct": "",
     "distractors": ["", "", ""], "vi": "", "example": ""},
]

# ── BỘ 2 — MCQ tình huống (type 2), MẶT TRƯỚC TIẾNG ANH. 8–15 thẻ ──
# situation: tình huống TIẾNG ANH; correct: câu Anh đúng nhất; distractors: 3 câu sai; why: giải thích ngắn.
BO2 = [
    {"situation": "", "icon": "🗣️", "correct": "",
     "distractors": ["", "", ""], "why": ""},
]

# ── BỘ 3 — Fill in the blank (type 3) + audio. 8–15 thẻ ──
# blank: câu có ______ (khuyết 1 từ/cụm key); answer: từ/cụm còn thiếu;
# full: câu đầy đủ (audio sẽ đọc câu này); vi: nghĩa Việt cả câu.
BO3 = [
    {"icon": "🔊", "answer": "", "blank": "", "full": "", "vi": ""},
]

# ── BỘ 4 — Phản xạ nhanh (type 1 Nhớ-Quên), MẶT TRƯỚC TIẾNG ANH. 8–15 thẻ ──
# prompt: cue tiếng Anh dạng  Use "<phrase>" to <tình huống>.
# sample: câu mẫu; variant: 1 biến thể. (Buộc tạo câu MỚI, không lặp câu gốc.)
BO4 = [
    {"icon": "⚡", "prompt": "", "sample": "", "variant": ""},
]

# ── BỘ 5 — Dịch Việt → Anh (type 7) + audio. 5–10 thẻ ──
# vi: câu tiếng Việt; en: câu tiếng Anh tự nhiên, KHÔNG dấu chấm cuối.
BO5 = [
    {"vi": "", "en": ""},
]

# ── HỘI THOẠI cho file audio 2 giọng — đúng thứ tự lượt, dùng nhãn "A"/"B" ──
DIALOGUE = [
    ("A", ""),
    ("B", ""),
]
