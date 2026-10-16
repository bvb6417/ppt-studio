"""书法字矢量化：把书法 / 毛笔字体的字形转成 PowerPoint 原生自由曲线形状。

为什么不直接用文本框：书法字体（广告毛笔字体、汉仪许静行楷 等）别的电脑上大多没装，且多数禁止嵌入
(OS/2 fsType=2)。转成形状后在任何电脑上都一样显示，还能做文本框做不到的事：图片填充、渐变、
任意拉伸、错落排版、平滑切换(Morph)时按形状变形。

    from brush import brush, seal, stroke
    brush(cv, '水脉', x, y, em=2.4, font='brush', fill='dark')               # 纯色
    brush(cv, '壹', x, y, em=5, image='ink.png')                              # 图片填充文字
    brush(cv, '目录', x, y, em=1.6, vertical=True, fill='FFFFFF')             # 竖排
    brush(cv, None, x, y, em=2, chars=[('安', 0, 0, 1), ('澜', .8, .45, .8)])  # 错落：(字, dx_em, dy_em, 缩放)
    seal(cv, cx, cy, 0.62, '安澜')                                            # 朱文/白文印章
"""
from __future__ import annotations

import os
import random
from functools import lru_cache

import numpy as np
import pathops
from fontTools.pens.basePen import BasePen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from lxml import etree
from PIL import Image, ImageFilter

from pptstudio import oxml as X
from pptstudio.canvas import Box
from pptstudio.units import emu

_WIN = r'C:\Windows\Fonts'
_USER = os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\Windows\Fonts')
FONTS = {                       # 别名 -> 字体文件（按本机已装字体）
    'brush': '广告毛笔字体.ttf',          # 粗犷毛笔：封面主视觉、章节数字、谢谢
    'xingkai': '1642321405439333.ttf',  # 汉仪许静行楷W：竖排诗句、小标语
    'fzxingkai': '方正行楷简体.ttf',
    'stxingkai': 'STXINGKA.TTF',
    'li': 'STLITI.TTF',                 # 华文隶书：印章
    'xinwei': 'STXINWEI.TTF',
    'biaosong': '方正小标宋简.TTF',
}
GEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_gen')


def font_file(name):
    fn = FONTS.get(name, name)
    if os.path.isabs(fn) and os.path.exists(fn):
        return fn
    for d in (_WIN, _USER):
        p = os.path.join(d, fn)
        if os.path.exists(p):
            return p
    raise FileNotFoundError(f'font not installed: {name} ({fn})')


@lru_cache(maxsize=None)
def _font(name):
    f = TTFont(font_file(name), lazy=True)
    return f, f.getGlyphSet(), f.getBestCmap(), f['head'].unitsPerEm


class _Rec(BasePen):
    """Records outlines as svgpath-style subpaths; quadratic segments -> cubic."""

    def __init__(self):
        super().__init__(None)
        self.subs, self.cur = [], None

    def _moveTo(self, p):
        self.cur = {'start': p, 'segs': [], 'closed': False}
        self.subs.append(self.cur)

    def _lineTo(self, p):
        self.cur['segs'].append(('L',) + tuple(p))

    def _curveToOne(self, a, b, c):
        self.cur['segs'].append(('C',) + tuple(a) + tuple(b) + tuple(c))

    def _qCurveToOne(self, a, b):
        p0 = self._getCurrentPoint()
        c1 = (p0[0] + 2 / 3 * (a[0] - p0[0]), p0[1] + 2 / 3 * (a[1] - p0[1]))
        c2 = (b[0] + 2 / 3 * (a[0] - b[0]), b[1] + 2 / 3 * (a[1] - b[1]))
        self.cur['segs'].append(('C',) + c1 + c2 + tuple(b))

    def _closePath(self):
        self.cur['closed'] = True

    def _endPath(self):
        pass


def outline(text=None, font='brush', spacing=0.0, vertical=False, chars=None):
    """Union outline of a string in em units (1 em = 1.0, y up). chars = [(ch, dx_em, dy_em, scale)] overrides
    the automatic horizontal / vertical flow (dy positive = downward). Returns a pathops.Path."""
    f, gs, cmap, upm = _font(font)
    hm = f['hmtx']
    if chars is None:
        chars, pos = [], 0.0
        for ch in text:
            if ch == ' ':
                pos += 0.5
                continue
            if vertical:
                chars.append((ch, 0.0, pos, 1.0))
                pos += 1.0 + spacing
            else:
                chars.append((ch, pos, 0.0, 1.0))
                adv = hm[cmap[ord(ch)]][0] / upm if ord(ch) in cmap else 1.0
                pos += adv + spacing
    path = pathops.Path()
    for ch, dx, dy, s in chars:
        g = cmap.get(ord(ch))
        if g is None:
            raise KeyError(f'{font} has no glyph for {ch!r}')
        k = s / upm
        gs[g].draw(TransformPen(path.getPen(), (k, 0, 0, k, dx, -dy)))
    path.simplify(fix_winding=True)       # 去掉笔画重叠，保证单路径填充时不出现“镂空”
    return path


def _subpaths(path, scale):
    rec = _Rec()
    path.draw(rec)
    x0, y0, x1, y1 = path.bounds
    def tr(x, y):
        return (x - x0) * scale, (y1 - y) * scale
    out = []
    for s in rec.subs:
        segs = []
        for sg in s['segs']:
            if sg[0] == 'L':
                segs.append(('L',) + tr(sg[1], sg[2]))
            else:
                segs.append(('C',) + tr(sg[1], sg[2]) + tr(sg[3], sg[4]) + tr(sg[5], sg[6]))
        out.append({'start': tr(*s['start']), 'segs': segs, 'closed': True})
    return out, (x1 - x0) * scale, (y1 - y0) * scale


def _custgeom_single(shape, subs, vb_w, vb_h):
    """All subpaths in ONE <a:path> so counters (口、日 …) stay hollow."""
    sp = X.spPr(shape)
    X.remove_children(sp, ['prstGeom', 'custGeom'])
    cg = etree.Element(X.qn('a:custGeom'))
    for t in ('a:avLst', 'a:gdLst', 'a:ahLst', 'a:cxnLst'):
        X.sub(cg, t)
    X.sub(cg, 'a:rect', l='0', t='0', r='r', b='b')
    pl = X.sub(cg, 'a:pathLst')
    p = X.sub(pl, 'a:path', w=int(round(vb_w)), h=int(round(vb_h)))

    def pt(parent, x, y):
        X.sub(parent, 'a:pt', x=int(round(x)), y=int(round(y)))
    for s in subs:
        pt(X.sub(p, 'a:moveTo'), *s['start'])
        for sg in s['segs']:
            if sg[0] == 'L':
                pt(X.sub(p, 'a:lnTo'), sg[1], sg[2])
            else:
                c = X.sub(p, 'a:cubicBezTo')
                pt(c, sg[1], sg[2]); pt(c, sg[3], sg[4]); pt(c, sg[5], sg[6])
        X.sub(p, 'a:close')
    X.insert_ordered(sp, cg, X.SPPR_ORDER)


def set_picture_fill(cv, shape, image, alpha=1.0, tile=False):
    """图片填充（形状 / 书法字 内透出图片）。image 应预先裁成与形状同宽高比，避免拉伸。"""
    _, rid = cv.slide.part.get_or_add_image_part(image)
    sp = X.spPr(shape)
    X.remove_children(sp, X.FILL_TAGS)
    bf = etree.Element(X.qn('a:blipFill'), rotWithShape='1')
    blip = X.sub(bf, 'a:blip')
    blip.set(X.qn('r:embed'), rid)
    if alpha < 1:
        X.sub(blip, 'a:alphaModFix', amt=str(int(alpha * 100000)))
    X.sub(bf, 'a:srcRect')
    if tile:
        X.sub(bf, 'a:tile', tx='0', ty='0', sx='100000', sy='100000', flip='none', algn='tl')
    else:
        X.sub(X.sub(bf, 'a:stretch'), 'a:fillRect')
    X.insert_ordered(sp, bf, X.SPPR_ORDER)


def _crop_to(image, aspect, focus=(0.5, 0.5)):
    os.makedirs(GEN, exist_ok=True)
    out = os.path.join(GEN, 'fill_%x_%.3f_%.2f_%.2f.png' % (abs(hash(os.path.abspath(image))) & 0xffffff,
                                                           aspect, *focus))
    if os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(image):
        return out
    im = Image.open(image).convert('RGB')
    W, H = im.size
    if W / H > aspect:
        nw = int(H * aspect); x0 = int(max(0, min(W - nw, focus[0] * W - nw / 2)))
        im = im.crop((x0, 0, x0 + nw, H))
    else:
        nh = int(W / aspect); y0 = int(max(0, min(H - nh, focus[1] * H - nh / 2)))
        im = im.crop((0, y0, W, y0 + nh))
    im.save(out)
    return out


def brush(cv, text, x, y, em=1.0, font='brush', fill='dark', alpha=1.0, grad=None, grad_angle=90, image=None,
          image_focus=(0.5, 0.5), image_alpha=1.0, shadow=None, spacing=0.0, vertical=False, chars=None, w=None,
          h=None, align='left', anchor='top', name=None, rot=0, line=None, line_w=1.0):
    """Calligraphy text as one vector shape. em = inches per em (≈ 字号/72). (x, y) = top-left of the INK
    bounding box (tight, not the font line box), adjusted by align/anchor when w/h are given.
    Returns (shape, Box of the ink)."""
    path = outline(text, font, spacing, vertical, chars)
    S = 4000.0                                          # path units per em
    subs, vw, vh = _subpaths(path, S)
    bw, bh = vw / S * em, vh / S * em
    if w is not None:
        x += {'left': 0, 'center': (w - bw) / 2, 'right': w - bw}[align]
    if h is not None:
        y += {'top': 0, 'middle': (h - bh) / 2, 'bottom': h - bh}[anchor]
    from pptx.enum.shapes import MSO_SHAPE
    sh = cv.slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, emu(x), emu(y), emu(bw), emu(bh))
    X.strip_style(sh)
    _custgeom_single(sh, subs, vw, vh)
    cv._style(sh, fill=None if image else fill, alpha=alpha, grad=grad, grad_angle=grad_angle, shadow=shadow,
              rot=rot, line=line, line_w=line_w)
    if image:
        set_picture_fill(cv, sh, _crop_to(image, bw / bh, image_focus), image_alpha)
    sh.name = name or 'brush:' + (text or ''.join(c[0] for c in chars))[:12]
    return sh, Box(x, y, bw, bh)


def measure(text, em=1.0, font='brush', spacing=0.0, vertical=False, chars=None):
    """Ink box size (w, h) in inches without drawing."""
    x0, y0, x1, y1 = outline(text, font, spacing, vertical, chars).bounds
    return (x1 - x0) * em, (y1 - y0) * em


def stroke(cv, x, y, w, h, fill='dark', alpha=1.0, name='deco:stroke', glyph='一', font='brush', flip=False, **kw):
    """一笔毛笔横画（取毛笔字“一”的轮廓拉伸），作标题下划线 / 装饰笔触。"""
    sh, b = brush(cv, glyph, x, y, em=1.0, font=font, fill=fill, alpha=alpha, name=name, **kw)
    sh.left, sh.top, sh.width, sh.height = emu(x), emu(y), emu(w), emu(h)
    if flip:
        X.set_flip(sh, h=True)
    return sh


# ------------------------------------------------------------------ 印章
def _seal_texture(color='B23A2E', seed=3, px=600):
    """朱砂印泥质感：底色 + 细颗粒 + 少量“未着墨”的斑驳透明点。"""
    os.makedirs(GEN, exist_ok=True)
    out = os.path.join(GEN, f'seal_{color}_{seed}.png')
    if os.path.exists(out):
        return out
    rng = np.random.default_rng(seed)
    r, g, b = (int(color[i:i + 2], 16) for i in (0, 2, 4))
    n = rng.normal(0, 1, (px, px))
    n = np.array(Image.fromarray(((n - n.min()) / np.ptp(n) * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(1.2)),
                 float) / 255
    a = np.full((px, px), 255.0)
    holes = np.array(Image.fromarray((rng.random((px // 6, px // 6)) * 255).astype('uint8')).resize((px, px),
                                                                                                    Image.BICUBIC), float) / 255
    a[holes > 0.86] *= 0.55
    a[n > 0.68] *= 0.8
    shade = 0.92 + 0.12 * n
    rgb = np.stack([np.clip(r * shade, 0, 255), np.clip(g * shade, 0, 255), np.clip(b * shade, 0, 255)], -1)
    Image.fromarray(np.dstack([rgb, a]).astype('uint8'), 'RGBA').save(out)
    return out


def _rough_square(cx, cy, s, rng, jitter=0.012, n=14, r=0.06):
    """Hand-cut seal outline: square with slightly rounded, jittered edges (absolute inches)."""
    pts = []
    h = s / 2
    corners = [(-h, -h), (h, -h), (h, h), (-h, h)]
    for i in range(4):
        (ax, ay), (bx, by) = corners[i], corners[(i + 1) % 4]
        for k in range(n):
            t = k / n
            px, py = ax + (bx - ax) * t, ay + (by - ay) * t
            if k == 0:  # pull corners in a bit -> rounded
                px -= np.sign(px) * r * s * 0.35
                py -= np.sign(py) * r * s * 0.35
            pts.append((cx + px + rng.uniform(-jitter, jitter) * s, cy + py + rng.uniform(-jitter, jitter) * s))
    return pts


def seal(cv, cx, cy, size=0.6, text='安澜', font='li', color='accent', kind='white', seed=5, rot=0, name='deco:seal'):
    """印章。kind='white' 白文印（红底白字）| 'red' 朱文印（红框红字）。2 字竖排一列；4 字按 右上→右下→左上→左下 排。"""
    rng = random.Random(seed)
    nrng = np.random.default_rng(seed)
    col = cv.c(color)
    pts = _rough_square(cx, cy, size, rng)
    if kind == 'white':
        sh = cv.poly(pts, fill=col, name=name, rot=rot)
        set_picture_fill(cv, sh, _seal_texture(col, seed))
        ink = 'FFFFFF'
    else:
        sh = cv.poly(pts, fill=None, line=col, line_w=max(1.5, size * 5), name=name, rot=rot)
        ink = col
    n = len(text)
    pad = size * 0.14
    inner = size - 2 * pad
    if n <= 2:
        cell_w, cell_h = inner * (0.82 if n == 2 else 1), inner / n
        cells = [(cx - cell_w / 2, cy - inner / 2 + i * cell_h) for i in range(n)]
        cw, ch_ = cell_w, cell_h
    else:
        cw = ch_ = inner / 2
        order = [(1, 0), (1, 1), (0, 0), (0, 1)]          # 右列先读
        cells = [(cx - inner / 2 + c * cw, cy - inner / 2 + r * ch_) for c, r in order[:n]]
    for chx, (x0, y0) in zip(text, cells):
        gw, gh = measure(chx, 1.0, font)
        em = min(cw / gw, ch_ / gh) * 0.92
        brush(cv, chx, x0, y0, em=em, font=font, fill=ink, w=cw, h=ch_, align='center', anchor='middle',
              name=name + ':' + chx)
    return sh
