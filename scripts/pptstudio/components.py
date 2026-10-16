"""Reusable visual components (house style distilled from the reference decks).

All functions take a Canvas `cv` first; coordinates in inches.
"""
from __future__ import annotations

import math

from . import color as C
from .canvas import Box, plain


# ---------------------------------------------------------------- backgrounds
def background(cv, kind='content', style=None, strength=1.0):
    """Page background per theme.bg_style: soft | plain | grid | dots | dark_glow.
    kind: content | cover | section (covers/sections get stronger decoration)."""
    t = cv.t
    style = style or t.bg_style
    W, H = cv.W, cv.H
    if t.is_dark or style == 'dark_glow':
        cv.rect(0, 0, W, H, grad=[(0, t.bg2, 1.0), (100, t.bg, 1.0)], grad_angle=60, name='bg:base')
        if t.decoration != 'min' or kind != 'content':
            glow_orb(cv, W * 0.92, -0.6, 3.6 * strength, 'primary', 0.38 if kind != 'content' else 0.22)
            glow_orb(cv, -0.8, H + 0.4, 3.2 * strength, 'secondary', 0.22 if kind != 'content' else 0.12)
        return
    if style == 'plain':
        cv.rect(0, 0, W, H, fill='bg', name='bg:base')
        return
    # soft light: very light diagonal gradient
    cv.rect(0, 0, W, H, grad=[(0, t.c('primary_bg'), 1.0), (55, t.bg, 1.0), (100, t.bg, 1.0)], grad_angle=35,
            name='bg:base')
    if style == 'grid':
        _grid(cv, 0.42, t.c('primary'), 0.05)
    elif style == 'dots':
        _dots(cv, 0.3, t.c('primary'), 0.10)
    deco = t.decoration
    if kind == 'content':
        if deco != 'min':
            glow_orb(cv, W + 0.4, -0.9, 2.6, 'primary', 0.07 if deco == 'normal' else 0.10)
        if deco == 'rich':
            glow_orb(cv, -0.9, H + 0.6, 2.4, 'secondary', 0.08)
    else:
        glow_orb(cv, W - 0.8, -0.5, 3.8 * strength, 'primary', 0.12)
        glow_orb(cv, 0.6, H + 0.9, 3.4 * strength, 'secondary', 0.10)


def _grid(cv, step, col, alpha):
    x = step
    while x < cv.W:
        cv.line(x, 0, x, cv.H, col, 0.5, alpha, name='bg:grid')
        x += step
    y = step
    while y < cv.H:
        cv.line(0, y, cv.W, y, col, 0.5, alpha, name='bg:grid')
        y += step


def _dots(cv, step, col, alpha):
    from .images import dot_texture
    p = dot_texture(col, alpha, step)
    cv.image(p, 0, 0, cv.W, cv.H, fit='stretch', name='bg:dots')


def glow_orb(cv, cx, cy, r, color='primary', alpha=0.2, name='deco:orb'):
    """Radial-gradient circle (color at center fading to transparent)."""
    return cv.circle(cx, cy, r, grad=[(0, color, alpha), (100, color, 0.0)], grad_kind='radial', name=name)


def watermark(cv, text, x, y, w, h, size=96, color='primary', alpha=0.06, align='left', role='heavy', spacing=0):
    """Huge faint (English) word as texture behind titles."""
    return cv.text(x, y, w, h, text, size=size, color=color, alpha=alpha, role=role, align=align, fit=True,
                   min_size=36, wrap=False, anchor='top', spacing=spacing, name='deco:watermark')


def waves(cv, y=5.9, h=1.7, colors=('primary', 'secondary'), alphas=(0.16, 0.10), phase=0.0, amp=0.18, n=2):
    """Layered smooth wave bands filling from y to slide bottom."""
    W, H = cv.W, cv.H
    out = []
    for i in range(n):
        pts = []
        k = 9
        a = amp * (1 - 0.25 * i)
        yy = y + i * h * 0.22
        for j in range(k + 1):
            x = W * j / k
            pts.append((x, yy + a * math.sin(2 * math.pi * (j / k) * 1.15 + phase + i * 1.3)))
        poly = pts + [(W, H + 0.02), (0, H + 0.02)]
        col = colors[i % len(colors)]
        al = alphas[i % len(alphas)]
        out.append(cv.poly(poly, fill=None, grad=[(col, al), (col, al * 1.8)], grad_angle=90, smooth=False,
                           name='deco:wave'))
    return out


def wave_curve(cv, x0, x1, y, amp, color='primary', width=1.5, alpha=0.5, periods=1.0, phase=0.0, name='deco:curve'):
    pts = []
    k = 24
    for j in range(k + 1):
        x = x0 + (x1 - x0) * j / k
        pts.append((x, y + amp * math.sin(2 * math.pi * periods * j / k + phase)))
    return cv.poly(pts, fill=None, line=color, line_w=width, closed=False, smooth=True, name=name)


# ---------------------------------------------------------------- titles & chrome
def page_title(cv, title, en=None, x=None, y=None, w=None, size=None, color='dark', align='left', logo=True):
    """Content-page title (top-left, single line, auto-shrinks). Returns bottom y (inches)."""
    t = cv.t
    x = t.margin_x if x is None else x
    y = t.title_y if y is None else y
    right_pad = 0
    if logo and cv.deck.meta.get('logo') and cv.deck.nav != 'top':
        right_pad = 1.6
    w = (cv.W - x - t.margin_x - right_pad) if w is None else w
    size = size or t.size_title
    tx = x
    if t.title_style == 'mark':
        cv.rect(x, y + 0.14, 0.09, size / 72 * 0.95, fill='primary', radius=0.03, name='deco:titlemark')
        tx = x + 0.22
    cv.text(tx, y, w - (tx - x), size / 72 * 1.35, title, size=size, color=color, role='title', align=align,
            wrap=False, fit=True, min_size=min(20, size), anchor='top', name='txt:title')
    bottom = y + size / 72 * 1.3
    if en and t.title_style in ('en', 'mark'):
        cv.text(tx, bottom - 0.02, w, 0.28, en.upper(), size=10, color='muted', role='body', wrap=False, fit=True,
                min_size=7, spacing=0.6, name='txt:title_en')
        bottom += 0.24
    return bottom


def logo(cv, path=None, x=None, y=None, h=0.42, align='right'):
    path = path or cv.deck.meta.get('logo')
    if not path:
        return None
    from PIL import Image
    with Image.open(path) as im:
        iw, ih = im.size
    w = h * iw / ih
    x = (cv.W - cv.t.margin_x - w) if x is None and align == 'right' else (cv.t.margin_x if x is None else x)
    y = cv.t.title_y + 0.05 if y is None else y
    return cv.image(path, x, y, w, h, fit='stretch', name='deco:logo')


def footer(cv, page=None, source=None, show_page=True):
    t = cv.t
    y = cv.H - 0.42
    if source:
        cv.text(t.margin_x, y, 9.5, 0.28, source, size=9, color='muted', fit=True, min_size=7, wrap=False,
                name='txt:source')
    if show_page and page is not None:
        cv.text(cv.W - t.margin_x - 1.0, y, 1.0, 0.28, f'{page:02d}', size=10, color='muted', role='number',
                align='right', fit=False, wrap=False, name='deco:pageno')


def nav_top(cv, sections, current, y=0.0, h=0.52, show_logo=True):
    """Horizontal navigation bar (web-style tabs). current: 0-based index. Returns bar bottom y."""
    t = cv.t
    W = cv.W
    cv.rect(0, y, W, h, fill='surface' if not t.is_dark else 'bg2', name='deco:navbar',
            shadow={'color': 'primary_dark', 'alpha': 0.06, 'blur': 10, 'dist': 2})
    x0 = t.margin_x
    lg = cv.deck.meta.get('logo')
    if lg and show_logo:
        logo(cv, lg, x=x0, y=y + 0.09, h=h - 0.18, align='left')
    n = len(sections)
    area_w = min(9.6, 1.7 * n)
    xs = W - t.margin_x - area_w
    cw = area_w / n
    for i, s in enumerate(sections):
        cx = xs + cw * i
        on = i == current
        cv.text(cx, y, cw, h, s, size=12, color='primary' if on else 'muted', bold=on, align='center',
                anchor='middle', wrap=False, fit=True, min_size=9, name=f'txt:nav{i}')
        if on:
            tw = min(cw * 0.7, cv.width_of(s, 12, bold=True) + 0.1)
            cv.rect(cx + (cw - tw) / 2, y + h - 0.06, tw, 0.06, fill='primary', radius=0.03, name='deco:navon')
    return y + h


def nav_left(cv, sections, current, w=2.05):
    """Left sidebar navigation: dark primary panel, logo on top, current item = light pill. Returns sidebar width."""
    t = cv.t
    H = cv.H
    cv.rect(0, 0, w, H, grad=[('primary', 1.0), ('primary_dark', 1.0)], grad_angle=90, name='deco:sidebar')
    lg = cv.deck.meta.get('logo')
    top = 0.55
    if lg:
        logo(cv, lg, x=0.35, y=0.45, h=0.5, align='left')
        top = 1.35
    n = len(sections)
    ih = min(0.52, (H - top - 0.8) / max(1, n))
    for i, s in enumerate(sections):
        yy = top + 0.35 + i * (ih + 0.08)
        on = i == current
        if on:
            cv.rect(0.22, yy, w - 0.22 + 0.12, ih, fill='surface', radius=ih / 2, name='deco:navpill')
        cv.text(0.45, yy, w - 0.6, ih, s, size=12.5, color='primary' if on else 'FFFFFF', bold=on,
                alpha=1.0 if on else 0.82, anchor='middle', wrap=False, fit=True, min_size=9, name=f'txt:nav{i}')
    return w


# ---------------------------------------------------------------- containers
def card(cv, box, style=None, radius=None, fill=None, name='deco:card', line=None, alpha=None):
    t = cv.t
    style = style or t.card_style
    r = t.radius if radius is None else radius
    if style == 'shadow':
        return cv.rect(box.x, box.y, box.w, box.h, fill=fill or 'surface', radius=r, shadow='soft', name=name,
                       alpha=alpha or 1.0)
    if style == 'tint':
        return cv.rect(box.x, box.y, box.w, box.h, fill=fill or 'primary_bg', radius=r, name=name, alpha=alpha or 1.0)
    if style == 'outline':
        return cv.rect(box.x, box.y, box.w, box.h, fill=fill or 'surface', radius=r, line=line or 'line', line_w=1.0,
                       name=name, alpha=alpha or 1.0)
    if style == 'glass':
        return cv.rect(box.x, box.y, box.w, box.h, fill=fill or 'surface', alpha=alpha or 0.62, radius=r,
                       line='FFFFFF', line_w=0.75, line_alpha=0.14, name=name)
    return cv.rect(box.x, box.y, box.w, box.h, fill=fill or 'bg2', radius=r, name=name, alpha=alpha or 1.0)


def icon_badge(cv, cx, cy, d, icon, style=None, color=None, name='deco:badge'):
    """Icon inside a circle. style: circle_grad | circle_pale | square_grad | ring | plain."""
    t = cv.t
    style = style or t.icon_style
    col = color or 'primary'
    if style == 'plain':
        return cv.icon(icon, cx - d / 2, cy - d / 2, d, col)
    if style in ('circle_grad', 'square_grad'):
        if style == 'circle_grad':
            cv.circle(cx, cy, d / 2, grad=[(0, 'secondary' if col == 'primary' else col + '+25', 1.0),
                                           (100, col, 1.0)], grad_angle=45, name=name,
                      shadow={'color': col, 'alpha': 0.25, 'blur': 12, 'dist': 3})
        else:
            cv.rect(cx - d / 2, cy - d / 2, d, d, radius=d * 0.26,
                    grad=[(0, 'secondary' if col == 'primary' else col + '+25', 1.0), (100, col, 1.0)],
                    grad_angle=45, name=name, shadow={'color': col, 'alpha': 0.25, 'blur': 12, 'dist': 3})
        s = d * 0.52
        return cv.icon(icon, cx - s / 2, cy - s / 2, s, 'FFFFFF')
    if style == 'ring':
        cv.circle(cx, cy, d / 2, fill='surface', line=col, line_w=1.25, name=name)
        s = d * 0.5
        return cv.icon(icon, cx - s / 2, cy - s / 2, s, col)
    # circle_pale
    cv.circle(cx, cy, d / 2, fill=(col + '+86') if not t.is_dark else col, alpha=1.0 if not t.is_dark else 0.25,
              name=name)
    s = d * 0.5
    return cv.icon(icon, cx - s / 2, cy - s / 2, s, col if not t.is_dark else 'FFFFFF')


def num_badge(cv, cx, cy, d, n, style='fill', color='primary', size=None):
    txt = f'{n:02d}' if isinstance(n, int) else str(n)
    size = max(10.5, size or d * 72 * 0.42)
    if style == 'fill':
        cv.circle(cx, cy, d / 2, grad=[(0, color + '+25', 1.0), (100, color, 1.0)], grad_angle=45, name='deco:numbadge')
        fc = 'FFFFFF'
    elif style == 'outline':
        cv.circle(cx, cy, d / 2, fill='surface', line=color, line_w=1.5, name='deco:numbadge')
        fc = color
    else:
        cv.circle(cx, cy, d / 2, fill=color + '+86', name='deco:numbadge')
        fc = color
    return cv.text(cx - d / 2, cy - d / 2, d, d, txt, size=size, color=fc, role='number', bold=True, align='center',
                   anchor='middle', wrap=False, fit=False, name='txt:num')


def pill(cv, x, y, text, size=12, fill='primary', color='FFFFFF', h=None, pad=0.16, align='left', bold=True,
         line=None, alpha=1.0, role='body'):
    """Rounded label. Returns (shape, width). align='center' treats x as center."""
    h = h or size / 72 * 1.9
    w = cv.width_of(text, size, role=role, bold=bold) + 2 * pad
    if align == 'center':
        x = x - w / 2
    elif align == 'right':
        x = x - w
    sh = cv.rect(x, y, w, h, fill=fill, radius=h / 2, line=line, alpha=alpha, name='deco:pill')
    cv.text(x, y, w, h, text, size=size, color=color, bold=bold, align='center', anchor='middle', wrap=False,
            fit=False, role=role, name='txt:pill')
    return sh, w


def kpi(cv, box, value, unit='', label='', sub=None, color='primary', align='left', size=None, trend=None,
        label_color='text'):
    """Big number + small unit + label (+ optional sub line). trend: 'up'|'down'|None."""
    t = cv.t
    num_h = box.h * 0.58 if label else box.h
    size = size or min(60, max(24, num_h * 72 * 0.72))
    # shrink to fit width
    usize = size * 0.42
    while size > 20 and (cv.width_of(str(value), size, role='number', bold=True) +
                         cv.width_of(unit, usize, bold=True) + 0.08) > box.w * 0.96:
        size -= 1
        usize = size * 0.42
    tb = cv.slide.shapes.add_textbox(*[int(v * 914400) for v in (box.x, box.y, box.w, num_h)])
    from . import oxml as X
    X.set_body(tb, 0, 0, 0, 0, anchor='b', wrap=False)
    p = tb.text_frame.paragraphs[0]
    X.set_para(p, align=align, line_spacing=0.9, bullet='')
    r = p.add_run()
    r.text = str(value)
    ea, lat, _ = t.font('number')
    X.style_run(r, size=size, bold=True, hexclr=t.c(color), ea=ea, latin=lat)
    if unit:
        r2 = p.add_run()
        r2.text = ' ' + unit if unit[0].isascii() and unit[0].isalpha() else unit
        X.style_run(r2, size=usize, bold=True, hexclr=t.c(color), ea=t.f_body, latin=lat)
    if trend:
        r3 = p.add_run()
        r3.text = ' ▲' if trend == 'up' else ' ▼'
        X.style_run(r3, size=usize * 0.8, hexclr=t.c('up' if trend == 'up' else 'down'), ea=t.f_body, latin=lat)
    tb.name = 'txt:kpi'
    y = box.y + num_h + 0.04
    if label:
        cv.text(box.x, y, box.w, max(0.3, box.h - num_h - 0.04), label + (('\n' + sub) if sub else ''),
                size=t.size_small, color=label_color, align=align, fit=True, min_size=9,
                name='txt:kpilabel')
    return tb


def heading_block(cv, x, y, w, head, body=None, head_size=None, body_size=None, head_color='dark',
                  body_color='text', gap=0.08, align='left', max_h=None, role_head='title'):
    """Heading + body paragraph stacked; returns total height used (inches)."""
    t = cv.t
    hs = head_size or t.size_heading
    bs = body_size or t.size_body - 1
    hh = cv.measure(head, w, hs, role=role_head)
    hh = max(hh, hs / 72 * 1.2)
    cv.text(x, y, w, hh + 0.02, head, size=hs, color=head_color, role=role_head, align=align, fit=True,
            min_size=hs - 4, name='txt:head')
    used = hh
    if body:
        avail = (max_h - hh - gap) if max_h else None
        bh = cv.measure(body, w, bs)
        if avail is not None:
            bh = max(0.3, min(bh + 0.05, avail))
        cv.text(x, y + hh + gap, w, bh + 0.02, body, size=bs, color=body_color, align=align, fit=True,
                name='txt:body')
        used += gap + bh
    return used


def bullets(cv, box, items, size=None, marker='dot', color='text', marker_color='primary', gap=None, ls=None):
    """Vertical list with markers: dot | num | check | icon (items as dicts with 'icon') | none."""
    t = cv.t
    size = size or t.size_body
    n = len(items)
    gap = gap if gap is not None else size / 72 * 0.55
    mk_w = size / 72 * (1.9 if marker == 'num' else 1.3)
    texts = [it['text'] if isinstance(it, dict) else it for it in items]
    heights = [cv.measure(tx, box.w - mk_w, size, ls=ls) for tx in texts]
    total = sum(heights) + gap * (n - 1)
    s = size
    while total > box.h and s > t.size_min:
        s -= 0.5
        heights = [cv.measure(tx, box.w - mk_w, s, ls=ls) for tx in texts]
        total = sum(heights) + gap * (n - 1)
    y = box.y
    for i, (tx, hgt) in enumerate(zip(texts, heights)):
        line1 = s / 72 * 1.2
        if marker == 'dot':
            d = s / 72 * 0.36
            cv.circle(box.x + d / 2 + 0.02, y + line1 / 2, d / 2, fill=marker_color, name='deco:dot')
        elif marker == 'num':
            num_badge(cv, box.x + s / 72 * 0.62, y + line1 / 2, s / 72 * 1.2, i + 1, style='fill', color=marker_color,
                      size=s * 0.62)
        elif marker == 'check':
            cv.icon('circle-check', box.x, y + (line1 - s / 72) / 2, s / 72, marker_color)
        elif marker == 'icon':
            ic = items[i].get('icon', 'circle-dot') if isinstance(items[i], dict) else 'circle-dot'
            cv.icon(ic, box.x, y + (line1 - s / 72 * 1.05) / 2, s / 72 * 1.05, marker_color)
        cv.text(box.x + mk_w, y, box.w - mk_w, hgt + 0.02, tx, size=s, color=color, fit=False, ls=ls,
                name='txt:bullet')
        y += hgt + gap
    return y - gap - box.y


def divider(cv, x, y, w, color='line', width=1.0, dash=None):
    return cv.line(x, y, x + w, y, color, width, dash=dash, name='deco:divider')


def quote_mark(cv, x, y, size=1.0, color='primary', alpha=0.25):
    return cv.text(x, y, size * 1.2, size * 1.2, '“', size=size * 110, color=color, alpha=alpha, role='serif',
                   fit=False, wrap=False, name='deco:quote')


def arrow(cv, x1, y1, x2, y2, color='primary', width=1.5, alpha=1.0, dash=None):
    return cv.line(x1, y1, x2, y2, color, width, alpha, dash=dash, tail='triangle', name='deco:arrow')


def chevron_arrow(cv, cx, cy, size=0.28, color='primary', alpha=1.0):
    """Small '›' style arrow (for process gaps)."""
    pts = [(cx - size * 0.25, cy - size * 0.5), (cx + size * 0.25, cy), (cx - size * 0.25, cy + size * 0.5)]
    return cv.poly(pts, fill=None, line=color, line_w=2.0, closed=False, name='deco:chev', alpha=alpha)


def section_label(cv, x, y, text, size=12, style='pill'):
    """'第二部分' / 'PART 02' chip."""
    if style == 'pill':
        return pill(cv, x, y, text, size=size, fill='primary', color='FFFFFF')
    return cv.text(x, y, 4, size / 72 * 1.6, text, size=size, color='primary', bold=True, fit=False, wrap=False,
                   spacing=1.0)


def fmt_num(n):
    return f'{n:02d}'



def screen_frame(cv, box, image=None, kind='browser', url='', shadow=True, placeholder='截图'):
    """Put a screenshot into a native device frame (all shapes editable). kind: browser | phone | laptop.
    The frame keeps the screenshot's aspect ratio and is centered in box. Returns the screen Box."""
    from PIL import Image as _I
    ar = 16 / 10
    if image:
        with _I.open(image) as im:
            ar = im.width / im.height
    if kind == 'phone':
        ar = min(ar, 0.62)
        bez = 0.09
        h = box.h
        w = (h - 2 * bez) * ar + 2 * bez
        if w > box.w:
            w = box.w
            h = (w - 2 * bez) / ar + 2 * bez
        x, y = box.x + (box.w - w) / 2, box.y + (box.h - h) / 2
        cv.rect(x, y, w, h, fill='1D1F24', radius=min(w, h) * 0.12, name='deco:phone',
                shadow='soft' if shadow else None)
        sc = Box(x + bez, y + bez, w - 2 * bez, h - 2 * bez)
        if image:
            cv.image(image, sc.x, sc.y, sc.w, sc.h, fit='cover', radius=min(sc.w, sc.h) * 0.1, name='img:screen')
        else:
            cv.rect(sc.x, sc.y, sc.w, sc.h, fill='panel', radius=min(sc.w, sc.h) * 0.1, name='deco:screen')
        cv.rect(x + w / 2 - w * 0.14, y + bez + 0.05, w * 0.28, 0.08, fill='1D1F24', radius=0.04, name='deco:notch')
        return sc
    top = 0.3 if kind == 'browser' else 0.14
    base_h = 0.22 if kind == 'laptop' else 0
    avail_h = box.h - base_h
    w = box.w if kind == 'browser' else box.w * 0.84
    sh = w / ar
    if sh + top > avail_h:
        sh = avail_h - top
        w = sh * ar
    h = sh + top
    x, y = box.x + (box.w - w) / 2, box.y + (avail_h - h) / 2
    if kind == 'browser':
        cv.rect(x, y, w, h, fill='FFFFFF', line='C9CED6', line_w=0.75, radius=0.08, name='deco:browser',
                shadow='soft' if shadow else None)
        cv.rect(x, y, w, top, fill='EEF0F3', radius=0.08, name='deco:browserbar')
        cv.rect(x, y + top - 0.08, w, 0.08, fill='EEF0F3', name='deco:browserbar2')
        for k, col in enumerate(('FF5F57', 'FEBC2E', '28C840')):
            cv.circle(x + 0.18 + k * 0.17, y + top / 2, 0.05, fill=col, name='deco:dot')
        cv.rect(x + 0.8, y + 0.07, min(4.0, w - 1.2), top - 0.14, fill='FFFFFF', radius=(top - 0.14) / 2,
                name='deco:urlbar')
        if url:
            cv.text(x + 0.95, y + 0.07, min(3.8, w - 1.4), top - 0.14, url, size=8, color='muted', anchor='middle',
                    wrap=False, fit=True, min_size=6, name='deco:url')
        sc = Box(x + 0.01, y + top, w - 0.02, sh - 0.01)
    else:  # laptop
        bz = 0.12
        cv.rect(x, y, w, h, fill='2A2D34', radius=0.1, name='deco:laptop', shadow='soft' if shadow else None)
        sc = Box(x + bz, y + bz, w - 2 * bz, h - 2 * bz)
        bw = w * 1.16
        cv.shape('trapezoid', x - (bw - w) / 2, y + h, bw, base_h, fill='C9CED6', adj={'adj': 12000},
                 name='deco:laptopbase', rot=180)
    if image:
        cv.image(image, sc.x, sc.y, sc.w, sc.h, fit='cover', name='img:screen')
    else:
        cv.rect(sc.x, sc.y, sc.w, sc.h, fill='panel', name='deco:screen')
        cv.text(sc.x, sc.cy - 0.15, sc.w, 0.3, placeholder, size=11, color='muted', align='center', wrap=False)
    return sc
