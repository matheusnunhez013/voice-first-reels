# voice-first-reels

A Claude Code skill that turns a video idea into a finished 9:16 video (Reels, TikTok, Shorts): script → voiceover → word-level timings → shot list → animated HyperFrames composition → soundtrack → MP4 → frame-by-frame review.

> Resumo em português: uma skill para o Claude Code que transforma uma ideia em um vídeo vertical pronto. A voz é gravada primeiro, o Whisper mede o tempo de cada palavra, e todas as legendas, cortes e animações são posicionados nesses tempos.

## Problem

Short videos made by AI tools usually look generated: captions drift from the voice, cuts land on random frames, and the music fights the narration. Editing by hand fixes it, but it takes hours per video.

## How it works

The rule behind it: **the voice is the clock.** The voiceover is produced before any scene is planned, and every caption, cut and animation is placed on the second the word is spoken.

| Step | What happens | Where |
|---|---|---|
| 1. Script | Hook → diagnosis → turn → proof → CTA, one idea per sentence | `SKILL.md` |
| 2. Voiceover | Kokoro TTS, auto speed to hit the target length, then faster-whisper word timestamps → `vo.wav` + `words.json` | `scripts/voiceover.py` |
| 3. Shot list | Each scene tied to the trigger words and their timestamps | `SKILL.md`, `references/example-script.md` |
| 4. Assets | Procedural paper, film grain, light rays, grid, flare; logo background removal | `scripts/gen_textures.py` |
| 5. Composition | HyperFrames HTML with layered scenes, kinetic type and camera moves | `references/motion-recipes.md` |
| 6. Soundtrack | Procedural music bed, low hits, max 3 whooshes, ducking under the voice → 48 kHz `mix.wav` | `scripts/soundtrack.py` |
| 7. Review | Draft render, contact sheet checked against the shot list, final H.264 encode | `SKILL.md` |

One detail that cost a full round to find: faster-whisper expects 16 kHz audio. Passing a 24 kHz array stretches every timestamp by 1.5×, so the audio is resampled first.

## Stack

Python (numpy, scipy, Pillow, faster-whisper) · Kokoro TTS · HyperFrames (HTML/GSAP) · ffmpeg · Claude Code skills

## Install

1. Requirements: [Claude Code](https://claude.com/claude-code), Node.js (for `npx hyperframes`), Python 3.10+ and ffmpeg.
2. Python packages:
   ```bash
   pip install faster-whisper numpy scipy pillow
   ```
3. Copy this folder to `~/.claude/skills/voice-first-reels/` (Windows: `C:\Users\<you>\.claude\skills\voice-first-reels\`).
4. Restart Claude Code. The skill loads when you ask for a video.

## Use

> Make a 30-second reel about my coffee shop's new cold brew. CTA: "order on our site".

Claude writes the script, generates and times the voice, plans each scene on those timings, builds the animation and renders the MP4. Follow-ups such as "captions bigger" or "less sound" iterate on the same project instead of starting over.

The scripts also run on their own:

```bash
python scripts/voiceover.py --text vo.txt --out-dir out --target 30
python scripts/gen_textures.py --out assets --base "#141414" --accent "#FF6B35"
python scripts/soundtrack.py --cues cues.json --vo out/vo.wav --out assets/mix.wav
```

## Limits

- The default voice is synthetic (Kokoro, English voices). For better voices, record your own or use ElevenLabs and run only the Whisper timing step.
- Rendering depends on HyperFrames and runs locally. There's no hosted version.

## License

MIT

Made by [@matheus.builds](https://instagram.com/matheus.builds) — building things solo with AI.
