#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render shadowing audio for lesson.SHADOW (10 key sentences).

Per sentence: VI(Kore,1x) -> 5s -> EN(1.2x) -> p -> EN(1x) -> p -> EN(0.85x); 5s between.
p = 2-4s by length:  p = max(2, min(4, round(dur_1x * 0.4))).
EN voice = Leda, VI voice = Kore. EN generated once at 1x; speeds via ffmpeg atempo.

Usage:  python3 make_shadowing.py <dir-containing-lesson.py>
Env:    GEMINI_API_KEY  (+ GCS key for public upload, optional)
Resumable: vi_NN.pcm / en_NN.pcm cached in <dir>/_shadow_pcm; assemble when all present.
Output:  <dir>/Shadowing_<TopicSlug>_<N>sentences.mp3  (+ public GCS URL if key available)
"""
import json, os, sys, base64, subprocess, urllib.request, urllib.error, time, datetime, importlib.util
from pathlib import Path

if len(sys.argv) < 2:
    sys.exit("Usage: make_shadowing.py <dir-containing-lesson.py>")
LESSON_DIR = Path(sys.argv[1]).resolve()
spec = importlib.util.spec_from_file_location("lesson", LESSON_DIR / "lesson.py")
L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L)


def _load_env(start):
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

GKEY = os.environ["GEMINI_API_KEY"]
TTS_MODEL = "gemini-2.5-flash-preview-tts"
RATE = 24000
SENTS = L.SHADOW
PCM = LESSON_DIR / "_shadow_pcm"; PCM.mkdir(exist_ok=True)
SLUG = "".join(c for c in L.TOPIC.title() if c.isalnum()) or "Reading"
SLUG_LO = "".join(c.lower() if c.isalnum() else "-" for c in L.TOPIC).strip("-")[:40] or "active3"
OUT = LESSON_DIR / f"Shadowing_{SLUG}_{len(SENTS)}sentences.mp3"


def tts_pcm(text, voice):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{TTS_MODEL}:generateContent?key={GKEY}"
    body = {"contents": [{"parts": [{"text": text}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                        headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=120) as r:
                return base64.b64decode(json.loads(r.read())["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 503) and attempt < 3:
                time.sleep(5 * (attempt + 1)); continue
            raise


def retempo(pcm, factor):
    if abs(factor - 1.0) < 1e-3:
        return pcm
    return subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "s16le",
                           "-ar", str(RATE), "-ac", "1", "-i", "pipe:0",
                           "-filter:a", f"atempo={factor}", "-f", "s16le", "pipe:1"],
                          input=pcm, stdout=subprocess.PIPE, check=True).stdout


def sil(sec):
    return b"\x00\x00" * int(RATE * sec)


def dur(pcm):
    return len(pcm) / (RATE * 2)


def gcs_upload(path, blob_name):
    key = os.environ.get("MIWIZ_GCS_KEY")
    if not key:
        for c in [LESSON_DIR.parent / ".miwiz-flc-config" / "gcs-key.json",
                  LESSON_DIR.parent.parent / ".miwiz-flc-config" / "gcs-key.json"]:
            if c.exists():
                key = str(c); break
    if not key or not Path(key).exists():
        return None
    from google.oauth2 import service_account
    from google.cloud import storage
    creds = service_account.Credentials.from_service_account_file(key)
    bucket = storage.Client(project=creds.project_id, credentials=creds).bucket("miwiz")
    blob = bucket.blob(blob_name)
    signed = blob.generate_signed_url(version="v4", expiration=datetime.timedelta(minutes=15),
                                      method="PUT", content_type="audio/mpeg")
    req = urllib.request.Request(signed, data=path.read_bytes(), method="PUT")
    req.add_header("Content-Type", "audio/mpeg")
    urllib.request.urlopen(req, timeout=180)
    return f"https://storage.googleapis.com/miwiz/{blob_name}"


jobs = []
for i, s in enumerate(SENTS):
    jobs.append((f"vi_{i:02d}", s["vi"], "Kore"))
    jobs.append((f"en_{i:02d}", s["en"], "Leda"))
todo = [(n, t, v) for n, t, v in jobs if not (PCM / f"{n}.pcm").exists()]
print(f"{len(jobs)-len(todo)} cached, {len(todo)} to do", flush=True)
for n, t, v in todo:
    (PCM / f"{n}.pcm").write_bytes(tts_pcm(t, v))
    print(f"  {n} ok", flush=True); time.sleep(0.3)

if any(not (PCM / f"{n}.pcm").exists() for n, _, _ in jobs):
    print("not all ready — run again"); sys.exit(0)

out = b""
for i in range(len(SENTS)):
    vi = (PCM / f"vi_{i:02d}.pcm").read_bytes()
    en = (PCM / f"en_{i:02d}.pcm").read_bytes()
    p = max(2, min(4, round(dur(en) * 0.4)))
    out += vi + sil(5) + retempo(en, 1.2) + sil(p) + en + sil(p) + retempo(en, 0.85)
    if i < len(SENTS) - 1:
        out += sil(5)
    print(f"  sentence {i+1}: en_1x={dur(en):.1f}s pause={p}s", flush=True)

subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "s16le",
                "-ar", str(RATE), "-ac", "1", "-i", "pipe:0", "-b:a", "128k", str(OUT)],
               input=out, check=True)
url = gcs_upload(OUT, f"flashcard/audio/{SLUG_LO}/shadowing/{OUT.name}")
total = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", str(OUT)],
                       capture_output=True, text=True).stdout.strip()
print(f"DONE: {OUT}  ({float(total):.0f}s)", flush=True)
if url:
    print(f"URL: {url}", flush=True)
