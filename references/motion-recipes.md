# Motion, layers and typography recipes (HyperFrames + GSAP)

Everything here was used in finished reels. Copy the snippets and adapt.

## Skeleton

```html
<div id="root" data-composition-id="main" data-start="0" data-duration="32.6" data-width="1080" data-height="1920">
  <div id="cam">                       <!-- camera: punch, 3D tilt, paper background -->
    <div id="gridL"></div>             <!-- technical grid (slow parallax) -->
    <div id="sA" class="scene clip" data-start="0" data-duration="11.55" data-track-index="1">…</div>
    <div id="sB" class="scene clip" data-start="11.45" data-duration="1.1" data-track-index="2">…</div>
  </div>
  <div id="hud" class="clip" …></div>  <!-- registration marks, 01/08 counter, progress bar -->
  <div id="leak" class="clip" …></div> <!-- light leak, screen blend -->
  <div id="grain" class="clip" …></div><!-- overlay grain -->
  <div id="vig" class="clip" …></div>
  <div id="wash" class="clip" …></div> <!-- colour flash on big turns -->
  <audio src="assets/mix.wav" data-start="0" data-duration="32.6" data-track-index="9" data-volume="1"></audio>
</div>
```

Neighbouring scenes alternate `data-track-index` 1/2 and overlap ~0.1 s for the transition.

## Kinetic typography

- Heavy 900 display face with `letter-spacing:-.045em; line-height:.86`, a 500 support weight, mono for data.
- Letter-by-letter reveal: split each `.split` into `<span class="ch"><i>c</i></span>` and animate `yPercent:140→0, rotation:5→0`, `stagger .03`, `power4.out`, on the word's time.
- **Accents/diacritics**: the `.ch{overflow:hidden}` mask clips them. Use `padding:.3em .005em .05em; margin-top:-.3em`.
- **Spaces between words**: `.wd` spans side by side have no real space; use `margin:0 .13em` and `white-space:nowrap`.
- Accent underline: an absolute `<span class="ul">` inside the word, `scaleX 0→1` 0.35 s after the word.
- Giant outline behind (`-webkit-text-stroke`, alpha ~.07) sliding slowly: the typographic back layer.
- Counters: tween an object `{v}` with `onUpdate` writing the text; end on the exact source number.
- Social-style captions (one word at a time): huge white 900 weight, `-webkit-text-stroke:14px #000; paint-order:stroke fill`, keywords in the accent colour, keep "?" on questions.

## Camera and depth

- Continuous tilt: `#cam` rotationX/Y ±1.2°, `transformPerspective:2200`, 4 s yoyo.
- Punch on beats: `fromTo("#cam",{scale:1.03},{scale:1,duration:.45,immediateRender:false})`.
- Slow push toward whoever is talking: `fromTo("#cam",{scale:1,transformOrigin:"<x>px 1500px"},{scale:1.035,duration:<line length>})`.
- Parallax: grid and outlines move slower than the object; blurred plates (`filter:blur(16px)`) cross in the foreground.
- Entrances with `filter:blur(10–14px)→0` + scale = cheap motion blur.
- Macro → pull back: start the object at `scale:3.4` with `xPercent` on the detail and pull back with `expo.out`.

## Light

- Rays (`rays.png`, screen blend) rotating 10–15° behind the object/brand.
- Glass shine: a div with `mask:url(object.png)` and a band gradient animating `background-position` 100%→-50%.
- Anamorphic flare the instant the brand forms and on the CTA click.
- Floor reflection: a `scaleY(-1)` copy with a gradient mask, opacity ~.15.

## Continuity transitions

- Big product → shrinks into an ad card → zoom-out reveals a sea of competing ads.
- Portal word: `scale:26` on an accent-coloured word + colour flash.
- Collapse: everything `scale:0` + lines converging to the centre → shards assemble the brand.
- An orbit flattens (`scaleY:.02`) into a line of light → the next scene opens with `clip-path` from that band.
- A card grows to fill the frame → becomes the next scene's panel.
- A panel folds into two sheets (`rotationY ±88`) → becomes the brand mark.

## Dialogue format (two characters)

- Characters as transparent PNG poses (closed mouth + 1–3 open shapes). Swap poses from the voice's loudness envelope at ~15 fps (RMS per window, normalised per line).
- The speaker slides in from the bottom; on quick back-and-forths, put both on screen side by side with the listener smaller and dimmed.
- Pixel/code effects as sprite sheets: a moving "code aura" behind the character (almost always on), a short RGB glitch on punchlines, a pixel dissolve for the goodbye.
- Top third: screenshots and motion panels timed to the word that names them. Middle: one-word caption. Bottom: the characters. Background: satisfying looping footage, dimmed lightly.

## Real-data proof

- Never redraw the screenshot. Crop cards out of it with `background-position` (tiles) and pop them in 3D; the panel recedes blurred.
- Reveal a chart with a sliding cover (don't redraw the curve).
- Green only for positive data; a "real case" note visible during the whole proof.

## Pitfalls that cost a round

- CSS `transform` + GSAP on the same axis → lint error; use `fromTo` or remove the CSS transform.
- Animating `left/top/width` → lint "snaps to integer pixels"; use x/y/scale/clip-path.
- Two pages with `data-composition-id` at the project root → move backups out.
- Dashed lines animated with `strokeDashoffset` don't disappear (the dash just slides); to "draw", use `pathLength=1` + `dasharray 1`, or just opacity.
- Future-scene elements visible too early: start them at `opacity:0` in CSS.
- `onUpdate` that touches styles is safe (deterministic) if it depends only on the tweened value.
