"""Cover / agenda variants distilled from 新参考 (国家科技进步奖 · 国家科学技术奖 · 国家重点研发计划 · 长江学者 ·
全国重点实验室 · 万人计划 templates). layouts_ac.cover()/agenda() dispatch here when the variant (usually set by
the skin) is one of COVERS / 'corner'.

  plaque   科技进步奖: white top (logo, year line), huge blue serif title, letter-spaced subtitle + fading rule,
           faint city skyline, presenter pill sitting on a bottom gradient band that holds the units + date.
  midband  科学技术奖 / 万人计划: logo or caption between rules, full-width blue band with the white serif title
           (+ subtitle), pill (solid | outline via theme.extras['cover_pill']), 牵头/依托单位 lines, units grid.
  arc      重点研发: navy block whose lower edge bows down (light echo crescent below), caption between rules,
           white serif title/subtitle, pill on the lowest point of the arc, units below.
  tag      长江学者: white card, navy trapezoid tag over its top edge, serif title, subtitle on a pale band with
           chevrons, split pill (汇报人 | name), navy swoosh along the bottom.
  lab      全国重点实验室: navy pill (评审 / 年度 line), lab name between long rules, huge serif title + subtitle,
           pale band with » 实验室主任：X «, left-aligned 依托 / 联合单位 block, halftone dot wave at the bottom.
"""
from __future__ import annotations

import math
import re

from . import images as IMG
from .canvas import Box, plain
from .parts import chevrons

W, H = 13.333, 7.5
COVERS = ('plaque', 'midband', 'arc', 'tag', 'lab')


# ------------------------------------------------------------------------------------------------ helpers
def rows_of(units, per=None):
    """Split a unit list into balanced rows (<= 5 per row unless `per` is given)."""
    units = [u for u in (units or []) if u]
    if not units:
        return []
    if per is None:
        per = len(units) if len(units) <= 3 else min(5, math.ceil(len(units) / math.ceil(len(units) / 5)))
    return [units[i:i + per] for i in range(0, len(units), per)]


def fading_rule(cv, x0, x1, y, color='primary+40', width=1.0, toward='left', name='deco:rule'):
    """Horizontal rule that fades out toward one end ('left' | 'right' | 'both')."""
    if toward == 'both':
        mid = (x0 + x1) / 2
        fading_rule(cv, x0, mid, y, color, width, 'left', name)
        return fading_rule(cv, mid, x1, y, color, width, 'right', name)
    stops = [(color, 0.0), (color, 1.0)] if toward == 'left' else [(color, 1.0), (color, 0.0)]
    return cv.line(x0, y, x1, y, color, width, grad=stops, name=name)


def rules_caption(cv, text, y, size=15, color='dark', rule='primary+40', h=0.42, x0=0.9, x1=None, gap=0.3,
                  role='title', bold=True, name='txt:cover_caption'):
    """Centered caption with long rules on both sides (fading toward the page edges). Returns the y below it."""
    x1 = W - 0.9 if x1 is None else x1
    tw = min(cv.width_of(text, size, role=role, bold=bold) + 0.12, x1 - x0 - 1.0)
    tx = (W - tw) / 2
    cv.text(tx, y, tw, h, text, size=size, color=color, role=role, bold=bold, align='center', anchor='middle',
            wrap=False, fit=True, min_size=9, name=name)
    if tx - gap - x0 > 0.3:
        fading_rule(cv, x0, tx - gap, y + h / 2, rule, 1.0, 'left', name='deco:caprule')
        fading_rule(cv, tx + tw + gap, x1, y + h / 2, rule, 1.0, 'right', name='deco:caprule')
    return y + h


def pill(cv, text, cx, y, h=0.52, size=17, style='solid', name='deco:pill'):
    """Presenter pill centred on cx. style: solid (blue gradient, white edge — sits on band edges) | navy (flat
    navy, no edge) | outline (white, grey edge, soft shadow, navy text) | ghost (white outline on dark)."""
    pw = cv.width_of(text, size, role='title', bold=True) + 1.0
    x = cx - pw / 2
    col = 'FFFFFF'
    if style == 'outline':
        cv.rect(x, y, pw, h, fill='FFFFFF', radius=h / 2, line='primary+62', line_w=1.0, name=name,
                shadow={'color': 'primary_deep', 'alpha': 0.16, 'blur': 10, 'dist': 2})
        col = 'primary_deep'
    elif style == 'ghost':
        cv.rect(x, y, pw, h, fill=None, line='FFFFFF', line_w=1.25, radius=h / 2, name=name)
    elif style == 'navy':
        cv.rect(x, y, pw, h, radius=h / 2, grad=[(0, 'primary_deep', 1.0), (100, 'primary', 1.0)], grad_angle=0,
                name=name)
    else:
        cv.rect(x, y, pw, h, radius=h / 2, grad=[(0, 'primary', 1.0), (100, 'primary_deep', 1.0)], grad_angle=0,
                line='FFFFFF', line_w=1.75, name=name,
                shadow={'color': 'primary_deep', 'alpha': 0.25, 'blur': 10, 'dist': 3})
    cv.text(x, y, pw, h, text, size=size, color=col, role='title', bold=True, align='center', anchor='middle',
            wrap=False, fit=True, min_size=10, name='txt:presenter')
    return pw


def split_pill(cv, text, cx, y, h=0.5, size=16):
    """长江-style pill: navy left half with the label (汇报人), white right half with the name."""
    if re.search('[：:]', text):
        k, v = re.split('[：:]', text, maxsplit=1)
    else:
        k, v = '汇报人', text
    k, v = k.strip(), v.strip()
    wl = cv.width_of(k, size, role='title', bold=True) + 0.8
    wr = cv.width_of(v, size, role='title', bold=True) + 0.9
    x = cx - (wl + wr) / 2
    cv.rect(x, y, wl + wr, h, fill='FFFFFF', radius=h / 2, line='primary+55', line_w=1.0, name='deco:pill_r',
            shadow={'color': 'primary_deep', 'alpha': 0.12, 'blur': 8, 'dist': 2})
    cv.rect(x, y, wl + 0.12, h, radius=h / 2, grad=[(0, 'primary_deep', 1.0), (100, 'primary', 1.0)], grad_angle=0,
            name='deco:pill_l')
    cv.text(x, y, wl + 0.12, h, k, size=size, color='FFFFFF', role='title', bold=True, align='center',
            anchor='middle', wrap=False, fit=True, min_size=10, name='txt:presenter_k')
    cv.text(x + wl + 0.12, y, wr - 0.12, h, v, size=size, color='primary_deep', role='title', bold=True,
            align='center', anchor='middle', wrap=False, fit=True, min_size=10, name='txt:presenter')


def units_grid(cv, units, y, size=12.5, color='dark', sep='primary+55', x0=0.75, x1=None, row_h=0.4, per=None,
               bold=True, sep_alpha=1.0):
    """Units as an aligned grid (科学技术奖 cover: 2 x 5 cells divided by thin vertical rules). Returns y below."""
    x1 = W - 0.75 if x1 is None else x1
    rows = rows_of(units, per)
    if not rows:
        return y
    ncol = max(len(r) for r in rows)
    maxw = max(cv.width_of(u, size, role='title' if bold else 'medium', bold=bold) for r in rows for u in r)
    cw = min((x1 - x0) / ncol, maxw + 0.75)
    for row in rows:
        off = (W - cw * len(row)) / 2
        for i, u in enumerate(row):
            cv.text(off + i * cw + 0.06, y, cw - 0.12, row_h, u, size=size, color=color,
                    role='title' if bold else 'medium', bold=bold, align='center', anchor='middle', wrap=False,
                    fit=True, min_size=7, name='txt:unit')
            if i:
                cv.line(off + i * cw, y + 0.1, off + i * cw, y + row_h - 0.1, sep, 1.0, alpha=sep_alpha,
                        name='deco:unitsep')
        y += row_h
    return y


def logo_center(cv, path, y, h=0.5):
    """Centred logo; returns its (x0, x1)."""
    from PIL import Image
    with Image.open(path) as im:
        iw, ih = im.size
    w = h * iw / ih
    x = (W - w) / 2
    cv.image(path, x, y, w, h, fit='stretch', name='deco:logo')
    return x, x + w


def _title_size(title, sizes=(64, 56, 46), limits=(9, 13)):
    n = len(plain(title).replace('\n', ''))
    return sizes[0] if n <= limits[0] else (sizes[1] if n <= limits[1] else sizes[2])


# ------------------------------------------------------------------------------------------------ covers
def cover(deck, variant, title, subtitle, project, presenter, infos, image=None, motif=None):
    cv = deck.new('cover', bg=False)
    {'plaque': _plaque, 'midband': _midband, 'arc': _arc, 'tag': _tag, 'lab': _lab}[variant](
        deck, cv, title, subtitle, project, presenter, list(infos or []), image, motif)
    return cv


def _plaque(deck, cv, title, subtitle, project, presenter, infos, image, motif):
    t, m = deck.theme, deck._meta
    units = m.get('units') or infos
    rows = rows_of(units, per=None if len(units) <= 3 else min(4, math.ceil(len(units) / 2)))
    date = m.get('date')
    bh = 0.42 + 0.42 * max(1, len(rows)) + (0.4 if date else 0) + 0.18
    by = H - bh
    cv.rect(0, 0, W, H, grad=[(0, 'FFFFFF', 1.0), (100, 'primary_bg', 1.0)], grad_angle=90, name='bg:base')
    if image:
        cv.image(IMG.fade(image, side='top', start=0.0, end=0.8), 0, by - 2.6, W, 2.6, fit='cover', alpha=0.4,
                 name='bg:photo')
    else:
        cv.image(IMG.skyline(t.c('primary+48'), size=(1600, 280), seed=5, alpha=0.38, fade='both', motif='city'),
                 0, by - 2.3, W, 2.3, fit='stretch', name='bg:skyline')
    y = 0.42
    if m.get('logo'):
        logo_center(cv, m['logo'], y, 0.46)
        y += 0.66
    else:
        y += 0.2
    if project:
        cv.text(1.0, y, W - 2.0, 0.42, project, size=16, color='dark', role='title', bold=True, align='center',
                wrap=False, fit=True, min_size=10, name='txt:project')
        y += 0.62
    ts = _title_size(title, (66, 56, 46))
    th = min(2.3, cv.measure(title, W - 1.4, ts, role='serif') + 0.12)
    cv.text(0.7, y, W - 1.4, th, title, size=ts, color='primary', role='serif', bold=True, align='center',
            anchor='middle', fit=True, min_size=30, max_lines=2, ls=1.05, spacing=2 if ts >= 56 else 0,
            grad=['primary+14', 'primary_deep'], grad_angle=90, name='txt:cover_title')
    y += th + 0.06
    if subtitle:
        cv.text(0.9, y, W - 1.8, 0.56, subtitle, size=23, color='primary_deep', role='serif', bold=True,
                align='center', wrap=False, fit=True, min_size=13, spacing=3, name='txt:subtitle')
        y += 0.68
        fading_rule(cv, 1.3, W - 1.3, y, 'primary+20', 1.0, 'both', name='deco:subrule')
    cv.rect(0, by, W, bh, grad=[(0, 'primary', 1.0), (100, 'primary_deep', 1.0)], grad_angle=0,
            name='deco:bottomband')
    N = 36
    wave = [(W * i / N, by + 0.16 + 0.1 * math.sin(2 * math.pi * i / N * 1.2 + 0.6)) for i in range(N + 1)]
    cv.poly(wave + [(W, by + bh), (0, by + bh)], fill='FFFFFF', alpha=0.07, smooth=True, name='deco:bandsheen')
    if presenter:
        pill(cv, presenter, W / 2, by - 0.28, h=0.56, size=18, style='solid')
    yy = by + (0.42 if presenter else 0.3)
    for row in rows:
        cv.text(0.6, yy, W - 1.2, 0.4, '  |  '.join(row), size=13.5, color='FFFFFF', role='title', bold=True,
                align='center', anchor='middle', wrap=False, fit=True, min_size=8, name='txt:units')
        yy += 0.42
    if date:
        cv.text(0.6, yy, W - 1.2, 0.38, date, size=13, color='FFFFFF', role='medium', align='center',
                anchor='middle', wrap=False, fit=True, alpha=0.92, name='txt:date')


def _midband(deck, cv, title, subtitle, project, presenter, infos, image, motif):
    t, m = deck.theme, deck._meta
    ex = t.extras or {}
    units = m.get('units') or []
    nrows = len(rows_of(units))
    cv.rect(0, 0, W, H, grad=[(0, 'FFFFFF', 1.0), (100, 'panel', 1.0)], grad_angle=90, name='bg:base')
    if ex.get('cover_texture', 'hex') == 'hex':
        cv.image(IMG.hexgrid(t.c('primary+30'), size=(1600, 900), alpha=0.18, fade='center'), 0, 0, W, H,
                 fit='stretch', name='bg:hex')
    else:      # plain: soft light sweep (万人计划)
        cv.poly([(0, H * 0.62), (W * 0.38, 0), (W * 0.55, 0), (0, H * 0.9)], fill='FFFFFF', alpha=0.7,
                name='bg:sweep')
        cv.rect(0, 0, W, H, grad=[(0, 'primary_bg', 0.0), (100, 'primary_bg', 0.9)], grad_angle=90,
                name='bg:fade')
    y = 0.42
    if m.get('logo'):
        a_, b_ = logo_center(cv, m['logo'], y, 0.5)
        fading_rule(cv, 1.2, a_ - 0.35, y + 0.25, 'primary+40', 1.0, 'left', name='deco:caprule')
        fading_rule(cv, b_ + 0.35, W - 1.2, y + 0.25, 'primary+40', 1.0, 'right', name='deco:caprule')
        y += 0.72
        if project:
            cv.text(1.0, y, W - 2.0, 0.4, project, size=15, color='dark', role='title', bold=True, align='center',
                    wrap=False, fit=True, min_size=9, name='txt:project')
            y += 0.5
    elif project and ex.get('cover_texture', 'hex') != 'hex':
        cv.text(1.0, y + 0.12, W - 2.0, 0.42, project, size=16, color='dark', role='title', bold=True,
                align='center', anchor='middle', wrap=False, fit=True, min_size=9, name='txt:project')
        y += 0.12 + 0.42 + 0.22
    elif project:
        y = rules_caption(cv, project, y + 0.12, size=16, color='dark', rule='primary+35') + 0.22
    else:
        y = 1.0
    # size the title so band + pill + info + units fit the page
    ts = _title_size(title, (60, 52, 44), (10, 14))
    while True:
        th = min(2.2, cv.measure(title, W - 1.6, ts, role='serif') + 0.12)
        band_h = 0.36 + th + (0.66 if subtitle else 0) + 0.3
        need = band_h + 0.36 + (0.8 if presenter else 0) + 0.44 * len(infos) + 0.4 * nrows + 0.1
        if y + 0.1 + need <= H - 0.3 or ts <= 34:
            break
        ts -= 2
    by = y + 0.1
    cv.rect(0, by, W, band_h, grad=[(0, 'primary', 1.0), (100, 'primary-12', 1.0)], grad_angle=0,
            name='bg:midband', shadow={'color': 'primary_deep', 'alpha': 0.28, 'blur': 16, 'dist': 5})
    tex = ex.get('band_image')
    if tex:
        cv.image(IMG.fade(tex, side='left', start=0.0, end=0.85), 0, by, W, band_h, fit='cover', alpha=0.22,
                 name='bg:bandphoto')
    else:
        cv.image(IMG.skyline('FFFFFF', size=(1600, 300), seed=9, alpha=0.14, fade='both', motif='city'),
                 0, by + band_h * 0.22, W, band_h * 0.78, fit='stretch', name='bg:bandsky')
    cv.text(0.8, by + 0.33, W - 1.6, th, title, size=ts, color='FFFFFF', role='serif', bold=True, align='center',
            anchor='middle', fit=True, min_size=28, max_lines=2, ls=1.1, spacing=2 if ts >= 52 else 0,
            name='txt:cover_title')
    if subtitle:
        cv.text(0.8, by + 0.33 + th + 0.02, W - 1.6, 0.6, subtitle, size=26, color='FFFFFF', role='serif',
                bold=True, align='center', anchor='middle', wrap=False, fit=True, min_size=14, name='txt:subtitle')
    y = by + band_h + 0.36
    if presenter:
        pill(cv, presenter, W / 2, y, h=0.52, size=17, style=ex.get('cover_pill', 'navy'))
        y += 0.8
    for line in infos:
        cv.text(1.0, y, W - 2.0, 0.4, line, size=15, color='dark', role='title', bold=True, align='center',
                anchor='middle', wrap=False, fit=True, min_size=9, name='txt:info')
        y += 0.44
    if units:
        units_grid(cv, units, y + 0.06, size=12.5, color='dark', sep='primary+50')


def _arc(deck, cv, title, subtitle, project, presenter, infos, image, motif):
    t, m = deck.theme, deck._meta
    lines = list(infos) + ['  |  '.join(r) for r in rows_of(m.get('units'))]
    cv.rect(0, 0, W, H, grad=[(0, 'panel', 1.0), (100, 'FFFFFF', 1.0)], grad_angle=90, name='bg:base')
    cv.image(IMG.skyline(t.c('primary+55'), size=(1600, 260), seed=3, alpha=0.3, fade='both', motif='water'),
             0, H - 1.55, W, 1.5, fit='stretch', name='bg:skyline')
    ts = _title_size(title, (60, 52, 44), (10, 14))
    th = min(2.1, cv.measure(title, W - 1.6, ts, role='serif') + 0.12)
    top = 0.55
    y = top + (0.62 if project else 0.1)
    y_title = y
    y += th + 0.04
    y_sub = y
    y += 0.66 if subtitle else 0
    ys = max(3.2, y + 0.45)                       # navy edge at the page sides
    yc = min(ys + 0.95, H - 0.6 - 0.46 * len(lines) - 0.2)   # lowest point (centre)
    yc = max(yc, ys + 0.5)
    N = 64

    def curve(y_side, y_mid):
        return [(W * i / N, y_side + (y_mid - y_side) * (1 - (2 * i / N - 1) ** 2)) for i in range(N + 1)]

    cv.poly([(0, 0), (W, 0)] + curve(ys + 0.12, yc + 0.24)[::-1], fill='primary+70', alpha=0.55,
            name='bg:arcecho')
    cv.poly([(0, 0), (W, 0)] + curve(ys, yc)[::-1], grad=[(0, 'primary_deep', 1.0), (100, 'primary', 1.0)],
            grad_angle=70, name='bg:arcblock')
    tex = (t.extras or {}).get('band_image')
    if tex:
        cv.image(IMG.fade(tex, side='left', start=0.0, end=0.9), W * 0.35, 0, W * 0.65, ys, fit='cover', alpha=0.2,
                 name='bg:arcphoto')
    else:
        cv.image(IMG.skyline('FFFFFF', size=(1600, 280), seed=13, alpha=0.13, fade='both', motif='water'),
                 0, ys - 1.65, W, 1.6, fit='stretch', name='bg:arcsky')
    if project:
        rules_caption(cv, project, top, size=15, color='FFFFFF', rule='FFFFFF', x0=1.6, x1=W - 1.6)
    cv.text(0.8, y_title, W - 1.6, th, title, size=ts, color='FFFFFF', role='serif', bold=True, align='center',
            anchor='middle', fit=True, min_size=28, max_lines=2, ls=1.08, spacing=2 if ts >= 52 else 0,
            name='txt:cover_title')
    if subtitle:
        cv.text(0.8, y_sub, W - 1.6, 0.6, subtitle, size=27, color='FFFFFF', role='serif', bold=True,
                align='center', anchor='middle', wrap=False, fit=True, min_size=14, spacing=1, name='txt:subtitle')
    if presenter:
        pill(cv, presenter, W / 2, yc - 0.28, h=0.56, size=17, style='solid')
    yy = yc + 0.48
    for line in lines:
        cv.text(1.0, yy, W - 2.0, 0.4, line, size=15, color='dark', role='title', bold=True, align='center',
                anchor='middle', wrap=False, fit=True, min_size=9, name='txt:info')
        yy += 0.46


def _tag(deck, cv, title, subtitle, project, presenter, infos, image, motif):
    m = deck._meta
    lines = list(infos) + ['  |  '.join(r) for r in rows_of(m.get('units'))]
    cv.rect(0, 0, W, H, grad=[(0, 'panel', 1.0), (100, 'primary_bg', 1.0)], grad_angle=45, name='bg:base')
    cv.poly([(0, H * 0.5), (W * 0.42, 0), (W * 0.6, 0), (0, H * 0.78)], fill='FFFFFF', alpha=0.55, name='bg:sweep')
    cv.poly([(W * 0.52, H), (W, H * 0.22), (W, H * 0.44), (W * 0.72, H)], fill='FFFFFF', alpha=0.5,
            name='bg:sweep')
    card = Box(0.7, 0.92, W - 1.4, H - 1.7)
    cv.rect(card.x, card.y, card.w, card.h, fill='FFFFFF', radius=0.1, name='deco:card',
            shadow={'color': 'primary_deep', 'alpha': 0.14, 'blur': 22, 'dist': 5})
    ts = _title_size(title, (66, 56, 46), (8, 12))
    th = min(2.1, cv.measure(title, card.w - 1.2, ts, role='serif') + 0.12)
    sub_h = 0.66 if subtitle else 0
    total = th + (0.18 + sub_h if subtitle else 0) + (0.38 + 0.5 if presenter else 0) + \
        (0.3 + 0.42 * len(lines) if lines else 0)
    y = max(card.y + 0.6, card.y + (card.h - total) / 2 + 0.05)
    inner_b = y + th + (0.18 + sub_h if subtitle else 0) + 0.25
    cv.rect(card.x + 0.4, card.y + 0.42, card.w - 0.8, inner_b - card.y - 0.42, radius=0.08,
            grad=[(0, 'FFFFFF', 1.0), (100, 'primary_bg', 1.0)], grad_angle=90, line='primary+82', line_w=0.75,
            name='deco:inner')
    if project:
        tw = min(card.w - 2.0, cv.width_of(project, 15, role='title', bold=True) + 1.3)
        tx, ty, tth = (W - tw) / 2, card.y - 0.24, 0.5
        cv.poly([(tx, ty), (tx + tw, ty), (tx + tw - 0.24, ty + tth), (tx + 0.24, ty + tth)],
                grad=[(0, 'primary_deep', 1.0), (100, 'primary', 1.0)], grad_angle=0, name='deco:tag')
        cv.text(tx + 0.3, ty, tw - 0.6, tth, project, size=15, color='FFFFFF', role='title', bold=True,
                align='center', anchor='middle', wrap=False, fit=True, min_size=9, name='txt:project')
    cv.text(card.x + 0.6, y, card.w - 1.2, th, title, size=ts, color='primary_deep', role='serif', bold=True,
            align='center', anchor='middle', fit=True, min_size=30, max_lines=2, ls=1.05,
            spacing=4 if ts >= 56 else 1, name='txt:cover_title')
    y += th + 0.18
    if subtitle:
        bw = min(card.w - 1.4, cv.width_of(subtitle, 26, role='serif', bold=True, spacing=2) + 3.0)
        bx = (W - bw) / 2
        cv.rect(bx, y, bw, sub_h, grad=[(0, 'primary+78', 0.0), (50, 'primary+78', 1.0), (100, 'primary+78', 0.0)],
                grad_angle=0, name='deco:subband')
        chevrons(cv, bx + 0.42, y + sub_h / 2, 'primary+35', point='right')
        chevrons(cv, bx + bw - 0.42 - 0.4, y + sub_h / 2, 'primary+35', point='left')
        cv.text(bx + 1.0, y, bw - 2.0, sub_h, subtitle, size=26, color='primary_deep', role='serif', bold=True,
                align='center', anchor='middle', wrap=False, fit=True, min_size=14, spacing=2, name='txt:subtitle')
        y += sub_h
    y = max(y, inner_b - 0.25) + 0.38
    if presenter:
        split_pill(cv, presenter, W / 2, y, h=0.5, size=16)
        y += 0.5 + 0.3
    for line in lines:
        cv.text(1.2, y, W - 2.4, 0.38, line, size=14, color='dark', role='title', bold=True, align='center',
                anchor='middle', wrap=False, fit=True, min_size=9, name='txt:info')
        y += 0.42
    # navy swoosh along the bottom (crosses the card's lower edge)
    N = 40
    cv.poly([(W * i / N, H - 0.86 + 0.66 * (i / N) ** 1.3) for i in range(N + 1)] + [(W, H), (0, H)],
            fill='primary+45', alpha=0.45, name='deco:swoosh2')
    cv.poly([(W * i / N, H - 0.6 + 0.5 * (i / N) ** 1.6) for i in range(N + 1)] + [(W, H), (0, H)],
            grad=[(0, 'primary_deep', 1.0), (100, 'primary', 1.0)], grad_angle=0, name='deco:swoosh')


def _lab(deck, cv, title, subtitle, project, presenter, infos, image, motif):
    t, m = deck.theme, deck._meta
    lab = m.get('lab')
    infos = [s for s in infos if not (lab and s.startswith('所在实验室'))]
    lines = list(infos) + ['  |  '.join(r) for r in rows_of(m.get('units'))]
    cv.rect(0, 0, W, H, grad=[(0, 'FFFFFF', 1.0), (100, 'panel', 1.0)], grad_angle=90, name='bg:base')
    cv.image(IMG.dot_wave(t.c('primary+25'), size=(1600, 420), alpha=0.3), 0, H - 2.5, W, 2.5, fit='stretch',
             name='bg:dotwave')
    ts = _title_size(title, (62, 54, 46), (10, 13))
    th = min(2.1, cv.measure(title, W - 1.4, ts, role='serif') + 0.12)
    total = (0.5 + 0.3 if project else 0) + (0.42 + 0.3 if lab else 0) + th + (0.62 if subtitle else 0) + \
        (0.3 + 0.62 if presenter else 0) + (0.25 + 0.44 * len(lines) if lines else 0)
    y = max(0.45, (H - total) / 2 - 0.15)
    if project:
        pill(cv, project, W / 2, y, h=0.5, size=16, style='navy', name='deco:toppill')
        y += 0.8
    if lab:
        y = rules_caption(cv, lab, y, size=15, color='primary_deep', rule='primary+25', x0=0.7, x1=W - 0.7) + 0.3
    cv.text(0.7, y, W - 1.4, th, title, size=ts, color='primary', role='serif', bold=True, align='center',
            anchor='middle', fit=True, min_size=30, max_lines=2, ls=1.05, spacing=2 if ts >= 54 else 0,
            name='txt:cover_title')
    y += th
    if subtitle:
        cv.text(0.8, y, W - 1.6, 0.6, subtitle, size=30, color='primary_deep', role='serif', bold=True,
                align='center', anchor='middle', wrap=False, fit=True, min_size=15, spacing=1, name='txt:subtitle')
        y += 0.62
    if presenter:
        y += 0.3
        cv.rect(0.8, y, W - 1.6, 0.62, grad=[(0, 'primary+80', 0.0), (50, 'primary+76', 1.0), (100, 'primary+80', 0.0)],
                grad_angle=0, name='deco:presband')
        pw = min(W - 4, cv.width_of(presenter, 19, role='title', bold=True) + 0.3)
        px = (W - pw) / 2
        cv.text(px, y, pw, 0.62, presenter, size=19, color='primary_deep', role='title', bold=True, align='center',
                anchor='middle', wrap=False, fit=True, min_size=11, name='txt:presenter')
        chevrons(cv, px - 0.75, y + 0.31, 'primary', point='right')
        chevrons(cv, px + pw + 0.35, y + 0.31, 'primary', point='left')
        y += 0.62
    if lines:
        y += 0.25
        lw = min(W - 2.0, max(cv.width_of(s, 15, role='title', bold=True) for s in lines) + 0.2)
        for line in lines:
            cv.text((W - lw) / 2, y, lw, 0.4, line, size=15, color='dark', role='title', bold=True, anchor='middle',
                    wrap=False, fit=True, min_size=9, name='txt:info')
            y += 0.44


# ------------------------------------------------------------------------------------------------ agenda
def agenda_corner(deck, cv, items, current=None, title='汇报目录', en='CONTENTS', descs=None):
    """重点研发 目录: white card with diagonal corner sashes, vertical serif title + faint vertical CONTENTS,
    numbered rows on soft fading bars (current chapter in red)."""
    t = deck.theme
    n = max(len(items), 1)
    cv.rect(0, 0, W, H, grad=[(0, 'panel', 1.0), (100, 'primary_bg', 1.0)], grad_angle=90, name='bg:base')
    cv.image(IMG.skyline(t.c('primary+50'), size=(1600, 260), seed=6, alpha=0.32, fade='both', motif='water'),
             0, H - 1.75, W, 1.65, fit='stretch', name='bg:skyline')
    cv.rect(0, H - 0.09, W, 0.09, fill='primary', name='deco:baseline')
    card = Box(1.3, 0.78, W - 2.6, H - 1.56)
    cv.rect(card.x, card.y, card.w, card.h, fill='FFFFFF', name='deco:card',
            shadow={'color': 'primary_deep', 'alpha': 0.16, 'blur': 24, 'dist': 6})
    d1, d2 = 0.6, 0.86
    cv.poly([(card.x, card.y + d1), (card.x + d1, card.y), (card.x + d2, card.y), (card.x, card.y + d2)],
            fill='primary', name='deco:corner')
    cv.poly([(card.r, card.b - d1), (card.r - d1, card.b), (card.r - d2, card.b), (card.r, card.b - d2)],
            fill='primary', name='deco:corner')
    tx = card.x + 0.9
    cv.text(tx, card.y + 0.55, 0.55, card.h - 1.1, en, size=26, color='primary+72', role='number', bold=True,
            vert='vert', align='center', anchor='middle', spacing=4, wrap=False, fit=False,
            name='deco:agenda_en')
    cv.line(tx + 0.78, card.y + 1.0, tx + 0.78, card.b - 1.0, 'primary+50', 1.0, name='deco:agenda_rule')
    chars = list(title if len(title) <= 4 else '目录')
    cv.text(tx + 1.0, card.y + 0.4, 1.25, card.h - 0.8, '\n'.join(chars), size=52, color='primary_deep',
            role='serif', bold=True, align='center', anchor='middle', ls=1.0, sa=4, fit=True, min_size=26,
            name='txt:agenda_title')
    area = Box(tx + 2.75, card.y + 0.5, card.r - (tx + 2.75) - 0.75, card.h - 1.0)
    rh = min(1.0, area.h / n)
    y0 = area.y + (area.h - rh * n) / 2
    for i, it in enumerate(items):
        on = current is not None and i == current
        dim = current is not None and not on
        y = y0 + i * rh
        hh = rh - 0.22
        cv.rect(area.x - 0.12, y + 0.11, area.w + 0.12, hh, grad=[(0, 'panel', 1.0), (100, 'FFFFFF', 0.0)],
                grad_angle=0, name='deco:agenda_row',
                shadow={'color': 'primary_deep', 'alpha': 0.07, 'blur': 8, 'dist': 3})
        col = 'emph' if on else ('A3ADBF' if dim else 'primary_deep')
        ncol = 'emph' if on else ('B8C2D6' if dim else 'primary')
        cv.text(area.x + 0.12, y + 0.11, 0.62, hh, f'{i + 1:02d}', size=24, color=ncol, role='number', bold=True,
                anchor='middle', wrap=False, fit=False, name='txt:agenda_num')
        cv.line(area.x + 0.8, y + 0.11 + hh * 0.26, area.x + 0.8, y + 0.11 + hh * 0.74, ncol, 1.25,
                name='deco:agenda_sep')
        cv.text(area.x + 1.02, y + 0.11, area.w - 1.1, hh * (0.6 if descs else 1), it, size=24, color=col,
                role='title', bold=True, anchor='middle' if not descs else 'bottom', spacing=2, wrap=False, fit=True,
                min_size=12, name='txt:agenda_item')
        if descs and i < len(descs) and descs[i]:
            cv.text(area.x + 1.04, y + 0.11 + hh * 0.62, area.w - 1.15, hh * 0.36, descs[i], size=11,
                    color='muted' if not dim else 'B8C2D6', wrap=False, fit=True, name='txt:agenda_desc')


def agenda_band(deck, cv, items, current=None, title='汇报提纲', en='CONTENTS', descs=None):
    """科技奖 横排目录: navy title band (serif title, spaced CONTENTS, faint skyline) + a row of numbered cards
    overlapping its lower edge (current chapter outlined in red, others dimmed)."""
    n = max(len(items), 1)
    cv.rect(0, 0, W, H, grad=[(0, 'FFFFFF', 1.0), (100, 'panel', 1.0)], grad_angle=90, name='bg:base')
    bh = 2.45
    cv.rect(0, 0, W, bh, grad=[(0, 'primary_deep', 1.0), (100, 'primary', 1.0)], grad_angle=0, name='deco:agendaband')
    cv.image(IMG.skyline('FFFFFF', size=(1600, 280), seed=4, alpha=0.14, fade='both', motif='city'), 0, bh - 1.45,
             W, 1.4, fit='stretch', name='bg:bandsky')
    cv.text(0, 0.4, W, 0.95, title, size=44, color='FFFFFF', role='serif', bold=True, align='center',
            anchor='middle', spacing=6, wrap=False, fit=True, min_size=24, name='txt:agenda_title')
    cv.text(0, 1.33, W, 0.38, en, size=14, color='FFFFFF', alpha=0.72, spacing=8, align='center', anchor='middle',
            wrap=False, fit=True, name='deco:agenda_en')
    area = Box(0.8, bh - 0.6, W - 1.6, H - bh - 0.05)
    for i, (b, it) in enumerate(zip(area.cols(n, gap=0.3), items)):
        on = current is not None and i == current
        dim = current is not None and not on
        cv.rect(b.x, b.y, b.w, b.h, fill='FFFFFF', radius=0.08, line='emph' if on else 'panel_line',
                line_w=1.5 if on else 0.75, name='deco:agenda_card',
                shadow={'color': 'primary_deep', 'alpha': 0.14, 'blur': 16, 'dist': 4})
        ncol = 'emph' if on else ('B8C2D6' if dim else 'primary')
        col = 'emph' if on else ('A3ADBF' if dim else 'primary_deep')
        desc = descs[i] if descs and i < len(descs) else None
        blk = 0.85 + 0.32 + 0.95 + (1.2 if desc else 0)
        y0 = b.y + max(0.25, (b.h - 0.6 - blk) / 2)
        cv.text(b.x, y0, b.w, 0.85, f'{i + 1:02d}', size=44, color=ncol, role='number', bold=True,
                align='center', anchor='middle', wrap=False, fit=False, name='txt:agenda_num')
        cv.rect(b.cx - 0.3, y0 + 0.92, 0.6, 0.06, fill=ncol, name='deco:agenda_rule')
        cv.text(b.x + 0.2, y0 + 1.17, b.w - 0.4, 0.95, it, size=21, color=col, role='title', bold=True,
                align='center', anchor='top', fit=True, min_size=12, max_lines=2, ls=1.1, name='txt:agenda_item')
        if desc:
            cv.text(b.x + 0.2, y0 + 2.17, b.w - 0.4, 1.15, desc, size=12, color='muted' if not dim else 'B8C2D6',
                    align='center', anchor='top', fit=True, min_size=9, name='txt:agenda_desc')
        cv.text(b.x, b.b - 0.55, b.w, 0.32, f'PART {i + 1:02d}', size=11, color=ncol, alpha=0.75, role='number',
                bold=True, spacing=3, align='center', anchor='middle', wrap=False, fit=False, name='deco:agenda_part')
