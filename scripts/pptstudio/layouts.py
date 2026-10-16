"""Page layouts. Every function takes the Deck first and returns the Canvas it drew on.

Catalog (see references/layout-catalog.md for when-to-use & capacity):
  cover, agenda, section, ending                       -- structure pages
  cards, bullets, text_image, kpis, quote, band, split -- text/content pages
  chart_page, table_page, timeline, process, hub, compare, matrix, pyramid, figure, team, image_grid,
  references                                           -- see layouts2.py
"""
from __future__ import annotations

from . import components as K
from . import images as IMG
from .canvas import Box, plain
from .units import SLIDE_W, SLIDE_H

REGISTRY = {}


def layout(fn):
    """Register a layout as a Deck method. Names are global across modules (modern + defense layouts share one
    namespace), so a second @layout with the same name is an error — pick a distinct name instead."""
    old = REGISTRY.get(fn.__name__)
    if old is not None and old.__module__ != fn.__module__:
        raise ValueError(f'layout name clash: {fn.__name__!r} already defined in {old.__module__}')
    REGISTRY[fn.__name__] = fn
    return fn


def _info_lines(deck, info):
    m = deck._meta
    if info is None:
        info = []
        if m.get('author'):
            info.append(('user', f"汇报人：{m['author']}"))
        if m.get('advisor'):
            info.append(('graduation-cap', f"指导教师：{m['advisor']}"))
        if m.get('org'):
            info.append(('building', m['org']))
        if m.get('date'):
            info.append(('calendar', m['date']))
    out = []
    for it in info:
        if isinstance(it, (tuple, list)):
            out.append((it[0], it[1]))
        else:
            out.append((None, str(it)))
    return out


def _deco_orbit(cv, cx, cy, r, color='primary', alpha=0.18, dots=True):
    """Concentric thin rings with small nodes (abstract 'orbit' ornament)."""
    for k, rr in enumerate((r, r * 1.28, r * 1.62)):
        cv.circle(cx, cy, rr, fill=None, line=color, line_w=1.0, line_alpha=alpha * (1 - 0.28 * k), name='deco:ring')
    if dots:
        import math
        for ang, rr, d in ((200, r * 1.28, 0.16), (320, r * 1.62, 0.11), (60, r, 0.13)):
            a = math.radians(ang)
            cv.circle(cx + rr * math.cos(a), cy + rr * math.sin(a), d / 2, fill=color, alpha=0.55, name='deco:node')


# =========================================================================== cover
@layout
def cover(deck, title=None, subtitle=None, en=None, tag=None, info=None, variant=None, image=None,
          image_mode='fade', watermark=None, notes=None, title_size=None):
    """Cover page. variant: left | center | split | dark | image (auto by scenario/theme).
    title: main title (<= 2 lines, break with \\n); subtitle: 2nd level; en: English title;
    tag: small chip above title (e.g. '学位论文答辩'); info: list of strings or (icon, text) tuples
    (default from deck.meta author/advisor/org/date); image: photo path (optional)."""
    t = deck.theme
    m = deck._meta
    title = title or m.get('title') or '演示文稿标题'
    subtitle = subtitle if subtitle is not None else m.get('subtitle')
    en = en if en is not None else m.get('en')
    if variant is None:
        variant = 'dark' if t.is_dark else ('image' if image else ('center' if deck.scenario == 'competition' else 'left'))
    wm = watermark if watermark is not None else (en.split(':')[0].split(' ')[0].upper() if en else None)
    cv = deck.new('cover', bg=False)
    W, H = cv.W, cv.H
    infos = _info_lines(deck, info)
    ts = title_size or t.size_cover

    if variant in ('left', 'image'):
        if variant == 'image' and image:
            cv.image(image, 0, 0, W, H, fit='cover', name='bg:photo')
            cv.rect(0, 0, W, H, grad=[(0, 'primary_dark', 0.92), (55, 'primary_dark', 0.72), (100, 'primary_dark', 0.05)],
                    grad_angle=0, name='bg:mask')
            fg, sub_c, mut = 'FFFFFF', 'FFFFFF', 'FFFFFF'
        else:
            p = IMG.diffuse(colors=(t.c('primary+30'), t.secondary, t.c('secondary+50')), base=t.c('bg'),
                            blobs=[(0.92, 0.18, 0.34), (0.86, 1.02, 0.30), (0.62, 0.62, 0.14)], blur=150, strength=0.55)
            cv.image(p, 0, 0, W, H, fit='stretch', name='bg:diffuse')
            if image:
                pf = IMG.fade(IMG.cover_crop(image, 7.6 / 7.5), side='left', start=0.0, end=0.55)
                cv.image(pf, W - 7.6, 0, 7.6, H, fit='stretch', name='img:cover')
            else:
                cv.circle(10.35, 3.55, 2.05, grad=[(0, 'secondary', 0.95), (100, 'primary', 0.95)], grad_angle=135,
                          name='deco:disc', shadow={'color': 'primary', 'alpha': 0.28, 'blur': 40, 'dist': 10})
                cv.circle(11.55, 2.35, 1.05, fill='FFFFFF', alpha=0.28, line='FFFFFF', line_w=1.2, line_alpha=0.8,
                          name='deco:glass')
                _deco_orbit(cv, 10.35, 3.55, 2.55, 'primary', 0.22)
            fg, sub_c, mut = t.c('dark'), t.c('primary'), t.c('muted')
        x0, wtxt = 0.95, 7.3
        if wm and variant != 'image':
            K.watermark(cv, wm, 0.65, 1.05, 11.8, 1.9, size=112, color='primary', alpha=0.05)
        # logo / org line
        y = 0.72
        if m.get('logo'):
            K.logo(cv, m['logo'], x=x0, y=y, h=0.52, align='left')
        elif m.get('org') and not any('building' == ic for ic, _ in infos):
            cv.text(x0, y, 6, 0.35, m['org'], size=13, color=mut, wrap=False, fit=True)
        y = 2.05 if not subtitle else 1.85
        if tag:
            K.pill(cv, x0, y - 0.55, tag, size=12, fill='primary' if variant != 'image' else 'FFFFFF',
                   color='FFFFFF' if variant != 'image' else 'primary')
        th = cv.measure(title, wtxt, ts, role='heavy')
        th = min(th, ts / 72 * 1.25 * 2.1)
        cv.text(x0, y, wtxt, th + 0.05, title, size=ts, color=fg, role='heavy', fit=True, min_size=30,
                max_lines=2, ls=1.05, name='txt:cover_title')
        y += th + 0.12
        if subtitle:
            ss = min(30, ts * 0.62)
            sh = cv.measure(subtitle, wtxt, ss, role='medium')
            cv.text(x0, y, wtxt, sh + 0.05, subtitle, size=ss, color=sub_c, role='medium', fit=True, min_size=18,
                    max_lines=2, name='txt:cover_sub')
            y += sh + 0.14
        if en:
            cv.text(x0, y, wtxt, 0.55, en, size=12, color=mut, fit=True, min_size=9, spacing=0.4, max_lines=2,
                    name='txt:cover_en')
            y += 0.55
        # info block at bottom-left
        yy = H - 0.6 - 0.36 * len(infos)
        for ic, tx in infos:
            if ic:
                cv.icon(ic, x0, yy + 0.06, 0.22, sub_c if variant != 'image' else 'FFFFFF')
            cv.text(x0 + (0.34 if ic else 0), yy, 6.5, 0.34, tx, size=13, color=fg if variant == 'image' else 'text',
                    wrap=False, fit=True, min_size=10, anchor='middle', name='txt:cover_info')
            yy += 0.36

    elif variant == 'center':
        p = IMG.diffuse(colors=(t.c('primary+25'), t.secondary, t.c('secondary+55')), base=t.c('bg'),
                        blobs=[(0.05, 0.05, 0.3), (0.98, 0.95, 0.33), (0.85, 0.1, 0.18), (0.12, 0.92, 0.16)],
                        blur=160, strength=0.5)
        if image:
            cv.image(image, 0, 0, W, H, fit='cover', name='bg:photo')
            cv.rect(0, 0, W, H, fill='bg', alpha=0.82, name='bg:mask')
        else:
            cv.image(p, 0, 0, W, H, fit='stretch', name='bg:diffuse')
        if wm:
            K.watermark(cv, wm, 0.3, 1.25, W - 0.6, 2.1, size=130, color='primary', alpha=0.05, align='center')
        y = 2.2
        if tag:
            K.pill(cv, W / 2, y - 0.62, tag, size=12, align='center')
        th = cv.measure(title, 11.0, ts + 4, role='heavy')
        th = min(th, (ts + 4) / 72 * 1.25 * 2.1)
        cv.text(1.1, y, W - 2.2, th + 0.05, title, size=ts + 4, color='dark', role='heavy', align='center', fit=True,
                min_size=30, max_lines=2, ls=1.05, name='txt:cover_title')
        y += th + 0.15
        if subtitle:
            ss = min(28, ts * 0.58)
            sw = min(9.0, cv.width_of(subtitle, ss, role='medium') + 0.2)
            cv.text((W - sw) / 2, y, sw, ss / 72 * 1.4, subtitle, size=ss, color='primary', role='medium', align='center',
                    wrap=False, fit=True, name='txt:cover_sub')
            ly = y + ss / 72 * 0.72
            cv.line((W - sw) / 2 - 1.1, ly, (W - sw) / 2 - 0.25, ly, 'primary', 1.25,
                    grad=[('primary', 0.0), ('primary', 1.0)])
            cv.line((W + sw) / 2 + 0.25, ly, (W + sw) / 2 + 1.1, ly, 'primary', 1.25,
                    grad=[('primary', 1.0), ('primary', 0.0)])
            y += ss / 72 * 1.4 + 0.12
        if en:
            cv.text(1.5, y, W - 3.0, 0.5, en, size=12, color='muted', align='center', fit=True, min_size=9, spacing=0.5,
                    max_lines=2, name='txt:cover_en')
        if infos:
            s = '   |   '.join(tx for _, tx in infos)
            K.pill(cv, W / 2, H - 1.25, s, size=12.5, fill='surface', color='text', align='center', bold=False,
                   line='primary+60', h=0.5, pad=0.35)

    elif variant == 'split':
        cv.rect(0, 0, W, H, fill='bg', name='bg:base')
        pw = 6.0
        cv.rect(0, 0, pw, H, grad=[(0, 'secondary', 1.0), (100, 'primary', 1.0)], grad_angle=120, name='bg:panel')
        _deco_orbit(cv, pw - 0.9, H - 1.0, 1.1, 'FFFFFF', 0.25)
        if image:
            cv.image(image, pw, 0, W - pw, H, fit='cover', name='img:cover')
        else:
            p = IMG.diffuse(colors=(t.c('primary+40'), t.c('secondary+30')), base=t.c('bg'),
                            blobs=[(0.8, 0.3, 0.35), (0.5, 0.9, 0.3)], blur=140, strength=0.45)
            cv.image(p, pw, 0, W - pw, H, fit='cover', name='bg:diffuse')
            if wm:
                K.watermark(cv, wm, pw + 0.4, H - 2.0, W - pw - 0.8, 1.6, size=100, color='primary', alpha=0.08)
        x0, wtxt = 0.8, pw - 1.4
        y = 1.9
        if tag:
            K.pill(cv, x0, y - 0.6, tag, size=12, fill='FFFFFF', color='primary')
        th = min(cv.measure(title, wtxt, ts - 4, role='heavy'), (ts - 4) / 72 * 1.25 * 3.1)
        cv.text(x0, y, wtxt, th + 0.05, title, size=ts - 4, color='FFFFFF', role='heavy', fit=True, min_size=26,
                max_lines=3, ls=1.05)
        y += th + 0.15
        if subtitle:
            cv.text(x0, y, wtxt, 0.9, subtitle, size=22, color='FFFFFF', role='medium', fit=True, min_size=14,
                    max_lines=2, alpha=0.92)
            y += 0.95
        if en:
            cv.text(x0, y, wtxt, 0.6, en, size=11, color='FFFFFF', alpha=0.75, fit=True, min_size=8, max_lines=2,
                    spacing=0.4)
        yy = H - 0.6 - 0.36 * len(infos)
        for ic, tx in infos:
            if ic:
                cv.icon(ic, x0, yy + 0.06, 0.22, 'FFFFFF')
            cv.text(x0 + (0.34 if ic else 0), yy, wtxt, 0.34, tx, size=13, color='FFFFFF', wrap=False, fit=True,
                    min_size=10, anchor='middle')
            yy += 0.36

    elif variant == 'dark':
        p = IMG.tech_bg(bg=t.bg, glow=t.primary, glow2=t.secondary)
        cv.image(image or p, 0, 0, W, H, fit='cover', name='bg:tech')
        if image:
            cv.rect(0, 0, W, H, grad=[(0, t.bg, 0.95), (60, t.bg, 0.6), (100, t.bg, 0.2)], grad_angle=0, name='bg:mask')
        if wm:
            K.watermark(cv, wm, 0.6, 0.9, 12.2, 2.2, size=120, color='FFFFFF', alpha=0.05)
        x0, wtxt = 0.95, 8.6
        y = 2.2
        if tag:
            K.pill(cv, x0, y - 0.62, tag, size=12, fill='primary', color='FFFFFF')
        th = min(cv.measure(title, wtxt, ts + 2, role='heavy'), (ts + 2) / 72 * 1.25 * 2.1)
        cv.text(x0, y, wtxt, th + 0.05, title, size=ts + 2, role='heavy', fit=True, min_size=30, max_lines=2, ls=1.05,
                grad=['FFFFFF', 'secondary+40'], grad_angle=0, name='txt:cover_title')
        y += th + 0.15
        if subtitle:
            cv.text(x0, y, wtxt, 0.8, subtitle, size=26, color='secondary', role='medium', fit=True, min_size=16,
                    max_lines=2)
            y += 0.85
        if en:
            cv.text(x0, y, wtxt, 0.5, en, size=12, color='muted', fit=True, min_size=9, spacing=0.5, max_lines=2)
        yy = H - 0.62 - 0.36 * len(infos)
        for ic, tx in infos:
            if ic:
                cv.icon(ic, x0, yy + 0.06, 0.22, 'secondary')
            cv.text(x0 + (0.34 if ic else 0), yy, 7, 0.34, tx, size=13, color='text', wrap=False, fit=True,
                    min_size=10, anchor='middle')
            yy += 0.36
    if notes:
        cv.notes(notes)
    return cv


# =========================================================================== agenda
@layout
def agenda(deck, items=None, variant=None, title='目录', en='CONTENTS', descs=None, image=None, notes=None):
    """Table of contents. items default = deck sections. descs: optional one-line description per item
    (or English names). variant: list (3-7 items) | cards (3-5) | grid (6-10)."""
    t = deck.theme
    items = list(items or deck.sections)
    descs = descs or (deck.section_en if deck.section_en and any(deck.section_en) else None)
    n = len(items)
    variant = variant or ('list' if n <= 6 else 'grid')
    cv = deck.new('content', bg=True)
    W, H = cv.W, cv.H
    if variant in ('list', 'grid'):
        pw = 4.3
        if image:
            cv.image(image, 0, 0, pw, H, fit='cover', name='img:agenda')
            cv.rect(0, 0, pw, H, grad=[(0, 'primary_dark', 0.35), (100, 'primary_dark', 0.85)], grad_angle=90,
                    name='deco:mask')
        else:
            cv.rect(0, 0, pw, H, grad=[(0, 'secondary', 1.0), (100, 'primary', 1.0)], grad_angle=115, name='deco:panel')
            _deco_orbit(cv, 0.6, H - 0.6, 1.3, 'FFFFFF', 0.25)
            K.glow_orb(cv, pw, 0.4, 1.8, 'FFFFFF', 0.12)
        cv.text(0.85, 2.35, pw - 1.2, 1.0, title, size=46, color='FFFFFF', role='heavy', wrap=False, fit=True,
                name='txt:agenda_title')
        cv.text(0.88, 3.3, pw - 1.2, 0.4, en, size=14, color='FFFFFF', alpha=0.78, spacing=2.0, wrap=False, fit=True)
        cv.rect(0.9, 3.9, 0.5, 0.05, fill='FFFFFF', alpha=0.85, name='deco:bar')
        area = Box(pw + 0.95, 0.75, W - pw - 1.75, H - 1.5)
        ncols = 1 if variant == 'list' else 2
        per = (n + ncols - 1) // ncols
        colboxes = area.cols(ncols, gap=0.5)
        rh = min(1.05, area.h / per)
        for i, it in enumerate(items):
            col = colboxes[i // per]
            r = i % per
            y0 = area.y + (area.h - rh * per) / 2 + r * rh
            d = min(0.62, rh * 0.62)
            K.num_badge(cv, col.x + d / 2, y0 + rh / 2, d, i + 1, style='fill')
            has_desc = descs and i < len(descs) and descs[i]
            ty = y0 + rh / 2 - (0.36 if has_desc else 0.22)
            cv.text(col.x + d + 0.3, ty, col.w - d - 0.3, 0.46, it, size=22 if ncols == 1 else 18, color='dark',
                    role='title', wrap=False, fit=True, min_size=13, anchor='middle', name='txt:agenda_item')
            if has_desc:
                cv.text(col.x + d + 0.3, ty + 0.46, col.w - d - 0.3, 0.3, descs[i], size=11.5, color='muted',
                        wrap=False, fit=True, min_size=8, spacing=0.3)
            if r < per - 1 and i < n - 1:
                cv.line(col.x + d + 0.3, y0 + rh, col.r, y0 + rh, 'line', 0.75, name='deco:sep')
    else:  # cards
        K.page_title(cv, title, en if t.title_style in ('en', 'mark') else None)
        box = Box(t.margin_x, 2.05, W - 2 * t.margin_x, 4.3)
        cols = box.cols(n, gap=0.3)
        for i, (c, it) in enumerate(zip(cols, items)):
            off = 0.35 if i % 2 else 0.0
            cb = Box(c.x, c.y + off, c.w, c.h - 0.35)
            K.card(cv, cb)
            cv.text(cb.x + 0.35, cb.y + 0.3, cb.w - 0.6, 1.0, f'{i + 1:02d}', size=48, role='number', bold=True,
                    grad=['secondary', 'primary'], grad_angle=90, wrap=False, fit=False, name='txt:agenda_num')
            cv.rect(cb.x + 0.38, cb.y + 1.42, 0.42, 0.05, fill='primary', name='deco:bar')
            cv.text(cb.x + 0.35, cb.y + 1.7, cb.w - 0.6, 1.1, it, size=20, color='dark', role='title', fit=True,
                    min_size=13, max_lines=2, name='txt:agenda_item')
            if descs and i < len(descs) and descs[i]:
                cv.text(cb.x + 0.35, cb.y + 2.8, cb.w - 0.6, 0.9, descs[i], size=12, color='muted', fit=True,
                        min_size=9, max_lines=3)
    if notes:
        cv.notes(notes)
    return cv


# =========================================================================== section
@layout
def section(deck, index, title=None, en=None, desc=None, variant=None, notes=None, label=None):
    """Chapter divider. index: 1-based. variant: bignum (default) | nav (agenda with current highlighted) | center."""
    t = deck.theme
    deck.cur_section = index - 1
    title = title or (deck.sections[index - 1] if deck.sections and index - 1 < len(deck.sections) else f'第{index}部分')
    if en is None and deck.section_en and index - 1 < len(deck.section_en):
        en = deck.section_en[index - 1]
    variant = variant or 'bignum'
    label = label or f'PART {index:02d}'
    if variant == 'nav' and deck.sections:
        cv = deck.new('content', bg=True)
        W, H = cv.W, cv.H
        items = deck.sections
        n = len(items)
        box = Box(1.2, 1.1, W - 2.4, H - 2.2)
        rh = min(0.95, box.h / n)
        y0 = box.y + (box.h - rh * n) / 2
        for i, it in enumerate(items):
            on = i == index - 1
            y = y0 + i * rh
            if on:
                cv.rect(box.x - 0.3, y + 0.06, box.w + 0.6, rh - 0.12, grad=[('secondary', 1.0), ('primary', 1.0)],
                        grad_angle=0, radius=0.12, shadow='strong', name='deco:navcur')
            cv.text(box.x, y, 1.2, rh, f'{i + 1:02d}', size=30 if on else 24, role='number', bold=True,
                    color='FFFFFF' if on else 'primary+55', anchor='middle', wrap=False, fit=False)
            cv.text(box.x + 1.3, y, box.w - 1.5, rh, it, size=26 if on else 20, role='title',
                    color='FFFFFF' if on else 'muted', anchor='middle', wrap=False, fit=True, min_size=12)
        if notes:
            cv.notes(notes)
        cv.transition('morph')
        return cv
    cv = deck.new('section', bg=False)
    W, H = cv.W, cv.H
    if t.is_dark:
        cv.image(IMG.tech_bg(bg=t.bg, glow=t.primary, glow2=t.secondary, grid=False), 0, 0, W, H, fit='stretch',
                 name='bg:tech')
    else:
        p = IMG.diffuse(colors=(t.c('primary+35'), t.secondary, t.c('secondary+55')), base=t.c('bg'),
                        blobs=[(0.95, 0.15, 0.32), (0.75, 1.0, 0.3)], blur=150, strength=0.5)
        cv.image(p, 0, 0, W, H, fit='stretch', name='bg:diffuse')
    if variant == 'center':
        cv.circle(W / 2, H / 2, 2.0, grad=[(0, 'secondary', 1.0), (100, 'primary', 1.0)], grad_angle=135,
                  shadow={'color': 'primary', 'alpha': 0.3, 'blur': 40, 'dist': 8})
        _deco_orbit(cv, W / 2, H / 2, 2.35, 'primary', 0.2)
        cv.text(W / 2 - 1.8, H / 2 - 1.15, 3.6, 0.45, label, size=14, color='FFFFFF', align='center', spacing=2,
                wrap=False, fit=False, alpha=0.85)
        cv.text(W / 2 - 1.75, H / 2 - 0.65, 3.5, 1.2, title, size=30, color='FFFFFF', role='heavy', align='center',
                anchor='middle', fit=True, min_size=18, max_lines=2)
        if en:
            cv.text(W / 2 - 1.7, H / 2 + 0.6, 3.4, 0.4, en.upper(), size=10, color='FFFFFF', alpha=0.8,
                    align='center', fit=True, min_size=7, spacing=0.6)
    else:  # bignum
        num = f'{index:02d}'
        cv.text(6.6, 0.55, 6.4, 5.9, num, size=300, role='number', bold=True, align='right', anchor='middle',
                grad=['secondary+20', 'primary'], grad_angle=90, wrap=False, fit=False, name='deco:bignum',
                alpha=1.0)
        _deco_orbit(cv, 10.6, 3.9, 2.6, 'primary', 0.12, dots=False)
        x0 = 0.95
        K.pill(cv, x0, 2.35, label, size=13, fill='primary', color='FFFFFF')
        th = cv.measure(title, 6.4, 42, role='heavy')
        cv.text(x0, 2.95, 6.6, min(th, 1.6) + 0.05, title, size=42, color='dark', role='heavy', fit=True,
                min_size=24, max_lines=2, ls=1.05, name='txt:section_title')
        y = 2.95 + min(th, 1.6) + 0.15
        if en:
            cv.text(x0, y, 6.4, 0.4, en.upper(), size=12, color='muted', spacing=0.8, wrap=False, fit=True,
                    min_size=8)
            y += 0.5
        if desc:
            cv.text(x0, y + 0.1, 5.8, 1.3, desc, size=15, color='text', fit=True, min_size=11, max_lines=3)
    if notes:
        cv.notes(notes)
    return cv


# =========================================================================== ending
@layout
def ending(deck, title=None, subtitle=None, en=None, variant='thanks', info=None, notes=None):
    """Closing page. Default variant 'thanks' = just “谢谢” (no English line, no watermark, no info pill unless
    info= is passed). Other variants only on request: qa (Q&A) | critique (恳请批评指正) | contact."""
    t = deck.theme
    defaults = {'thanks': ('谢谢', ''), 'qa': ('Q & A', 'QUESTIONS & ANSWERS'),
                'critique': ('恳请各位老师批评指正', 'THANK YOU'), 'contact': ('期待与您合作', 'CONTACT US')}
    d_title, d_en = defaults.get(variant, defaults['thanks'])
    title = title or d_title
    en = en if en is not None else d_en
    cv = deck.new('cover', bg=False)
    W, H = cv.W, cv.H
    if t.is_dark:
        cv.image(IMG.tech_bg(bg=t.bg, glow=t.primary, glow2=t.secondary), 0, 0, W, H, fit='stretch', name='bg:tech')
        fg = 'FFFFFF'
    else:
        p = IMG.diffuse(colors=(t.c('primary+25'), t.secondary, t.c('secondary+55')), base=t.c('bg'),
                        blobs=[(0.05, 0.05, 0.3), (0.98, 0.95, 0.33), (0.85, 0.1, 0.18), (0.12, 0.92, 0.16)],
                        blur=160, strength=0.5)
        cv.image(p, 0, 0, W, H, fit='stretch', name='bg:diffuse')
        fg = 'dark'
    if variant != 'thanks':
        K.watermark(cv, 'THANKS' if variant != 'qa' else 'Q&A', 0.3, 1.1, W - 0.6, 2.3, size=150, color='primary',
                    alpha=0.05 if not t.is_dark else 0.06, align='center')
    ts = 96 if len(plain(title)) <= 2 else (60 if len(plain(title)) <= 6 else 44)
    cv.text(1.0, 2.35, W - 2.0, 1.25, title, size=ts, role='heavy', color=fg, align='center', anchor='middle',
            fit=True, min_size=28, max_lines=1, wrap=False, name='txt:end_title',
            grad=None if not t.is_dark else ['FFFFFF', 'secondary+40'])
    y = 3.7
    if en:
        cv.text(1.5, y, W - 3.0, 0.4, en, size=13, color='muted', align='center', spacing=2.0, wrap=False, fit=True)
        y += 0.55
    if subtitle:
        cv.text(1.5, y, W - 3.0, 0.5, subtitle, size=18, color='primary', role='medium', align='center', fit=True,
                min_size=12, wrap=False)
        y += 0.6
    infos = _info_lines(deck, info) if info is not None else []
    if infos:
        s = '   |   '.join(tx for _, tx in infos)
        K.pill(cv, W / 2, H - 1.3, s, size=12.5, fill='surface' if not t.is_dark else 'bg2', color='text',
               align='center', bold=False, line='primary+60' if not t.is_dark else 'line', h=0.5, pad=0.35)
    if notes:
        cv.notes(notes)
    return cv


# =========================================================================== cards
@layout
def cards(deck, title, items, en=None, variant='icon_top', cols=None, style=None, summary=None, source=None,
          notes=None, section=None, body_size=None):
    """2-6 parallel points as cards. items: [{'icon': 'droplet'|'水', 'title': '...', 'text': '...', 'tag': opt}].
    variant: icon_top | icon_left (lighter, no boxes) | number | header (colored header strip).
    summary: optional one-line takeaway shown as a banner at the bottom (the '结论先行' reinforcement)."""
    t = deck.theme
    cv = deck.page(title, en, source=source, section=section)
    box = cv.content
    n = len(items)
    if summary:
        sb_h = 0.62
        box = Box(box.x, box.y, box.w, box.h - sb_h - 0.25)
    bs = body_size or (t.size_body + (1 if n <= 3 else 0) - (1 if n >= 5 else 0))
    if variant == 'icon_left':
        ncol = cols or (1 if n <= 3 else 2)
        cells = box.grid(n, ncol, gap=0.6, row_gap=0.35)
        hs = t.size_heading + 2
        d = 0.82
        for c, it in zip(cells, items):
            need = cv.measure(it.get('title', ''), c.w - d - 0.35, hs, role='title') + 0.1
            if it.get('text'):
                need += cv.measure(it.get('text', ''), c.w - d - 0.35, bs)
            y0 = c.y + max(0, (c.h - need) / 2 - 0.1)
            K.card(cv, Box(c.x - 0.1, c.y, c.w + 0.2, c.h), style='tint', radius=0.14)
            K.icon_badge(cv, c.x + 0.25 + d / 2, y0 + d / 2, d, it.get('icon', 'circle-dot'))
            K.heading_block(cv, c.x + d + 0.55, y0, c.w - d - 0.7, it.get('title', ''), it.get('text'),
                            head_size=hs, body_size=bs, max_h=c.b - y0 - 0.1)
    else:
        ncol = cols or (n if n <= 4 else 3)
        nrow = (n + ncol - 1) // ncol
        gap = 0.3 if ncol <= 3 else 0.24
        cw = (box.w - gap * (ncol - 1)) / ncol
        pad = 0.32 if cw > 2.6 else 0.24
        # height needed
        hs = t.size_heading + (2 if n <= 3 else 0) if cw > 2.4 else t.size_heading - 1
        need = 0
        for it in items:
            hh = cv.measure(it.get('title', ''), cw - 2 * pad, hs, role='title')
            bh = cv.measure(it.get('text', ''), cw - 2 * pad, bs) if it.get('text') else 0
            need = max(need, hh + bh)
        top_h = {'icon_top': 0.95, 'number': 0.95, 'header': 0.2}.get(variant, 0.95)
        min_h = (box.h * (0.72 if n <= 4 else 0.6)) if nrow == 1 else (box.h - 0.3) / nrow
        card_h = max(need + top_h + 2 * pad + 0.25, min_h)
        row_gap = 0.3
        total = nrow * card_h + (nrow - 1) * row_gap
        if total > box.h:
            card_h = (box.h - (nrow - 1) * row_gap) / nrow
            total = box.h
        y0 = box.y + (box.h - total) / 2 if nrow == 1 else box.y
        for i, it in enumerate(items):
            r, cidx = divmod(i, ncol)
            k = min(ncol, n - r * ncol)
            xoff = (ncol - k) * (cw + gap) / 2
            cb = Box(box.x + xoff + cidx * (cw + gap), y0 + r * (card_h + row_gap), cw, card_h)
            if variant == 'header':
                K.card(cv, cb, style=style)
                hh = 0.62
                cv.rect(cb.x, cb.y, cb.w, hh, radius=t.radius, grad=[('secondary', 1.0), ('primary', 1.0)],
                        grad_angle=0, name='deco:cardhead')
                cv.rect(cb.x, cb.y + hh - t.radius, cb.w, t.radius, grad=[('secondary', 1.0), ('primary', 1.0)],
                        grad_angle=0, name='deco:cardhead2')
                if it.get('icon'):
                    cv.icon(it['icon'], cb.x + pad, cb.y + (hh - 0.34) / 2, 0.34, 'FFFFFF')
                cv.text(cb.x + pad + (0.46 if it.get('icon') else 0), cb.y, cb.w - 2 * pad - (0.46 if it.get('icon') else 0),
                        hh, it.get('title', ''), size=hs, color='FFFFFF', role='title', anchor='middle', wrap=False,
                        fit=True, min_size=11)
                if it.get('text'):
                    cv.text(cb.x + pad, cb.y + hh + 0.22, cb.w - 2 * pad, cb.h - hh - 0.4, it['text'], size=bs,
                            color='text', fit=True)
                continue
            K.card(cv, cb, style=style)
            ix, iy = cb.x + pad, cb.y + pad
            if variant == 'number':
                cv.text(ix, iy - 0.05, 1.5, 0.8, f'{i + 1:02d}', size=36, role='number', bold=True,
                        grad=['secondary', 'primary'], grad_angle=90, wrap=False, fit=False)
            else:
                d = 0.66
                K.icon_badge(cv, ix + d / 2, iy + d / 2, d, it.get('icon', 'circle-dot'))
            if it.get('tag'):
                K.pill(cv, cb.r - pad, iy + 0.12, it['tag'], size=10, fill='primary_pale', color='primary',
                       align='right', bold=True)
            ty = iy + top_h
            hh = cv.measure(it.get('title', ''), cb.w - 2 * pad, hs, role='title')
            cv.text(ix, ty, cb.w - 2 * pad, hh + 0.04, it.get('title', ''), size=hs, color='dark', role='title',
                    fit=True, min_size=11, max_lines=2)
            if it.get('text'):
                avail_h = cb.b - pad - (ty + hh + 0.12)
                s_ = bs
                while s_ < bs + 3 and cv.measure(it['text'], cb.w - 2 * pad, s_ + 0.5) < avail_h * 0.6:
                    s_ += 0.5
                cv.text(ix, ty + hh + 0.12, cb.w - 2 * pad, avail_h, it['text'], size=s_, color='text', fit=True)
    if summary:
        _summary_band(cv, summary)
    if notes:
        cv.notes(notes)
    return cv


def _summary_band(cv, text, y=None):
    t = cv.t
    b = cv.content
    y = y if y is not None else b.b - 0.62
    cv.rect(b.x, y, b.w, 0.62, radius=0.31, grad=[('primary', 1.0), ('secondary', 1.0)], grad_angle=0,
            name='deco:summary', shadow={'color': 'primary', 'alpha': 0.2, 'blur': 14, 'dist': 3})
    cv.icon('lightbulb', b.x + 0.28, y + 0.16, 0.3, 'FFFFFF')
    cv.text(b.x + 0.72, y, b.w - 1.0, 0.62, text, size=t.size_body, color='FFFFFF', bold=True, anchor='middle',
            wrap=False, fit=True, min_size=11, name='txt:summary')


# =========================================================================== bullets
@layout
def bullets(deck, title, points, en=None, image=None, marker='num', side='right', source=None, notes=None,
            section=None, lead=None, image_caption=None, style='rows'):
    """Key points list. points: list[str] ('**加粗小标题**：说明' recommended) or dicts {'text','icon'}.
    style: rows (each point on a tinted row card with a number/icon badge - fills the page) | plain (simple list).
    image: optional picture on one side. lead: one intro sentence above the list."""
    t = deck.theme
    cv = deck.page(title, en, source=source, section=section)
    box = cv.content
    if image:
        tb, ib = box.split(0.56, gap=0.55)
        if side != 'right':
            ib, tb = box.split(0.44, gap=0.55)
        cap_h = 0.4 if image_caption else 0
        cv.image(image, ib.x, ib.y, ib.w, ib.h - cap_h, fit='cover', radius=0.12, shadow='soft')
        if image_caption:
            cv.text(ib.x, ib.b - 0.32, ib.w, 0.3, image_caption, size=11, color='muted', align='center', fit=True,
                    wrap=False)
    else:
        tb = box
    y = tb.y
    if lead:
        lsz = t.size_body + 2
        lh = cv.measure(lead, tb.w, lsz, role='medium')
        cv.text(tb.x, y, tb.w, lh + 0.05, lead, size=lsz, color='dark', role='medium', fit=True)
        y += lh + 0.28
    area = Box(tb.x, y, tb.w, tb.b - y)
    n = len(points)
    if style == 'plain':
        K.bullets(cv, area, points, marker=marker, size=t.size_body + (2 if n <= 4 else 0))
    else:
        gap = 0.2 if n <= 5 else 0.14
        rh = min(1.25, (area.h - gap * (n - 1)) / n)
        fs = t.size_body + (2 if n <= 4 and rh >= 0.9 else 0)
        total = rh * n + gap * (n - 1)
        y0 = area.y + max(0, (area.h - total) / 2) if not lead else area.y
        for i, pt in enumerate(points):
            txt = pt['text'] if isinstance(pt, dict) else pt
            yy = y0 + i * (rh + gap)
            cv.rect(area.x, yy, area.w, rh, fill='primary_bg' if not t.is_dark else 'surface', radius=0.1,
                    name='deco:row')
            d = min(0.56, rh * 0.62)
            if marker == 'icon' and isinstance(pt, dict) and pt.get('icon'):
                K.icon_badge(cv, area.x + 0.35 + d / 2, yy + rh / 2, d, pt['icon'])
            else:
                K.num_badge(cv, area.x + 0.35 + d / 2, yy + rh / 2, d, i + 1, style='fill')
            cv.text(area.x + 0.35 + d + 0.3, yy, area.w - d - 1.0, rh, txt, size=fs, color='text', anchor='middle',
                    fit=True, name='txt:point')
    if notes:
        cv.notes(notes)
    return cv


# =========================================================================== text + image
@layout
def text_image(deck, title, heading=None, text=None, image=None, en=None, side='right', points=None, source=None,
               notes=None, section=None, caption=None, visual=None):
    """One idea explained with a picture. heading: bold lead line; text: paragraph(s); points: optional bullets.
    image: photo path; visual: callable(cv, box) to draw a native illustration instead of a photo."""
    t = deck.theme
    cv = deck.page(title, en, source=source, section=section)
    box = cv.content
    tb, ib = box.split(0.47, gap=0.6)
    if side == 'left':
        ib, tb = box.split(0.53, gap=0.6)
    if image:
        cap_h = 0.38 if caption else 0
        cv.rect(ib.x + 0.25, ib.y + 0.25, ib.w, ib.h - cap_h, fill='primary_pale', radius=0.14, name='deco:offset')
        cv.image(image, ib.x, ib.y, ib.w - 0.02, ib.h - cap_h - 0.02, fit='cover', radius=0.14, shadow='soft')
        if caption:
            cv.text(ib.x, ib.b - 0.3, ib.w, 0.3, caption, size=11, color='muted', align='center', wrap=False, fit=True)
    elif visual:
        visual(cv, ib)
    y = tb.y
    if heading:
        hh = cv.measure(heading, tb.w, t.size_heading + 4, role='title')
        cv.text(tb.x, y, tb.w, hh + 0.05, heading, size=t.size_heading + 4, color='primary', role='title', fit=True,
                min_size=14)
        y += hh + 0.22
    if text:
        th = min(cv.measure(text, tb.w, t.size_body), tb.b - y)
        cv.text(tb.x, y, tb.w, th + 0.05, text, size=t.size_body, color='text', fit=True, align='justify')
        y += th + 0.3
    if points:
        K.bullets(cv, Box(tb.x, y, tb.w, tb.b - y), points, marker='check', size=t.size_body)
    if notes:
        cv.notes(notes)
    return cv


# =========================================================================== KPIs
@layout
def kpis(deck, title, items, en=None, lead=None, variant='cards', source=None, notes=None, section=None,
         summary=None):
    """2-5 headline numbers. items: [{'value': '1432', 'unit': 'km', 'label': '总干渠长度', 'desc': opt,
    'icon': opt, 'trend': 'up'|'down'|None}]. variant: cards | row (dividers, no boxes) | rings (value = %)."""
    t = deck.theme
    cv = deck.page(title, en, source=source, section=section)
    box = cv.content
    y = box.y
    if lead:
        lh = cv.measure(lead, box.w, t.size_body + 1)
        cv.text(box.x, y, box.w, lh + 0.05, lead, size=t.size_body + 1, color='text', fit=True)
        y += lh + 0.35
    if summary:
        area = Box(box.x, y, box.w, box.b - y - 0.9)
    else:
        area = Box(box.x, y, box.w, box.b - y)
    n = len(items)
    cols = area.cols(n, gap=0.3)
    has_desc = any(it.get('desc') for it in items)
    ch = min(area.h, max(3.3 if has_desc else 2.6, area.h * 0.62))
    cy0 = area.y + (area.h - ch) / 2
    for i, (c, it) in enumerate(zip(cols, items)):
        cb = Box(c.x, cy0, c.w, ch)
        if variant == 'cards':
            K.card(cv, cb)
            inner = cb.inset(0.3, 0.28)
        elif variant == 'row':
            inner = cb.inset(0.15, 0.1)
            if i > 0:
                cv.line(cb.x - 0.15, cb.y + 0.3, cb.x - 0.15, cb.b - 0.3, 'line', 1.0)
        else:  # rings
            inner = cb
        if variant == 'rings':
            r = min(cb.w, 2.0) / 2 * 0.9
            ccx, ccy = cb.cx, cb.y + r + 0.05
            try:
                pct = float(str(it['value']).strip('%'))
            except ValueError:
                pct = 75
            cv.ring(ccx, ccy, r, r * 0.16, color='primary_pale', name='deco:ringbg')
            cv.ring(ccx, ccy, r, r * 0.16, color='primary', start=0, sweep=max(1, min(359.9, pct * 3.6)),
                    name='deco:ringval')
            cv.text(ccx - r, ccy - 0.35, 2 * r, 0.7, f"{it['value']}", size=min(30, r * 72 * 0.5), role='number',
                    bold=True, color='primary', align='center', anchor='middle', wrap=False, fit=True)
            cv.text(cb.x, ccy + r + 0.15, cb.w, 0.4, it.get('label', ''), size=t.size_body - 1, color='dark',
                    role='title', align='center', fit=True, min_size=10, wrap=False)
            if it.get('desc'):
                cv.text(cb.x, ccy + r + 0.55, cb.w, 0.7, it['desc'], size=t.size_small, color='muted', align='center',
                        fit=True, min_size=9)
            continue
        yy = inner.y + (0.15 if variant == 'cards' else 0)
        if it.get('icon'):
            K.icon_badge(cv, inner.x + 0.3, yy + 0.3, 0.6, it['icon'], style='circle_pale')
            yy += 0.8
        numh = 1.25 if n <= 3 else 1.05
        K.kpi(cv, Box(inner.x, yy, inner.w, numh), it['value'], it.get('unit', ''), label=None,
              trend=it.get('trend'), align='left', size=60 if n <= 3 else 48)
        yy += numh + 0.12
        cv.rect(inner.x, yy, 0.45, 0.05, fill='primary', name='deco:bar')
        yy += 0.18
        cv.text(inner.x, yy, inner.w, 0.42, it.get('label', ''), size=t.size_body + 1, color='dark',
                role='title', fit=True, min_size=10, wrap=False)
        if it.get('desc'):
            cv.text(inner.x, yy + 0.46, inner.w, max(0.3, inner.b - yy - 0.46), it['desc'], size=t.size_small + 1,
                    color='muted', fit=True, min_size=9)
    if summary:
        _summary_band(cv, summary)
    if notes:
        cv.notes(notes)
    return cv


# =========================================================================== quote / key message
@layout
def quote(deck, text, source=None, title=None, en=None, variant='center', notes=None, section=None):
    """Key message / golden quote page (金句页) — one sentence worth remembering."""
    t = deck.theme
    if title:
        cv = deck.page(title, en, section=section)
    else:
        cv = deck.new('section', bg=True, bg_kind='section')
    W, H = cv.W, cv.H
    K.quote_mark(cv, 1.2, 1.2 if not title else 1.9, 1.3, 'primary', 0.22)
    cv.text(1.6, 2.3 if not title else 2.8, W - 3.2, 2.2, text, size=34 if len(plain(text)) <= 30 else 26,
            role='heavy', color='dark', align='center', anchor='middle', fit=True, min_size=18, ls=1.25,
            name='txt:quote')
    if source:
        cv.text(1.6, 4.75 if not title else 5.2, W - 3.2, 0.45, '—— ' + source, size=14, color='muted', align='center',
                fit=True, wrap=False)
    if notes:
        cv.notes(notes)
    return cv


# late import of second batch (registers more layouts)
from . import layouts2  # noqa: E402,F401
from . import layouts_ac  # noqa: E402,F401
from . import layouts_rs  # noqa: E402,F401
from . import layouts_pro  # noqa: E402,F401
