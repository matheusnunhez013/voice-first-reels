# voice-first-reels 🦈

A Claude Code skill that turns a video idea into a finished vertical video (Reels / TikTok / Shorts): script → voiceover → word-level timings → shot list → animated HyperFrames composition → subtle soundtrack → MP4 → frame-by-frame review.

The one rule behind it: **the voice is the clock.** Every caption, cut and animation is placed on the exact second the word is spoken, measured by Whisper — that's why it looks hand-edited.

## Install

1. You need [Claude Code](https://claude.com/claude-code), Node.js (for `npx hyperframes`), Python 3.10+ and ffmpeg.
2. Python packages:
   ```bash
   pip install faster-whisper numpy scipy pillow
   ```
3. Copy this folder into your skills directory:
   - macOS / Linux: `~/.claude/skills/voice-first-reels/`
   - Windows: `C:\Users\<you>\.claude\skills\voice-first-reels\`
4. Restart Claude Code. The skill loads by itself when you ask for a video.

## Use

Just ask, e.g.:

> Make a 30-second reel about my coffee shop's new cold brew. CTA: "order on our site".

> Make a 60-second dialogue video: a skeptic asks why my app is better, I answer. End with "Comment APP".

Claude writes the script, generates the voice, times every word, plans each scene on those timings, builds the animation and renders the MP4. Then ask for changes ("make it 10x better", "less sound", "captions bigger") and it iterates instead of starting over.

## What's inside

```
SKILL.md                       the process Claude follows (7 steps)
references/example-script.md   a finished dialogue script, beat by beat
references/motion-recipes.md   typography, camera, light, transitions, pitfalls
references/procedural-assets.md textures, cut-outs, pixel/code character effects
scripts/voiceover.py           TTS (Kokoro) + Whisper word timings -> vo.wav + words.json
scripts/soundtrack.py          procedural music + subtle SFX + ducking -> mix.wav
scripts/gen_textures.py        paper, grain, light rays, grid, flare, logo cut-out
```

## Tips

- Better voices: generate them in ElevenLabs (or record yourself) and let the skill time them with Whisper.
- Keep sound subtle: no notification "pings", max 3 whooshes.
- Always look at the contact sheet before the final render — it catches 90% of problems.

Made by [@matheus.builds](https://instagram.com/matheus.builds) — building things solo with AI.
