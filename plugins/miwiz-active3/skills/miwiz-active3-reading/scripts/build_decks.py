#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build 3 Active-3 decks + permanent audio (Active 2 & 3) from a lesson.py.

Usage:  python3 build_decks.py <dir-containing-lesson.py>
Env:    MIWIZ_IDENTIFIER, MIWIZ_PASSWORD, GEMINI_API_KEY, [MIWIZ_GCS_KEY]
Resumable: writes perm_cache.json + state.json into the lesson dir.
"""
import json, os, sys, base64, subprocess, urllib.request, urllib.error, time, hashlib, datetime, importlib.util
from pathlib import Path

if len(sys.argv) < 2:
    sys.exit("Usage: build_decks.py <dir-containing-lesson.py>")
LESSON_DIR = Path(sys.argv[1]).resolve()
spec = importlib.util.spec_from_file_location("lesson", LESSON_DIR / "lesson.py")
L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L)


def _load_env(start):
    """Auto-load creds from a .miwiz-flc-config/.env found up the tree (don't override existing env)."""
    for base in [start, start.parent, start.parent.parent, start.parent.parent.parent]:
        f = base / ".miwiz-flc-config" / ".env"
        if f.exists():
            for line in f.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())
            return
_load_env(LESSON_DIR)

BASE = "https://miwizapp.com"
GKEY = os.environ["GEMINI_API_KEY"]
TTS_MODEL = "gemini-2.5-flash-preview-tts"
VOICE = "Leda"
BUCKET = "miwiz"
SLUG = "".join(c.lower() if c.isalnum() else "-" for c in L.TOPIC).strip("-")[:40] or "active3"
AUDIO_PREFIX = f"flashcard/audio/{SLUG}"
CACHE = LESSON_DIR / "perm_cache.json"
STATE = LESSON_DIR / "state.json"

# locate GCS service-account key
GCS_KEY = os.environ.get("MIWIZ_GCS_KEY")
if not GCS_KEY:
    for cand in [LESSON_DIR.parent / ".miwiz-flc-config" / "gcs-key.json",
                 LESSON_DIR.parent.parent / ".miwiz-flc-config" / "gcs-key.json",
                 Path.home() / ".config" / "miwiz" / "gcs-key.json"]:
        if cand.exists():
            GCS_KEY = str(cand); break
if not GCS_KEY or not Path(GCS_KEY).exists():
    sys.exit("GCS key not found — set MIWIZ_GCS_KEY to the service-account json path")

from google.oauth2 import service_account
from google.cloud import storage
_creds = service_account.Credentials.from_service_account_file(GCS_KEY)
_bucket = storage.Client(project=_creds.project_id, credentials=_creds).bucket(BUCKET)


def load(p, d):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else d


def save(p, o):
    p.write_text(json.dumps(o, ensure_ascii=False, indent=2), encoding="utf-8")


def mhttp(method, path, body=None, token=None):
    h = {"User-Agent": "Mozilla/5.0"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    d = None
    if body is not None:
        h["Content-Type"] = "application/json"
        d = json.dumps(body, ensure_ascii=False).encode("utf-8")
    last = None
    for attempt in range(5):
        req = urllib.request.Request(BASE + path, data=d, method=method, headers=h)
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            last = f"{method} {path} → {e.code}: {e.read().decode('utf-8','replace')[:200]}"
            if e.code in (500, 502, 503, 520, 521, 522, 524, 429) and attempt < 4:
                time.sleep(3 * (attempt + 1)); continue
            raise RuntimeError(last)
        except urllib.error.URLError:
            if attempt < 4:
                time.sleep(3 * (attempt + 1)); continue
            raise
    raise RuntimeError(last)


def tts_mp3(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{TTS_MODEL}:generateContent?key={GKEY}"
    body = {"contents": [{"parts": [{"text": text}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": VOICE}}}}}
    last = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                        headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=90) as r:
                part = json.loads(r.read())["candidates"][0]["content"]["parts"][0]["inlineData"]
            break
        except urllib.error.HTTPError as e:
            last = e
            if e.code in (429, 500, 503) and attempt < 3:
                time.sleep(1.5 * (attempt + 1)); continue
            raise
    else:
        raise last
    rate = 24000
    for tok in part.get("mimeType", "").split(";"):
        if "rate=" in tok:
            rate = int(tok.split("rate=")[1])
    pcm = base64.b64decode(part["data"])
    p = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "s16le",
                        "-ar", str(rate), "-ac", "1", "-i", "pipe:0", "-f", "mp3", "pipe:1"],
                       input=pcm, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        raise RuntimeError("ffmpeg: " + p.stderr.decode()[:200])
    return p.stdout


def gcs_upload(data, blob_name):
    blob = _bucket.blob(blob_name)
    signed = blob.generate_signed_url(version="v4", expiration=datetime.timedelta(minutes=15),
                                      method="PUT", content_type="audio/mpeg")
    req = urllib.request.Request(signed, data=data, method="PUT")
    req.add_header("Content-Type", "audio/mpeg")
    urllib.request.urlopen(req, timeout=90)
    return f"https://storage.googleapis.com/{BUCKET}/{blob_name}"


def audio_file(url):
    return {"url": url, "type": "audio", "file_name": url.split("/")[-1], "file_path": url}


def get_audio(cache, text):
    if text in cache:
        return cache[text]
    h = hashlib.md5(text.encode("utf-8")).hexdigest()[:16]
    url = gcs_upload(tts_mp3(text), f"{AUDIO_PREFIX}/{h}.mp3")
    cache[text] = url
    save(CACHE, cache)
    return url


# ── card builders ──
def c_a1(r):
    return {"type": 2, "question": f"What is the meaning of: \"{r['phrase']}\"?",
            "question_files": {"files": []},
            "explanation": {"text": f"{r['icon']} Example: {r['example']}\n🇻🇳 Nghĩa: {r['vi']}", "files": []},
            "answers": [{"answer_text": r["correct"], "is_correct": True, "order_index": 0, "answer_files": {"files": []}}]
            + [{"answer_text": d, "is_correct": False, "order_index": i + 1, "answer_files": {"files": []}} for i, d in enumerate(r["distractors"])]}


def c_a2(r, cache):
    url = get_audio(cache, r["full"])
    return {"type": 3, "question": f"Fill in the blank:\n{r['blank']}",
            "question_files": {"files": [audio_file(url)]},
            "explanation": {"text": f"{r['icon']} Full sentence:\n➡️ {r['full']}\n🇻🇳 {r['vi']}", "files": []},
            "answers": [{"answer_text": r["answer"], "is_correct": True, "order_index": 0, "answer_files": {"files": []}}]}


def c_a3(r, cache):
    url = get_audio(cache, r["en"])
    return {"type": 7, "question": f"Translate this sentence into English:\n\n🇻🇳 {r['vi']}",
            "question_files": {"files": []},
            "explanation": {"text": "", "files": [audio_file(url)]},
            "answers": [{"answer_text": r["en"], "is_correct": True, "order_index": 0, "answer_files": {"files": []}}]}


def main():
    token = mhttp("POST", "/api/v2/auth/login",
                  {"identifier": os.environ["MIWIZ_IDENTIFIER"], "password": os.environ["MIWIZ_PASSWORD"]})["data"]["access_token"]
    print("✅ login", flush=True)
    cache = load(CACHE, {})
    state = load(STATE, {"decks": {}})
    T = L.TOPIC
    decks = [
        (f"{T} — Active 1: MCQ (nghĩa cụm từ)", "Chọn nghĩa tiếng Anh đúng của các cụm từ trong bài đọc.",
         lambda: [c_a1(r) for r in L.ACTIVE1]),
        (f"{T} — Active 2: Nghe & điền chỗ trống", "Nghe audio và điền CỤM TỪ còn thiếu vào câu.",
         lambda: [c_a2(r, cache) for r in L.ACTIVE2]),
        (f"{T} — Active 3: Dịch Việt → Anh", "Dịch câu tiếng Việt sang tiếng Anh (có audio đọc mẫu ở mặt sau).",
         lambda: [c_a3(r, cache) for r in L.ACTIVE3]),
    ]
    results = []
    for di, (title, desc, build) in enumerate(decks):
        key = str(di)
        st = state["decks"].get(key, {})
        cards = build()
        deck_id = st.get("deck_id")
        if not deck_id:
            deck_id = mhttp("POST", "/api/deck", {"title": title, "description": desc,
                          "is_public": False, "price": 0, "test_time": 20, "tags": L.TAGS}, token=token)["data"]["deck"]["id"]
            st = {"deck_id": deck_id, "pushed": 0}
            state["decks"][key] = st; save(STATE, state)
            print(f"✅ deck#{deck_id}: {title}", flush=True)
        for i in range(st["pushed"], len(cards)):
            c = dict(cards[i]); c["deck_id"] = deck_id; c["order_index"] = i + 1
            try:
                mhttp("POST", "/api/flashcard", c, token=token)
                st["pushed"] = i + 1; save(STATE, state)
                print(f"  ✅ Active{di+1} [{i+1:02d}/{len(cards)}] type{c['type']}", flush=True)
            except Exception as e:
                print(f"  ❌ Active{di+1}[{i+1}] {e}", flush=True)
            time.sleep(0.08)
        n = mhttp("GET", f"/api/deck/{deck_id}", token=token)["data"]["deck"]["flashcard_count"]
        results.append((title, deck_id, n, len(cards)))
    print("\n" + "=" * 60, flush=True)
    for title, did, n, total in results:
        print(f"{n}/{total}  https://miwiz.net/flashcard/deck/{did}  — {title}", flush=True)
    print("=" * 60, flush=True)


if __name__ == "__main__":
    main()
