# Procedural asset techniques (Python: numpy, scipy, PIL)

## Surfaces with relief (brain, coral, mazes)
- **Gray-Scott reaction-diffusion** in the maze regime (`f=.029, k=.057`, diffusion `Du=.2, Dv=.1` to stay stable with a 5-point Laplacian; `Du=1` blows up). ~11,000 steps on a 520×660 grid; cache it as `.npy`.
- Blur lightly and raise to a power (`gaussian 2.2, **.7`) for rounded folds; warp with noise (`map_coordinates`) to follow a shape.
- **Heightfield → normals → light**: `gy,gx=np.gradient(Z)`; diffuse + specular + cavity occlusion (`gaussian(Z,6)-Z`) + rim light.

## Spherical objects (eyes, buttons, drops)
- Dome `z=sqrt(1-r²)`, iris with radial fibres at several frequencies, veins by random walk, soft window reflection (blur it!), offset contact shadow.

## Human figures
- Don't invent realistic faces or real people. Use a stylised backlit bust (strong rim light, face in shadow) — it reads as a statue and avoids the uncanny valley. For the shape, use `gaussian_filter(mask)` as height (a distance transform creates a "seam" down the middle).

## Editorial finish
- **Halftone**: grid rotated 45°, dot radius ∝ sqrt(1-luminance), multiply ~.2–.4.
- **Paper**: noise at 5 scales + anisotropic fibres `gaussian(σ=(.5,10))` + vignette + soft clouds at the top + optional creases.
- **Grain**: 6 noise frames, overlay blend, swapped every 2 frames at varied positions.
- **Dust/hairs**: sparse dots + short random walks; use sparingly, it gets heavy fast.

## Cut-outs
- Product on a light background: `npx hyperframes remove-background photo.jpg -o product.png`.
- Cartoon characters on white: automatic removal can punch holes in light clothing. Flood-fill near-white, low-saturation pixels connected to the border, add large interior white holes, then `binary_fill_holes` and a 0.8 px gaussian on alpha.
- Logo on a flat colour: `gen_textures.py --key-logo` (alpha from distance to the background colour, with un-premultiplication).

## Generic thumbnails (sea of competitors, catalogues)
- Simple PIL silhouettes (sneaker, bag, bottle, watch, headphones, box, t-shirt, mug), diagonal light, texture and floor shadow, in grey — no brands.

## Pixel / code effects on a character
- **Code aura**: dilate the alpha (`MaxFilter`) and blur it into a halo; draw mono glyphs (`01{}<>/=;`) on a grid inside the halo, falling and wrapping over 8 frames; add a pixelated outline ring that flickers. Save as a sprite sheet.
- **Glitch**: roll R and B channels in opposite directions, shift 6–8 random horizontal slices, pixelate one band, darken every 4th row for scanlines.
- **Dissolve**: a noisy front sweeps across the body; behind it the pixels become cyan blocks and glyphs that fly off and fade.

Always render a preview (`ffmpeg ... hstack` or overlay on the scene's background colour) and look at it before composing.
