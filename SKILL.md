---
name: voice-first-reels
description: Turns a video idea (brand, product, service, concept, story) into a finished 9:16 Reel/Short/TikTok — script with voiceover and on-screen text, a voiceover whose every word is timed by Whisper, a shot list locked to those timings, code-generated assets, a layered HyperFrames composition with kinetic typography, a subtle soundtrack, an MP4 render and a frame-by-frame review. Use whenever the user sends a video idea, asks for a reel, short, TikTok, video ad or launch video, asks for a reel script or shot list, or asks to redo/improve a reel like this — even if they don't say "reel" or "HyperFrames".
---

# Voice-first reels: from idea to MP4

The core idea: **the voiceover is the clock of the video**. Every word on screen, every cut, every move and every sound hit comes from the real time each word is spoken, measured by Whisper. That is what makes the video feel hand-edited. So the voice is produced **before** any scene is planned, and the plan is built on real timings, not guesses.

Deliverables, in the project folder:
1. `script.md` — hook, voiceover, on-screen text, caption and hashtags.
2. `DIRECTION.md` — concept, visual direction and the **shot list**: every scene tied to the words that trigger it (format below).
3. `<slug>-9x16.mp4` — the rendered video, plus the editable `hyperframes-project/`.

Quality bar: `references/example-script.md` (a finished dialogue script) and `references/motion-recipes.md` (motion, layers and typography that worked). Read both before starting.

## Step 0 — Understand the idea (fast)

Collect from the request and the project: audience, goal, offer, CTA, palette and fonts, real assets (logo, product photo, screenshots of results). Ask only what blocks you — usually the CTA and publishing constraints. Default length: 25–35 s for ads, 60–90 s for story/dialogue formats.

## Step 1 — Script (`script.md`)

A structure that works: **hook (pain/question) → diagnosis → turn (the solution) → delivery → proof → promise → CTA**. Short, spoken sentences, one idea each — every sentence becomes a scene or a beat. Proof numbers only from a real source, spelled out in the voiceover ("forty-five thousand") so TTS reads them right. On-screen text short, uppercase, one idea per scene. Add a disclaimer when you show results.

Dialogue format (two characters): the skeptic asks, the expert answers, a line every 1–4 s, a joke every 10–15 s. Questions end with "?" — keep that "?" in the captions.

## Step 2 — Voiceover with the time of every word

```bash
python <skill>/scripts/voiceover.py --text vo.txt --out-dir <project> --target 30
```

Produces `vo.wav` (Kokoro; English voices like `am_michael`) and `words.json`. Check the printed transcript: if Whisper recognises every word, the pronunciation is fine. Way over the target? Cut words instead of speeding past ~1.15× (it sounds rushed).

Better voices (ElevenLabs, your own recording): generate/record, then run only the Whisper part. One file per line is easiest; one long take also works if you leave ~1 s pauses and split it by aligning Whisper's words to the script. Write tricky names phonetically for the TTS ("Comfy U I", "V-RAM") and fix them back in the captions.

**Gotcha:** faster-whisper expects 16 kHz audio. If you pass it a raw numpy array at 24 kHz, every timestamp stretches ×1.5. Resample first.

## Step 3 — Direction and shot list (`DIRECTION.md`)

First the direction in a few lines: **concept** (one sentence), **palette** (hex), **typography**, **texture/light**, **visual thread** (the object or shape that runs through the video and transforms — it's what makes it feel like a film), and the **real assets** with paths.

Then the shot list. This is where effort pays off: the more concrete, the better the video. One scene per script beat:

```markdown
### Scene N — <name> · <start>–<end> s

- **Trigger words:** "sell" @2.35 → portal word · "enough" @4.33 → underline + hit
- **Screen:** exact text, where, and how it enters (letter by letter, word by word)
- **Layers:** back = … · middle = real object/asset … · front = labels, lines, data
- **Camera:** macro → pull back / push / tilt / parallax
- **Assets:** real (path) and procedural to generate (what)
- **Transition → next:** which shape/colour/direction of this scene becomes the next
- **Sound:** low hit? whoosh (max 3 in the whole video)? breath?
```

Times come from `words.json` plus the voice offset in the video. Every transition reuses a shape, colour or direction from the previous element (the product shrinks into an ad; an orbit flattens into a laptop screen; a panel folds into the logo) — that is what separates "film" from "slides". The shot list is also the checklist for the composition: every line must exist in the HTML.

## Step 4 — Assets

- **Real first:** product without background (`npx hyperframes remove-background photo.jpg -o assets/product.png`), flat-background logos cut out (`python <skill>/scripts/gen_textures.py --key-logo logo.png --name logo.png --out assets`), result screenshots untouched.
- **Procedural** (`python <skill>/scripts/gen_textures.py --out assets --base "#141414" --accent "#FF6B35"`): paper/graphite, 6 grain frames, light rays, technical grid, anamorphic flare.
- **Idea-specific:** a short Python generator (numpy/scipy/PIL) for whatever the shot list needs. Techniques in `references/procedural-assets.md`.
- Preview every asset before using it. Don't invent real people, realistic faces or third-party brands/characters.

## Step 5 — HyperFrames composition

Read the HyperFrames core contract if you haven't this session, and `references/motion-recipes.md` before composing. Structure: `index.html` with a 1080×1920 `#root`, a camera (`#cam`) holding the scenes as `.clip` elements (`data-start/data-duration/data-track-index`), global layers on top (HUD, light leak, grain, vignette, flash) and one `<audio>` with the mix. One paused GSAP timeline in `window.__timelines["main"]`, using the shot-list times. Wrap the script in an IIFE.

Minimum finish:
- **Three layers per scene:** giant type/outline behind, real object in the middle, technical data in front.
- **Kinetic typography:** letter-by-letter masked reveal on the exact word; accent underline on impact words.
- **Living camera:** subtle continuous 3D tilt, punch on beats, parallax, motion blur on entrances.
- **Living content** inside cards and screens (text typing, chart drawing) instead of static icons.
- **Instagram safe zone:** nothing important above y≈250 or below y≈1536; CTA readable for ≥ 2.2 s.
- **Honest proof:** real screenshots cropped/highlighted, counters that end on the exact number.

Seek-safety rules that cost a round each:
- Don't toggle `visibility` on children of a `.clip` — a child set to `visible` shows even when the clip is hidden. Toggle `opacity` on a wrapper instead, with `fromTo(..., {immediateRender:false})`.
- Thousands of `tl.set` calls can crash the runtime; animate grain with one `steps()` tween on `backgroundPosition`.
- Sprite sheets: tween `backgroundPosition` to `-(frames-1)*width` with `steps(frames-1)`, or the last step lands on an empty frame.
- Background/footage videos need dense keyframes: re-encode with `-g 30`.

## Step 6 — Soundtrack (subtle)

Build `cues.json` from the shot list's **Sound** lines and run `python <skill>/scripts/soundtrack.py --cues cues.json --vo vo.wav --out assets/mix.wav` (format inside the script). Sound stays in the background: **no notification "plings"**, low whoosh on at most 3 key transitions, low hits on the strongest words, music that opens at the turn and breathes before the CTA, ducking under the voice.

## Step 7 — Render, review, deliver

1. `npx hyperframes check` — fix every lint error.
2. Draft: `npx hyperframes render -o draft.mp4 -q draft`, then a contact sheet:
   `ffmpeg -i draft.mp4 -vf "fps=1/2.5,scale=270:-1,tile=8x3" -frames:v 1 sheet.png`. **Look at the sheet** against the shot list: text over the object, clipped accents, words glued together, elements too early, safe zone. When in doubt, pull the full-res frame (`-ss <t> -frames:v 1`).
3. Final: `-q delivery`, then re-encode for posting:
   `ffmpeg -i final-hi.mp4 -c:v libx264 -preset slow -b:v 16M -maxrate 20M -bufsize 32M -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k -movflags +faststart <slug>-9x16.mp4`
4. Copy HTML, scripts, cues, `words.json` and assets into `hyperframes-project/` next to the MP4.

Report honestly: real length vs. target, synthetic voice, what is illustrative vs. real, and any check that failed.

## Iterations ("make it 10x better")

Don't start over: keep script, voice and timings, save the previous version with a suffix, and raise the finish in layers — richer assets, more depth (DOF, parallax, volumetric light), living content in cards, stronger continuity transitions, masked typography and underlines. Render `-v2`, `-v3`… applying the feedback first.
