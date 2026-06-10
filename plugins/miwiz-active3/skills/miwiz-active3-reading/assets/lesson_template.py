# -*- coding: utf-8 -*-
"""LESSON TEMPLATE — copy this to <Topic>_decks/lesson.py and fill in.
Then run:  python3 scripts/build_decks.py    <Topic>_decks
           python3 scripts/make_reading.py   <Topic>_decks
           python3 scripts/make_shadowing.py <Topic>_decks
See references/workflow.md for payload rules."""

TOPIC = "My Reading Topic"                 # dùng đặt tên deck + file audio
TAGS = ["English", "Reading", "Active 3"]

# ── ACTIVE 1 — MCQ nghĩa CỤM TỪ (type 2). ≥15 thẻ ──
# Mỗi thẻ: phrase (cụm/collocation), icon, correct (định nghĩa Anh đúng),
#          distractors (3 cái gần nghĩa), example (câu ví dụ Anh từ bài), vi (nghĩa Việt ngắn).
ACTIVE1 = [
    {"phrase": "", "icon": "💡", "correct": "",
     "distractors": ["", "", ""], "example": "", "vi": ""},
]

# ── ACTIVE 2 — Fill in the blank (type 3) + audio. ≥12 thẻ ──
# ⚠️ KHOÉT TRỐNG CẢ CỤM/collocation (KHÔNG khoét từ đơn), ưu tiên trùng cụm ở ACTIVE1.
# blank: câu có ______; answer: nguyên CỤM còn thiếu; full: câu đầy đủ (audio đọc câu này);
# vi: nghĩa Việt cả câu; icon.
ACTIVE2 = [
    {"icon": "🔊", "answer": "", "blank": "", "full": "", "vi": ""},
]

# ── ACTIVE 3 — Dịch Việt → Anh (type 7) + audio. ≥10 thẻ ──
# vi: câu tiếng Việt; en: câu tiếng Anh tự nhiên, KHÔNG dấu chấm cuối (UI tự xáo từ).
ACTIVE3 = [
    {"vi": "", "en": ""},
]

# ── READING — bài đọc tách theo câu/đoạn cho file audio đọc cả bài (giọng Leda, 1x) ──
# Tip: đặt nhãn "First, ...", "Second, ..." cho các mục để nghe rõ cấu trúc.
READING_CHUNKS = [
    "",
]

# ── SHADOW — 10 câu cốt lõi cho file shadowing (VI → EN 1.2x → EN 1x → EN 0.85x) ──
SHADOW = [
    {"en": "", "vi": ""},
]
