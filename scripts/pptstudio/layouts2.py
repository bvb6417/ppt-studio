"""Second batch of layouts: data (chart/table/kpi side panels), diagrams (timeline, process, hub, compare,
matrix, pyramid, band, split), figures (scientific figure, image grid, team) and references."""
from __future__ import annotations

import math

from . import components as K
from .canvas import Box, plain
from .charts import chart as _chart
from .tables import table as _table
from .layouts import layout, REGISTRY, _summary_band  # noqa: F401


def _center_y(box, block_h, bias=0.42):
    """y where a block of height block_h sits in box with free space split bias:(1-bias) (slightly above middle)."""
    free = max(0.0, box.h - block_h)
    return box.y + free * bias


def _fit_up(cv, content, w, h, smin, smax, role='body', ratio=0.92):
    """Largest size in [smin, smax] whose rendered height <= h*ratio (grow text to fill a roomy container)."""
    s = smax
    while s > smin and cv.measure(content, w, s, role=role) > h * ratio:
        s -= 0.5
    return s


# =========================================================================== chart page
@layout
def chart_page(deck, title, chart, points=None, kpis=None, en=None, side='right', source=None, notes=None,
               section=None, chart_title=None, unit=None, summary=None):
    """Chart + key findings. chart: dict(kind='column'|'bar'|'line'|'area'|'pie'|'donut'|'stacked',
    categories=[...], series={'name': [...]}, highlight=idx, number_format='0.0', ...) passed to charts.chart.
    points: 2-4 takeaway sentences (right panel); kpis: 2-3 {'value','unit','label'} shown in the panel instead.
    chart_title: small caption above the chart (e.g. '图 各工程输水线路长度'); unit: e.g. '单位：km'."""
    t = deck.theme
    cv = deck.page(title, en, source=source, section=section)
    box = cv.content
    if summary:
        box = Box(box.x, box.y, box.w, box.h - 0.87)
    has_panel = bool(points or kpis)
    if has_panel:
        cb, pb = box.split(0.62, gap=0.35) if side == 'right' else box.split(0.38, gap=0.35)[::-1]
        if side != 'right':
            pb, cb = box.split(0.38, gap=0.35)
    else:
        cb, pb = box, None
    K.card(cv, cb)
    inner = cb.inset(0.3, 0.25)
    y = inner.y
    if chart_title or unit:
        if chart_title:
            cv.text(inner.x, y, inner.w * 0.7, 0.36, chart_title, size=t.size_body, color='dark', role='title',
                    wrap=False, fit=True, min_size=11)
        if unit:
            cv.text(inner.x + inner.w * 0.6, y, inner.w * 0.4, 0.36, unit, size=11, color='muted', align='right',
                    wrap=False, fit=True, min_size=8)
        y += 0.45
    spec = dict(chart)
    kind = spec.pop('kind', 'column')
    _chart(cv, inner.x - 0.05, y, inner.w + 0.1, inner.b - y, kind=kind, **spec)
    if pb is not None:
        if kpis:
            n = len(kpis)
            rows = pb.rows(n, gap=0.25)
            for r, k in zip(rows, kpis):
                K.card(cv, r, style='tint')
                K.kpi(cv, Box(r.x + 0.3, r.y + 0.15, r.w - 0.5, r.h * 0.58), k['value'], k.get('unit', ''),
                      trend=k.get('trend'), size=min(44, r.h * 72 * 0.4))
                cv.text(r.x + 0.3, r.y + 0.15 + r.h * 0.58 + 0.04, r.w - 0.5, r.h * 0.34, k.get('label', ''),
                        size=t.size_body - 1, color='text', fit=True, min_size=10)
        else:
            cv.text(pb.x, pb.y, pb.w, 0.45, '关键发现' if not t.is_dark else 'KEY FINDINGS', size=t.size_heading,
                    color='primary', role='title', wrap=False, fit=True)
            cv.rect(pb.x, pb.y + 0.5, 0.5, 0.05, fill='primary', name='deco:bar')
            area = Box(pb.x, pb.y + 0.8, pb.w, pb.b - pb.y - 0.8)
            n = len(points)
            gap = 0.34
            fs = t.size_body + 2
            hs = [cv.measure(p, area.w - 0.55, fs) for p in points]
            while sum(hs) + gap * (n - 1) > area.h * 0.9 and fs > t.size_min:
                fs -= 0.5
                hs = [cv.measure(p, area.w - 0.55, fs) for p in points]
            yy = area.y
            for i, (p, hh) in enumerate(zip(points, hs)):
                K.num_badge(cv, area.x + 0.2, yy + fs / 72 * 0.62, 0.42, i + 1, style='pale', size=12)
                cv.text(area.x + 0.55, yy, area.w - 0.55, hh + 0.05, p, size=fs, color='text', fit=True)
                yy += hh + gap
    if summary:
        _summary_band(cv, summary, y=cv.content.b - 0.62)
    if notes:
        cv.notes(notes)
    return cv


# =========================================================================== table page
@layout
def table_page(deck, title, columns, rows, en=None, style='header', highlight_col=None, highlight_mode='fill',
               highlight_rows=None, note=None, source=None, notes=None, section=None, col_widths=None, align=None,
               font_size=None, summary=None):
    """Styled table. style: header | three_line (academic) | minimal. note: small caption under the table.
    highlight_col / highlight_mode ('fill' | 'raised'); highlight_rows: list of data-row indices."""
    t = deck.theme
    cv = deck.page(title, en, source=source, section=section)
    box = cv.content
    bottom_reserve = (0.87 if summary else 0) + (0.45 if note else 0)
    area = Box(box.x, box.y + (0.1 if highlight_mode == 'raised' else 0), box.w,
               box.h - bottom_reserve - (0.2 if highlight_mode == 'raised' else 0))
    fs = font_size
    if fs is None:
        nrow = len(rows) + 1
        fs = t.size_body + (2 if nrow <= 5 else (1 if nrow <= 8 else -1))
    gf, geo = _table(cv, area.x, area.y, area.w, area.h, columns, rows, style=style, col_widths=col_widths,
                     align=align, font_size=fs, highlight_col=highlight_col, highlight_mode=highlight_mode,
                     highlight_rows=highlight_rows, max_row_h=0.72)
    # re-center the finished table vertically (move all shapes created by the table call)
    th = geo['height']
    dy = max(0.0, (area.h - th) * 0.4)
    if dy > 0.05:
        from .units import emu as _emu
        gf.top = gf.top + _emu(dy)
        for shp in cv.slide.shapes:
            if shp.name == 'deco:colcard':
                shp.top = shp.top + _emu(dy)
        area = Box(area.x, area.y + dy, area.w, area.h)
    yb = area.y + geo['height']
    if note:
        cv.text(area.x, yb + 0.1, area.w, 0.35, note, size=11, color='muted', fit=True, wrap=False, min_size=8,
                name='txt:note')
    if summary:
        _summary_band(cv, summary, y=cv.content.b - 0.62)
    if notes:
        cv.notes(notes)
    return cv


# =========================================================================== timeline
@layout
def timeline(deck, title, events, en=None, variant='axis', source=None, notes=None, section=None, highlight=None):
    """Chronology / milestones. events: [{'date': '2002', 'title': '...', 'text': '...'}] (3-8).
    variant: axis (gradient bar, events alternate above/below) | cards (row of year cards + arrow) |
    rise (ascending curve with nodes — growth story). highlight: index of the key event."""
    t = deck.theme
    cv = deck.page(title, en, source=source, section=section)
    box = cv.content
    n = len(events)
    hl = (highlight % n) if highlight is not None else None
    if variant == 'cards':
        cols = box.cols(n, gap=0.18)
        ch = box.h - 0.55
        for i, (c, e) in enumerate(zip(cols, events)):
            on = i == hl
            cb = Box(c.x, box.y, c.w, ch)
            K.card(cv, cb, fill='primary' if on else None)
            cv.text(cb.x + 0.2, cb.y + 0.22, cb.w - 0.4, 0.5, e.get('date', ''), size=22, role='number', bold=True,
                    color='FFFFFF' if on else 'primary', wrap=False, fit=True, min_size=12)
            cv.line(cb.x + 0.2, cb.y + 0.82, cb.r - 0.2, cb.y + 0.82, 'FFFFFF' if on else 'line', 1.0,
                    alpha=0.5 if on else 1.0)
            hh = cv.measure(e.get('title', ''), cb.w - 0.4, t.size_body + 1, role='title')
            cv.text(cb.x + 0.2, cb.y + 0.98, cb.w - 0.4, hh + 0.05, e.get('title', ''), size=t.size_body + 1,
                    role='title', color='FFFFFF' if on else 'dark', fit=True, min_size=11, max_lines=3)
            if e.get('text'):
                ty = cb.y + 0.98 + hh + 0.12
                fs = _fit_up(cv, e['text'], cb.w - 0.4, cb.b - 0.2 - ty, t.size_min - 1, t.size_body - 1)
                cv.text(cb.x + 0.2, ty, cb.w - 0.4, cb.b - 0.2 - ty, e['text'], size=fs,
                        color='FFFFFF' if on else 'text', fit=True, min_size=9)
        ay = box.b - 0.25
        cv.line(box.x, ay, box.r, ay, 'primary', 2.0, tail='triangle', grad=[('primary', 0.25), ('primary', 1.0)])
        return _done(cv, notes)
    if variant == 'rise':
        x0, x1 = box.x + 0.3, box.r - 0.3
        yb, yt = box.b - 0.6, box.y + 1.4
        pts = []
        for i in range(n):
            f = i / max(1, n - 1)
            pts.append((x0 + (x1 - x0) * f, yb - (yb - yt) * (f ** 1.25)))
        cv.poly(pts, fill=None, line='primary', line_w=3.0, closed=False, smooth=True, name='deco:curve')
        area_pts = pts + [(x1, box.b), (x0, box.b)]
        cv.poly(area_pts, fill=None, grad=[('primary', 0.16), ('primary', 0.0)], grad_angle=90, smooth=False,
                name='deco:curvefill')
        cw = min(2.6, (x1 - x0) / max(1, n - 1) * 0.95) if n > 1 else 2.6
        for i, ((px, py), e) in enumerate(zip(pts, events)):
            on = i == hl or (hl is None and i == n - 1)
            cv.circle(px, py, 0.13 if on else 0.1, fill='FFFFFF', line='primary', line_w=3 if on else 2)
            tx = min(max(px - cw / 2, box.x), box.r - cw)
            cv.text(tx, py - 1.45, cw, 0.42, e.get('date', ''), size=20 if on else 17, role='number', bold=True,
                    color='primary', align='center', wrap=False, fit=True, min_size=11)
            cv.text(tx, py - 1.05, cw, 0.36, e.get('title', ''), size=t.size_body, role='title', color='dark',
                    align='center', wrap=False, fit=True, min_size=10)
            if e.get('text'):
                cv.text(tx, py - 0.68, cw, 0.5, e['text'], size=t.size_small, color='muted', align='center', fit=True,
                        min_size=9, max_lines=2)
        return _done(cv, notes)
    # axis (default)
    ay = box.y + box.h * 0.5
    cv.rect(box.x, ay - 0.07, box.w, 0.14, radius=0.07, grad=[('secondary', 1.0), ('primary', 1.0)], grad_angle=0,
            name='deco:axis')
    slot = box.w / n
    for i, e in enumerate(events):
        cx = box.x + slot * (i + 0.5)
        on = i == hl
        up = i % 2 == 0
        _, pw = K.pill(cv, cx, ay - 0.21, e.get('date', ''), size=12 if not on else 13, align='center',
                       fill='surface' if not on else 'accent', color='primary' if not on else 'FFFFFF',
                       line='primary' if not on else None, h=0.42, pad=0.14)
        tw = min(slot * 1.7, 3.0) if n <= 4 else slot * 1.9
        tw = min(tw, box.w)
        tx = min(max(cx - tw / 2, box.x), box.r - tw)
        text_h = box.h * 0.5 - 0.55
        if up:
            cv.line(cx, ay - 0.25, cx, ay - 0.55, 'primary', 1.0, alpha=0.6)
            yb = ay - 0.6
            hh = cv.measure(e.get('title', ''), tw, t.size_body + 1, role='title')
            bh = cv.measure(e.get('text', ''), tw, t.size_small) if e.get('text') else 0
            blk = min(text_h, hh + (bh + 0.06 if bh else 0))
            y0 = yb - blk
            cv.text(tx, y0, tw, hh + 0.04, e.get('title', ''), size=t.size_body + 1, role='title', color='dark',
                    align='center', fit=True, min_size=10, max_lines=2)
            if e.get('text'):
                cv.text(tx, y0 + hh + 0.06, tw, max(0.3, yb - (y0 + hh + 0.06)), e['text'], size=t.size_small,
                        color='text', align='center', fit=True, min_size=9)
        else:
            cv.line(cx, ay + 0.25, cx, ay + 0.55, 'primary', 1.0, alpha=0.6)
            y0 = ay + 0.6
            hh = cv.measure(e.get('title', ''), tw, t.size_body + 1, role='title')
            cv.text(tx, y0, tw, hh + 0.04, e.get('title', ''), size=t.size_body + 1, role='title', color='dark',
                    align='center', fit=True, min_size=10, max_lines=2)
            if e.get('text'):
                cv.text(tx, y0 + hh + 0.06, tw, max(0.3, box.b - (y0 + hh + 0.06)), e['text'], size=t.size_small,
                        color='text', align='center', fit=True, min_size=9)
    return _done(cv, notes)


def _done(cv, notes):
    if notes:
        cv.notes(notes)
    return cv


# =========================================================================== process
@layout
def process(deck, title, steps, en=None, variant='chevron', source=None, notes=None, section=None, summary=None):
    """Sequential steps (3-6). steps: [{'title','text','icon'}]. variant: chevron (arrow band + text below) |
    circles (numbered nodes on a dashed line) | cards (cards with > between; the last step is emphasized)."""
    t = deck.theme
    cv = deck.page(title, en, source=source, section=section)
    box = cv.content
    if summary:
        box = Box(box.x, box.y, box.w, box.h - 0.87)
    n = len(steps)
    w = box.w / n
    fs = t.size_body + (2 if n <= 4 else 0)
    if variant == 'chevron':
        bh = 1.0
        has_icon = any(s.get('icon') for s in steps)
        text_h = max((cv.measure(s.get('text', ''), w - 0.4, fs) for s in steps if s.get('text')), default=0)
        block = bh + 0.4 + (1.0 if has_icon else 0) + text_h
        y = _center_y(box, block)
        for i, s in enumerate(steps):
            x = box.x + i * w
            shp = 'homePlate' if i == 0 else 'chevron'
            col = 'primary' if i == n - 1 else ('primary+' + str(int(55 - 45 * i / max(1, n - 1))))
            cv.shape(shp, x, y, w + (0.25 if i < n - 1 else 0), bh, fill=col, adj={'adj': 30000}, name='deco:chev')
            cv.text(x + (0.3 if i else 0.2), y, w - 0.45, bh, s.get('title', ''), size=t.size_body + 2,
                    role='title', color='FFFFFF' if i >= n / 2 or n <= 2 else 'dark', align='center',
                    anchor='middle', wrap=True, fit=True, min_size=10, max_lines=2)
            ty = y + bh + 0.4
            if s.get('icon'):
                K.icon_badge(cv, x + w / 2, ty + 0.38, 0.76, s['icon'], style='circle_pale')
                ty += 1.0
            if s.get('text'):
                cv.text(x + 0.2, ty, w - 0.4, max(text_h + 0.1, 0.4), s['text'], size=fs, color='text',
                        align='center', fit=True)
    elif variant == 'circles':
        d = min(1.15, w * 0.42)
        th = max((cv.measure(s.get('title', ''), w - 0.3, t.size_heading + 1, role='title') for s in steps), default=0.3)
        tx = max((cv.measure(s.get('text', ''), w - 0.3, fs) for s in steps if s.get('text')), default=0)
        block = d + 0.72 + th + 0.12 + tx
        y = _center_y(box, block)
        cv.line(box.x + w / 2, y + d / 2, box.r - w / 2, y + d / 2, 'primary+60', 2.0, dash='dash')
        for i, s in enumerate(steps):
            cx = box.x + w * (i + 0.5)
            if s.get('icon'):
                K.icon_badge(cv, cx, y + d / 2, d, s['icon'])
            else:
                K.num_badge(cv, cx, y + d / 2, d, i + 1)
            K.pill(cv, cx, y + d + 0.22, f'STEP {i + 1:02d}', size=10.5, fill='primary_pale', color='primary',
                   align='center')
            ty = y + d + 0.72
            cv.text(cx - w / 2 + 0.15, ty, w - 0.3, th + 0.04, s.get('title', ''), size=t.size_heading + 1,
                    role='title', color='dark', align='center', fit=True, min_size=11, max_lines=2)
            if s.get('text'):
                cv.text(cx - w / 2 + 0.15, ty + th + 0.12, w - 0.3, tx + 0.1, s['text'], size=fs, color='text',
                        align='center', fit=True)
    else:  # cards with arrows, visual weight increasing
        gap = 0.45
        cols = box.cols(n, gap=gap)
        cw = cols[0].w
        th = max((cv.measure(s.get('title', ''), cw - 0.5, t.size_heading + 1, role='title') for s in steps), default=0.3)
        tx = max((cv.measure(s.get('text', ''), cw - 0.5, fs) for s in steps if s.get('text')), default=0)
        ch = max(1.05 + th + 0.15 + tx + 0.35, box.h * 0.62)
        ch = min(ch, box.h)
        y = _center_y(box, ch)
        for i, (c, s) in enumerate(zip(cols, steps)):
            c = Box(c.x, y, c.w, ch)
            last = i == n - 1
            K.card(cv, c, fill='primary' if last else None)
            fg = 'FFFFFF' if last else 'dark'
            cv.text(c.x + 0.25, c.y + 0.22, 1.4, 0.7, f'{i + 1:02d}', size=34, role='number', bold=True,
                    color='FFFFFF' if last else 'primary', alpha=0.9, wrap=False, fit=False)
            if s.get('icon'):
                cv.icon(s['icon'], c.r - 0.75, c.y + 0.32, 0.45, 'FFFFFF' if last else 'primary')
            cv.text(c.x + 0.25, c.y + 1.05, c.w - 0.5, th + 0.04, s.get('title', ''), size=t.size_heading + 1,
                    role='title', color=fg, fit=True, min_size=11, max_lines=2)
            if s.get('text'):
                ty = c.y + 1.05 + th + 0.15
                fs2 = _fit_up(cv, s['text'], c.w - 0.5, c.b - 0.25 - ty, t.size_min, fs + 1)
                cv.text(c.x + 0.25, ty, c.w - 0.5, c.b - 0.25 - ty, s['text'], size=fs2,
                        color='FFFFFF' if last else 'text', fit=True)
            if i < n - 1:
                K.chevron_arrow(cv, c.r + gap / 2, c.cy, 0.3, 'primary')
    if summary:
        _summary_band(cv, summary, y=cv.content.b - 0.62)
    return _done(cv, notes)

# =========================================================================== hub (center + satellites)
@layout
def hub(deck, title, center, items, en=None, center_sub=None, source=None, notes=None, section=None):
    """One core concept with 3-6 related aspects around it (surround layout — tolerant of uneven text).
    items: [{'icon','title','text'}] split into left/right columns."""
    t = deck.theme
    cv = deck.page(title, en, source=source, section=section)
    box = cv.content
    n = len(items)
    left = items[:(n + 1) // 2]
    right = items[(n + 1) // 2:]
    R = min(1.45, box.h * 0.3)
    cx, cy = box.cx, box.cy
    for k, rr in enumerate((R + 0.45, R + 0.9)):
        cv.circle(cx, cy, rr, fill=None, line='primary', line_w=1.0, line_alpha=0.25 - 0.1 * k, dash=None,
                  name='deco:ring')
    cv.circle(cx, cy, R, grad=[(0, 'secondary', 1.0), (100, 'primary', 1.0)], grad_angle=135, name='deco:hub',
              shadow={'color': 'primary', 'alpha': 0.3, 'blur': 30, 'dist': 6})
    cv.text(cx - R * 0.8, cy - R * 0.55, R * 1.6, R * (0.8 if center_sub else 1.1), center, size=26, role='heavy',
            color='FFFFFF', align='center', anchor='middle' if not center_sub else 'bottom', fit=True, min_size=14,
            max_lines=2)
    if center_sub:
        cv.text(cx - R * 0.8, cy + R * 0.3, R * 1.6, R * 0.45, center_sub, size=12, color='FFFFFF', alpha=0.85,
                align='center', fit=True, min_size=9, max_lines=2)
    colw = (box.w - 2 * (R + 0.95)) / 2
    for side, group in (('L', left), ('R', right)):
        m = len(group)
        if not m:
            continue
        rows = Box(box.x, box.y, colw, box.h).rows(m, gap=0.25)
        for r, it in zip(rows, group):
            d = 0.62
            if side == 'L':
                ix = box.x + colw - d
                tx, tw, al = box.x, colw - d - 0.25, 'right'
                cv.line(ix + d + 0.05, r.cy, cx - R - 0.05, cy + (r.cy - cy) * 0.35, 'primary+50', 1.0, dash='sysDash')
            else:
                ix = box.r - colw
                tx, tw, al = ix + d + 0.25, colw - d - 0.25, 'left'
                cv.line(cx + R + 0.05, cy + (r.cy - cy) * 0.35, ix - 0.05, r.cy, 'primary+50', 1.0, dash='sysDash')
            K.icon_badge(cv, ix + d / 2, r.cy, d, it.get('icon', 'circle-dot'))
            hh = cv.measure(it.get('title', ''), tw, t.size_heading, role='title')
            bh = cv.measure(it.get('text', ''), tw, t.size_body - 1) if it.get('text') else 0
            blk = min(r.h, hh + (bh + 0.06 if bh else 0))
            y0 = r.cy - blk / 2
            cv.text(tx, y0, tw, hh + 0.03, it.get('title', ''), size=t.size_heading, role='title', color='dark',
                    align=al, fit=True, min_size=11, max_lines=2)
            if it.get('text'):
                cv.text(tx, y0 + hh + 0.06, tw, max(0.3, r.b - (y0 + hh + 0.06)), it['text'], size=t.size_body - 1,
                        color='text', align=al, fit=True)
    return _done(cv, notes)


# =========================================================================== compare
@layout
def compare(deck, title, left, right, en=None, variant='cards', source=None, notes=None, section=None,
            vs_text='VS', rows=None, highlight='right', summary=None):
    """Two-way comparison. left/right: {'title','subtitle','points': [...], 'icon'}.
    variant: cards (two cards with VS badge) | rows (parameter rows: rows=[(label, left_val, right_val)]).
    highlight: which side is 'ours/new' (main color); the other side is neutral gray."""
    t = deck.theme
    cv = deck.page(title, en, source=source, section=section)
    box = cv.content
    if summary:
        box = Box(box.x, box.y, box.w, box.h - 0.87)
    colors = {'left': 'muted' if highlight == 'right' else 'primary', 'right': 'primary' if highlight == 'right' else 'muted'}
    if variant == 'rows' and rows:
        lw = box.w * 0.34
        cw = box.w - 2 * lw
        n = len(rows)
        rh = min(0.85, (box.h - 0.95) / n)
        block = 0.95 + n * rh
        hy = _center_y(box, block)
        for side, spec, x in (('left', left, box.x), ('right', right, box.x + lw + cw)):
            col = colors[side]
            cv.rect(x, hy, lw, 0.75, radius=0.1, fill=col if col == 'primary' else 'bg2', name='deco:head')
            cv.text(x, hy, lw, 0.75, spec.get('title', ''), size=t.size_heading + 2, role='title',
                    color='FFFFFF' if col == 'primary' else 'dark', align='center', anchor='middle', wrap=False,
                    fit=True)
        for i, (lab, lv, rv) in enumerate(rows):
            y = hy + 0.95 + i * rh
            if i % 2 == 0:
                cv.rect(box.x, y, box.w, rh, fill='primary_bg', name='deco:zebra')
            cv.text(box.x, y, lw, rh, lv, size=t.size_body + 1, color='text', align='center', anchor='middle', fit=True)
            cv.text(box.x + lw, y, cw, rh, lab, size=t.size_body + 1, role='title', color='dark', align='center',
                    anchor='middle', fit=True)
            cv.text(box.x + lw + cw, y, lw, rh, rv, size=t.size_body + 1, color='primary', bold=True, align='center',
                    anchor='middle', fit=True)
        if summary:
            _summary_band(cv, summary, y=cv.content.b - 0.62)
        return _done(cv, notes)
    lb, rb = box.split(0.5, gap=0.9)
    head_h = 1.05
    npts = max(len(left.get('points', [])), len(right.get('points', [])))
    fs = t.size_body + (2 if npts <= 4 else 0)
    need = 0
    for spec in (left, right):
        pts = spec.get('points', [])
        hh = sum(cv.measure(p, lb.w - 0.7 - fs / 72 * 1.3, fs) for p in pts) + fs / 72 * 0.55 * max(0, len(pts) - 1)
        need = max(need, hh)
    ch = min(box.h, max(head_h + 0.4 + need + 0.5, box.h * 0.6))
    y0 = _center_y(box, ch)
    for side, spec, b in (('left', left, lb), ('right', right, rb)):
        b = Box(b.x, y0, b.w, ch)
        col = colors[side]
        on = col == 'primary'
        K.card(cv, b, fill=None)
        if on:
            cv.rect(b.x, b.y, b.w, head_h, radius=t.radius, grad=[('secondary', 1.0), ('primary', 1.0)], grad_angle=0,
                    name='deco:head')
            cv.rect(b.x, b.y + head_h - t.radius, b.w, t.radius, grad=[('secondary', 1.0), ('primary', 1.0)],
                    grad_angle=0, name='deco:head2')
        else:
            cv.rect(b.x, b.y, b.w, head_h, radius=t.radius, fill='bg2', name='deco:head')
            cv.rect(b.x, b.y + head_h - t.radius, b.w, t.radius, fill='bg2', name='deco:head2')
        fg = 'FFFFFF' if on else 'dark'
        ix = b.x + 0.35
        if spec.get('icon'):
            cv.icon(spec['icon'], ix, b.y + (head_h - 0.46) / 2, 0.46, 'FFFFFF' if on else 'muted')
            ix += 0.66
        cv.text(ix, b.y + 0.14, b.r - ix - 0.3, 0.5, spec.get('title', ''), size=t.size_heading + 3, role='title',
                color=fg, wrap=False, fit=True, min_size=12)
        if spec.get('subtitle'):
            cv.text(ix, b.y + 0.6, b.r - ix - 0.3, 0.35, spec['subtitle'], size=12.5, color=fg,
                    alpha=0.85 if on else 1.0, wrap=False, fit=True, min_size=9)
        K.bullets(cv, Box(b.x + 0.4, b.y + head_h + 0.4, b.w - 0.75, b.h - head_h - 0.6), spec.get('points', []),
                  marker='check' if on else 'dot', marker_color='primary' if on else 'muted', size=fs)
    cxv, cyv = box.cx, y0 + head_h / 2
    cv.circle(cxv, cyv, 0.42, fill='surface', line='primary+60', line_w=1.5, name='deco:vs',
              shadow={'color': 'primary', 'alpha': 0.2, 'blur': 12, 'dist': 2})
    cv.text(cxv - 0.42, cyv - 0.42, 0.84, 0.84, vs_text, size=18, role='number', bold=True, color='primary',
            align='center', anchor='middle', wrap=False, fit=False)
    if summary:
        _summary_band(cv, summary, y=cv.content.b - 0.62)
    return _done(cv, notes)

# =========================================================================== matrix
@layout
def matrix(deck, title, items, en=None, x_label=None, y_label=None, source=None, notes=None, section=None,
           highlight=None):
    """2x2 quadrant (SWOT, priority, etc.). items: 4 dicts {'title','text','icon'} ordered TL, TR, BL, BR."""
    t = deck.theme
    cv = deck.page(title, en, source=source, section=section)
    box = cv.content
    inner = Box(box.x + (0.45 if y_label else 0), box.y, box.w - (0.45 if y_label else 0),
                box.h - (0.4 if x_label else 0))
    cells = inner.grid(4, 2, gap=0.2)
    for i, (c, it) in enumerate(zip(cells, items)):
        on = i == highlight
        K.card(cv, c, fill='primary' if on else ('primary_bg' if i in (0, 3) else None), style='shadow' if not on else None)
        fg = 'FFFFFF' if on else 'dark'
        ix = c.x + 0.3
        if it.get('icon'):
            K.icon_badge(cv, ix + 0.3, c.y + 0.5, 0.6, it['icon'], style='circle_grad' if not on else 'ring')
            ix += 0.8
        cv.text(ix, c.y + 0.25, c.r - ix - 0.25, 0.5, it.get('title', ''), size=t.size_heading + 1, role='title',
                color=fg, wrap=False, fit=True, min_size=11)
        if it.get('text'):
            ty = c.y + 0.95
            fs = _fit_up(cv, it['text'], c.w - 0.6, c.b - 0.2 - ty, t.size_min, t.size_body)
            cv.text(c.x + 0.3, ty, c.w - 0.6, c.b - 0.2 - ty, it['text'], size=fs, color='FFFFFF' if on else 'text',
                    fit=True)
    if x_label:
        cv.line(inner.x, inner.b + 0.2, inner.r, inner.b + 0.2, 'muted', 1.25, tail='triangle')
        cv.text(inner.r - 3.0, inner.b + 0.24, 3.0, 0.3, x_label, size=11, color='muted', align='right', wrap=False,
                fit=True)
    if y_label:
        cv.line(box.x + 0.15, inner.b, box.x + 0.15, inner.y, 'muted', 1.25, tail='triangle')
        cv.text(box.x - 0.2, inner.y, 0.35, 2.5, y_label, size=11, color='muted', vert='eaVert', fit=False,
                wrap=True)
    return _done(cv, notes)


# =========================================================================== pyramid / layers
@layout
def pyramid(deck, title, levels, en=None, source=None, notes=None, section=None, variant='pyramid'):
    """Hierarchy / layered architecture. levels (top -> bottom): [{'title','text'}] (3-5).
    variant: pyramid (trapezoid stack + descriptions right) | layers (full-width stacked bars, e.g. system
    architecture: 应用层/平台层/数据层/感知层)."""
    t = deck.theme
    cv = deck.page(title, en, source=source, section=section)
    box = cv.content
    n = len(levels)
    if variant == 'layers':
        rows = box.rows(n, gap=0.16)
        for i, (r, lv) in enumerate(zip(rows, levels)):
            lab_w = 2.2
            col = 'primary' if i == 0 else ('primary+' + str(int(20 + 55 * i / max(1, n - 1))))
            cv.rect(r.x, r.y, lab_w, r.h, radius=0.1, fill=col, name='deco:layerlab')
            cv.text(r.x, r.y, lab_w, r.h, lv.get('title', ''), size=t.size_heading, role='title',
                    color='FFFFFF' if i < n / 2 + 0.5 else 'dark', align='center', anchor='middle', fit=True,
                    wrap=False, min_size=10)
            cv.rect(r.x + lab_w + 0.15, r.y, r.w - lab_w - 0.15, r.h, radius=0.1, fill='primary_bg',
                    name='deco:layerbody')
            chips = lv.get('items')
            if chips:
                m = len(chips)
                cb = Box(r.x + lab_w + 0.35, r.y + 0.14, r.w - lab_w - 0.55, r.h - 0.28).cols(m, gap=0.15)
                for c, ch in zip(cb, chips):
                    cv.rect(c.x, c.y, c.w, c.h, radius=0.08, fill='surface', line='primary+70', line_w=0.75,
                            name='deco:chip')
                    cv.text(c.x + 0.05, c.y, c.w - 0.1, c.h, ch, size=t.size_body - 1, color='dark', align='center',
                            anchor='middle', fit=True, min_size=9)
            elif lv.get('text'):
                cv.text(r.x + lab_w + 0.4, r.y, r.w - lab_w - 0.6, r.h, lv['text'], size=t.size_body, color='text',
                        anchor='middle', fit=True)
        return _done(cv, notes)
    pw = min(5.4, box.w * 0.44)
    rows = Box(box.x, box.y, pw, box.h).rows(n, gap=0.1)
    for i, (r, lv) in enumerate(zip(rows, levels)):
        top_w = pw * (0.18 + 0.82 * i / n)
        bot_w = pw * (0.18 + 0.82 * (i + 1) / n)
        cxp = box.x + pw / 2
        pts = [(cxp - top_w / 2, r.y), (cxp + top_w / 2, r.y), (cxp + bot_w / 2, r.b), (cxp - bot_w / 2, r.b)]
        col = 'primary' if i == 0 else ('primary+' + str(int(15 + 60 * i / max(1, n - 1))))
        cv.poly(pts, fill=col, name='deco:pyr')
        cv.text(cxp - bot_w / 2 + 0.2, r.y, bot_w - 0.4, r.h, lv.get('title', ''), size=t.size_body + 1,
                role='title', color='FFFFFF' if i < n / 2 else 'dark', align='center', anchor='middle', fit=True,
                min_size=9, max_lines=2)
        # description + leader
        dx = box.x + pw + 0.9
        cv.line(cxp + (top_w + bot_w) / 4 + 0.1, r.cy, dx - 0.15, r.cy, 'primary+50', 1.0, dash='sysDash')
        cv.circle(dx - 0.15, r.cy, 0.06, fill='primary')
        if lv.get('text'):
            cv.text(dx, r.y, box.r - dx, r.h, lv['text'], size=t.size_body, color='text', anchor='middle', fit=True)
    return _done(cv, notes)


# =========================================================================== band (拦腰型)
@layout
def band(deck, title, statement, items, en=None, icon='lightbulb', source=None, notes=None, section=None):
    """'拦腰型' layout: a full-width colored band states the core idea, 2-4 supporting blocks below."""
    t = deck.theme
    cv = deck.page(title, en, source=source, section=section)
    box = cv.content
    n = len(items)
    cols = box.cols(n, gap=0.4)
    cw = cols[0].w
    fs = t.size_body + (2 if n <= 3 else 1)
    tx = max((cv.measure(it.get('text', ''), cw, fs) for it in items if it.get('text')), default=0)
    bh = 1.35
    block = bh + 0.55 + 0.75 + 0.22 + tx
    by = _center_y(box, block, bias=0.3)
    cv.rect(0, by, cv.W, bh, grad=[('primary', 1.0), ('secondary', 1.0)], grad_angle=0, name='deco:band')
    K.glow_orb(cv, cv.W - 1.0, by + bh / 2, 1.6, 'FFFFFF', 0.18)
    cv.icon(icon, box.x, by + (bh - 0.6) / 2, 0.6, 'FFFFFF')
    cv.text(box.x + 0.9, by, box.w - 0.9, bh, statement, size=t.size_heading + 5, role='title', color='FFFFFF',
            anchor='middle', fit=True, min_size=13, max_lines=2)
    y = by + bh + 0.55
    for c, it in zip(cols, items):
        d = 0.72
        K.icon_badge(cv, c.x + d / 2, y + d / 2, d, it.get('icon', 'circle-dot'), style='circle_pale')
        cv.text(c.x + d + 0.22, y, c.w - d - 0.22, d, it.get('title', ''), size=t.size_heading + 2, role='title',
                color='dark', anchor='middle', fit=True, min_size=11, max_lines=2)
        if it.get('text'):
            cv.text(c.x, y + d + 0.22, c.w, max(tx + 0.1, 0.4), it['text'], size=fs, color='text', fit=True)
    return _done(cv, notes)

# =========================================================================== split (分割型)
@layout
def split(deck, title, panels, en=None, arrows=False, source=None, notes=None, section=None):
    """'分割型' layout: 2-4 full-height panels, each {'title','points' | 'text','icon','tag'}.
    arrows=True for progression (visual weight rises toward the last panel)."""
    t = deck.theme
    cv = deck.page(title, en, source=source, section=section)
    box = cv.content
    n = len(panels)
    gap = 0.4 if arrows else 0.2
    cols = box.cols(n, gap=gap)
    for i, (c, p) in enumerate(zip(cols, panels)):
        strong = arrows and i == n - 1
        fill = 'primary' if strong else ('primary_bg' if i % 2 == 0 else 'bg2')
        cv.rect(c.x, c.y, c.w, c.h, fill=fill, radius=0.12, name='deco:panel',
                shadow='soft' if strong else None)
        fg = 'FFFFFF' if strong else 'dark'
        y = c.y + 0.35
        if p.get('icon'):
            K.icon_badge(cv, c.x + 0.35 + 0.33, y + 0.33, 0.66, p['icon'], style='circle_grad' if not strong else 'ring')
            y += 0.9
        if p.get('tag'):
            K.pill(cv, c.x + 0.35, y, p['tag'], size=10, fill='FFFFFF' if strong else 'primary',
                   color='primary' if strong else 'FFFFFF')
            y += 0.45
        hh = cv.measure(p.get('title', ''), c.w - 0.7, t.size_heading + 2, role='title')
        cv.text(c.x + 0.35, y, c.w - 0.7, hh + 0.04, p.get('title', ''), size=t.size_heading + 2, role='title',
                color=fg, fit=True, min_size=12, max_lines=2)
        y += hh + 0.2
        if p.get('points'):
            K.bullets(cv, Box(c.x + 0.35, y, c.w - 0.7, c.b - y - 0.3), p['points'], marker='dot',
                      marker_color='FFFFFF' if strong else 'primary', color='FFFFFF' if strong else 'text',
                      size=t.size_body + (2 if len(p['points']) <= 4 else 0), gap=0.18)
        elif p.get('text'):
            fs = _fit_up(cv, p['text'], c.w - 0.7, c.b - y - 0.3, t.size_min, t.size_body + 1)
            cv.text(c.x + 0.35, y, c.w - 0.7, c.b - y - 0.3, p['text'], size=fs, color='FFFFFF' if strong else 'text',
                    fit=True)
        if arrows and i < n - 1:
            K.chevron_arrow(cv, c.r + gap / 2, c.cy, 0.26, 'primary')
    return _done(cv, notes)


# =========================================================================== figure (scientific)
@layout
def figure(deck, title, image, caption=None, points=None, en=None, side='left', source=None, notes=None,
           section=None, fig_no=None, frac=0.6):
    """Scientific figure page: figure kept in original colors on a white card, caption '图x ...' under it,
    explanation points beside it. frac: figure width fraction."""
    t = deck.theme
    cv = deck.page(title, en, source=source, section=section)
    box = cv.content
    if points:
        fb, pb = box.split(frac, gap=0.45)
        if side == 'right':
            pb, fb = box.split(1 - frac, gap=0.45)
    else:
        fb, pb = box, None
    cap_h = 0.42 if caption else 0
    K.card(cv, fb)
    inner = fb.inset(0.2, 0.2)
    cv.image(image, inner.x, inner.y, inner.w, inner.h - cap_h, fit='contain', name='img:figure')
    if caption:
        cap = (f'图{fig_no}  ' if fig_no else '') + caption
        cv.text(inner.x, inner.b - cap_h + 0.05, inner.w, cap_h - 0.05, cap, size=12, color='muted', align='center',
                fit=True, wrap=False, min_size=8, name='txt:caption')
    if pb is not None:
        K.bullets(cv, Box(pb.x, pb.y + 0.25, pb.w, pb.h - 0.25), points, marker='num', size=t.size_body + 1,
                  gap=0.28)
    return _done(cv, notes)


# =========================================================================== image grid
@layout
def image_grid(deck, title, images, en=None, cols=None, source=None, notes=None, section=None, radius=0.1):
    """2-8 pictures cropped to identical size (align + equal gaps), captions under each.
    images: [{'path','caption'}] or paths."""
    t = deck.theme
    cv = deck.page(title, en, source=source, section=section)
    box = cv.content
    imgs = [i if isinstance(i, dict) else {'path': i} for i in images]
    n = len(imgs)
    cols = cols or (n if n <= 4 else (3 if n in (5, 6, 9) else 4))
    cells = box.grid(n, cols, gap=0.25, row_gap=0.3)
    for c, im in zip(cells, imgs):
        cap_h = 0.42 if im.get('caption') else 0
        cv.image(im['path'], c.x, c.y, c.w, c.h - cap_h, fit='cover', radius=radius, shadow='soft')
        if im.get('caption'):
            cv.text(c.x, c.b - cap_h + 0.08, c.w, cap_h - 0.08, im['caption'], size=t.size_small + 1, color='dark',
                    align='center', fit=True, wrap=False, min_size=9)
    return _done(cv, notes)


# =========================================================================== team
@layout
def team(deck, title, members, en=None, source=None, notes=None, section=None):
    """Team / people cards: [{'name','role','desc','photo'(opt)}] (2-6). Without photo an initial avatar is drawn."""
    t = deck.theme
    cv = deck.page(title, en, source=source, section=section)
    box = cv.content
    n = len(members)
    cols = box.grid(n, n if n <= 4 else 3, gap=0.3, row_gap=0.3)
    for c, m in zip(cols, members):
        K.card(cv, c)
        d = min(1.4, c.w * 0.5, c.h * 0.38)
        cx, cy = c.cx, c.y + 0.3 + d / 2
        if m.get('photo'):
            cv.image(m['photo'], cx - d / 2, cy - d / 2, d, d, fit='cover', shape='ellipse', line='FFFFFF', line_w=3,
                     shadow='soft')
        else:
            cv.circle(cx, cy, d / 2, grad=[(0, 'secondary', 1.0), (100, 'primary', 1.0)], grad_angle=135)
            cv.text(cx - d / 2, cy - d / 2, d, d, m.get('name', '?')[:1], size=d * 72 * 0.42, role='heavy',
                    color='FFFFFF', align='center', anchor='middle', wrap=False, fit=False)
        y = cy + d / 2 + 0.2
        cv.text(c.x + 0.2, y, c.w - 0.4, 0.45, m.get('name', ''), size=t.size_heading + 1, role='title', color='dark',
                align='center', wrap=False, fit=True)
        if m.get('role'):
            K.pill(cv, cx, y + 0.5, m['role'], size=11, fill='primary_pale', color='primary', align='center')
        if m.get('desc'):
            ty = y + 1.02
            fs = _fit_up(cv, m['desc'], c.w - 0.5, c.b - 0.15 - ty, t.size_min - 1, t.size_body - 1)
            cv.text(c.x + 0.25, ty, c.w - 0.5, c.b - 0.15 - ty, m['desc'], size=fs, color='text', align='center',
                    fit=True, min_size=9)
    return _done(cv, notes)


# =========================================================================== references
@layout
def references(deck, title='参考文献', refs=(), en='REFERENCES', source=None, notes=None, size=None, numbered=True):
    """Numbered reference list (GB/T 7714 style strings). Two columns when > 8 entries.
    numbered=False keeps the strings as given (e.g. '[13] Meng W, …' to match a paper's own numbering)."""
    t = deck.theme
    cv = deck.page(title, en, source=source)
    box = cv.content
    refs = list(refs)
    n = len(refs)
    ncol = 1 if n <= 8 else 2
    cols = box.cols(ncol, gap=0.5)
    per = (n + ncol - 1) // ncol
    fs = size or (13 if n <= 8 else 11)
    for ci, c in enumerate(cols):
        chunk = refs[ci * per:(ci + 1) * per]
        paras = [f'[{ci * per + i + 1}] {r}' if numbered else r for i, r in enumerate(chunk)]
        cv.text(c.x, c.y, c.w, c.h, paras, size=fs, color='text', fit=True, min_size=8, ls=1.15, sa=fs * 0.6,
                indent=0, name='txt:refs')
    return _done(cv, notes)
