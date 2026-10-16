"""Research-deck diagram helpers distilled from the 2024–2026 tutorial-image review (notes/03_article_visuals.md).

Re-exported by `pptstudio.academic`, so call them as `A.formula_card(...)`, `A.cycle(...)` etc.

    card_box        white card (soft tinted shadow / top accent line / outline / pale) -> inner Box
    symbol_strip    legend under a formula: typeset symbol above its meaning, thin separators
    formula_block   display formula + symbol strip inside a box
    formula_card    card = small header + one-line meaning + formula + symbol strip
    cycle           closed loop: ring of N arrow-tipped segments, labels along the ring, centre
    stat_grid       number grid: small label above a big value (+unit), thin column rules
    progress_bars   horizontal bars with track, value at the end, one highlighted
    vs_badge        round "VS" badge between two comparison cards
    hbracket        horizontal phase bracket with a label (spanning several columns)
    water_waves     layered wave shapes (水利 / 流域 motif, covers)
All coordinates in inches; colors are theme roles / named colors / hex.
"""
from __future__ import annotations

import math

from .canvas import Box, plain


# ---------------------------------------------------------------- cards
def card_box(cv, box, style='shadow', accent='primary', radius=0.08, fill='FFFFFF', pad=0.16, name='deco:card'):
    """Card container. style: shadow (white + diffuse tinted shadow) | topline (white, accent line on top) |
    outline (white, accent border) | pale (panel fill). Returns the padded inner Box."""
    if style == 'topline':
        cv.rect(box.x, box.y, box.w, box.h, fill=fill, radius=0.03, line='panel_line', line_w=0.5, name=name,
                shadow={'color': 'primary_deep', 'alpha': 0.08, 'blur': 12, 'dist': 3})
        cv.rect(box.x, box.y, box.w, 0.06, fill=accent, name='deco:cardtop')
        return Box(box.x + pad, box.y + pad + 0.06, box.w - 2 * pad, box.h - 2 * pad - 0.06)
    if style == 'outline':
        cv.rect(box.x, box.y, box.w, box.h, fill=fill, radius=radius, line=accent + '+45', line_w=1.0, name=name)
    elif style == 'pale':
        cv.rect(box.x, box.y, box.w, box.h, fill='panel_light', radius=radius, line='panel_line', line_w=0.75,
                name=name)
    else:  # shadow — 弥散阴影: tinted, soft, small offset (利3: ~90 % transparent, large blur)
        cv.rect(box.x, box.y, box.w, box.h, fill=fill, radius=radius, line='panel_line', line_w=0.5, name=name,
                shadow={'color': 'primary_deep', 'alpha': 0.13, 'blur': 18, 'dist': 4})
    return Box(box.x + pad, box.y + pad, box.w - 2 * pad, box.h - 2 * pad)


def card_title(cv, x, y, w, title, icon=None, size=None, color='primary_deep', sub=None, sub_size=None):
    """Card header row: optional navy icon badge + bold title (+ muted subtitle under it). Returns height used."""
    t = cv.t
    size = size or t.size_body + 1
    h = size / 72 * 1.75
    tx = x
    if icon:
        from .academic import icon_badge_ac
        d = min(0.5, h * 1.15)
        icon_badge_ac(cv, x + d / 2 + 0.03, y + d / 2 + 0.02, d, icon)
        tx = x + d + 0.18
        h = max(h, d + 0.06)
    cv.text(tx, y, x + w - tx, h, title, size=size, color=color, role='title', anchor='middle', wrap=False, fit=True,
            min_size=10, emph='emph', name='txt:cardtitle')
    used = h
    if sub:
        ss = sub_size or t.size_small
        sh = min(0.6, cv.measure(sub, w, ss, role='medium') + 0.04)
        cv.text(x, y + used, w, sh, sub, size=ss, color='muted', role='medium', fit=True, min_size=9,
                name='txt:cardsub')
        used += sh + 0.02
    return used + 0.06


# ---------------------------------------------------------------- formulas
def symbol_strip(cv, box, symbols, size=None, sym_size=None, cols=None, fill='panel'):
    """Symbol legend under a formula: each cell = typeset symbol (TeX, e.g. r'\\eta_c') above its meaning.
    symbols: [(tex, meaning)]. cols default: up to 4 per row."""
    t = cv.t
    n = len(symbols)
    if not n:
        return
    cols = cols or min(n, 4 if box.w > 4.2 else (3 if box.w > 2.6 else 2))
    nrow = (n + cols - 1) // cols
    if fill:
        cv.rect(box.x, box.y, box.w, box.h, fill=fill, radius=0.04, name='deco:symstrip')
    rows = box.inset(0.06, 0.05).rows(nrow, gap=0.04)
    size = size or max(9.5, t.size_small - 1)
    k = 0
    for r in rows:
        m = min(cols, n - k)
        cells = Box(r.x, r.y, r.w * m / cols, r.h).cols(m, gap=0.0)
        for j, c in enumerate(cells):
            tex, desc = symbols[k]
            k += 1
            sh = c.h * 0.5
            cv.equation(tex, c.x + 0.04, c.y + 0.01, size=sym_size or t.size_body + 1, color='primary_deep',
                        w=c.w - 0.08, h=sh, align='center', anchor='middle')
            cv.text(c.x + 0.04, c.y + sh, c.w - 0.08, c.h - sh, desc, size=size, color='dark', role='medium',
                    align='center', anchor='top', fit=True, min_size=8, name='txt:symdesc')
            if j:
                cv.line(c.x, c.y + 0.06, c.x, c.b - 0.06, 'panel_line', 0.75, name='deco:symrule')


def formula_block(cv, box, tex, symbols=(), num=None, size=None, note=None, cols=None):
    """Display formula (true size, shrunk to fit) with an optional symbol strip under it."""
    from .academic import formula
    t = cv.t
    sym_h = 0
    if symbols:
        cols = cols or min(len(symbols), 4 if box.w > 4.2 else (3 if box.w > 2.6 else 2))
        nrow = (len(symbols) + cols - 1) // cols
        sym_h = min(0.74 * nrow, box.h * 0.5)
    fb = Box(box.x, box.y, box.w, box.h - sym_h - (0.1 if symbols else 0))
    eb = formula(cv, fb, tex, num=num, size=size or t.size_body + 4, note=note)
    if symbols:
        symbol_strip(cv, Box(box.x, box.b - sym_h, box.w, sym_h), symbols, cols=cols)
    return eb


def formula_card(cv, box, tex, title=None, meaning=None, symbols=(), num=None, size=None, style='shadow',
                 accent='primary', icon=None):
    """Formula card: header with accent mark, one-line meaning, the formula, a symbol legend strip.
    Returns the inner Box of the card."""
    t = cv.t
    inner = card_box(cv, box, style=style, accent=accent)
    y = inner.y
    if title:
        if not icon:
            cv.rect(inner.x, y + 0.08, 0.06, 0.28, fill=accent, name='deco:fmark')
        y += card_title(cv, inner.x + (0 if icon else 0.14), y, inner.w - (0 if icon else 0.14), title, icon=icon)
    if meaning:
        mh = min(0.62, cv.measure(meaning, inner.w, t.size_small, role='medium') + 0.06)
        cv.text(inner.x, y, inner.w, mh, meaning, size=t.size_small, color='muted', role='medium', fit=True,
                min_size=9, emph='emph', name='txt:fmeaning')
        y += mh + 0.04
    formula_block(cv, Box(inner.x, y, inner.w, inner.b - y), tex, symbols=symbols, num=num, size=size)
    return inner


# ---------------------------------------------------------------- loops
def _pt(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.sin(a), cy - r * math.cos(a)


def cycle(cv, cx, cy, r, labels, thickness=None, colors=None, center=None, center_sub=None, icon=None,
          gap_deg=4.0, size=None, start_deg=0.0, label_color='FFFFFF', center_fill='FFFFFF', name='deco:cycle'):
    """Closed loop (闭环): a ring of N arrow-tipped segments running clockwise from `start_deg` (0 = 12 o'clock),
    each labelled along the ring (text follows the tangent, kept upright), plus a centre disc with text/icon.
    Returns [(mid_angle_deg, color)] per segment so callers can place detail blocks around the ring."""
    t = cv.t
    n = len(labels)
    th = thickness or max(0.34, min(0.62, r * 0.32))
    rc = r - th / 2
    colors = colors or ['primary_deep', 'primary', 'secondary', 'primary+25', 'primary-15', 'secondary-20']
    seg = 360.0 / n
    arrow_deg = math.degrees(th * 0.62 / rc)
    out = []
    for i, lab in enumerate(labels):
        col = colors[i % len(colors)]
        a0 = start_deg + i * seg + gap_deg / 2
        sweep = seg - gap_deg - arrow_deg
        cv.ring(cx, cy, r, th, color=col, start=a0, sweep=sweep, name=name)
        ae = a0 + sweep
        b1 = _pt(cx, cy, r + 0.07, ae)
        b2 = _pt(cx, cy, r - th - 0.07, ae)
        tip = _pt(cx, cy, rc, ae + arrow_deg)
        cv.poly([b1, tip, b2], fill=col, name=name + 'arrow')
        mid = a0 + sweep / 2
        lx, ly = _pt(cx, cy, rc, mid)
        chord = 2 * rc * math.sin(math.radians(min(sweep, 170) / 2)) * 0.92
        rot = mid % 360
        if 90 < rot < 270:
            rot -= 180
        ls = size or max(9.5, min(t.size_body, th * 72 * 0.42))
        cv.text(lx - chord / 2, ly - th / 2, chord, th, lab, size=ls, color=label_color, role='title',
                align='center', anchor='middle', wrap=False, fit=True, min_size=8, rot=rot, name='txt:cyclelabel')
        out.append((mid % 360, col))
    ri = r - th - 0.14
    if ri > 0.25:
        cv.circle(cx, cy, ri, fill=center_fill, line='panel_line', line_w=0.75, name=name + 'center',
                  shadow={'color': 'primary_deep', 'alpha': 0.12, 'blur': 14, 'dist': 3})
        ty = cy - ri * 0.62
        if icon:
            s = ri * 0.62
            cv.icon(icon, cx - s / 2, cy - ri * 0.72, s, 'primary')
            ty = cy - ri * 0.05
        if center:
            hh = ri * (0.62 if icon else 0.8)
            cv.text(cx - ri * 0.86, ty if icon else cy - (hh if center_sub else hh / 2), ri * 1.72, hh, center,
                    size=min(t.size_body + 3, ri * 72 * 0.3), color='primary_deep', role='title', align='center',
                    anchor='middle' if not center_sub else 'bottom', fit=True, min_size=9, ls=1.0, sa=0,
                    name='txt:cyclecenter')
            if center_sub:
                cv.text(cx - ri * 0.8, cy + 0.02, ri * 1.6, ri * 0.55, center_sub, size=t.size_small, color='muted',
                        role='medium', align='center', fit=True, min_size=8, name='txt:cyclesub')
    return out


# ---------------------------------------------------------------- numbers
def _value_runs(cv, x, y, w, h, value, unit='', size=28, color='primary', align='left', anchor='b'):
    from . import oxml as X
    t = cv.t
    tb = cv.slide.shapes.add_textbox(*[int(v * 914400) for v in (x, y, w, h)])
    X.set_body(tb, 0, 0, 0, 0, anchor=anchor, wrap=False)
    p = tb.text_frame.paragraphs[0]
    X.set_para(p, align=align, bullet='', line_spacing=0.9)
    r = p.add_run()
    r.text = str(value)
    ea, lat, _ = t.font('number')
    X.style_run(r, size=size, bold=True, hexclr=t.c(color), ea=ea, latin=lat)
    if unit:
        r2 = p.add_run()
        r2.text = unit
        X.style_run(r2, size=size * 0.5, bold=True, hexclr=t.c(color), ea=t.f_body, latin=lat)
    tb.name = 'txt:value'
    return tb


def stat_grid(cv, box, items, cols=None, color='primary', size=None, label_size=None, rules=True, align='left'):
    """Number grid: each cell = small label above a big value with unit.
    items: [{'label', 'value', 'unit'}]. Highlight one cell with 'color': 'emph'."""
    t = cv.t
    n = len(items)
    cols = cols or (n if n <= 4 else (3 if n in (5, 6, 9) else 4))
    nrow = (n + cols - 1) // cols
    rows = box.rows(nrow, gap=0.1)
    ls = label_size or max(9.5, t.size_small - 0.5)
    k = 0
    for r in rows:
        cells = r.cols(cols, gap=0.0)
        for j, c in enumerate(cells):
            if k >= n:
                break
            it = items[k]
            k += 1
            lh = min(0.36, c.h * 0.36)
            px = c.x + (0.14 if j else 0.04)
            cw = c.w - (0.18 if j else 0.08)
            cv.text(px, c.y, cw, lh, it.get('label', ''), size=ls, color='muted', role='medium', align=align,
                    anchor='bottom', wrap=False, fit=True, min_size=8, name='txt:gridlabel')
            vs = size or min(30, max(16, (c.h - lh) * 72 * 0.62))
            vu = str(it.get('value', '')) + str(it.get('unit', ''))
            while vs > 12 and cv.width_of(vu, vs, role='number', bold=True) > cw * 0.98:
                vs -= 1
            _value_runs(cv, px, c.y + lh, cw, c.h - lh, it.get('value', ''), it.get('unit', ''), size=vs,
                        color=it.get('color', color), align=align, anchor='t')
            if rules and j:
                cv.line(c.x, c.y + 0.06, c.x, c.b - 0.06, 'panel_line', 1.0, name='deco:gridrule')


def progress_bars(cv, box, items, color='primary', max_value=100.0, highlight=None, size=None, label_w=None,
                  value_fmt='{:g}%'):
    """Horizontal bars (track + fill, rounded): label | bar | value. items: [{'label','value','display'}].
    value is a percentage unless max_value is given; highlight: index drawn in the emphasis color."""
    t = cv.t
    n = len(items)
    if not n:
        return
    rh = box.h / n
    bar_h = max(0.12, min(0.24, rh * 0.42))
    size = size or max(10, min(t.size_body - 1, rh * 72 * 0.42))
    label_w = label_w or min(box.w * 0.36, max(cv.width_of(plain(str(it.get('label', ''))), size, role='medium')
                                              for it in items) + 0.15)
    val_w = 0.78
    tx = box.x + label_w + 0.08
    tw = box.r - val_w - 0.08 - tx
    for i, it in enumerate(items):
        y = box.y + i * rh
        cv.text(box.x, y, label_w, rh, it.get('label', ''), size=size, color='dark', role='medium', align='right',
                anchor='middle', wrap=False, fit=True, min_size=8, name='txt:barlabel')
        by = y + (rh - bar_h) / 2
        cv.rect(tx, by, tw, bar_h, fill='panel', radius=bar_h / 2, name='deco:bartrack')
        v = float(it.get('value', 0))
        frac = max(0.0, min(1.0, v / float(max_value or 100.0)))
        col = 'emph' if (highlight is not None and i == highlight) else it.get('color', color)
        if frac > 0:
            cv.rect(tx, by, max(bar_h, tw * frac), bar_h, radius=bar_h / 2, name='deco:barfill',
                    grad=[(0, col + '+35' if not col.startswith('#') else col, 1.0), (100, col, 1.0)], grad_angle=0)
        disp = it.get('display') or value_fmt.format(v)
        cv.text(box.r - val_w, y, val_w, rh, disp, size=size, color=col, role='number', bold=True, anchor='middle',
                wrap=False, fit=True, min_size=8, name='txt:barvalue')


def vs_badge(cv, cx, cy, d=0.64, text='VS'):
    cv.circle(cx, cy, d / 2 + 0.07, fill='FFFFFF', line='panel_line', line_w=1.0, name='deco:vsring',
              shadow={'color': 'primary_deep', 'alpha': 0.15, 'blur': 10, 'dist': 2})
    cv.circle(cx, cy, d / 2, grad=[(0, 'emph+10', 1.0), (100, 'emph-15', 1.0)], grad_angle=45, name='deco:vs')
    cv.text(cx - d / 2, cy - d / 2, d, d, text, size=d * 72 * 0.36, color='FFFFFF', role='number', bold=True,
            align='center', anchor='middle', wrap=False, fit=False, name='txt:vs')


def hbracket(cv, x0, x1, y, label=None, color='primary', size=None, tick=0.12):
    """Phase bracket: a line from x0 to x1 at y with down ticks at both ends and a label pill on the middle."""
    t = cv.t
    cv.line(x0, y, x1, y, color, 1.25, name='deco:bracket')
    cv.line(x0, y, x0, y + tick, color, 1.25, name='deco:bracket')
    cv.line(x1, y, x1, y + tick, color, 1.25, name='deco:bracket')
    if label:
        size = size or t.size_small
        lw = min(x1 - x0 - 0.2, cv.width_of(plain(label), size, role='title') + 0.4)
        cx = (x0 + x1) / 2
        h = size / 72 * 1.7
        cv.rect(cx - lw / 2, y - h / 2, lw, h, fill='primary_bg', line=color, line_w=0.75, radius=h / 2,
                name='deco:bracketlabel')
        cv.text(cx - lw / 2, y - h / 2, lw, h, label, size=size, color=color, role='title', align='center',
                anchor='middle', wrap=False, fit=True, min_size=8, name='txt:bracket')


def water_waves(cv, x0, x1, y, h, colors=('primary+40', 'secondary+25', 'FFFFFF'), alphas=(0.5, 0.45, 1.0),
                amp=None, periods=1.15, phase=0.4, name='deco:waterwave'):
    """Layered wave shapes filling the strip [y, y+h] (水波 motif for 水利 / 流域 / 海洋 topics).
    The last layer is drawn lowest; make it the page color so content can sit on it."""
    n = len(colors)
    amp = amp if amp is not None else h * 0.14
    out = []
    for i in range(n):
        top = y + h * 0.18 * i
        pts = []
        k = 28
        for j in range(k + 1):
            x = x0 + (x1 - x0) * j / k
            pts.append((x, top + amp * (1 - 0.18 * i) *
                        math.sin(2 * math.pi * periods * j / k + phase + i * 1.25)))
        poly = pts + [(x1, y + h), (x0, y + h)]
        out.append(cv.poly(poly, fill=colors[i], alpha=alphas[i % len(alphas)], smooth=False, name=name))
    return out
