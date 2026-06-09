# Miwiz Skills — Claude plugin marketplace

Marketplace chứa các skill học tiếng Anh cho Miwiz. Hiện có:

- **miwiz-active5** — biến 1 đoạn hội thoại tiếng Anh thành **5 bộ flashcard Miwiz Active 5** + **1 file audio hội thoại 2 giọng**, tự đẩy lên app Miwiz.

---

## Cài trên bất kỳ Claude nào (Claude Code / Cowork)

Sau khi repo này đã ở trên GitHub (ví dụ `your-username/miwiz-skills-marketplace`):

```
/plugin marketplace add your-username/miwiz-skills-marketplace
/plugin install miwiz-active5@miwiz-skills
```

Cài xong, gõ **`/miwiz-active5-conversation`** là skill hiện ra. Dán hội thoại tiếng Anh vào là chạy.

Cập nhật khi repo đổi: `/plugin marketplace update miwiz-skills`

---

## Cách đưa repo này lên GitHub (làm 1 lần)

Trên máy có `git`, tại thư mục `miwiz-skills-marketplace/`:

```bash
git init
git add .
git commit -m "Miwiz Active 5 skill — initial release"
git branch -M main
# tạo repo rỗng tên miwiz-skills-marketplace trên github.com trước, rồi:
git remote add origin https://github.com/<your-username>/miwiz-skills-marketplace.git
git push -u origin main
```

> Repo để **public** thì ai có link cũng `marketplace add` được.

---

## Yêu cầu để skill chạy được (mỗi máy dùng)

Skill cần credentials của Miwiz (KHÔNG commit vào repo công khai). Trên máy chạy, đặt biến môi trường:

- `MIWIZ_IDENTIFIER`, `MIWIZ_PASSWORD` — tài khoản Miwiz
- `GEMINI_API_KEY` — Gemini TTS
- `MIWIZ_GCS_KEY` — đường dẫn tới service-account JSON của bucket `miwiz`

Cần `ffmpeg` và `pip install google-cloud-storage`.

---

## Cấu trúc repo

```
miwiz-skills-marketplace/
├── .claude-plugin/
│   └── marketplace.json          ← định nghĩa marketplace
└── plugins/
    └── miwiz-active5/
        ├── .claude-plugin/
        │   └── plugin.json        ← định nghĩa plugin
        └── skills/
            └── miwiz-active5-conversation/
                ├── SKILL.md
                ├── references/workflow.md
                ├── scripts/build_decks.py
                ├── scripts/make_dialogue.py
                └── assets/lesson_template.py
```
