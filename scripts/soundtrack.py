"""Procedural music bed + subtle SFX + voiceover with ducking -> mix.wav (48 kHz stereo).

Usage:
  python soundtrack.py --cues cues.json --vo vo.wav --out assets/mix.wav

cues.json (times in seconds on the VIDEO timeline, vo_offset already added):
{
  "duration": 32.6,          // total video length
  "vo_offset": 0.15,         // voice delay inside the video
  "bpm": 110,
  "chords": [[57,60,64],[53,57,60],[48,52,55],[55,59,62]],   // MIDI, 2 bars each
  "lift": 11.6,              // where the music "opens up" (snare, arp, eighth-note bass)
  "breaks": [[25.3, 27.9]],  // drum-free stretches (a breath before the CTA, for example)
  "hits": [[4.3, 0.8], [11.6, 1.0]],   // soft low impacts [time, gain] on key words
  "whooshes": [3.45, 11.35, 27.85],    // 3 max: only the most important transitions
  "risers": [[11.6, 1.3], [27.9, 1.4]],// [arrival time, length]
  "sub_drops": [25.4]
}

Philosophy: sound stays in the background. No notification "plings" (dings, glass, ticks,
clicks). Low, quiet whooshes on a few transitions only. Low hits on key words and a music
bed ducked under the voice carry the rhythm.
"""
import argparse, json, wave
import numpy as np
from scipy.signal import lfilter

ap = argparse.ArgumentParser()
ap.add_argument("--cues", required=True); ap.add_argument("--vo", required=True); ap.add_argument("--out", required=True)
a = ap.parse_args()
C = json.load(open(a.cues, encoding="utf8"))
SR = 48000; DUR = C["duration"]; N = int(SR * DUR); t = np.arange(N) / SR
mus = np.zeros(N); sfx = np.zeros(N); rng = np.random.default_rng(4)


def lp(s, fc): al = np.exp(-2 * np.pi * fc / SR); return lfilter([1 - al], [1, -al], s)
def hp(s, fc): return s - lp(s, fc)
def env(n, at, d):
    e = np.ones(n); ai = max(1, int(at * SR)); e[:ai] = np.linspace(0, 1, ai)
    e[ai:] = np.exp(-np.arange(n - ai) / (d * SR)); return e
def add(buf, sig, at, g=1.0):
    i = int(at * SR)
    if i < 0: sig = sig[-i:]; i = 0
    j = min(N, i + len(sig))
    if i < N: buf[i:j] += sig[:j - i] * g
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def saw(f, n, det=(-.005, .005)):
    tt = np.arange(n) / SR; return sum((tt * f * (1 + d)) % 1 * 2 - 1 for d in det) / len(det)
def in_break(b): return any(s0 < b < s1 for s0, s1 in C.get("breaks", []))


beat = 60 / C.get("bpm", 110); bar = 4 * beat; LIFT = C.get("lift", DUR * .35); chords = C["chords"]
for k in range(int(DUR / (2 * bar)) + 1):
    ch = chords[k % len(chords)]; root = ch[0]; st = k * 2 * bar; n = int(2 * bar * SR); tt = np.arange(n) / SR
    e = np.minimum(1, tt / .6) * np.minimum(1, (2 * bar - tt) / .6)
    add(mus, lp(sum(saw(hz(m), n) for m in ch), 700 if st < LIFT else 1400) * e, st, .05)
    step = beat / 2 if st >= LIFT - 2 * bar else 2 * bar
    for i0 in range(int(round(2 * bar / step))):
        bt = st + i0 * step
        if bt < 2 or in_break(bt) or bt > DUR - 1.2: continue
        ln = int(min(step, .5) * SR)
        s = np.sin(2 * np.pi * hz(root - 24) * np.arange(ln) / SR) + .35 * lp(saw(hz(root - 24), ln), 400)
        add(mus, s * env(ln, .005, .18 if step < 1 else .9), bt, .22 if bt >= LIFT else .14)
    notes = ch + [ch[1] + 12, ch[2] + 12]
    for i0 in range(32):
        bt = st + i0 * beat / 4
        if bt < LIFT or bt > DUR - 1.4 or in_break(bt): continue
        ln = int(.18 * SR)
        add(mus, lp(saw(hz(notes[(i0 * 3) % len(notes)] + 12), ln, (0,)), 2600) * env(ln, .002, .06), bt, .035)

ln = int(.45 * SR); tt = np.arange(ln) / SR
K = np.sin(2 * np.pi * np.cumsum(42 + 110 * np.exp(-tt / .035)) / SR) * env(ln, .001, .17)
ln = int(.3 * SR); tt = np.arange(ln) / SR
SN = hp(rng.standard_normal(ln), 1500) * env(ln, .001, .07) * .7 + np.sin(2 * np.pi * 190 * tt) * env(ln, .001, .05) * .5
b = 0.0
while b < DUR - 1.4:
    i = int(round(b / beat))
    if not in_break(b):
        if b >= LIFT:
            add(mus, K, b, .6)
            if i % 2: add(mus, SN, b, .35)
            ln = int(.08 * SR); add(mus, hp(rng.standard_normal(ln), 7000) * env(ln, .001, .02), b + beat / 2, .09)
        elif b > 2 and i % 2 == 0:
            add(mus, K, b, .4)
    b += beat


def soft_hit():
    ln = int(1.6 * SR); tt = np.arange(ln) / SR
    return lp(np.sin(2 * np.pi * np.cumsum(34 + 40 * np.exp(-tt / .06)) / SR) * env(ln, .004, .55), 300)
def airwhoosh():
    ln = int(.9 * SR); x = np.linspace(0, 1, ln)
    return lp(lp(rng.standard_normal(ln), 900), 900) * np.sin(np.pi * x) ** 2 * 2.2
def riser(d):
    ln = int(d * SR); x = np.linspace(0, 1, ln)
    return (lp(rng.standard_normal(ln), 2500) * x ** 2 + np.sin(2 * np.pi * np.cumsum(150 + 900 * x ** 2) / SR) * x ** 3 * .35) * .6
def sub_drop():
    ln = int(SR); tt = np.arange(ln) / SR
    return np.sin(2 * np.pi * np.cumsum(90 - 60 * tt) / SR) * env(ln, .01, .4)


for at, g in C.get("hits", []): add(sfx, soft_hit() * g, at, .5)
for at in C.get("whooshes", [])[:3]: add(sfx, airwhoosh(), at - .45, .12)
for at, d in C.get("risers", []): add(sfx, riser(d), at - d, .17)
for at in C.get("sub_drops", []): add(sfx, sub_drop(), at, .35)

with wave.open(a.vo) as w:
    sr = w.getframerate(); ch = w.getnchannels()
    raw = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64).reshape(-1, ch).mean(1) / 32768
vo = np.interp(np.arange(int(len(raw) * SR / sr)) / SR, np.arange(len(raw)) / sr, raw)
vo = hp(vo / np.abs(vo).max() * .85, 90); vo = np.tanh(vo * 1.6) / np.tanh(1.6)
V = np.zeros(N); i = int(C.get("vo_offset", .15) * SR); V[i:i + len(vo)] = vo[:max(0, N - i)]
venv = lp(np.abs(V), 5); duck = 1 - .6 * np.clip(venv / (venv.max() * .22 + 1e-9), 0, 1)
fade = np.clip((DUR - t) / 1.4, 0, 1)
M = mus * duck * fade * .95
out = np.tanh((M + sfx * fade + V * .95) * 1.05) * .93
R = out.copy(); d = int(.012 * SR); R[d:] += .3 * (M[:-d] - M[d:])
st = np.clip(np.stack([out, R], 1), -1, 1)
with wave.open(a.out, "w") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype(np.int16).tobytes())
print("mix ->", a.out)
