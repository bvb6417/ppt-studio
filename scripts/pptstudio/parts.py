"""Building blocks distilled from 新参考 (国家科技奖 / 重点研发 / 长江学者 / 重点实验室 / 万人计划 decks and 科研架构图).
Re-exported by `pptstudio.academic`, so call them as `A.level_chip(...)`, `A.laurel(...)` etc.

    LEVELS, level_key, level_color   risk levels: 低 green 72AE48 · 中 orange EE7F32 · 高 red BF0202
    chip            small rounded label: soft (grey-blue, navy text) | outline | fill
    level_chip      '级别高' chip (soft with a colored level word, or filled with the level color)
    chevrons        » / « chevron group (cover bands, risk headers, closing bars)
    silhouette      ID-photo placeholder drawn with shapes (blue background, suit silhouette)
    person          photo (or silhouette) + navy name band + red role caption
    laurel          award badge: two laurel branches + award name + grade + ★
    stars           row of ★ (center one larger)
    certificate     certificate placeholder (gold frame, title, text lines, red seal) or a framed certificate photo
    metric_box      dashed box: label + big red value (+ ↑ / ↓)
    converge        V-shaped convergence: left / right statements -> centre keyword -> red conclusion
    vchain          bordered column with a navy header and boxes joined by down arrows
    arc_text        characters placed along a circular arc (curved labels on hub diagrams)
    hub_node        ring node of a 科研架构图 (white circle, colored outline, title + sub bubbles / sub label)
    cylinder        horizontal 3-D can with text (bottom chains of 科研架构图)
All coordinates in inches; colors are theme roles / named colors / hex.
"""
from __future__ import annotations

import math

from .canvas import Box, plain

LEVELS = {'低': '72AE48', '中': 'EE7F32', '高': 'BF0202'}
_ALIASES = {'low': '低', 'l': '低', 'medium': '中', 'mid': '中', 'm': '中', 'high': '高', 'h': '高'}


def level_key(level):
    s = str(level or '').strip()
    s = _ALIASES.get(s.lower(), s)
    for k in LEVELS:
        if k in s:
            return k
    return '中'


def level_color(level):
    return LEVELS[level_key(level)]


# ---------------------------------------------------------------- chips
def chip(cv, x, y, w, h, text, style='soft', color='primary', size=None, name='deco:chip'):
    """Small label. style: soft (grey-blue gradient, navy text, tiny shadow) | outline (white, colored border and
    text) | fill (colored, white text). Text may carry {{color|..}} / [[..]] markup."""
    size = size or min(cv.t.size_body, h * 72 * 0.48)
    if style == 'fill':
        cv.rect(x, y, w, h, fill=color, radius=0.05, name=name)
        fg = 'FFFFFF'
    elif style == 'outline':
        cv.rect(x, y, w, h, fill='FFFFFF', line=color, line_w=1.0, radius=0.05, name=name)
        fg = color
    else:
        cv.rect(x, y, w, h, grad=[(0, 'panel', 1.0), (100, 'primary+80', 1.0)], grad_angle=90, radius=0.05,
                name=name, shadow={'color': 'primary_deep', 'alpha': 0.1, 'blur': 4, 'dist': 1})
        fg = 'primary_deep'
    cv.text(x + 0.04, y, w - 0.08, h, text, size=size, color=fg, role='title', bold=True, align='center',
            anchor='middle', wrap=False, fit=True, min_size=8, name='txt:chip')


def level_chip(cv, x, y, w, h, level, style='soft', prefix='级别', size=None):
    """Risk-level chip: soft = grey chip '级别' + level word in its color; fill = chip filled with the level color."""
    k = level_key(level)
    col = LEVELS[k]
    if style == 'fill':
        chip(cv, x, y, w, h, f'{prefix}{k}', style='fill', color=col, size=size)
    else:
        chip(cv, x, y, w, h, prefix + '{{' + col + '|' + k + '}}', style='soft', size=size)


def chevrons(cv, x, cy, color='primary', n=2, size=0.24, point='right', alpha=1.0, gap=0.1):
    """Small » / « chevron group; x = left edge of the group. Returns the group width."""
    step = size * 0.55 + gap * 0.4
    for k in range(n):
        fade = k if point == 'right' else n - 1 - k
        cv.shape('chevron', x + k * step, cy - size / 2, size * 0.55, size, fill=color, alpha=alpha * (1 - 0.3 * fade),
                 adj={'adj': 55000}, rot=180 if point == 'left' else 0, name='deco:chev')
    return n * step


# ---------------------------------------------------------------- people
def silhouette(cv, x, y, w, h, bg='primary+55', body='primary_deep'):
    """ID-photo placeholder: blue gradient background, head + suit silhouette (replace with a real photo)."""
    cv.rect(x, y, w, h, grad=[(0, bg + '+25' if '+' not in bg else 'primary+75', 1.0), (100, bg, 1.0)],
            grad_angle=90, name='deco:photo_bg')
    hr = min(w * 0.19, h * 0.15)
    cx = x + w / 2
    hy = y + h * 0.38
    bw = min(w * 0.78, hr * 4.2)
    cv.shape('round2SameRect', cx - bw / 2, hy + hr * 1.18, bw, y + h - (hy + hr * 1.18), fill=body, alpha=0.92,
             adj={'adj1': 50000, 'adj2': 0}, name='deco:photo_body')
    cv.shape('triangle', cx - hr * 0.42, hy + hr * 1.12, hr * 0.84, hr * 1.0, fill='FFFFFF', rot=180,
             name='deco:photo_collar')
    cv.circle(cx, hy, hr, fill='F3F6FB', name='deco:photo_head')


def person(cv, box, name=None, role=None, photo=None, band=True, role_color='emph', size=None, focus=(0.5, 0.3)):
    """Photo card: photo (cover-cropped) or silhouette; navy name band over the photo's lower edge (band=False puts
    the name under the photo); role caption under it in red."""
    t = cv.t
    size = size or max(9.5, min(t.size_body, box.w * 72 * 0.14))
    nh = size / 72 * 1.7
    cap_h = (size / 72 * 1.5) if role else 0
    below = 0 if band else nh
    ph = box.h - cap_h - below
    if photo:
        cv.image(photo, box.x, box.y, box.w, ph, fit='cover', focus=focus, name='img:person')
    else:
        silhouette(cv, box.x, box.y, box.w, ph)
    if name:
        if band:
            cv.rect(box.x, box.y + ph - nh, box.w, nh, fill='primary_deep', alpha=0.9, name='deco:nameband')
            cv.text(box.x, box.y + ph - nh, box.w, nh, name, size=size, color='FFFFFF', role='title', bold=True,
                    align='center', anchor='middle', wrap=False, fit=True, min_size=7, name='txt:person')
        else:
            cv.text(box.x - 0.1, box.y + ph, box.w + 0.2, nh, name, size=size, color='primary_deep', role='title',
                    bold=True, align='center', anchor='middle', wrap=False, fit=True, min_size=7, name='txt:person')
    if role:
        cv.text(box.x - 0.12, box.b - cap_h, box.w + 0.24, cap_h, role, size=size - 1.5, color=role_color,
                role='title', bold=True, align='center', anchor='middle', wrap=False, fit=True, min_size=7,
                name='txt:role')


# ---------------------------------------------------------------- awards
def stars(cv, cx, cy, n=3, size=0.14, color='primary', gap=0.05, center_big=True):
    """Row of ★ centred on (cx, cy); with an odd count the middle star is slightly larger."""
    total = n * size + (n - 1) * gap
    x0 = cx - total / 2
    for i in range(n):
        s = size * (1.3 if center_big and n % 2 == 1 and n > 1 and i == n // 2 else 1.0)
        cv.shape('star5', x0 + i * (size + gap) + (size - s) / 2, cy - s / 2, s, s, fill=color, name='deco:star')


def laurel(cv, cx, cy, w, h, title, sub=None, color='primary', sub_color='emph', n_stars=3, size=None):
    """Award badge: two laurel branches around the award name (navy) and grade (red), small ★ under them."""
    R = min(w * 0.5, h * 0.62)
    stem = max(0.018, R * 0.03)
    L, Wd = R * 0.3, R * 0.12
    for th0, th1, left in ((205, 335, True), (25, 155, False)):    # degrees clockwise from 12 o'clock
        cv.ring(cx, cy, R, stem, color=color, start=th0, sweep=th1 - th0, name='deco:laurelstem')
        n = 6
        for k in range(n):
            th = th0 + (th1 - th0) * (k + 0.55) / n
            px = cx + R * math.sin(math.radians(th))
            py = cy - R * math.cos(math.radians(th))
            up = th if left else th + 180          # direction pointing toward the branch tip (upwards)
            sc = 0.7 + 0.3 * (k / (n - 1) if left else 1 - k / (n - 1))
            for off in (-34, 34):
                a = up + off
                lx = px + math.cos(math.radians(a)) * L * sc * 0.5
                ly = py + math.sin(math.radians(a)) * L * sc * 0.5
                cv.ellipse(lx - L * sc / 2, ly - Wd * sc / 2, L * sc, Wd * sc, fill=color, rot=a, name='deco:leaf')
    tw = R * 1.55
    size = size or max(10, min(15, tw * 72 / max(4, len(plain(title))) * 0.95))
    th_ = size / 72 * 1.5
    y = cy - (th_ * (2 if sub else 1)) / 2 - (0.06 if n_stars else 0)
    cv.text(cx - tw / 2, y, tw, th_, title, size=size, color='primary_deep', role='title', bold=True, align='center',
            anchor='middle', wrap=False, fit=True, min_size=8, name='txt:laurel')
    if sub:
        cv.text(cx - tw / 2, y + th_, tw, th_, sub, size=size, color=sub_color, role='title', bold=True,
                align='center', anchor='middle', wrap=False, fit=True, min_size=8, name='txt:laurelsub')
    if n_stars:
        stars(cv, cx, y + th_ * (2 if sub else 1) + 0.1, n_stars, size=0.11, color=color, gap=0.05)


def certificate(cv, box, image=None, title='荣誉证书', seal=True):
    """Certificate on a shelf: a framed photo (image=) or a drawn placeholder (gold frame, title, text lines, seal)."""
    shadow = {'color': '000000', 'alpha': 0.2, 'blur': 10, 'dist': 3}
    if image:
        cv.rect(box.x, box.y, box.w, box.h, fill='FFFFFF', line='D5D9E0', line_w=0.5, shadow=shadow,
                name='deco:cert')
        cv.image(image, box.x + 0.04, box.y + 0.04, box.w - 0.08, box.h - 0.08, fit='contain', name='img:cert')
        return
    cv.rect(box.x, box.y, box.w, box.h, fill='FFFEF9', line='D9C38F', line_w=0.75, shadow=shadow, name='deco:cert')
    m = min(box.w, box.h) * 0.06
    cv.rect(box.x + m, box.y + m, box.w - 2 * m, box.h - 2 * m, fill=None, line='C9A45C', line_w=1.25,
            name='deco:certframe')
    cv.rect(box.x + m * 1.6, box.y + m * 1.6, box.w - 3.2 * m, box.h - 3.2 * m, fill=None, line='E3CFA0',
            line_w=0.5, name='deco:certframe2')
    n = max(1, len(plain(title)))
    ts = max(6, min(16, box.w * 72 * 0.13, (box.w - 4 * m) * 72 / (n * (0.74 if plain(title).isascii() else 1.08))))
    cv.text(box.x, box.y + box.h * 0.14, box.w, ts / 72 * 1.6, title, size=ts, color='B3261E', role='serif',
            bold=True, align='center', anchor='middle', wrap=False, fit=True, min_size=6, spacing=1,
            name='txt:certtitle')
    lx0, lx1 = box.x + box.w * 0.2, box.r - box.w * 0.2
    for k in range(4):
        yy = box.y + box.h * (0.42 + 0.1 * k)
        cv.rect(lx0 + (0.0 if k else box.w * 0.08), yy, (lx1 - lx0) * (0.62 if k == 3 else 1.0) -
                (0.0 if k else box.w * 0.16), max(0.012, box.h * 0.018), fill='CBD2DC', name='deco:certline')
    if seal:
        r = min(box.w, box.h) * 0.11
        cv.circle(box.r - box.w * 0.28, box.b - box.h * 0.2, r, fill=None, line='D62828', line_w=1.25,
                  name='deco:seal')
        cv.shape('star5', box.r - box.w * 0.28 - r * 0.45, box.b - box.h * 0.2 - r * 0.45, r * 0.9, r * 0.9,
                 fill='D62828', name='deco:sealstar')


# ---------------------------------------------------------------- metrics / flows
def metric_box(cv, box, label, value, unit='', arrow=None, dashed=True, color='emph', size=None):
    """Dashed box with a label and a big red value ('复杂场景决策准确率降低 25.6%'). arrow: 'up' | 'down' | None."""
    t = cv.t
    cv.rect(box.x, box.y, box.w, box.h, fill='FFFFFF', line='primary', line_w=1.0, dash='dash' if dashed else None,
            radius=0.04, name='deco:metric')
    size = size or min(26, box.h * 72 * 0.55)
    ls = max(10, min(t.size_body, size * 0.55))
    vw = cv.width_of(f'{value}{unit}', size, role='number', bold=True) + 0.1
    aw = 0.3 if arrow else 0
    lw = min(box.w - vw - aw - 0.3, cv.width_of(label, ls, role='medium') + 0.1)
    x0 = box.x + (box.w - lw - vw - aw - 0.1) / 2
    cv.text(x0, box.y, lw, box.h, label, size=ls, color='dark', role='medium', anchor='middle', wrap=False, fit=True,
            min_size=8, name='txt:metriclabel')
    cv.text(x0 + lw + 0.1, box.y, vw, box.h, f'{value}{unit}', size=size, color=color, role='number', bold=True,
            anchor='middle', wrap=False, fit=False, name='txt:metric')
    if arrow:
        ah = box.h * 0.5
        cv.shape('upArrow' if arrow == 'up' else 'downArrow', x0 + lw + 0.1 + vw, box.cy - ah / 2, 0.22, ah,
                 fill=color, name='deco:metricarrow')


def converge(cv, box, left=None, right=None, center='科学机遇', conclusion=None, color='primary', size=None):
    """V-shaped convergence (长江学者 背景页): side statements funnel into a red centre keyword and a red conclusion.
    box: the whole strip (≈ 1.3–1.7 in tall)."""
    t = cv.t
    size = size or t.size_body
    side_w = box.w * 0.36
    th = min(0.66, box.h * 0.42)
    if left:
        cv.text(box.x, box.y, side_w, th, left, size=size, color='dark', role='medium', align='center',
                anchor='middle', fit=True, min_size=9, name='txt:convleft')
    if right:
        cv.text(box.r - side_w, box.y, side_w, th, right, size=size, color='dark', role='medium', align='center',
                anchor='middle', fit=True, min_size=9, name='txt:convright')
    if center:
        cv.text(box.cx - 1.4, box.y + 0.02, 2.8, th * 0.75, center, size=size + 4, color='emph', role='title',
                bold=True, align='center', anchor='middle', wrap=False, fit=True, min_size=10, spacing=1,
                name='txt:convcenter')
    ya = box.y + th + 0.02
    yb = ya + max(0.22, box.h * 0.2)
    tk = 0.09
    x0, x1 = box.x + box.w * 0.08, box.r - box.w * 0.08
    cv.poly([(x0, ya), (box.cx, yb), (x1, ya), (x1, ya + tk), (box.cx, yb + tk * 1.6), (x0, ya + tk)],
            grad=[(0, color + '+75', 0.3), (50, color + '+30', 1.0), (100, color + '+75', 0.3)], grad_angle=0,
            name='deco:converge')
    cv.shape('triangle', box.cx - 0.13, yb + tk * 1.2, 0.26, 0.14, fill=color + '+30', rot=180,
             name='deco:convtip')
    if conclusion:
        cv.text(box.x, yb + tk * 1.2 + 0.16, box.w, box.b - (yb + tk * 1.2 + 0.16), conclusion, size=size + 3,
                color='emph', role='title', bold=True, align='center', anchor='middle', fit=True, min_size=10,
                name='txt:convconclusion')


def vchain(cv, box, items, header=None, highlight=(), size=None, header_h=0.5):
    """Bordered column (实施路径 / 保障机制): navy header + stacked light boxes joined by ▼ arrows.
    highlight: indices whose text is red."""
    t = cv.t
    size = size or t.size_body + 1
    cv.rect(box.x, box.y, box.w, box.h, fill='FFFFFF', line='primary', line_w=1.5, name='deco:vchain')
    y = box.y
    if header:
        cv.rect(box.x, box.y, box.w, header_h, grad=[(0, 'primary', 1.0), (100, 'primary_deep', 1.0)],
                grad_angle=0, name='deco:vchainhead')
        cv.text(box.x + 0.08, box.y, box.w - 0.16, header_h, header, size=size + 1, color='FFFFFF', role='title',
                bold=True, align='center', anchor='middle', wrap=False, fit=True, min_size=9, name='txt:vchainhead')
        y += header_h
    n = max(len(items), 1)
    inner = Box(box.x + 0.16, y + 0.16, box.w - 0.32, box.b - y - 0.32)
    g = 0.3
    bh = min(0.72, (inner.h - g * (n - 1)) / n)
    y0 = inner.y + (inner.h - bh * n - g * (n - 1)) / 2
    for i, it in enumerate(items):
        yy = y0 + i * (bh + g)
        cv.rect(inner.x, yy, inner.w, bh, grad=[(0, 'FFFFFF', 1.0), (100, 'primary_bg', 1.0)], grad_angle=90,
                line='primary+55', line_w=0.75, name='deco:vchainbox',
                shadow={'color': 'primary_deep', 'alpha': 0.08, 'blur': 6, 'dist': 2})
        cv.text(inner.x + 0.08, yy, inner.w - 0.16, bh, it, size=size, color='emph' if i in highlight else
                'primary_deep', role='title', bold=True, align='center', anchor='middle', fit=True, min_size=9,
                name='txt:vchainitem')
        if i < n - 1:
            cv.shape('downArrow', inner.cx - 0.13, yy + bh + 0.04, 0.26, g - 0.08, fill='primary+25',
                     adj={'adj1': 50000, 'adj2': 45000}, name='deco:vchainarrow')


# ---------------------------------------------------------------- hub diagrams (科研架构图)
def arc_text(cv, cx, cy, r, text, start, end=None, size=14, color='emph', role='title', bold=True):
    """Characters placed along a circle of radius r around (cx, cy). Angles in degrees, clockwise from 12 o'clock.
    Give start > end to run counter-clockwise (upright text along the lower half). Without end the spacing follows
    the font size."""
    chars = [c for c in plain(text) if c.strip()]
    n = len(chars)
    if not n:
        return
    step = math.degrees((size / 72 * 1.15) / r)
    if end is not None and n > 1:
        step = (end - start) / (n - 1)
    elif end is not None and end < start:
        step = -step
    s = size / 72 * 1.3
    for i, ch in enumerate(chars):
        th = start + i * step
        x = cx + r * math.sin(math.radians(th))
        y = cy - r * math.cos(math.radians(th))
        tt = th % 360
        rot = th if (tt <= 90 or tt >= 270) else th + 180
        cv.text(x - s / 2, y - s / 2, s, s, ch, size=size, color=color, role=role, bold=bold, align='center',
                anchor='middle', wrap=False, fit=False, rot=rot % 360, name='txt:arc')


def hub_node(cv, cx, cy, r, title, subs=None, color='primary_deep', size=None):
    """Ring node: white circle with a colored outline, bold title, and either up to two small filled sub bubbles
    (subs=[a, b]) or one rounded sub label (subs='...')."""
    size = size or max(10, min(16, r * 72 * 0.3))
    cv.circle(cx, cy, r, fill='FFFFFF', line=color, line_w=1.75, name='deco:hubnode',
              shadow={'color': 'primary_deep', 'alpha': 0.12, 'blur': 8, 'dist': 2})
    if not subs:
        cv.text(cx - r * 0.85, cy - r * 0.5, r * 1.7, r, title, size=size, color=color, role='title', bold=True,
                align='center', anchor='middle', fit=True, min_size=8, name='txt:hubnode')
        return
    cv.text(cx - r * 0.85, cy - r * 0.78, r * 1.7, r * 0.6, title, size=size, color=color, role='title', bold=True,
            align='center', anchor='middle', wrap=False, fit=True, min_size=8, name='txt:hubnode')
    if isinstance(subs, str):
        bw, bh = r * 1.5, r * 0.62
        cv.rect(cx - bw / 2, cy - 0.02, bw, bh, fill='FFFFFF', line=color + '+40', line_w=0.75, radius=bh / 2,
                name='deco:hubsub')
        cv.text(cx - bw / 2 + 0.04, cy - 0.02, bw - 0.08, bh, subs, size=size * 0.62, color='dark', role='title',
                bold=True, align='center', anchor='middle', fit=True, min_size=6.5, name='txt:hubsub')
        return
    k = min(2, len(subs))
    br = r * (0.35 if k == 2 else 0.4)
    for i, s_ in enumerate(subs[:2]):
        bx = cx + (i - (k - 1) / 2) * br * 2.2
        cv.circle(bx, cy + r * 0.3, br, fill=color, name='deco:hubbubble')
        cv.text(bx - br, cy + r * 0.3 - br, 2 * br, 2 * br, s_, size=max(10, min(12, br * 72 * 0.6)),
                color='FFFFFF', role='title', bold=True, align='center', anchor='middle', wrap=False, fit=True,
                min_size=9, name='txt:hubbubble')


def cylinder(cv, x, y, w, h, text, color='primary_deep', size=None, highlight=False):
    """Horizontal 3-D can with a label (bottom chains of hub diagrams)."""
    cap = h * 0.42
    col = 'emph' if highlight else color
    cv.ellipse(x, y, cap, h, fill=col + '-10' if col.isalpha() or '_' in col else col, name='deco:cylcap0')
    cv.rect(x + cap / 2, y, w - cap, h, grad=[(0, col + '+30', 1.0), (45, col, 1.0), (100, col + '-15', 1.0)],
            grad_angle=90, name='deco:cylbody')
    cv.ellipse(x + w - cap, y, cap, h, grad=[(0, col + '+45', 1.0), (100, col + '+20', 1.0)], grad_angle=45,
               name='deco:cylcap1')
    size = size or max(9, min(15, h * 72 * 0.42))
    cv.text(x + cap * 0.5, y, w - cap * 1.5, h, text, size=size, color='FFFFFF', role='title', bold=True,
            align='center', anchor='middle', wrap=False, fit=True, min_size=7, name='txt:cylinder')
