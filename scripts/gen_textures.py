"""Reusable procedural assets (9:16 1080x1920 by default; --size 1920x1080 for 16:9).

Usage:
  python gen_textures.py --out assets --base "#141414" --accent "#FF6B35"
  python gen_textures.py --out assets --key-logo logo-original.png --name logo.png

Generates (without --key-logo):
  paper.png   paper/graphite texture in the --base colour, with vignette and fibres
  grain0..5   six film-grain frames (swap every 2 frames, overlay blend)
  rays.png    volumetric light rays in the --accent colour (screen blend, opacity 0.3-0.8)
  grid.png    technical grid with registration marks and rulers (background layer, parallax)
  flare.png   horizontal anamorphic flare (screen blend, for key moments)
--key-logo: removes the flat (dark or light) background of an RGB logo and saves it with alpha.
Requires: numpy, scipy, pillow.
"""
import argparse, os
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter

ap = argparse.ArgumentParser()
ap.add_argument("--out", default="assets")
ap.add_argument("--base", default="#141414")
ap.add_argument("--accent", default="#FF6B35")
ap.add_argument("--rays-center", default=None)
ap.add_argument("--size", default="1080x1920", help="LxA, ex.: 1920x1080 para 16:9")
ap.add_argument("--key-logo")
ap.add_argument("--name", default="logo.png")
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
W, H = map(int, a.size.lower().split("x"))
rng = np.random.default_rng(7)


def hexrgb(h):
    h = h.lstrip("#"); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)]) / 255


def save(rgb, alpha, name):
    rgb = np.clip(rgb, 0, 1)
    img = np.concatenate([rgb, np.clip(alpha, 0, 1)[..., None]], -1) if alpha is not None else rgb
    Image.fromarray((img * 255 + .5).astype(np.uint8)).save(os.path.join(a.out, name))


def noise(h, w, s, seed):
    n = gaussian_filter(np.random.default_rng(seed).standard_normal((h, w)), s)
    return (n - n.mean()) / (n.std() + 1e-9)


if a.key_logo:
    im = np.asarray(Image.open(a.key_logo).convert("RGB"), np.float32) / 255
    bg = np.median(np.concatenate([im[:8].reshape(-1, 3), im[-8:].reshape(-1, 3)]), 0)
    d = np.abs(im - bg[None, None]).max(-1)
    al = np.clip((d - .06) / .16, 0, 1) ** .8
    rgb = np.where(al[..., None] > 1e-3, np.clip((im - bg * (1 - al[..., None])) / np.maximum(al[..., None], 1e-3), 0, 1), 0)
    save(rgb, al, a.name); print("logo cut out:", a.name); raise SystemExit

y, x = np.mgrid[0:H, 0:W].astype(np.float32)
base = hexrgb(a.base); acc = hexrgb(a.accent)
light = base.mean() > .5

# paper / graphite
n = sum(wt * noise(H, W, s, 10 + i) for i, (s, wt) in enumerate(zip([.7, 2, 8, 40, 160], [.4, .3, .2, .2, .25])))
fib = gaussian_filter(rng.standard_normal((H, W)), (.5, 10)); fib /= fib.std()
vign = 1 - .5 * (((x - W / 2) / W) ** 2 * 1.3 + ((y - H * .46) / H) ** 2 * 1.4)
amp = .035 if light else .09
L = base[None, None] * vign[..., None] * (1 + amp * n[..., None] + amp * .6 * fib[..., None])
save(L, None, "paper.png")

# grain
for i in range(6):
    g = gaussian_filter(np.random.default_rng(200 + i).standard_normal((H // 2, W // 2)), .6)
    g = .5 + g / g.std() * .2
    save(np.repeat(g[..., None], 3, -1), np.ones_like(g), f"grain{i}.png")

# rays
cx, cy = map(float, a.rays_center.split(",")) if a.rays_center else (W / 2, H * .4)
ang = np.arctan2(y - cy, x - cx); r = np.hypot(x - cx, y - cy)
k = np.arange(720); streak = gaussian_filter(rng.random(720) ** 7, 1.0, mode="wrap")
s = np.interp((ang + np.pi) / (2 * np.pi) * 720, np.append(k, 720), np.append(streak, streak[0]))
al = np.clip(s * 1.6, 0, 1) * np.exp(-r / 430) * np.clip(r / 60, 0, 1) * .75 + np.exp(-r / 220) * .35
col = np.clip(acc[None, None] * .8 + .35 * np.exp(-r / 250)[..., None], 0, 1)
save(col, al, "rays.png")

# technical grid
ink = (20, 20, 20) if light else (248, 250, 252)
g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
for gx in range(0, W + 1, 90): d.line([(gx, 0), (gx, H)], fill=ink + (10,))
for gy in range(0, H + 1, 90): d.line([(0, gy), (W, gy)], fill=ink + (10,))
for gx in range(0, W + 1, 90):
    for gy in range(0, H + 1, 90):
        d.line([(gx - 5, gy), (gx + 5, gy)], fill=ink + (38,)); d.line([(gx, gy - 5), (gx, gy + 5)], fill=ink + (38,))
for gy in range(0, H, 18):
    t = 8 if gy % 90 else 18
    d.line([(0, gy), (t, gy)], fill=ink + (50,)); d.line([(W - t, gy), (W, gy)], fill=ink + (50,))
r0 = min(W, H) * .39; d.ellipse([W / 2 - r0, H * .47 - r0, W / 2 + r0, H * .47 + r0], outline=ink + (16,), width=2)
g.save(os.path.join(a.out, "grid.png"))

# anamorphic flare
fw, fh = int(W * 1.5), 200
yy, xx = np.mgrid[0:fh, 0:fw].astype(np.float32)
core = np.exp(-((yy - fh / 2) / 3.5) ** 2) * np.exp(-((xx - fw / 2) / 520) ** 2)
halo = np.exp(-((yy - fh / 2) / 30) ** 2) * np.exp(-((xx - fw / 2) / 180) ** 2) * .5
dot = np.exp(-(((xx - fw / 2) / 26) ** 2 + ((yy - fh / 2) / 26) ** 2))
al = np.clip(core + halo + dot, 0, 1)
col = np.clip(acc[None, None] * (1 - dot[..., None]) + dot[..., None], 0, 1) * .6 + .4
save(col, al, "flare.png")
print("ok ->", a.out)
