"""水墨风素材：宣纸纹理（程序生成，正式使用）+ 图片占位（imagegen 图片放进 img/ 后自动替换）。

占位图只为让版式先跑通：远山、墨韵纹理都是程序画的，质感不如生成图。
"""
from __future__ import annotations

import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(HERE, 'img')
GEN = os.path.join(HERE, '_gen')
os.makedirs(GEN, exist_ok=True)


def _rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _noise(shape, scale, rng, octaves=4):
    """Smooth fractal value noise in [0, 1]."""
    h, w = shape
    out = np.zeros(shape)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        s = max(2, int(scale * 2 ** o))
        small = rng.random((max(2, h * s // w + 1), s + 1))
        layer = np.array(Image.fromarray((small * 255).astype('uint8')).resize((w, h), Image.BICUBIC), float) / 255
        out += layer * amp
        tot += amp
        amp *= 0.5
    out /= tot
    return (out - out.min()) / max(1e-6, np.ptp(out))


def pick(name, fallback):
    """img/<name>.png|jpg if the user supplied it, else the procedural fallback (callable -> path)."""
    for ext in ('.png', '.jpg', '.jpeg', '.webp'):
        p = os.path.join(IMG_DIR, name + ext)
        if os.path.exists(p):
            return p, True
    return fallback(), False


# ------------------------------------------------------------------ 宣纸
def paper(base='F7F4EE', size=(2400, 1350), seed=1):
    out = os.path.join(GEN, f'paper_{base}_{seed}.jpg')
    if os.path.exists(out):
        return out
    rng = np.random.default_rng(seed)
    h, w = size[1], size[0]
    r, g, b = _rgb(base)
    cloud = _noise((h, w), 3, rng, 5) - 0.5                       # 大块深浅（纸浆不匀）
    grain = rng.normal(0, 1, (h, w))                               # 细颗粒
    arr = np.stack([np.full((h, w), r, float), np.full((h, w), g, float), np.full((h, w), b, float)], -1)
    arr += (cloud * 7)[..., None] + (grain * 1.6)[..., None]
    im = Image.fromarray(np.clip(arr, 0, 255).astype('uint8'))
    # 纤维：短细弧线，极淡
    fib = Image.new('L', (w, h), 0)
    dr = ImageDraw.Draw(fib)
    for _ in range(1600):
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        L, ang = rng.uniform(8, 40), rng.uniform(0, np.pi)
        pts = [(x + np.cos(ang + 0.15 * k) * L * k / 4, y + np.sin(ang + 0.15 * k) * L * k / 4) for k in range(5)]
        dr.line(pts, fill=int(rng.uniform(18, 40)), width=1)
    fib = fib.filter(ImageFilter.GaussianBlur(0.6))
    dark = Image.new('RGB', (w, h), (max(r - 22, 0), max(g - 22, 0), max(b - 26, 0)))
    im = Image.composite(dark, im, fib.point(lambda v: v // 3))
    im.save(out, quality=92)
    return out


# ------------------------------------------------------------------ 远山（占位）
def mountains(size=(2560, 1440), seed=4, ink='1B2A36', tint='5C7A8C', paper_c='F7F4EE', empty='left', river=True):
    """Layered ink-wash ridges fading into mist; `empty` side kept blank for text."""
    out = os.path.join(GEN, f'mount_{size[0]}x{size[1]}_{seed}_{empty}.jpg')
    if os.path.exists(out):
        return out
    rng = np.random.default_rng(seed)
    w, h = size
    pc = np.array(_rgb(paper_c), float)
    img = np.ones((h, w, 3)) * pc
    yy = np.arange(h)[:, None]
    xs = np.linspace(0, 1, w)
    keep = np.ones(w)
    if empty == 'left':
        keep = np.clip((xs - 0.22) / 0.4, 0, 1) ** 1.3
    elif empty == 'right':
        keep = np.clip((0.78 - xs) / 0.4, 0, 1) ** 1.3
    elif empty == 'center':
        keep = np.clip(np.abs(xs - 0.5) / 0.3, 0.25, 1)
    layers = 5
    for k in range(layers):
        far = 1 - k / (layers - 1)                     # 1 = 最远
        base = h * (0.38 + 0.12 * k)
        ridge = np.zeros(w)
        for o in range(5):
            f = 1.1 * 2 ** o
            ridge += np.sin(xs * f * np.pi * 2 + rng.uniform(0, 6.28)) * (h * 0.11 / 1.9 ** o)
        ridge = (ridge - ridge.min()) / np.ptp(ridge)
        ridge = ridge ** 1.6 * (0.7 + 0.3 * np.sin(xs * 2.3 + k * 1.7))           # 尖峰 + 缓坡
        peak = base - (ridge * h * 0.26 + h * 0.03) * keep + (1 - keep) * h * 0.55   # 留白侧山体沉下去
        d = yy - peak[None, :]
        dens = np.where(d > 0, np.exp(-d / (h * (0.07 + 0.03 * k))) * 0.8 + 0.2, 0)
        dens = np.array(Image.fromarray((dens * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(3 + 2 * far)),
                        float) / 255
        tex = _noise((h, w), 6 + 2 * k, rng, 4)
        dens = dens * (0.6 + 0.4 * tex) * (0.35 + 0.65 * (1 - far))
        mist = np.clip((yy - (base + h * 0.06)) / (h * 0.14), 0, 1)       # 山脚入雾
        dens *= (1 - mist * 0.9)
        col = np.array(_rgb(tint), float) * far + np.array(_rgb(ink), float) * (1 - far)
        a = np.clip(dens, 0, 1)[..., None]
        img = img * (1 - a) + col * a
    if river:  # 一条淡淡的引水线（示意输水干线）
        im = Image.fromarray(np.clip(img, 0, 255).astype('uint8'))
        dr = ImageDraw.Draw(im)
        pts = [(w * (0.36 + 0.64 * t), h * (0.86 - 0.28 * t + 0.05 * np.sin(t * 9))) for t in np.linspace(0, 1, 80)]
        dr.line(pts, fill=_rgb('B9C6CC'), width=max(3, w // 500))
        img = np.array(im, float)
    Image.fromarray(np.clip(img, 0, 255).astype('uint8')).filter(ImageFilter.GaussianBlur(1.2)).save(out, quality=92)
    return out


# ------------------------------------------------------------------ 墨韵纹理（占位）
def ink_texture(size=(1600, 1600), seed=9, colors=('0C1720', '1E4A6B', '6C93A8', 'D9E2E4')):
    """Domain-warped noise -> ink diffusing in water (used as picture fill inside big calligraphy)."""
    out = os.path.join(GEN, f'inktex_{size[0]}_{seed}.jpg')
    if os.path.exists(out):
        return out
    rng = np.random.default_rng(seed)
    w, h = size
    n1, n2, n3 = (_noise((h, w), 3, rng, 5) for _ in range(3))
    yy, xx = np.mgrid[0:h, 0:w]
    wx = np.clip((xx + (n1 - 0.5) * w * 0.35).astype(int), 0, w - 1)
    wy = np.clip((yy + (n2 - 0.5) * h * 0.35).astype(int), 0, h - 1)
    v = n3[wy, wx]
    v = (v - v.min()) / np.ptp(v)
    stops = np.linspace(0, 1, len(colors))
    cols = np.array([_rgb(c) for c in colors], float)
    rgb = np.stack([np.interp(v, stops, cols[:, i]) for i in range(3)], -1)
    Image.fromarray(rgb.astype('uint8')).filter(ImageFilter.GaussianBlur(1.0)).save(out, quality=93)
    return out


def toned(size=(2400, 1000), seed=12, dark='0F1E29', mid='2C5670', light='8FB0C0'):
    """占位“照片”：带山形与光感的黛青色调图（用于大图拦腰 / 创新点卡片）。"""
    out = os.path.join(GEN, f'toned_{size[0]}x{size[1]}_{seed}.jpg')
    if os.path.exists(out):
        return out
    m = Image.open(mountains((size[0], size[1]), seed, ink='0B1620', tint='6F8FA0', paper_c='C9D6DC',
                             empty='none', river=True)).convert('L')
    arr = np.array(m, float) / 255
    stops = [0, 0.55, 1]
    cols = np.array([_rgb(dark), _rgb(mid), _rgb(light)], float)
    rgb = np.stack([np.interp(arr, stops, cols[:, i]) for i in range(3)], -1)
    yy = np.linspace(0, 1, size[1])[:, None, None]
    rgb = rgb * (0.75 + 0.35 * (1 - yy))                       # 天空亮、地面暗
    Image.fromarray(np.clip(rgb, 0, 255).astype('uint8')).save(out, quality=92)
    return out


def alpha_from_white(path, out_name, color='14212B', strength=1.0):
    """白底墨迹图 -> 透明底（黑色部分保留为 color 的不透明度）。用于 imagegen 的“白底水墨晕染/笔触”。"""
    out = os.path.join(GEN, out_name)
    if os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(path):
        return out
    g = np.array(Image.open(path).convert('L'), float) / 255
    a = np.clip((1 - g) * 1.15 * strength, 0, 1)
    rgb = np.ones(g.shape + (3,)) * np.array(_rgb(color), float)
    Image.fromarray(np.dstack([rgb, a * 255]).astype('uint8'), 'RGBA').save(out)
    return out
