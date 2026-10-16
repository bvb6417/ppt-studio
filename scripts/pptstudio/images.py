"""Procedural backgrounds & photo processing (Pillow + numpy). All functions return a PNG/JPG path.

Techniques from the references implemented as pixel ops so no Photoshop / plug-in is needed:
  * diffuse()      '弥散' soft color-blob backgrounds
  * duotone()      unify random photos with the theme hue (e.g. school-color landmark photo)
  * fade()         gradient transparency on a photo (OKPlus '渐变透明') -> blends into the page
  * line_art()     landmark/building line drawing at low opacity (清华 cover style)
  * desaturate()/tint(), dot/grid textures, tech_bg() dark glow lines
"""
from __future__ import annotations

import hashlib
import math
import os
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

from . import color as C

_DIR = None


def cache_dir():
    global _DIR
    if _DIR is None:
        _DIR = os.path.join(tempfile.gettempdir(), 'pptstudio_img')
        os.makedirs(_DIR, exist_ok=True)
    return _DIR


def _key(*args):
    return hashlib.md5(repr(args).encode('utf-8')).hexdigest()[:12]


def _rgb(c):
    return C.rgb(c)


# ---------------------------------------------------------------- textures / backgrounds
def dot_texture(color='1F57C3', alpha=0.1, step_in=0.3, size=(2000, 1125), r_px=2):
    p = os.path.join(cache_dir(), f'dots_{_key(color, alpha, step_in, size, r_px)}.png')
    if os.path.exists(p):
        return p
    W, H = size
    im = Image.new('RGBA', size, (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    step = int(W / 13.333 * step_in)
    rgb = _rgb(color)
    for y in range(step // 2, H, step):
        for x in range(step // 2, W, step):
            d.ellipse([x - r_px, y - r_px, x + r_px, y + r_px], fill=rgb + (int(255 * alpha),))
    im.save(p)
    return p


def dot_map(color='1F57C3', alpha=0.35, size=(1600, 900), step=14, seed=3):
    """Abstract 'dot-matrix world map' texture: dots masked by smooth noise continents."""
    p = os.path.join(cache_dir(), f'dotmap_{_key(color, alpha, size, step, seed)}.png')
    if os.path.exists(p):
        return p
    W, H = size
    rng = np.random.default_rng(seed)
    small = rng.random((9, 16))
    noise = np.array(Image.fromarray((small * 255).astype('uint8')).resize((W, H), Image.BICUBIC)) / 255.0
    noise = np.array(Image.fromarray((noise * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(40))) / 255.0
    im = Image.new('RGBA', size, (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rgb = _rgb(color)
    thr = np.quantile(noise, 0.55)
    for y in range(step // 2, H, step):
        for x in range(step // 2, W, step):
            v = noise[y, x]
            if v > thr:
                a = int(255 * alpha * min(1, (v - thr) * 6 + 0.3))
                r = 2.2
                d.ellipse([x - r, y - r, x + r, y + r], fill=rgb + (a,))
    im.save(p)
    return p


def diffuse(colors=('1F57C3', '3FA2F7', 'A5D8FF'), base='FFFFFF', size=(1600, 900), seed=7, blobs=None,
            blur=160, strength=0.55):
    """Soft blurred color blobs ('弥散风'). blobs: list of (cx, cy, r) in 0..1 units (x rel. width,
    y rel. height, r rel. width), else random. Colors are composited through blurred masks (no gray fringe)."""
    p = os.path.join(cache_dir(), f'diffuse2_{_key(colors, base, size, seed, blobs, blur, strength)}.jpg')
    if os.path.exists(p):
        return p
    W, H = size
    rng = np.random.default_rng(seed)
    if blobs is None:
        blobs = [(rng.uniform(0.55, 1.05), rng.uniform(-0.2, 0.4), rng.uniform(0.25, 0.45)),
                 (rng.uniform(-0.1, 0.35), rng.uniform(0.6, 1.1), rng.uniform(0.25, 0.4)),
                 (rng.uniform(0.3, 0.8), rng.uniform(0.3, 0.8), rng.uniform(0.12, 0.22))]
    out = np.array(Image.new('RGB', size, _rgb(base)), float)
    for i, (cx, cy, r) in enumerate(blobs):
        mask = Image.new('L', size, 0)
        d = ImageDraw.Draw(mask)
        R = r * W
        d.ellipse([cx * W - R, cy * H - R, cx * W + R, cy * H + R], fill=int(255 * strength))
        mask = mask.filter(ImageFilter.GaussianBlur(blur))
        a = (np.array(mask, float) / 255.0)[..., None]
        col = np.array(_rgb(colors[i % len(colors)]), float)[None, None, :]
        out = out * (1 - a) + col * a
    Image.fromarray(np.clip(out, 0, 255).astype('uint8')).save(p, quality=92)
    return p


def tech_bg(bg='07122B', glow='2F7CFF', glow2='22D3EE', size=(1600, 900), seed=5, grid=True):
    """Dark tech background: radial glows, perspective grid floor."""
    p = os.path.join(cache_dir(), f'tech2_{_key(bg, glow, glow2, size, seed, grid)}.jpg')
    if os.path.exists(p):
        return p
    W, H = size
    out = np.array(Image.new('RGB', size, _rgb(bg)), float)
    for col, box, al in ((glow, [W * 0.55, -H * 0.5, W * 1.35, H * 0.7], 0.55), (glow2, [-W * 0.3, H * 0.55, W * 0.35, H * 1.4], 0.3)):
        m = Image.new('L', size, 0)
        ImageDraw.Draw(m).ellipse(box, fill=int(255 * al))
        m = m.filter(ImageFilter.GaussianBlur(170))
        a = (np.array(m, float) / 255.0)[..., None]
        out = out * (1 - a) + np.array(_rgb(col), float)[None, None, :] * a
    if grid:
        gm = Image.new('L', size, 0)
        dg = ImageDraw.Draw(gm)
        hor = H * 0.62
        for i in range(-24, 25):
            x0 = W / 2 + i * W * 0.06
            dg.line([(W / 2 + i * 8, hor), (x0 + (x0 - W / 2) * 2.5, H)], fill=70, width=1)
        y, k = hor, 1.0
        while y < H:
            dg.line([(0, y), (W, y)], fill=70, width=1)
            y += 6 * k
            k *= 1.35
        fadem = np.clip((np.linspace(0, 1, H)[:, None] - 0.62) / 0.38, 0, 1)
        a = (np.array(gm, float) / 255.0 * fadem)[..., None]
        out = out * (1 - a) + np.array(_rgb(glow), float)[None, None, :] * a
    Image.fromarray(np.clip(out, 0, 255).astype('uint8')).save(p, quality=92)
    return p


def circuit(color='124CAD', size=(1600, 900), seed=3, alpha=0.55, fade='left'):
    """Transparent PNG of circuit-board traces (orthogonal polylines + pads) fading towards one side — the
    '科技背景' used on 重点研发 / 科研报告 covers. fade: left | right | none."""
    p = os.path.join(cache_dir(), f'circuit_{_key(color, size, seed, alpha, fade)}.png')
    if os.path.exists(p):
        return p
    import random
    rnd = random.Random(seed)
    W, H = size
    m = Image.new('L', size, 0)
    d = ImageDraw.Draw(m)
    step = 24
    for _ in range(int(W * H / 9000)):
        x = rnd.randrange(0, W // step) * step
        y = rnd.randrange(0, H // step) * step
        pts = [(x, y)]
        for _k in range(rnd.randint(2, 5)):
            if rnd.random() < 0.5:
                x += rnd.choice((-1, 1)) * rnd.randint(2, 9) * step
            else:
                y += rnd.choice((-1, 1)) * rnd.randint(1, 6) * step
            pts.append((x, y))
        v = rnd.randint(90, 255)
        d.line(pts, fill=v, width=2)
        ex, ey = pts[-1]
        r = rnd.choice((3, 4, 5))
        d.ellipse([ex - r, ey - r, ex + r, ey + r], outline=v, width=2)
        if rnd.random() < 0.25:
            d.rectangle([pts[0][0] - 4, pts[0][1] - 4, pts[0][0] + 4, pts[0][1] + 4], fill=v)
    a = np.array(m, float) / 255.0 * alpha
    if fade != 'none':
        ramp = np.clip(np.linspace(-0.25, 1.15, W), 0, 1) ** 1.4
        a *= (ramp if fade == 'left' else ramp[::-1])[None, :]
    rgba = np.zeros((H, W, 4), dtype='uint8')
    rgba[..., :3] = np.array(_rgb(color), dtype='uint8')
    rgba[..., 3] = np.clip(a * 255, 0, 255).astype('uint8')
    Image.fromarray(rgba, 'RGBA').save(p)
    return p


def skyline(color='FFFFFF', size=(1400, 240), seed=11, alpha=0.32, fade='left', motif='mixed'):
    """Transparent PNG of an engineering skyline silhouette (buildings, lattice towers, wind turbines, an offshore
    platform, a bridge) fading towards one side — stands in for the faded topic photo at the end of 重点研发-style
    title bands. motif: mixed | water (dam + bridge + turbines) | city. fade: left | right | both | none."""
    p = os.path.join(cache_dir(), f'skyline_{_key(color, size, seed, alpha, fade, motif)}.png')
    if os.path.exists(p):
        return p
    import random
    rnd = random.Random(seed)
    S = 3
    W, H = size[0] * S, size[1] * S
    m = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(m)
    base = int(H * 0.9)
    d.rectangle([0, base, W, base + 2 * S], fill=170)            # ground / sea line
    x = int(W * 0.02)
    while x < W:
        kind = rnd.random()
        if motif == 'water' and kind < 0.35:
            kind = 0.95
        elif motif == 'city':                                    # mostly towers of offices, a mast, a bridge
            kind = 0.3 if kind < 0.74 else (0.5 if kind < 0.84 else 0.95)
        if kind < 0.45:                                          # building block
            bw = rnd.randint(int(W * 0.018), int(W * 0.045))
            bh = rnd.randint(int(H * 0.18), int(H * 0.62))
            d.rectangle([x, base - bh, x + bw, base], fill=rnd.randint(150, 230))
            for wy in range(base - bh + 10 * S, base - 6 * S, 9 * S):   # window rows
                d.line([(x + 3 * S, wy), (x + bw - 3 * S, wy)], fill=60, width=S)
            x += bw + rnd.randint(2 * S, 9 * S)
        elif kind < 0.6:                                         # lattice transmission tower
            tw = rnd.randint(int(W * 0.02), int(W * 0.03))
            th = rnd.randint(int(H * 0.55), int(H * 0.8))
            top = (x + tw // 2, base - th)
            d.line([top, (x, base)], fill=230, width=2 * S)
            d.line([top, (x + tw, base)], fill=230, width=2 * S)
            for k in range(1, 6):
                yy = base - th + th * k // 6
                half = tw * k // 12
                d.line([(x + tw // 2 - half, yy), (x + tw // 2 + half, yy)], fill=210, width=S)
            d.line([(x - tw // 3, base - th + th // 6), (x + tw + tw // 3, base - th + th // 6)], fill=230, width=S)
            x += tw + rnd.randint(4 * S, 12 * S)
        elif kind < 0.78:                                        # wind turbine
            th = rnd.randint(int(H * 0.36), int(H * 0.56))
            hub = (x, base - th)
            d.line([(x, base), hub], fill=235, width=2 * S)
            L = int(th * 0.42)
            a0 = rnd.random() * 2 * math.pi
            for k in range(3):
                a = a0 + k * 2 * math.pi / 3
                d.line([hub, (x + int(L * math.cos(a)), base - th + int(L * math.sin(a)))], fill=235, width=2 * S)
            x += int(L * 1.2) + rnd.randint(4 * S, 10 * S)
        elif kind < 0.9:                                         # offshore platform
            pw = rnd.randint(int(W * 0.05), int(W * 0.07))
            ph = int(H * 0.36)
            deck = base - ph
            for lx in (x + pw // 6, x + pw - pw // 6):
                d.line([(lx, deck), (lx - pw // 10, base)], fill=220, width=2 * S)
            d.rectangle([x, deck - 8 * S, x + pw, deck], fill=225)
            d.rectangle([x + pw // 5, deck - ph // 2, x + pw // 2, deck - 8 * S], fill=200)
            dx = x + int(pw * 0.72)
            d.line([(dx - 10 * S, deck - 8 * S), (dx, deck - ph), (dx + 10 * S, deck - 8 * S)], fill=230, width=2 * S)
            x += pw + rnd.randint(6 * S, 14 * S)
        else:                                                    # bridge span
            bw = rnd.randint(int(W * 0.1), int(W * 0.16))
            yb = base - int(H * 0.16)
            d.line([(x, yb), (x + bw, yb)], fill=230, width=2 * S)
            for k in range(2):
                px_ = x + bw * (k + 1) // 3
                d.line([(px_, base), (px_, yb - int(H * 0.3))], fill=230, width=2 * S)
                for j in range(-3, 4):
                    if j:
                        d.line([(px_, yb - int(H * 0.28)), (px_ + j * bw // 14, yb)], fill=170, width=S)
            x += bw + rnd.randint(4 * S, 10 * S)
    m = m.resize(size, Image.LANCZOS)
    a = np.array(m, float) / 255.0 * alpha
    if fade == 'both':                                           # strongest in the middle, gone at both ends
        a *= (np.sin(np.linspace(0, math.pi, size[0])) ** 0.9)[None, :]
    elif fade != 'none':
        ramp = np.clip(np.linspace(-0.15, 1.1, size[0]), 0, 1) ** 1.3
        a *= (ramp if fade == 'left' else ramp[::-1])[None, :]
    rgba = np.zeros((size[1], size[0], 4), dtype='uint8')
    rgba[..., :3] = np.array(_rgb(color), dtype='uint8')
    rgba[..., 3] = np.clip(a * 255, 0, 255).astype('uint8')
    Image.fromarray(rgba, 'RGBA').save(p)
    return p


def hexgrid(color='1369C1', size=(1600, 900), r=46, alpha=0.18, fade='center', width=2, seed=4):
    """Transparent PNG of hexagon outlines (科学技术奖 cover texture). Random cells are dropped / dimmed so the
    grid reads as a light technical pattern. fade: center (clear in the middle, visible at the sides) | top |
    bottom | none."""
    p = os.path.join(cache_dir(), f'hexgrid_{_key(color, size, r, alpha, fade, width, seed)}.png')
    if os.path.exists(p):
        return p
    import random
    rnd = random.Random(seed)
    S = 2
    W, H = size[0] * S, size[1] * S
    R = r * S
    m = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(m)
    dx, dy = R * 1.5, R * math.sqrt(3)
    col = 0
    x = -R
    while x < W + R:
        y = -R + (dy / 2 if col % 2 else 0)
        while y < H + R:
            v = rnd.random()
            if v > 0.25:
                pts = [(x + R * math.cos(math.radians(60 * k)), y + R * math.sin(math.radians(60 * k)))
                       for k in range(7)]
                d.line(pts, fill=int(110 + 145 * v), width=width * S)
            y += dy
        x += dx
        col += 1
    m = m.resize(size, Image.LANCZOS)
    a = np.array(m, float) / 255.0 * alpha
    xs = np.linspace(-1, 1, size[0])
    ys = np.linspace(0, 1, size[1])
    if fade == 'center':
        a *= np.clip(np.abs(xs) * 1.4 - 0.15, 0, 1)[None, :]
    elif fade == 'top':
        a *= ys[:, None]
    elif fade == 'bottom':
        a *= ys[::-1][:, None]
    rgba = np.zeros((size[1], size[0], 4), dtype='uint8')
    rgba[..., :3] = np.array(_rgb(color), dtype='uint8')
    rgba[..., 3] = np.clip(a * 255, 0, 255).astype('uint8')
    Image.fromarray(rgba, 'RGBA').save(p)
    return p


def dot_wave(color='1F57C3', size=(1600, 420), step=12, alpha=0.4, waves=2.2, seed=2):
    """Halftone dot field shaped like a rolling surface (dots grow along wave crests and fade upward) — the light
    'data wave' texture at the bottom of 重点实验室 / 科研报告 covers."""
    p = os.path.join(cache_dir(), f'dotwave_{_key(color, size, step, alpha, waves, seed)}.png')
    if os.path.exists(p):
        return p
    S = 2
    W, H = size[0] * S, size[1] * S
    st = step * S
    im = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(im)
    for yi, y in enumerate(range(st // 2, H, st)):
        fy = y / H                                     # 0 top .. 1 bottom
        for x in range(st // 2 + (st // 2 if yi % 2 else 0), W, st):
            fx = x / W
            crest = 0.55 + 0.22 * math.sin(2 * math.pi * (fx * waves + 0.15)) + 0.1 * math.sin(2 * math.pi * fx * 5.3)
            k = max(0.0, 1 - abs(fy - crest) * 2.6) * (0.35 + 0.65 * fy)
            if k <= 0.04:
                continue
            rr = st * 0.36 * k
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=int(255 * min(1, 0.4 + k)))
    im = im.resize(size, Image.LANCZOS)
    a = np.array(im, float) / 255.0 * alpha
    xs = np.linspace(0, math.pi, size[0])
    a *= (0.35 + 0.65 * np.sin(xs) ** 0.6)[None, :]
    rgba = np.zeros((size[1], size[0], 4), dtype='uint8')
    rgba[..., :3] = np.array(_rgb(color), dtype='uint8')
    rgba[..., 3] = np.clip(a * 255, 0, 255).astype('uint8')
    Image.fromarray(rgba, 'RGBA').save(p)
    return p


def gradient_png(stops, size=(1600, 900), angle=90):
    """Plain gradient image (for backgrounds that must render identically everywhere)."""
    p = os.path.join(cache_dir(), f'grad_{_key(stops, size, angle)}.png')
    if os.path.exists(p):
        return p
    W, H = size
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    a = math.radians(angle)
    t = (xx * math.cos(a) + yy * math.sin(a))
    t = (t - t.min()) / (t.max() - t.min() + 1e-9)
    out = np.zeros((H, W, 4))
    pos = [s[0] / 100 for s in stops]
    cols = [np.array(_rgb(s[1]) + (int(255 * (s[2] if len(s) > 2 else 1)),), float) for s in stops]
    for i in range(len(stops) - 1):
        m = (t >= pos[i]) & (t <= pos[i + 1])
        f = ((t - pos[i]) / max(1e-9, pos[i + 1] - pos[i]))[..., None]
        out[m] = (cols[i] * (1 - f) + cols[i + 1] * f)[m]
    Image.fromarray(out.astype('uint8'), 'RGBA').save(p)
    return p


# ---------------------------------------------------------------- photo processing
def _out(path, tag, ext='.png'):
    base = os.path.splitext(os.path.basename(path))[0]
    return os.path.join(cache_dir(), f'{base}_{tag}{ext}')


def cover_crop(path, aspect, focus=(0.5, 0.5), max_w=2400):
    """Crop image to aspect (w/h) around focus point, downscale to max_w."""
    im = Image.open(path).convert('RGB')
    w, h = im.size
    if w / h > aspect:
        nw = int(h * aspect)
        x0 = int(max(0, min(w - nw, focus[0] * w - nw / 2)))
        im = im.crop((x0, 0, x0 + nw, h))
    else:
        nh = int(w / aspect)
        y0 = int(max(0, min(h - nh, focus[1] * h - nh / 2)))
        im = im.crop((0, y0, w, y0 + nh))
    if im.width > max_w:
        im = im.resize((max_w, int(max_w / aspect)), Image.LANCZOS)
    p = _out(path, f'crop{aspect:.2f}', '.jpg')
    im.save(p, quality=90)
    return p


def duotone(path, dark='0B2A5B', light='E8F1FF', contrast=1.1):
    """Map luminance to a 2-color ramp (theme-colored photo)."""
    im = Image.open(path).convert('L')
    im = ImageOps.autocontrast(im, cutoff=1)
    if contrast != 1.0:
        arr = np.array(im, float)
        arr = np.clip((arr - 128) * contrast + 128, 0, 255)
        im = Image.fromarray(arr.astype('uint8'))
    out = ImageOps.colorize(im, black=_rgb(dark), white=_rgb(light))
    p = _out(path, f'duo_{dark}_{light}', '.jpg')
    out.save(p, quality=90)
    return p


def desaturate(path, amount=1.0, brightness=1.0):
    im = Image.open(path).convert('RGB')
    g = ImageOps.grayscale(im).convert('RGB')
    out = Image.blend(im, g, amount)
    if brightness != 1.0:
        from PIL import ImageEnhance
        out = ImageEnhance.Brightness(out).enhance(brightness)
    p = _out(path, f'desat{amount:.2f}', '.jpg')
    out.save(p, quality=90)
    return p


def tint(path, color='1F57C3', amount=0.35):
    im = Image.open(path).convert('RGB')
    layer = Image.new('RGB', im.size, _rgb(color))
    out = Image.blend(im, layer, amount)
    p = _out(path, f'tint_{color}{amount:.2f}', '.jpg')
    out.save(p, quality=90)
    return p


def fade(path, side='bottom', start=0.45, end=1.0, max_w=2400):
    """Gradient transparency: image fully opaque until `start` then fades to 0 at `end` toward `side`
    ('bottom'|'top'|'left'|'right'). Use to blend a photo into the slide background."""
    im = Image.open(path).convert('RGBA')
    if im.width > max_w:
        im = im.resize((max_w, int(im.height * max_w / im.width)), Image.LANCZOS)
    w, h = im.size
    n = h if side in ('top', 'bottom') else w
    ramp = np.ones(n)
    i0, i1 = int(start * n), int(end * n)
    if i1 > i0:
        ramp[i0:i1] = np.linspace(1, 0, i1 - i0)
    ramp[i1:] = 0
    if side in ('top', 'left'):
        ramp = ramp[::-1]
    if side in ('top', 'bottom'):
        mask = np.tile(ramp[:, None], (1, w))
    else:
        mask = np.tile(ramp[None, :], (h, 1))
    a = np.array(im.split()[3], float) * mask
    im.putalpha(Image.fromarray(a.astype('uint8')))
    p = _out(path, f'fade_{side}{start:.2f}{end:.2f}', '.png')
    im.save(p)
    return p


def line_art(path, color='FFFFFF', alpha=0.5, threshold=40, blur=0.6, max_w=1800):
    """Edge-detected line drawing on transparent background."""
    im = Image.open(path).convert('L')
    if im.width > max_w:
        im = im.resize((max_w, int(im.height * max_w / im.width)), Image.LANCZOS)
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    edges = im.filter(ImageFilter.FIND_EDGES)
    arr = np.array(edges, float)
    arr = np.clip((arr - threshold) * 3, 0, 255) * alpha
    out = Image.new('RGBA', im.size, _rgb(color) + (0,))
    out.putalpha(Image.fromarray(arr.astype('uint8')))
    p = _out(path, f'line_{color}{alpha:.2f}', '.png')
    out.save(p)
    return p


def blur(path, radius=18):
    im = Image.open(path).convert('RGB')
    out = im.filter(ImageFilter.GaussianBlur(radius))
    p = _out(path, f'blur{radius}', '.jpg')
    out.save(p, quality=88)
    return p
