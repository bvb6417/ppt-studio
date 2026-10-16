"""Research-deck layouts distilled from the 2024–2026 tutorial-image review (1,679 images of 57 articles; see
references/design-rules.md §13). Style-aware: they use the defense building blocks and theme colors, so they work in
every skin and theme.

    band_cards      拦腰: colored band (headline / KPIs / pills / figure) + cards overlapping its lower edge
    architecture    分层架构图: vertical tier labels + tier rows of chips (+ groups) + side columns + top banner
    versus          本文 vs 对比: highlighted card (✓ rows) vs gray cards with a VS badge
    process_matrix  技术路线矩阵: phase brackets + chevron steps (deepening color) + grid of cells + arrows
    cycle           闭环: ring of arrow segments in the middle, numbered detail blocks around it
    bands           横向色带: horizontal bands with a big faded word (国外 / 国内研究现状) + text columns
    tree            层级树: root → level-2 nodes → stacked leaves (课题分解 / 组织架构)
"""
from __future__ import annotations

import math

from . import academic as A
from . import diagrams as D
from . import images as IMG
from .canvas import Box, plain
from .layouts import layout
from .layouts_ac import _fill_panel, _list_h, _unify_lists

W, H = 13.333, 7.5


def _frame(deck, title, statement=None, stmt_style=None, stmt_label=None, conclusion=None,
           conclusion_style='navy', num=None, en=None, source=None, section=None):
    """Common page frame: chrome + optional statement bar + optional conclusion bar. Returns (cv, area Box)."""
    cv = deck.page(title, en, source=source, section=section, num=num)
    box = cv.content
    y = box.y
    if statement:
        y += A.statement(cv, box.x, y, box.w, statement, style=stmt_style, label=stmt_label) + 0.17
    bottom = box.b
    if conclusion:
        cy = A.conclusion(cv, conclusion, y=box.b - 0.55, x=box.x, w=box.w, h=0.55, style=conclusion_style,
                          serif=conclusion_style == 'yellow')
        bottom = cy - 0.16
    return cv, Box(box.x, y, box.w, bottom - y)


def _done(cv, notes):
    _unify_lists(cv)
    if notes:
        cv.notes(notes)
    return cv


def _tints(n, lo=30, deep=True):
    """n colors deepening left -> right: primary+lo ... primary, last = primary_deep."""
    if n == 1:
        return ['primary_deep' if deep else 'primary']
    out = []
    for i in range(n):
        amt = round(lo * (1 - i / (n - 1)))
        out.append('primary_deep' if (deep and i == n - 1) else (f'primary+{amt}' if amt else 'primary'))
    return out


# =========================================================================== 拦腰 band + overlapping cards
@layout
def band_cards(deck, title, cards, headline=None, text=None, kpis=None, pills=None, image=None, caption=None,
               band_h=None, overlap=0.5, card_style='shadow', conclusion=None, conclusion_style='navy', num=None,
               en=None, source=None, notes=None, section=None):
    """拦腰式: a full-width colored band carries the 总 (headline + 1–3 lines of text,
    optional KPI row, keyword pills, a figure at the right) and the 分 cards overlap its lower edge.
    cards (2–5): dicts with any of 'title', 'icon', 'tag', 'subtitle', 'image'+'caption', 'chart', 'table',
    'formula'+'symbols', 'stats', 'stat_grid', 'bars', 'points', 'text' (rendered top→bottom).
    kpis: [{'value','unit','label'}] shown in the band. card_style: shadow | topline | outline | pale."""
    t = deck.theme
    cv, area = _frame(deck, title, conclusion=conclusion, conclusion_style=conclusion_style, num=num, en=en,
                      source=source, section=section)
    bh = band_h or max(1.5, min(2.45, area.h * 0.43))
    if not band_h:   # short cards -> shorter cards and a taller band (no empty card bottoms)
        flex = ('image', 'chart', 'table', 'formula', 'visual', 'placeholder', 'stat_grid', 'bars', 'flow', 'stats')
        if cards and not any(any(k in cd for k in flex) for cd in cards):
            cw = (area.w - 0.22 * (len(cards) - 1)) / len(cards) - 0.32
            need = 0.0
            for cd in cards:
                h_ = (0.38 if cd.get('tag') else 0) + (0.56 if cd.get('title') else 0) + (0.36 if cd.get('subtitle') else 0)
                if cd.get('points'):
                    h_ += _list_h(cv, cd['points'], cw, t.size_body + 1)
                elif cd.get('text'):
                    h_ += cv.measure(cd['text'], cw, t.size_body, role='medium')
                need = max(need, h_ + 0.32 + 0.3)
            card_h = area.h - (bh - overlap) - 0.02
            if need < card_h - 0.3:
                new_card_h = max(need, card_h * 0.6)
                bh = min(area.h * 0.62, bh + (card_h - new_card_h))
    by = area.y + 0.02
    cv.rect(0, by, W, bh, grad=[(0, 'primary_deep', 1.0), (100, 'primary', 1.0)], grad_angle=0, name='bg:band')
    dots = IMG.dot_map(t.c('secondary+45'), alpha=0.22, size=(1100, 300), step=12, seed=9)
    cv.image(dots, W * 0.55, by, W * 0.45, bh, fit='stretch', name='bg:banddots')
    top, bot = by + 0.2, by + bh - overlap - 0.14
    x0, x1 = area.x, area.r
    if image:
        iw = area.w * 0.3
        ib = Box(x1 - iw, by + 0.1, iw, bh - overlap - 0.16)
        pic = cv.image(image, ib.x, ib.y, ib.w, ib.h, fit='contain', name='img:band')
        if caption:
            pb = A.pic_box(pic)
            cv.text(pb.x, pb.b - 0.28, pb.w, 0.26, caption, size=9.5, color='FFFFFF', alpha=0.85, align='center',
                    wrap=False, fit=True, min_size=7, name='txt:bandcap')
        x1 = ib.x - 0.3
    if kpis:
        kw = min((x1 - x0) * 0.48, 1.65 * len(kpis))
        kh = min(bot - top, 1.3)
        kb = Box(x1 - kw, top + (bot - top - kh) / 2, kw, kh)
        for c, k in zip(kb.cols(len(kpis), gap=0.12), kpis):
            D._value_runs(cv, c.x, c.y, c.w, c.h * 0.58, k.get('value', ''), k.get('unit', ''),
                          size=min(32, c.h * 72 * 0.42), color='yellow', align='center')
            cv.text(c.x, c.y + c.h * 0.6, c.w, c.h * 0.4, k.get('label', ''), size=t.size_small, color='FFFFFF',
                    role='medium', align='center', fit=True, min_size=8, alpha=0.92, name='txt:bandkpi')
        x1 = kb.x - 0.35
    tw = x1 - x0
    pill_h = 0.34 if pills else 0
    block = (cv.measure(headline, tw, t.size_body + 5, role='title') + 0.12 if headline else 0) +         (cv.measure(text, tw, t.size_body - 0.5, role='medium') + 0.12 if text else 0) + (pill_h if pills else 0)
    y = top + max(0.0, (bot - top - block) / 2)   # centre the band text in the visible band
    if headline:
        hs = t.size_body + 5
        hh = min(bot - y - pill_h, cv.measure(headline, tw, hs, role='title') + 0.06)
        cv.text(x0, y, tw, hh, headline, size=hs, color='FFFFFF', role='title', fit=True, min_size=13,
                emph='yellow', name='txt:bandhead')
        y += hh + 0.06
    if text:
        th_ = max(0.3, bot - y - (pill_h + 0.08 if pills else 0))
        th_ = min(th_, cv.measure(text, tw, t.size_body - 0.5, role='medium') + 0.06)
        cv.text(x0, y, tw, th_, text, size=t.size_body - 0.5, color='FFFFFF', role='medium', fit=True, min_size=10,
                emph='yellow', alpha=0.95, anchor='top', name='txt:bandtext')
        y += th_ + 0.06
    if pills:
        px = x0
        for pl in pills:
            pw = cv.width_of(plain(pl), t.size_small, role='medium') + 0.36
            if px + pw > x0 + tw:
                break
            cv.rect(px, y, pw, pill_h, fill=None, line='FFFFFF', line_w=1.0, radius=pill_h / 2, name='deco:bandpill')
            cv.text(px, y, pw, pill_h, pl, size=t.size_small, color='FFFFFF', role='medium', align='center',
                    anchor='middle', wrap=False, fit=True, min_size=8, name='txt:bandpill')
            px += pw + 0.12
    cy0 = by + bh - overlap
    cells = Box(area.x, cy0, area.w, area.b - cy0).cols(len(cards), gap=0.22)
    for c, cd in zip(cells, cards):
        inner = A.card_box(cv, c, style=card_style, accent='yellow' if card_style == 'topline' else 'primary')
        yy = inner.y
        if cd.get('tag'):
            A.tag(cv, inner.x, yy, min(inner.w, cv.width_of(plain(cd['tag']), 11, role='title') + 0.4), 0.3,
                  cd['tag'], style='pill', size=11)
            yy += 0.38
        if cd.get('title'):
            yy += A.card_title(cv, inner.x, yy, inner.w, cd['title'], icon=cd.get('icon'))
        rest = {k: v for k, v in cd.items() if k not in ('title', 'icon', 'tag')}
        rest.setdefault('anchor', 'top')
        _fill_panel(cv, Box(inner.x, yy, inner.w, inner.b - yy), rest)
    return _done(cv, notes)


# =========================================================================== 分层架构图
def _chips(cv, box, items, size=None, cols=None, fill='FFFFFF', line='panel_line', color='dark'):
    """Grid of rounded chips (str or {'text','icon'}) filling `box`."""
    t = cv.t
    n = len(items)
    if not n:
        return
    size = size or max(10.5, t.size_small)
    min_w = 1.0
    per = cols or max(1, min(n, int((box.w + 0.1) // (min_w + 0.1))))
    nrow = (n + per - 1) // per
    if nrow > 1 and cols is None:          # balance rows
        per = (n + nrow - 1) // nrow
    rows = box.rows(nrow, gap=0.08)
    k = 0
    for r in rows:
        m = min(per, n - k)
        ch = min(r.h, 0.62)
        cw_full = r.w
        cells = Box(r.x, r.y + (r.h - ch) / 2, cw_full * m / per if nrow > 1 else cw_full, ch).cols(m, gap=0.1)
        for c in cells:
            it = items[k]
            k += 1
            txt = it if isinstance(it, str) else it.get('text', '')
            icon = None if isinstance(it, str) else it.get('icon')
            cv.rect(c.x, c.y, c.w, c.h, fill=fill, line=line, line_w=0.75, radius=0.05, name='deco:chip')
            tx = c.x + 0.06
            if icon:
                s = min(0.26, c.h * 0.5)
                cv.icon(icon, c.x + 0.1, c.cy - s / 2, s, 'primary')
                tx = c.x + 0.1 + s + 0.06
            cv.text(tx, c.y, c.r - tx - 0.06, c.h, txt, size=size, color=color, role='medium',
                    align='center' if not icon else 'left', anchor='middle', fit=True, min_size=8, name='txt:chip')


@layout
def architecture(deck, title, tiers, top=None, sides=None, statement=None, conclusion=None, conclusion_style='navy',
                 label_w=0.62, num=None, en=None, source=None, notes=None, section=None):
    """分层架构图: tiers top→bottom, each = vertical label tab (solid primary) + pale row
    container of white chips. tiers: [{'label': '应用层', 'items': [str | {'text','icon'}], 'groups': [{'title',
    'items'}] (sub-containers instead of items), 'fill': label color}]. top: banner text over the tiers (goal /
    platform name). sides: [{'label': '标准规范体系', 'side': 'left'|'right'}] tall columns spanning all tiers.
    Three color levels only: solid (labels, banner) · pale (rows) · white (chips)."""
    t = deck.theme
    cv, area = _frame(deck, title, statement=statement, conclusion=conclusion, conclusion_style=conclusion_style,
                      num=num, en=en, source=source, section=section)
    sides = sides or []
    ls = [s for s in sides if s.get('side', 'left') == 'left']
    rs = [s for s in sides if s.get('side', 'left') == 'right']
    sw, sg = 0.66, 0.12
    ix0 = area.x + len(ls) * (sw + sg)
    ix1 = area.r - len(rs) * (sw + sg)
    ty = area.y
    if top:
        cv.rect(ix0, ty, ix1 - ix0, 0.52, grad=[(0, 'primary_deep', 1.0), (100, 'primary', 1.0)], grad_angle=0,
                radius=0.05, name='deco:archtop')
        cv.text(ix0 + 0.2, ty, ix1 - ix0 - 0.4, 0.52, top, size=t.size_body + 1, color='FFFFFF', role='title',
                align='center', anchor='middle', wrap=False, fit=True, min_size=10, emph='yellow', name='txt:archtop')
        ty += 0.52 + 0.12
    weights = []
    for tier in tiers:
        n = len(tier.get('items') or []) or sum(len(g.get('items', [])) for g in tier.get('groups', []))
        weights.append(1.0 + (0.45 if tier.get('groups') else 0) + (0.35 if n > 8 else 0))
    rows = Box(ix0, ty, ix1 - ix0, area.b - ty).rows(len(tiers), gap=0.12, weights=weights)
    for i, (r, tier) in enumerate(zip(rows, tiers)):
        lab = tier.get('label', '')
        if len(plain(lab)) <= 6:
            A.vlabel(cv, r.x, r.y, label_w, r.h, lab, fill=tier.get('fill', 'primary'))
            lw = label_w
        else:
            lw = 1.35
            cv.rect(r.x, r.y, lw, r.h, fill=tier.get('fill', 'primary'), name='deco:tierlabel')
            cv.text(r.x + 0.08, r.y, lw - 0.16, r.h, lab, size=t.size_body, color='FFFFFF', role='title',
                    align='center', anchor='middle', fit=True, min_size=9, name='txt:tierlabel')
        body = Box(r.x + lw + 0.08, r.y, r.w - lw - 0.08, r.h)
        cv.rect(body.x, body.y, body.w, body.h, fill='panel_light', line='panel_line', line_w=0.75, radius=0.04,
                name='deco:tierbody')
        groups = tier.get('groups')
        if groups:
            gcells = body.inset(0.1, 0.08).cols(len(groups), gap=0.12,
                                                 weights=[max(1, len(g.get('items', []))) for g in groups])
            for gc, g in zip(gcells, groups):
                cv.rect(gc.x, gc.y, gc.w, gc.h, fill='FFFFFF', line='panel_line', line_w=0.5, radius=0.04,
                        name='deco:tiergroup')
                gh = 0.32
                cv.rect(gc.x, gc.y, gc.w, gh, fill='primary+78', radius=0.04, name='deco:tiergrouphead')
                cv.text(gc.x + 0.06, gc.y, gc.w - 0.12, gh, g.get('title', ''), size=t.size_small, color='primary_deep',
                        role='title', align='center', anchor='middle', wrap=False, fit=True, min_size=8,
                        name='txt:tiergroup')
                _chips(cv, Box(gc.x + 0.08, gc.y + gh + 0.06, gc.w - 0.16, gc.h - gh - 0.12), g.get('items', []),
                       fill='panel_light')
        else:
            _chips(cv, body.inset(0.12, 0.1), tier.get('items', []))
    for k, s in enumerate(ls):
        x = area.x + k * (sw + sg)
        _side_col(cv, Box(x, area.y, sw, area.h), s)
    for k, s in enumerate(rs):
        x = ix1 + sg + k * (sw + sg)
        _side_col(cv, Box(x, area.y, sw, area.h), s)
    return _done(cv, notes)


def _side_col(cv, b, s):
    cv.rect(b.x, b.y, b.w, b.h, fill='primary_bg', line='primary+40', line_w=1.0, radius=0.04, name='deco:sidecol')
    cv.rect(b.x, b.y, b.w, 0.08, fill='primary', name='deco:sidecoltop')
    cv.text(b.x, b.y + 0.15, b.w, b.h - 0.3, '\n'.join(list(plain(s.get('label', '')))), size=min(15, b.w * 72 * 0.4),
            color='primary_deep', role='title', align='center', anchor='middle', fit=True, min_size=9, ls=1.0, sa=0,
            name='txt:sidecol')


# =========================================================================== 本文 vs 对比
@layout
def versus(deck, title, ours, others, statement=None, conclusion=None, conclusion_style='yellow', num=None, en=None,
           source=None, notes=None, section=None):
    """本文方法 vs 对比方法: ours = highlighted card (deep header, badge, ✓ rows with values
    in the emphasis color, soft shadow); others = gray cards with the same rows; a VS badge between them.
    ours / others[i]: {'name', 'sub', 'badge', 'rows': [(label, value)], 'points': [...] (instead of rows)}.
    1–3 others. Keep the same row labels in the same order on every card so rows line up."""
    t = deck.theme
    cv, area = _frame(deck, title, statement=statement, conclusion=conclusion, conclusion_style=conclusion_style,
                      num=num, en=en, source=source, section=section)
    others = list(others)[:3]
    cells = area.cols(1 + len(others), gap=0.62 if len(others) == 1 else 0.42,
                      weights=[1.3] + [1.0] * len(others))
    nrows = max([len(ours.get('rows') or [])] + [len(o.get('rows') or []) for o in others])
    for k, (c, card) in enumerate(zip(cells, [ours] + others)):
        hi = k == 0
        hh = 0.86 if card.get('sub') else 0.66
        if hi:
            cv.rect(c.x, c.y, c.w, c.h, fill='FFFFFF', line='primary', line_w=1.5, radius=0.08, name='deco:vscard',
                    shadow={'color': 'primary_deep', 'alpha': 0.2, 'blur': 20, 'dist': 5})
            cv.rect(c.x, c.y, c.w, hh, grad=[(0, 'primary_deep', 1.0), (100, 'primary', 1.0)], grad_angle=0,
                    radius=0.08, name='deco:vshead')
            fg, sub_c = 'FFFFFF', 'FFFFFF'
        else:
            cv.rect(c.x, c.y + 0.12, c.w, c.h - 0.12, fill='FFFFFF', line='panel_line', line_w=0.75, radius=0.08,
                    name='deco:vscard')
            cv.rect(c.x, c.y + 0.12, c.w, hh - 0.12, fill='D5DAE3', radius=0.08, name='deco:vshead')
            fg, sub_c = '4A5262', '6B7489'
        ny = c.y + (0.06 if hi else 0.14)
        bw_ = (cv.width_of(plain(card['badge']), 11, role='title') + 0.5) if (hi and card.get('badge')) else 0
        cv.text(c.x + 0.2 + bw_, ny, c.w - 0.4 - 2 * bw_, 0.42, card.get('name', ''), size=t.size_body + (4 if hi else 2), color=fg,
                role='title', align='center', anchor='middle', wrap=False, fit=True, min_size=10, name='txt:vsname')
        if card.get('sub'):
            cv.text(c.x + 0.2, ny + 0.4, c.w - 0.4, 0.3, card['sub'], size=t.size_small, color=sub_c,
                    alpha=0.9 if hi else 1.0, role='medium', align='center', wrap=False, fit=True, min_size=8)
        if hi and card.get('badge'):
            bw = cv.width_of(plain(card['badge']), 11, role='title') + 0.36
            cv.rect(c.r - bw - 0.1, c.y - 0.16, bw, 0.32, fill='yellow', radius=0.16, name='deco:vsbadge',
                    shadow={'color': '000000', 'alpha': 0.15, 'blur': 6, 'dist': 2})
            cv.text(c.r - bw - 0.1, c.y - 0.16, bw, 0.32, card['badge'], size=11, color='primary_deep', role='title',
                    align='center', anchor='middle', wrap=False, fit=True, min_size=8, name='txt:vsbadge')
        body = Box(c.x + 0.22, c.y + hh + 0.14, c.w - 0.44, c.b - (c.y + hh + 0.14) - 0.16)
        rows = card.get('rows')
        if rows:
            rh = min(0.66, body.h / max(nrows, 1))
            oy = body.y + max(0.0, (body.h - rh * nrows) / 2)
            for i, (lab, val) in enumerate(rows):
                ry = oy + i * rh
                if i:
                    cv.line(body.x, ry, body.r, ry, 'panel_line', 0.75, dash='sysDash', name='deco:vsrule')
                ix = body.x
                if hi:
                    cv.icon('circle-check', body.x, ry + (rh - 0.24) / 2, 0.24, 'emph')
                    ix += 0.32
                lw_ = (body.r - ix) * 0.55
                cv.text(ix, ry, lw_, rh, lab, size=t.size_body - (1 if hi else 1.5), color='dark' if hi else '6B7489',
                        role='medium', anchor='middle', fit=True, min_size=9, name='txt:vslabel')
                cv.text(ix + lw_, ry, body.r - ix - lw_, rh, val, size=t.size_body + (1 if hi else -1),
                        color='emph' if hi else '6B7489', role='title' if hi else 'medium', bold=hi, align='right',
                        anchor='middle', fit=True, min_size=9, name='txt:vsvalue')
        elif card.get('points'):
            A.arrow_list(cv, body, card['points'], size=t.size_body - (0 if hi else 1),
                         color='dark' if hi else '6B7489', marker_color='primary' if hi else '9AA3B2')
    if others:
        gx = (cells[0].r + cells[1].x) / 2
        A.vs_badge(cv, gx, cells[0].cy, d=0.62 if len(others) == 1 else 0.54)
    return _done(cv, notes)


# =========================================================================== 技术路线矩阵
@layout
def process_matrix(deck, title, steps, cells, rows=None, phases=None, arrows=None, notes_row=None, statement=None,
                   conclusion=None, conclusion_style='navy', num=None, en=None, source=None, notes=None, section=None):
    """模块化递进图 / 技术路线矩阵: chevron header of steps whose color deepens left→right,
    optional phase brackets above (phases: [(label, first_col, last_col)]), optional row labels at the left
    (rows: [str]), grid of cells (cells[r][c] = str | {'title','text'} | None), optional dashed arrows between
    cells [(r1, c1, r2, c2)], optional notes row under the grid (notes_row: [str] one per step, or [(text, c0, c1)])."""
    t = deck.theme
    cv, area = _frame(deck, title, statement=statement, conclusion=conclusion, conclusion_style=conclusion_style,
                      num=num, en=en, source=source, section=section)
    nc = len(steps)
    nr = len(cells)
    lw = 1.25 if rows else 0.0
    gx = area.x + lw + (0.12 if rows else 0)
    gw = area.r - gx
    colw = gw / nc
    y = area.y
    if phases:
        for lab, c0, c1 in phases:
            A.hbracket(cv, gx + c0 * colw + 0.08, gx + (c1 + 1) * colw - 0.08, y + 0.2, lab)
        y += 0.46
    hh = 0.5
    cols_c = _tints(nc, lo=32)
    for c, (st, col) in enumerate(zip(steps, cols_c)):
        x = gx + c * colw
        cv.shape('homePlate' if c == 0 else 'chevron', x - (0 if c == 0 else 0.1), y, colw + (0.06 if c == 0 else 0.16),
                 hh, fill=col, adj={'adj': 32000}, name='deco:mxhead')
        cv.text(x + (0.12 if c == 0 else 0.22), y, colw - 0.4, hh, st, size=t.size_body, color='FFFFFF', role='title',
                align='center', anchor='middle', wrap=False, fit=True, min_size=9, name='txt:mxhead')
    y += hh + 0.1
    nh = 0.0
    if notes_row:
        nh = 0.72
    gb = Box(gx, y, gw, area.b - y - (nh + 0.12 if notes_row else 0))
    cv.rect(gb.x - 0.06, gb.y - 0.04, gb.w + 0.12, gb.h + 0.08, fill='panel_light', line='panel_line', line_w=0.5,
            radius=0.05, name='deco:mxbody')
    rh = gb.h / nr
    centers = {}
    for r in range(nr):
        ry = gb.y + r * rh
        if rows and r < len(rows):
            cv.rect(area.x, ry + 0.05, lw, rh - 0.1, fill='primary+78', radius=0.05, name='deco:mxrow')
            cv.text(area.x + 0.08, ry + 0.05, lw - 0.16, rh - 0.1, rows[r], size=t.size_body - 1, color='primary_deep',
                    role='title', align='center', anchor='middle', fit=True, min_size=9, name='txt:mxrow')
        for c in range(nc):
            cell = cells[r][c] if c < len(cells[r]) else None
            if not cell:
                continue
            b = Box(gx + c * colw + 0.08, ry + 0.07, colw - 0.16, rh - 0.14)
            cv.rect(b.x, b.y, b.w, b.h, fill='FFFFFF', line='panel_line', line_w=0.75, radius=0.05, name='deco:mxcell')
            centers[(r, c)] = b
            if isinstance(cell, str):
                cv.text(b.x + 0.08, b.y, b.w - 0.16, b.h, cell, size=t.size_small, color='dark', role='medium',
                        align='center', anchor='middle', fit=True, min_size=8, emph='emph', name='txt:mxcell')
            else:
                th_ = 0.34 if cell.get('text') else b.h
                cv.text(b.x + 0.08, b.y + 0.04, b.w - 0.16, th_, cell.get('title', ''), size=t.size_small + 0.5,
                        color='primary_deep', role='title', align='center', anchor='middle', wrap=False, fit=True,
                        min_size=8, name='txt:mxcelltitle')
                if cell.get('text'):
                    cv.text(b.x + 0.08, b.y + 0.38, b.w - 0.16, b.h - 0.42, cell['text'], size=t.size_small - 1,
                            color='dark', role='medium', align='center', anchor='top', fit=True, min_size=8,
                            emph='emph', name='txt:mxcelltext')
    for r1, c1, r2, c2 in (arrows or []):
        a, b = centers.get((r1, c1)), centers.get((r2, c2))
        if not a or not b:
            continue
        if c1 == c2:
            p1, p2 = (a.cx, a.b if r2 > r1 else a.y), (b.cx, b.y if r2 > r1 else b.b)
        else:
            p1, p2 = (a.r if c2 > c1 else a.x, a.cy), (b.x if c2 > c1 else b.r, b.cy)
        cv.line(p1[0], p1[1], p2[0], p2[1], 'primary', 1.25, dash='sysDash', tail='triangle', name='deco:mxarrow')
    if notes_row:
        ny = gb.b + 0.12
        items = notes_row if (notes_row and isinstance(notes_row[0], (tuple, list))) else \
            [(txt, i, i) for i, txt in enumerate(notes_row)]
        for txt, c0, c1 in items:
            b = Box(gx + c0 * colw + 0.04, ny, (c1 - c0 + 1) * colw - 0.08, nh)
            cv.rect(b.x, b.y, b.w, b.h, fill='primary_bg', line='primary+60', line_w=0.75, radius=0.05,
                    name='deco:mxnote')
            cv.text(b.x + 0.1, b.y, b.w - 0.2, b.h, txt, size=t.size_small - 0.5, color='primary_deep', role='medium',
                    align='center', anchor='middle', fit=True, min_size=8, emph='emph', name='txt:mxnote')
        if rows:
            A.vlabel(cv, area.x, ny, lw, nh, '要点', fill='primary')
    return _done(cv, notes)


# =========================================================================== 闭环
@layout
def cycle(deck, title, steps, center=None, center_sub=None, icon=None, statement=None, conclusion=None,
          conclusion_style='navy', num=None, en=None, source=None, notes=None, section=None, colors=None):
    """闭环 / 循环: a ring of N arrow segments (labels along the ring) with a centre
    disc, and numbered detail blocks left and right of it in ring order. steps (3–6): [{'label': short ring text
    (default = title[:4]), 'title', 'text' | 'points'}]."""
    t = deck.theme
    cv, area = _frame(deck, title, statement=statement, conclusion=conclusion, conclusion_style=conclusion_style,
                      num=num, en=en, source=source, section=section)
    n = len(steps)
    r = min(area.h / 2 - 0.08, 1.9)
    cx, cy = area.cx, area.cy
    segs = A.cycle(cv, cx, cy, r, [s.get('label') or plain(s.get('title', ''))[:4] for s in steps], center=center,
                   center_sub=center_sub, icon=icon, colors=colors, start_deg=-180.0 / n if n % 4 == 2 else 0.0)
    right = [(i, a, c) for i, (a, c) in enumerate(segs) if 0 <= a < 180]
    left = [(i, a, c) for i, (a, c) in enumerate(segs) if a >= 180]
    while abs(len(right) - len(left)) > 1:          # balance the two columns
        if len(right) > len(left):
            left.append(right.pop())
        else:
            right.insert(0, left.pop(0))
    right.sort(key=lambda x: x[1])                  # top → bottom on the right: angle ascending
    left.sort(key=lambda x: -x[1])                  # top → bottom on the left: angle descending
    colw = cx - r - 0.5 - area.x
    for side, items in (('L', left), ('R', right)):
        if not items:
            continue
        x = area.x if side == 'L' else cx + r + 0.5
        bxs = Box(x, area.y, colw, area.h).rows(len(items), gap=0.16)
        for b, (i, ang, col) in zip(bxs, items):
            st = steps[i]
            cv.rect(b.x, b.y, b.w, b.h, fill='FFFFFF', line='panel_line', line_w=0.75, radius=0.06, name='deco:cyblk',
                    shadow={'color': 'primary_deep', 'alpha': 0.08, 'blur': 10, 'dist': 2})
            d = 0.42
            cv.circle(b.x + 0.16 + d / 2, b.y + 0.14 + d / 2, d / 2, fill=col, name='deco:cynum')
            cv.text(b.x + 0.16, b.y + 0.14, d, d, f'{i + 1:02d}', size=12, color='FFFFFF', role='number', bold=True,
                    align='center', anchor='middle', wrap=False, fit=False, name='txt:cynum')
            cv.text(b.x + 0.7, b.y + 0.12, b.w - 0.85, 0.46, st.get('title', ''), size=t.size_body + 1,
                    color='primary_deep', role='title', anchor='middle', wrap=False, fit=True, min_size=10,
                    name='txt:cytitle')
            tb = Box(b.x + 0.18, b.y + 0.66, b.w - 0.34, b.h - 0.74)
            if st.get('points'):
                A.arrow_list(cv, tb, st['points'], size=t.size_body - 1.5)
            elif st.get('text'):
                cv.text(tb.x, tb.y, tb.w, tb.h, st['text'], size=t.size_body - 1.5, color='dark', role='medium',
                        fit=True, min_size=9, emph='emph', name='txt:cytext')
            ox, oy = D._pt(cx, cy, r + 0.12, ang)
            ex = b.r if side == 'L' else b.x
            cv.line(ex, b.cy, ox, oy, col, 1.0, dash='sysDash', name='deco:cylead')
    return _done(cv, notes)


# =========================================================================== 横向色带 (国内外研究现状)
@layout
def bands(deck, title, bands, statement=None, conclusion=None, conclusion_style='navy', word_w=2.0, num=None,
          en=None, source=None, notes=None, section=None):
    """横向色带 (国内外研究现状): 2–3 full-width bands stacked vertically; each = a big faded serif word at the
    left ('国外' / '国内') with its label, then 1–3 columns of points. The first band is deep (white text), the next
    pale, alternating. bands: [{'word': '国外', 'label': '国外研究现状', 'cols': [{'title', 'points'}] |
    'points': [...]}]. Finish with a conclusion such as '现有研究不足：…'."""
    t = deck.theme
    cv, area = _frame(deck, title, statement=statement, conclusion=conclusion, conclusion_style=conclusion_style,
                      num=num, en=en, source=source, section=section)
    rows = area.rows(len(bands), gap=0.16)
    for i, (b, bd) in enumerate(zip(rows, bands)):
        deep = i % 2 == 0
        if deep:
            cv.rect(b.x, b.y, b.w, b.h, grad=[(0, 'primary_deep', 1.0), (100, 'primary', 1.0)], grad_angle=0,
                    radius=0.06, name='deco:band')
        else:
            cv.rect(b.x, b.y, b.w, b.h, fill='panel', line='panel_line', line_w=0.75, radius=0.06, name='deco:band')
        fg = 'FFFFFF' if deep else 'dark'
        word = bd.get('word', '')
        ws = min(66, b.h * 72 * 0.5, (word_w - 0.2) * 72 / max(1, len(plain(word))) * 0.8)
        cv.text(b.x + 0.15, b.y + 0.05, word_w - 0.2, b.h * 0.66, word, size=ws, color='FFFFFF' if deep else 'primary',
                role='serif', bold=True, align='center', anchor='middle', wrap=False, fit=False,
                alpha=0.32 if deep else 0.22, name='txt:bandword')
        if bd.get('label'):
            cv.text(b.x + 0.15, b.y + b.h * 0.64, word_w - 0.2, b.h * 0.3, bd['label'], size=t.size_body,
                    color='FFFFFF' if deep else 'primary_deep', role='title', align='center', anchor='top',
                    wrap=False, fit=True, min_size=9, name='txt:bandlabel')
        cv.line(b.x + word_w, b.y + 0.2, b.x + word_w, b.b - 0.2, 'FFFFFF' if deep else 'panel_line', 1.0,
                alpha=0.5 if deep else 1.0, name='deco:bandsep')
        cb = Box(b.x + word_w + 0.25, b.y + 0.14, b.w - word_w - 0.45, b.h - 0.28)
        cols = bd.get('cols') or [{'points': bd.get('points', [])}]
        for c, col in zip(cb.cols(len(cols), gap=0.3), cols):
            y = c.y
            if col.get('title'):
                cv.text(c.x, y, c.w, 0.36, col['title'], size=t.size_body + 0.5, color='yellow' if deep else 'primary_deep',
                        role='title', anchor='middle', wrap=False, fit=True, min_size=10, name='txt:bandcoltitle')
                y += 0.4
            A.arrow_list(cv, Box(c.x, y, c.w, c.b - y), col.get('points', []), size=t.size_body - 1, color=fg,
                         marker_color='yellow' if deep else 'primary')
    return _done(cv, notes)


# =========================================================================== 层级树
@layout
def tree(deck, title, root, children, root_sub=None, statement=None, conclusion=None, conclusion_style='navy',
         num=None, en=None, source=None, notes=None, section=None):
    """层级树 (课题分解 / 项目组织架构): root (deep) → level-2 nodes (primary) → stacked white
    leaves hanging from a spine under each node. children: [{'name', 'sub', 'children': [str | {'name','sub'}]}]
    (2–6 nodes, ≤ 5 leaves each). Levels by color depth; connectors thin and light."""
    t = deck.theme
    cv, area = _frame(deck, title, statement=statement, conclusion=conclusion, conclusion_style=conclusion_style,
                      num=num, en=en, source=source, section=section)
    rw = min(4.6, area.w * 0.42)
    rh = 0.66 if not root_sub else 0.84
    rb = Box(area.cx - rw / 2, area.y, rw, rh)
    cv.rect(rb.x, rb.y, rb.w, rb.h, grad=[(0, 'primary_deep', 1.0), (100, 'primary', 1.0)], grad_angle=0,
            radius=0.08, name='deco:treeroot', shadow={'color': 'primary_deep', 'alpha': 0.18, 'blur': 12, 'dist': 3})
    cv.text(rb.x + 0.2, rb.y + 0.04, rb.w - 0.4, 0.5 if root_sub else rb.h - 0.08, root, size=t.size_body + 3,
            color='FFFFFF', role='title', align='center', anchor='middle', wrap=False, fit=True, min_size=10,
            name='txt:treeroot')
    if root_sub:
        cv.text(rb.x + 0.2, rb.y + 0.5, rb.w - 0.4, 0.3, root_sub, size=t.size_small, color='FFFFFF', alpha=0.9,
                role='medium', align='center', wrap=False, fit=True, min_size=8)
    n2 = len(children)
    has_sub = any(c.get('sub') for c in children)
    h2 = 0.84 if has_sub else 0.6
    y2 = rb.b + 0.42
    cells = Box(area.x, y2, area.w, h2).cols(n2, gap=0.2)
    ym = (rb.b + y2) / 2
    lc = 'primary+35'
    cv.line(rb.cx, rb.b, rb.cx, ym, lc, 1.5, name='deco:treeline')
    if n2 > 1:
        cv.line(cells[0].cx, ym, cells[-1].cx, ym, lc, 1.5, name='deco:treeline')
    for c, ch in zip(cells, children):
        cv.line(c.cx, ym, c.cx, c.y, lc, 1.5, name='deco:treeline')
        cv.rect(c.x, c.y, c.w, c.h, fill='primary', radius=0.06, name='deco:treenode')
        cv.text(c.x + 0.08, c.y + 0.03, c.w - 0.16, 0.5 if ch.get('sub') else c.h - 0.06, ch.get('name', ''),
                size=t.size_body, color='FFFFFF', role='title', align='center', anchor='middle', fit=True, min_size=9,
                name='txt:treenode')
        if ch.get('sub'):
            cv.text(c.x + 0.08, c.y + 0.5, c.w - 0.16, 0.3, ch['sub'], size=t.size_small - 1, color='FFFFFF',
                    alpha=0.9, role='medium', align='center', wrap=False, fit=True, min_size=8)
        leaves = ch.get('children') or []
        if not leaves:
            continue
        y3 = c.b + 0.2
        avail = area.b - y3
        lh = min(0.78, (avail - 0.12 * (len(leaves) - 1)) / len(leaves))
        sx = c.x + 0.16
        last_cy = None
        for k, lf in enumerate(leaves):
            ly = y3 + k * (lh + 0.12)
            lb = Box(c.x + 0.36, ly, c.w - 0.36, lh)
            name_ = lf if isinstance(lf, str) else lf.get('name', '')
            sub_ = None if isinstance(lf, str) else lf.get('sub')
            cv.rect(lb.x, lb.y, lb.w, lb.h, fill='FFFFFF', line='panel_line', line_w=0.75, radius=0.05,
                    name='deco:treeleaf')
            cv.rect(lb.x, lb.y, 0.06, lb.h, fill='primary+30', name='deco:treeleafbar')
            if sub_:
                cv.text(lb.x + 0.14, lb.y + 0.02, lb.w - 0.22, lb.h * 0.52, name_, size=t.size_small + 0.5,
                        color='primary_deep', role='title', anchor='bottom', fit=True, min_size=8, name='txt:treeleaf')
                cv.text(lb.x + 0.14, lb.y + lb.h * 0.54, lb.w - 0.22, lb.h * 0.44, sub_, size=t.size_small - 1.5,
                        color='muted', role='medium', anchor='top', fit=True, min_size=7.5, name='txt:treeleafsub')
            else:
                cv.text(lb.x + 0.14, lb.y, lb.w - 0.22, lb.h, name_, size=t.size_small + 0.5, color='dark',
                        role='medium', anchor='middle', fit=True, min_size=8, emph='emph', name='txt:treeleaf')
            cv.line(sx, lb.cy, lb.x, lb.cy, lc, 1.0, name='deco:treetick')
            last_cy = lb.cy
        cv.line(sx, c.b, sx, last_cy, lc, 1.0, name='deco:treespine')
    return _done(cv, notes)
