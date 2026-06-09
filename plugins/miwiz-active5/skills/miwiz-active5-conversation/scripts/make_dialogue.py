#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render a conversation (lesson.DIALOGUE) to ONE mp3 with two voices.

Usage:  python3 make_dialogue.py <dir-containing-lesson.py>
Env:    GEMINI_API_KEY
Resumable: each turn cached as <dir>/chunks/NN.mp3; concat when all present.
Output:  <dir>/<TopicSlug>_dialogue.mp3
"""
import json, os, sys, base64, subprocess, urllib.request, urllib.error, time, importlib.util
from pathlib import Path

if len(sys.argv) < 2:
    sys.exit("Usage: make_dialogue.py <dir-containing-lesson.py>")
LESSON_DIR = Path(sys.argv[1]).resolve()
spec = importlib.util.spec_from_file_location("lesson", LESSON_DIR / "lesson.py")
L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L)

GKEY = os.environ["GEMINI_API_KEY"]
TTS_MODEL = "gemini-2.5-flash-preview-tts"
VOICE = getattr(L, "VOICE", {"A": "Kore", "B": "Puck"})
DIALOGUE = L.DIALOGUE
CHUNKS = LESSON_DIR / "chunks"; CHUNKS.mkdir(exist_ok=True)
SLUG = "".join(c for c in L.TOPIC.title() if c.isalnum()) or "Conversation"
OUT = LESSON_DIR / f"{SLUG}_dialogue.mp3"


def tts_pcm(text, voice):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{TTS_MODEL}:generateContent?key={GKEY}"
    body = {"contents": [{"parts": [{"text": text}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
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
    return base64.b64decode(part["data"]), rate


def chunk(i, sp, text):
    p = CHUNKS / f"{i:02d}.mp3"
    if p.exists() and p.stat().st_size > 0:
        return False
    pcm, rate = tts_pcm(text, VOICE[sp])
    proc = subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "s16le",
                           "-ar", str(rate), "-ac", "1", "-i", "pipe:0", str(p)],
                          input=pcm, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.decode()[:200])
    return True


def main():
    made = 0
    for i, (sp, text) in enumerate(DIALOGUE):
        if chunk(i, sp, text):
            made += 1
            print(f"  ✅ turn {i:02d} [{sp}/{VOICE[sp]}]", flush=True)
        time.sleep(0.1)
    done = sum(1 for i in range(len(DIALOGUE)) if (CHUNKS / f"{i:02d}.mp3").exists())
    print(f"chunks: {done}/{len(DIALOGUE)} (new {made})", flush=True)
    if done < len(DIALOGUE):
        print("⏳ rerun to finish.", flush=True); return
    sil = CHUNKS / "_sil.mp3"
    if not sil.exists():
        subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi",
                        "-i", "anullsrc=r=24000:cl=mono", "-t", "0.45", str(sil)], check=True)
    lines = []
    for i in range(len(DIALOGUE)):
        lines.append(f"file '{(CHUNKS / f'{i:02d}.mp3').as_posix()}'")
        if i < len(DIALOGUE) - 1:
            lines.append(f"file '{sil.as_posix()}'")
    (CHUNKS / "list.txt").write_text("\n".join(lines), encoding="utf-8")
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat",
                    "-safe", "0", "-i", str(CHUNKS / "list.txt"), "-c:a", "libmp3lame", "-q:a", "4", str(OUT)], check=True)
    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", str(OUT)], capture_output=True, text=True).stdout.strip()
    print(f"\n🎧 {OUT.name} | {float(dur):.1f}s | {OUT.stat().st_size//1024} KB | "
          f"A={VOICE.get('A')} B={VOICE.get('B')}", flush=True)


if __name__ == "__main__":
    main()
