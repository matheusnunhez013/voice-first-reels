"""Voiceover (Kokoro TTS via HyperFrames) + the exact time of every word (faster-whisper).

Usage:
  python voiceover.py --text vo.txt --out-dir <project> [--voice am_michael] [--lang en-us]
                      [--target 30] [--speed 1.0]

- With --target (seconds) it measures the take at speed 1.0 and recomputes the speed
  to fit the target (clamped to 0.9-1.18; faster than that sounds rushed).
- Writes <out-dir>/vo.wav and <out-dir>/words.json ([{"t","s","e"}], times in seconds).
- Prints the transcript so you can check pronunciation: if Whisper understands every
  word, your audience will too.
- Recorded your own voice (or used ElevenLabs)? Skip the TTS part and only run Whisper on it.
Requires: node/npx (hyperframes) and `pip install faster-whisper`.
"""
import argparse, json, subprocess, wave, os, sys


def tts(text, voice, lang, speed, out):
    cmd = ["npx", "hyperframes", "tts", text, "-v", voice, "-l", lang, "-s", f"{speed:.3f}", "-o", out]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=(os.name == "nt"))


def dur(path):
    with wave.open(path) as w:
        return w.getnframes() / w.getframerate()


ap = argparse.ArgumentParser()
ap.add_argument("--text", required=True)
ap.add_argument("--out-dir", required=True)
ap.add_argument("--voice", default="am_michael")  # en-us: am_michael, am_puck, af_heart ...
ap.add_argument("--lang", default="en-us")
ap.add_argument("--speed", type=float, default=1.0)
ap.add_argument("--target", type=float, default=None)
ap.add_argument("--model", default="medium")
a = ap.parse_args()
sys.stdout.reconfigure(encoding="utf-8")

os.makedirs(a.out_dir, exist_ok=True)
vo = os.path.join(a.out_dir, "vo.wav")
speed = a.speed
if a.target:
    tts(a.text, a.voice, a.lang, 1.0, vo)
    speed = min(1.18, max(0.9, dur(vo) / a.target))
tts(a.text, a.voice, a.lang, speed, vo)
print(f"voice={a.voice} speed={speed:.3f} duration={dur(vo):.2f}s")

from faster_whisper import WhisperModel
m = WhisperModel(a.model, device="cpu", compute_type="int8")
segs, _ = m.transcribe(vo, language=a.lang.split("-")[0], word_timestamps=True)
words = [{"t": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)} for s in segs for w in s.words]
with open(os.path.join(a.out_dir, "words.json"), "w", encoding="utf8") as f:
    json.dump(words, f, ensure_ascii=False, indent=0)
print(" ".join(f'{w["t"]}@{w["s"]}' for w in words))
