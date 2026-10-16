"""'科研答辩风' components — the NSFC / 国省科技奖 / 毕业答辩 visual language.

Distilled from public defense decks (学术风参考图, online NSFC/defense template previews):
  * title bar: section number + title in navy bold, slanted/vertical marks at left, logo right, navy rule under it,
    navy rule at the bottom with page number
  * statement bar: light panel with navy left bar, bold text, KEY PHRASES IN RED ([[...]] markup)
  * navy ribbon headers on light panels, ➢ (Wingdings 'Ø') bullets, chevron / pill / red tags, vertical labels
  * conclusion bar: full-width navy bar, white or yellow bold text (serif for the strongest statements)
  * big red numbers for achievements, block arrows with gradient, gradient axis with nodes
Dense by design: body 14-16pt, content fills the page.
"""
from __future__ import annotations

import math

from . import oxml as X
from .canvas import Box, plain

WING_ARROW = 'Ø'  # Wingdings: ➢


# ---------------------------------------------------------------- page chrome
def background(cv, kind='content'):
    """Page background. Decoration from the skin ('deco'): corner (faint triangle, default) | arcs (亮蓝白 corner
    arcs) | dots (重点研发 tech dot field) | none."""
    t = cv.t
    W, H = cv.W, cv.H
    deco = (t.extras or {}).get('deco', 'corner')
    cv.rect(0, 0, W, H, fill='FFFFFF', name='bg:base')
    if kind != 'content':
        cv.rect(0, 0, W, H, grad=[(0, 'panel', 0.0), (100, 'panel', 1.0)], grad_angle=90, name='bg:fade')
        return
    cv.rect(0, H * 0.55, W, H * 0.45, grad=[(0, 'panel', 0.0), (100, 'panel', 0.9 if deco != 'none' else 0.5)],
            grad_angle=90, name='bg:fade')
    if deco == 'corner':
        cv.shape('rtTriangle', W - 2.6, H - 1.6, 2.6, 1.6, grad=[(0, 'primary', 0.0), (100, 'primary', 0.10)],
                 grad_angle=45, name='bg:corner', rot=0)
    elif deco == 'arcs':
        cv.shape('blockArc', W - 1.15, H - 1.15, 2.3, 2.3, fill='primary', alpha=0.85, adj={'adj1': 10800000,
                 'adj2': 16200000, 'adj3': 7000}, name='bg:arc1')
        cv.shape('blockArc', W - 0.85, H - 0.85, 1.7, 1.7, fill='secondary', alpha=0.4, adj={'adj1': 10800000,
                 'adj2': 16200000, 'adj3': 6000}, name='bg:arc2')
    elif deco == 'dots':
        from . import images as IMG
        p = IMG.dot_map(t.c('primary'), alpha=0.18, size=(900, 500), step=12, seed=4)
        cv.image(p, W - 4.6, H - 2.55, 4.6, 2.55, fit='stretch', name='bg:dots', alpha=0.85)


def mini_nav_width(cv, labels, size=10.5):
    """Total width of a mini_nav chip row (to centre it, e.g. nav='bottom')."""
    return sum(cv.width_of(lb, size, role='title') + 0.3 for lb in labels) + 0.05 * (len(labels) - 1)


def mini_nav(cv, labels, current, right, y, h=0.3, size=10.5, dark=False):
    """Compact chapter progress chips drawn right-aligned at `right` (past = pale, current = solid, future = gray).
    Lighter alternative to a full navigation band (学术课件用导航栏表达讲课进度). dark=True for chips placed on a
    colored title band. Returns the left x used."""
    pad, gap = 0.15, 0.05
    ws = [cv.width_of(lb, size, role='title') + 2 * pad for lb in labels]
    x = right - sum(ws) - gap * (len(ws) - 1)
    x_left = x
    for i, (lb, w) in enumerate(zip(labels, ws)):
        if dark:
            fill, color = (('FFFFFF', 'primary_deep') if i == current else
                           (('FFFFFF', 'FFFFFF') if i < current else ('FFFFFF', 'FFFFFF')))
            cv.rect(x, y, w, h, fill=fill, radius=0.04, alpha=1.0 if i == current else (0.28 if i < current else 0.12),
                    name=f'deco:mnav{i}')
            cv.text(x, y, w, h, lb, size=size, color=color, role='title' if i == current else 'medium',
                    align='center', anchor='middle', wrap=False, fit=False, name=f'txt:mnav{i}')
            x += w + gap
            continue
        fill, color = (('primary', 'FFFFFF') if i == current else
                       (('primary+82', 'primary') if i < current else ('panel', 'muted')))
        cv.rect(x, y, w, h, fill=fill, radius=0.04, name=f'deco:mnav{i}')
        cv.text(x, y, w, h, lb, size=size, color=color, role='title' if i == current else 'medium', align='center',
                anchor='middle', wrap=False, fit=False, name=f'txt:mnav{i}')
        x += w + gap
    return x_left


def skin(cv, key, default=None):
    """Value of a style-family ('skin') setting stored in theme.extras (see theme.SKINS)."""
    return (cv.t.extras or {}).get(key, default)


TITLE_STYLES = ('slant', 'bars', 'underline', 'band', 'badge', 'center', 'tab', 'lightband', 'vband', 'photoband',
                'numbox', 'square', 'thin', 'halfdisc', 'slash')
DARK_TITLES = ('band', 'badge', 'vband', 'photoband')


def _title_w(cv, title, size, tx, right, en):
    """Width of the title text box: the full row, or just the title when an English label follows it (so the
    two boxes never overlap)."""
    if not en:
        return right - tx
    return min(right - tx, cv.width_of(title, size, role='title') * 1.05 + 0.15)


def _en_after(cv, tx, y0, th, title, size, right, en):
    if not en:
        return
    ew = cv.width_of(title, size, role='title')
    cv.text(tx + ew + 0.2, y0 + 0.22, max(0.5, right - tx - ew - 0.2), 0.3, en.upper(), size=10, color='muted',
            wrap=False, fit=True, min_size=7, spacing=0.4, anchor='middle')


def title_bar(cv, title, num=None, style=None, logo=True, en=None, nav=None):
    """Draw the page title bar. style (default from the skin): slant 像素答辩 · bars 树叶答辩 · underline 百宝箱 ·
    band 亮蓝白通栏 · badge 深蓝白通栏+圆形序号 · center 居中章节标题 · tab 色块标签 · lightband 浅色底带 ·
    vband 科技进步奖亮蓝通栏+竖线 · photoband 重点研发深蓝通栏+右端图带 · numbox 长江学者编号方块 · square 重点实验室方标 ·
    thin 万人计划细线 · halfdisc 申报书半圆标 · slash 科学技术奖斜杠.
    nav=(labels, current) adds compact chapter chips at the right. Returns the y (inches) where content may start."""
    t = cv.t
    style = style or t.extras.get('title_bar', 'slant')
    W = cv.W
    mx = 0.42
    y0 = 0.28
    th = 0.62
    size = t.size_title
    right = W - mx
    on_dark = style in DARK_TITLES
    lg = cv.deck.meta.get('logo') if logo else None
    if lg:
        from . import components as K
        K.logo(cv, lg, x=None, y=y0 + 0.08, h=0.44, align='right')
        right -= 1.9
    if nav:
        ny = (_band_h(style) - 0.3) / 2 if on_dark else y0 + (th - 0.3) / 2 + 0.02
        if on_dark:   # draw the band first so the chips sit on top of it
            _title_band(cv, style)
        right = mini_nav(cv, nav[0], nav[1], right, ny, dark=on_dark) - 0.3
    num_txt = (num + '  ') if num else ''
    if on_dark:
        if not nav:
            _title_band(cv, style)
        bh = _band_h(style)
        ty = (bh - 0.62) / 2
        tx = mx + 0.12
        if style == 'vband':                      # white vertical bar before the number (科技进步奖)
            cv.rect(tx, bh * 0.3, 0.06, bh * 0.4, fill='FFFFFF', name='deco:vbar')
            tx += 0.3
        if num and style == 'badge':
            d = 0.5
            nw = max(d, cv.width_of(num, size * 0.62, role='number', bold=True) + 0.2)
            cv.rect(tx, 0.14, nw, d, fill='FFFFFF', radius=d / 2, name='deco:badge')
            cv.text(tx, 0.14, nw, d, num, size=size * 0.62, color='primary_deep', role='number', bold=True,
                    align='center', anchor='middle', wrap=False, fit=False, name='txt:titlenum')
            tx += nw + 0.2
        elif num:
            nw = cv.width_of(num, size, role='number', bold=True) * 1.12 + 0.06
            cv.text(tx, ty, nw, 0.62, num, size=size, color='FFFFFF', role='number', bold=True, anchor='middle',
                    wrap=False, fit=False, alpha=0.95, name='txt:titlenum')
            tx += nw + 0.2
        cv.text(tx, ty, right - tx, 0.62, title, size=size, color='FFFFFF', role='title', anchor='middle',
                wrap=False, fit=True, min_size=18, name='txt:title')
        return bh + 0.22
    if style == 'center':
        txt = num_txt + title
        tw = min(right - mx - 1.4, cv.width_of(txt, size, role='title') + 0.2)
        cx = (mx + right) / 2 if not nav else (mx + right) / 2
        cv.text(cx - tw / 2, y0, tw, th, txt, size=size, color='primary_deep', role='title', align='center',
                anchor='middle', wrap=False, fit=True, min_size=18, name='txt:title')
        ly = y0 + th / 2
        for side in (-1, 1):
            x_in = cx + side * (tw / 2 + 0.15)
            x_out = cx + side * (tw / 2 + 1.25)
            cv.line(min(x_in, x_out), ly, max(x_in, x_out), ly, 'primary', 1.5,
                    grad=[('primary', 1.0), ('primary', 0.0)] if side > 0 else [('primary', 0.0), ('primary', 1.0)],
                    name='deco:centerline')
            cv.shape('diamond', x_in - 0.05 if side > 0 else x_in - 0.05, ly - 0.05, 0.1, 0.1, fill='emph',
                     name='deco:centerdot')
        cv.line(mx, y0 + th + 0.1, W - mx, y0 + th + 0.1, 'primary+70', 0.75, name='deco:titlerule')
        return y0 + th + 0.3
    if style == 'tab':
        txt = num_txt + title
        tw = min(right - mx - 0.5, cv.width_of(txt, size * 0.92, role='title') + 0.75)
        cv.shape('homePlate', mx, y0 + 0.02, tw, th - 0.04, fill='primary', adj={'adj': 32000}, name='deco:titletab')
        cv.text(mx + 0.2, y0 + 0.02, tw - 0.45, th - 0.04, txt, size=size * 0.92, color='FFFFFF', role='title',
                anchor='middle', wrap=False, fit=True, min_size=16, name='txt:title')
        cv.line(mx, y0 + th - 0.02, W - mx, y0 + th - 0.02, 'primary', 2.0, name='deco:titlerule')
        return y0 + th + 0.24
    if style == 'lightband':
        cv.rect(0, 0, W, 0.98, grad=[(0, 'primary_bg', 1.0), (100, 'FFFFFF', 1.0)], grad_angle=0,
                name='deco:titleband')
        cv.rect(mx, y0 + 0.13, 0.1, th - 0.26, fill='primary', name='deco:mark1')
        tx = mx + 0.26
        cv.text(tx, y0, right - tx, th, num_txt + title, size=size, color='primary_deep', role='title',
                anchor='middle', wrap=False, fit=True, min_size=18, name='txt:title')
        cv.line(0, 0.98, W, 0.98, 'primary', 1.5, grad=[('primary', 1.0), ('primary', 0.15)], name='deco:titlerule')
        return 1.16
    if style == 'numbox':                      # 长江学者: navy number box + ▸ + title, box sits on the rule
        nw = max(0.82, cv.width_of(num or '', size * 0.95, role='number', bold=True) + 0.32) if num else 0
        tx = mx
        if num:
            cv.rect(mx, y0, nw, th + 0.02, fill='primary_deep', name='deco:numbox')
            cv.text(mx, y0, nw, th, num, size=size * 0.95, color='FFFFFF', role='number', bold=True, align='center',
                    anchor='middle', wrap=False, fit=False, name='txt:titlenum')
            tx = mx + nw + 0.08
            cv.shape('triangle', tx, y0 + th / 2 - 0.08, 0.13, 0.16, fill='primary', rot=90, name='deco:numtri')
            tx += 0.24
        cv.text(tx, y0, _title_w(cv, title, size, tx, right, en), th, title, size=size, color='primary_deep',
                role='title', anchor='middle', wrap=False, fit=True, min_size=18, name='txt:title')
        _en_after(cv, tx, y0, th, title, size, right, en)
        cv.line(mx, y0 + th + 0.02, W - mx, y0 + th + 0.02, 'primary_deep', 2.25, name='deco:titlerule')
        return y0 + th + 0.26
    if style in ('square', 'halfdisc', 'slash', 'thin'):
        tx = mx
        if style == 'square':                  # 重点实验室: two-tone square icon
            cv.rect(mx + 0.13, y0 + 0.27, 0.2, 0.2, fill='primary+62', name='deco:sq2')
            cv.rect(mx, y0 + 0.15, 0.24, 0.24, fill='primary', name='deco:sq1')
            tx = mx + 0.5
        elif style == 'halfdisc':              # 申报书: navy disc + light disc
            cv.circle(mx + 0.21, y0 + th / 2 - 0.02, 0.21, fill='primary_deep', name='deco:disc1')
            cv.circle(mx + 0.33, y0 + th / 2 + 0.1, 0.13, fill='primary+60', name='deco:disc2')
            tx = mx + 0.62
        elif style == 'slash':                 # 科学技术奖: two thin slashes
            for k, (dx, a_) in enumerate(((0.0, 1.0), (0.12, 0.55))):
                cv.line(mx + 0.06 + dx, y0 + th - 0.04, mx + 0.26 + dx, y0 + 0.04, 'primary', 2.0, alpha=a_,
                        name=f'deco:slash{k}')
            tx = mx + 0.56
        if num:
            nw = cv.width_of(num, size, role='number', bold=True) * 1.12 + 0.06
            cv.text(tx, y0, nw, th, num, size=size, color='primary' if style != 'thin' else 'primary_deep',
                    role='number', bold=True, anchor='middle', wrap=False, fit=False, name='txt:titlenum')
            tx += nw + 0.18
        cv.text(tx, y0, _title_w(cv, title, size, tx, right, en), th, title, size=size,
                color='primary_deep' if style != 'thin' else 'primary', role='title', anchor='middle', wrap=False,
                fit=True, min_size=18, name='txt:title')
        _en_after(cv, tx, y0, th, title, size, right, en)
        ly = y0 + th + 0.08
        if style == 'halfdisc':
            tw = min(W - mx - tx, cv.width_of(title, size, role='title') + 0.3)
            cv.line(mx, ly, W - mx, ly, 'primary+65', 1.0, name='deco:titlerule')
            cv.line(mx, ly, tx + tw, ly, 'primary_deep', 3.0, name='deco:titlerule2')
        else:
            cv.line(mx, ly, W - mx, ly, 'primary' if style != 'slash' else 'primary', 2.0 if style != 'slash' else 1.25,
                    name='deco:titlerule')
        return ly + 0.22
    if style == 'underline':
        cv.text(mx + 0.05, y0, right - mx, th, num_txt + title, size=size, color='primary_deep', role='title',
                anchor='middle', wrap=False, fit=True, min_size=18, name='txt:title')
        cv.line(mx, y0 + th + 0.08, W - mx, y0 + th + 0.08, 'primary_deep', 2.75,
                grad=[('primary_deep', 1.0), ('primary', 0.15)], name='deco:titlerule')
        cv.line(mx, y0 + th + 0.15, W - mx, y0 + th + 0.15, 'primary+60', 0.75, name='deco:titlerule2')
        return y0 + th + 0.32
    # marks
    if style == 'bars':          # 树叶答辩: thick block + thin bar, double rule
        cv.rect(mx, y0 + 0.07, 0.17, 0.48, fill='primary_deep', name='deco:mark1')
        cv.rect(mx + 0.23, y0 + 0.07, 0.05, 0.48, fill='primary_deep', name='deco:mark2')
        tx = mx + 0.42
    else:  # slant
        cv.shape('parallelogram', mx - 0.05, y0 + 0.02, 0.26, 0.58, fill='primary', adj={'adj': 45000},
                 name='deco:mark1')
        cv.shape('parallelogram', mx + 0.18, y0 + 0.02, 0.14, 0.58, fill='primary+55', adj={'adj': 80000},
                 name='deco:mark2')
        tx = mx + 0.48
    if num:
        nw = cv.width_of(num, size, role='number', bold=True) * 1.12 + 0.04
        cv.text(tx, y0, nw + 0.06, th, num, size=size, color='primary_deep', role='number', bold=True,
                anchor='middle', wrap=False, fit=False, name='txt:titlenum')
        tx += nw + 0.14
        if style == 'slant':
            cv.line(tx, y0 + 0.16, tx, y0 + th - 0.12, 'primary+40', 1.5)
            tx += 0.16
    cv.text(tx, y0, _title_w(cv, title, size, tx, right, en), th, title, size=size, color='primary_deep',
            role='title', anchor='middle', wrap=False, fit=True, min_size=18, name='txt:title')
    if en:
        ew = cv.width_of(title, size, role='title')
        cv.text(tx + ew + 0.2, y0 + 0.22, max(0.5, right - tx - ew - 0.2), 0.3, en.upper(), size=10, color='muted',
                wrap=False, fit=True, min_size=7, spacing=0.4, anchor='middle')
    ly = y0 + th + 0.1
    if style == 'bars':
        cv.line(mx, ly, W - mx, ly, 'primary_deep', 2.25, name='deco:titlerule')
        cv.line(mx, ly + 0.07, W - mx, ly + 0.07, 'primary+55', 0.75, name='deco:titlerule2')
        return ly + 0.26
    cv.line(mx, ly, W - mx, ly, 'primary', 2.5, name='deco:titlerule')
    return ly + 0.2


def _band_h(style):
    return {'photoband': 0.82}.get(style, 0.78)


def _title_band(cv, style):
    """Full-width title band: band (亮蓝白, bright gradient + light sweep) · badge (深蓝白) · vband (科技进步奖, royal blue)
    · photoband (重点研发, deep blue with a faded engineering skyline at the right end)."""
    W = cv.W
    if style == 'vband':
        cv.rect(0, 0, W, 0.78, grad=[(0, 'primary', 1.0), (100, 'primary+12', 1.0)], grad_angle=0,
                name='deco:titleband')
        cv.rect(0, 0.78, W, 0.03, fill='primary-25', alpha=0.6, name='deco:bandedge')
        return
    if style == 'photoband':
        from . import images as IMG
        cv.rect(0, 0, W, 0.82, grad=[(0, 'primary_deep', 1.0), (100, 'primary', 1.0)], grad_angle=0,
                name='deco:titleband')
        img = (cv.t.extras or {}).get('band_image')
        if img:
            cv.image(IMG.fade(img, side='left', start=0.0, end=0.75), W * 0.62, 0, W * 0.38, 0.82, fit='cover',
                     alpha=0.35, name='deco:bandimg')
        else:
            cv.image(IMG.skyline('FFFFFF', size=(1400, 240), alpha=0.32), W * 0.55, 0.06, W * 0.45, 0.76,
                     fit='stretch', name='deco:bandimg')
        return
    if style == 'band':
        cv.rect(0, 0, W, 0.78, grad=[(0, 'primary', 1.0), (100, 'secondary', 1.0)], grad_angle=0,
                name='deco:titleband')
        cv.shape('parallelogram', W * 0.62, 0, W * 0.2, 0.78, grad=[(0, 'FFFFFF', 0.0), (100, 'FFFFFF', 0.16)],
                 grad_angle=0, adj={'adj': 40000}, name='deco:bandsweep')
    else:
        cv.rect(0, 0, W, 0.78, grad=[(0, 'primary_deep', 1.0), (100, 'primary', 1.0)], grad_angle=0,
                name='deco:titleband')
        cv.rect(0, 0.78, W, 0.05, fill='secondary', alpha=0.8, name='deco:bandedge')


def bottom_rule(cv, page=None, style=None):
    """Page footer. style (default from the skin): rule (navy line + page no.) | band (thin navy strip with the
    page number in white) | none (page number only)."""
    W, H = cv.W, cv.H
    style = style or (cv.t.extras or {}).get('bottom', 'rule')
    if style == 'band':
        cv.rect(0, H - 0.2, W, 0.2, grad=[(0, 'primary_deep', 1.0), (100, 'primary', 1.0)], grad_angle=0,
                name='deco:bottomband')
        if page is not None:
            cv.text(W - 1.0, H - 0.2, 0.62, 0.2, str(page), size=9.5, color='FFFFFF', role='number', bold=True,
                    align='right', anchor='middle', wrap=False, fit=False, name='deco:pageno')
        return
    y = H - 0.26
    if style != 'none':
        cv.line(0.42, y, W - 0.42, y, 'primary', 2.5, name='deco:bottomrule')
    if page is not None:
        cv.text(W - 1.0, y - 0.27, 0.58, 0.25, str(page), size=11, color='primary_deep', role='number', bold=True,
                align='right', wrap=False, fit=False, name='deco:pageno')


# ---------------------------------------------------------------- text blocks
def statement(cv, x, y, w, text, style=None, label=None, size=None, color='dark', h=None, align='left',
              label_w=1.6):
    """Lead statement (the page's key sentence). [[x]] -> red emphasis. Returns height used.
    style (default from the skin, else 'bar'): bar (light box + navy left bar) | label (navy arrow-label e.g. '核心阐述'
    + box) | centered (▪▪▪ text ▪▪▪) | pink (light pink box, red text) | plain | box (white box, thin navy border —
    重点研发/重点实验室) | key (◆ red key phrase ▶ navy text on a pale band — 科学技术奖; the key phrase is `label`,
    or the text before the first '：' / '，')."""
    t = cv.t
    size = size or t.size_body + 1
    style = style or (t.extras or {}).get('statement', 'bar')
    if style == 'key':
        key, rest = label, text
        if not key:
            for sep in ('：', ':', '，'):
                if sep in plain(text)[:24]:
                    key, rest = text.split(sep, 1)
                    break
        x0 = x + 0.2
        hh = h or max(size / 72 * 2.0, cv.measure(rest, w - 0.6 - (cv.width_of(plain(key), size, role='title')
                                                                     + 0.75 if key else 0), size, role='title') + 0.16)
        cv.rect(x, y, w, hh, grad=[(0, 'primary_bg', 1.0), (100, 'primary_bg', 0.45)], grad_angle=0,
                name='deco:stmtbg')
        cv.shape('diamond', x0, y + hh / 2 - 0.07, 0.14, 0.14, fill='emph', name='deco:keydiamond')
        x0 += 0.3
        if key:
            kw = min(w * 0.5, cv.width_of(plain(key), size, role='title') + 0.08)
            cv.text(x0, y, kw, hh, key, size=size, color='emph', role='title', anchor='middle', wrap=False, fit=True,
                    min_size=11, name='txt:stmtkey')
            x0 += kw + 0.1
            cv.shape('chevron', x0, y + hh / 2 - 0.1, 0.13, 0.2, fill='primary+20', adj={'adj': 60000},
                     name='deco:keychev')
            x0 += 0.28
        cv.text(x0, y, x + w - x0 - 0.15, hh, rest, size=size, color='primary', role='title', anchor='middle',
                fit=True, min_size=11, emph='emph', name='txt:stmt')
        return hh
    if style == 'box':
        pad = 0.24
        hh = h or cv.measure(text, w - pad - 0.3, size, role='medium') + 0.24
        cv.rect(x, y, w, hh, fill='FFFFFF', line='primary_deep', line_w=1.0, name='deco:stmtbg',
                shadow={'color': 'primary_deep', 'alpha': 0.07, 'blur': 8, 'dist': 2})
        cv.text(x + pad, y, w - pad - 0.15, hh, text, size=size, color=color, role='title', anchor='middle',
                align=align, fit=True, min_size=11, emph='emph', name='txt:stmt')
        return hh
    if style == 'centered':
        tw = min(w - 1.4, cv.width_of(text, size, role='title') + 0.1)
        hh = h or size / 72 * 1.55
        cv.text(x + (w - tw) / 2, y, tw, hh, text, size=size, color=color, role='title', align='center',
                anchor='middle', wrap=False, fit=True, min_size=11, emph='emph', name='txt:stmt')
        for side in (-1, 1):
            for k in range(3):
                sz = 0.075
                cx = x + w / 2 + side * (tw / 2 + 0.2 + k * 0.16)
                cv.rect(cx - sz / 2, y + hh / 2 - sz / 2, sz, sz, fill='primary', alpha=1 - 0.3 * k if side else 1,
                        name='deco:dot')
        return hh
    inner_x = x
    inner_w = w
    if style == 'label' and label:
        lw = label_w
        hh = h or max(size / 72 * 2.9, cv.measure(text, w - lw - 0.45, size, role='medium') + 0.24)
        cv.rect(x, y, w, hh, fill='panel', name='deco:stmtbg')
        cv.shape('homePlate', x, y, lw, hh, fill='primary', adj={'adj': 22000}, name='deco:stmtlabel')
        cv.text(x + 0.08, y, lw - 0.3, hh, label, size=size + 2, color='FFFFFF', role='title', align='center',
                anchor='middle', wrap=False, fit=True, min_size=11, name='txt:stmtlabel')
        cv.text(x + lw + 0.2, y, w - lw - 0.35, hh, text, size=size, color=color, role='medium', anchor='middle',
                fit=True, min_size=11, emph='emph', name='txt:stmt')
        return hh
    pad = 0.24
    hh = h or cv.measure(text, w - pad - 0.3, size, role='medium') + 0.22
    fill = 'emph_pale' if style == 'pink' else 'panel'
    if style != 'plain':
        cv.rect(x, y, w, hh, grad=[(0, fill, 1.0), (100, fill, 0.35)], grad_angle=0, name='deco:stmtbg')
    if style == 'bar':
        cv.rect(x, y, 0.07, hh, fill='primary', name='deco:stmtbar')
    cv.text(x + pad, y, w - pad - 0.15, hh, text, size=size, color='emph' if style == 'pink' else color,
            role='medium', anchor='middle', align=align, fit=True, min_size=11, emph='emph', name='txt:stmt')
    return hh


def header_shape(cv):
    """Ribbon shape matching the skin's panel headers (pill / tab / fade / pale / dash / notch / rect)."""
    return {'pill': 'pill', 'trap': 'tab', 'fade': 'fade', 'pale': 'pale', 'dash': 'dash',
            'notch': 'notch'}.get((cv.t.extras or {}).get('panel_header', 'ribbon'), 'rect')


def ribbon(cv, x, y, w, text, h=None, fill='primary', color='FFFFFF', size=None, shape='rect', align='center'):
    """Navy header label. shape: rect | tab (trapezoid-ish tab) | chevron | pill | fade (strip fading to the right,
    left-aligned text — 重点研发) | pale (light strip, navy text — 重点实验室) | dash (— title — without fill — 科学技术奖)
    | notch (navy strip with a small down-pointing notch — 树叶)."""
    t = cv.t
    size = size or t.size_body + 1
    h = h or size / 72 * 1.85
    if shape == 'fade':
        cv.rect(x, y, w, h, grad=[(0, fill, 1.0), (70, fill, 0.55), (100, fill, 0.0)], grad_angle=0,
                name='deco:ribbon')
        cv.text(x + 0.14, y, w - 0.2, h, text, size=size, color=color, role='title', align='left', anchor='middle',
                wrap=False, fit=True, min_size=9, name='txt:ribbon')
        return h
    if shape == 'pale':
        cv.rect(x, y, w, h, fill='primary+86', line='primary+60', line_w=0.75, name='deco:ribbon')
        cv.text(x + 0.08, y, w - 0.16, h, text, size=size, color='primary_deep', role='title', align=align,
                anchor='middle', wrap=False, fit=True, min_size=9, name='txt:ribbon')
        return h
    if shape == 'dash':
        tw = min(w - 0.9, cv.width_of(plain(text), size + 2, role='title') + 0.2)
        cv.text(x + (w - tw) / 2, y, tw, h, text, size=size + 2, color='primary', role='title', align='center',
                anchor='middle', wrap=False, fit=True, min_size=9, name='txt:ribbon')
        for side in (-1, 1):
            xa = x + w / 2 + side * (tw / 2 + 0.08)
            xb = x + w / 2 + side * (tw / 2 + 0.42)
            cv.line(min(xa, xb), y + h / 2, max(xa, xb), y + h / 2, 'primary', 1.5, name='deco:ribbondash')
        return h
    if shape == 'notch':
        cv.rect(x, y, w, h, fill=fill, name='deco:ribbon')
        cv.shape('triangle', x + w / 2 - 0.11, y + h - 0.01, 0.22, 0.12, fill=fill, rot=180, name='deco:notch')
        cv.text(x + 0.08, y, w - 0.16, h, text, size=size, color=color, role='title', align=align, anchor='middle',
                wrap=False, fit=True, min_size=9, name='txt:ribbon')
        return h
    if shape == 'tab':
        cv.shape('trapezoid', x, y, w, h, fill=fill, adj={'adj': int(min(25000, h / max(w, 0.1) * 60000))},
                 name='deco:ribbon', rot=180)
    elif shape == 'chevron':
        cv.shape('homePlate', x, y, w, h, fill=fill, adj={'adj': 30000}, name='deco:ribbon')
    elif shape == 'pill':
        cv.rect(x, y, w, h, fill=fill, radius=h / 2, name='deco:ribbon')
    else:
        cv.rect(x, y, w, h, grad=[(0, fill, 1.0), (100, fill + '-12' if not fill.startswith('#') and fill.isalpha() else fill, 1.0)],
                grad_angle=90, name='deco:ribbon')
    cv.text(x + 0.08, y, w - 0.16 - (0.15 if shape == 'chevron' else 0), h, text, size=size, color=color,
            role='title', align=align, anchor='middle', wrap=False, fit=True, min_size=9, name='txt:ribbon')
    return h


def panel(cv, box, header=None, header_style=None, fill='panel_light', line='panel_line', header_w=None,
          size=None, header_fill='primary'):
    """Light panel with an optional navy header. Returns the inner content Box.
    header_style (default from the skin): ribbon (centered navy label straddling the top edge) | strip (full-width
    header) | tab (left-aligned label) | pill (rounded label, 树叶答辩) | trap (trapezoid tab, 百宝箱) | fade (strip fading
    to the right, 重点研发) | pale (light header strip, 重点实验室) | dash (— title — on a white card, 科学技术奖) | notch
    (navy strip with a down notch, 树叶)."""
    t = cv.t
    size = size or t.size_body + 1
    header_style = header_style or (t.extras or {}).get('panel_header', 'ribbon')
    top = box.y
    if header and header_style in ('pill', 'trap'):
        hh = size / 72 * 1.8
        cv.rect(box.x, box.y + hh / 2, box.w, box.h - hh / 2, fill=fill, line=line, line_w=0.75,
                radius=0.06 if header_style == 'pill' else 0.0, name='deco:panel')
        hw = header_w or min(box.w - 0.3, max(1.7, cv.width_of(header, size, role='title', bold=True) + 0.7))
        ribbon(cv, box.x + (box.w - hw) / 2, box.y, hw, header, h=hh, size=size,
               shape='pill' if header_style == 'pill' else 'tab', fill=header_fill)
        return Box(box.x + 0.14, box.y + hh + 0.1, box.w - 0.28, box.h - hh - 0.2)
    if header and header_style in ('strip', 'fade', 'pale', 'notch'):
        hh = size / 72 * 1.9
        cv.rect(box.x, box.y, box.w, box.h, fill='FFFFFF' if header_style in ('fade', 'pale') else fill, line=line,
                line_w=0.75, name='deco:panel')
        ribbon(cv, box.x, box.y, box.w, header, h=hh, size=size, fill=header_fill,
               shape={'strip': 'rect'}.get(header_style, header_style))
        extra = 0.08 if header_style == 'notch' else 0.0
        return Box(box.x + 0.14, box.y + hh + 0.12 + extra, box.w - 0.28, box.h - hh - 0.22 - extra)
    if header and header_style == 'dash':
        hh = size / 72 * 2.1
        cv.rect(box.x, box.y, box.w, box.h, fill='FFFFFF', line=line, line_w=0.75, name='deco:panel',
                shadow={'color': 'primary_deep', 'alpha': 0.06, 'blur': 8, 'dist': 2})
        ribbon(cv, box.x, box.y + 0.04, box.w, header, h=hh, size=size, shape='dash')
        return Box(box.x + 0.14, box.y + hh + 0.1, box.w - 0.28, box.h - hh - 0.2)
    if header and header_style in ('ribbon', 'tab'):
        hh = size / 72 * 1.8
        cv.rect(box.x, box.y + hh / 2, box.w, box.h - hh / 2, fill=fill, line=line, line_w=0.75, name='deco:panel')
        hw = header_w or min(box.w - 0.3, max(1.6, cv.width_of(header, size, role='title', bold=True) + 0.6))
        hx = box.x + (box.w - hw) / 2 if header_style == 'ribbon' else box.x
        ribbon(cv, hx, box.y, hw, header, h=hh, size=size, shape='rect', fill=header_fill)
        return Box(box.x + 0.14, box.y + hh + 0.1, box.w - 0.28, box.h - hh - 0.2)
    cv.rect(box.x, box.y, box.w, box.h, fill=fill, line=line, line_w=0.75, name='deco:panel')
    return Box(box.x + 0.14, box.y + 0.12, box.w - 0.28, box.h - 0.24)


def arrow_list(cv, box, items, size=None, color='dark', role='medium', gap=None, sep=False, fit=True,
               marker_color='primary', anchor='top'):
    """➢ bullet list (native Wingdings bullets, editable). items: list of str ([[red]] / **bold** markup)."""
    t = cv.t
    size = size or t.size_body
    paras = [{'text': it, 'bullet': WING_ARROW} for it in items]
    return cv.text(box.x, box.y, box.w, box.h, paras, size=size, color=color, role=role, fit=fit, min_size=10,
                   bullet=WING_ARROW, bullet_color=marker_color, bullet_font='Wingdings', emph='emph',
                   sa=gap if gap is not None else size * 0.45, ls=1.12, anchor=anchor, name='txt:arrowlist')


def tag(cv, x, y, w, h, text, style='navy', size=None):
    """Small label. style: navy (rect) | chevron (navy arrow tag) | pill (navy pill) | red (red rect) |
    light (light-blue rounded, navy text) | outline (white, navy border)."""
    t = cv.t
    size = size or min(t.size_body, h * 72 * 0.45)
    fills = {'navy': ('primary', 'FFFFFF'), 'chevron': ('primary', 'FFFFFF'), 'pill': ('primary_deep', 'FFFFFF'),
             'red': ('emph', 'FFFFFF'), 'light': ('primary+75', 'primary_deep'), 'outline': ('FFFFFF', 'primary')}
    f, c = fills.get(style, fills['navy'])
    if style == 'chevron':
        tip = 0.28 * min(w, h)
        cv.shape('homePlate', x, y, w, h, fill=f, adj={'adj': 28000}, name='deco:tag')
        tw = w - tip
    elif style in ('pill', 'light'):
        cv.rect(x, y, w, h, fill=f, radius=h / 2, name='deco:tag')
        tw = w
    elif style == 'outline':
        cv.rect(x, y, w, h, fill=f, line='primary', line_w=1.0, radius=0.04, name='deco:tag')
        tw = w
    else:
        cv.rect(x, y, w, h, fill=f, name='deco:tag')
        tw = w
    cv.text(x + 0.04, y, tw - 0.08, h, text, size=size, color=c, role='title', align='center', anchor='middle',
            fit=True, min_size=8, name='txt:tag')


def vlabel(cv, x, y, w, h, text, fill='primary', color='FFFFFF', size=None):
    """Vertical navy label bar with stacked characters (e.g. 教育经历 / 扩散范围)."""
    size = size or min(16, w * 72 * 0.5)
    cv.rect(x, y, w, h, fill=fill, name='deco:vlabel')
    cv.text(x, y, w, h, '\n'.join(list(plain(text))), size=size, color=color, role='title', align='center',
            anchor='middle', fit=True, min_size=9, ls=1.0, sa=0, name='txt:vlabel')


def conclusion(cv, text, y=None, x=None, w=None, h=0.58, style='navy', serif=False, size=None, icon=None):
    """Full-width key-conclusion bar. style: navy (white text) | yellow (yellow text on navy) | red | light."""
    t = cv.t
    x = 0.42 if x is None else x
    w = (cv.W - 2 * 0.42) if w is None else w
    y = (cv.H - 0.42 - h) if y is None else y
    size = size or t.size_body + 2
    fills = {'navy': ('primary_deep', 'FFFFFF'), 'yellow': ('primary_deep', 'yellow'), 'red': ('emph', 'FFFFFF'),
             'light': ('panel', 'primary_deep')}
    f, c = fills.get(style, fills['navy'])
    cv.rect(x, y, w, h, grad=[(0, f, 1.0), (100, f + '+12' if f.isalpha() or '_' in f else f, 1.0)], grad_angle=0,
            name='deco:conclusion')
    tx = x + 0.2
    if icon:
        cv.icon(icon, tx, y + (h - 0.3) / 2, 0.3, c)
        tx += 0.42
    cv.text(tx, y, x + w - tx - 0.2, h, text, size=size, color=c, role='serif' if serif else 'title', bold=True,
            align='center', anchor='middle', wrap=False, fit=True, min_size=11, emph='yellow' if style != 'yellow' else 'FFFFFF',
            name='txt:conclusion')
    return y


def block_arrow(cv, x, y, w, h, direction='right', color='primary', label=None, label_color='emph', size=11,
                light=False):
    """Thick gradient block arrow. direction: right | left | up | down | lr (double)."""
    prst = {'right': 'rightArrow', 'left': 'leftArrow', 'up': 'upArrow', 'down': 'downArrow',
            'lr': 'leftRightArrow'}[direction]
    ang = {'right': 0, 'left': 180, 'up': 270, 'down': 90, 'lr': 0}[direction]
    stops = [(0, color, 0.25 if light else 0.55), (100, color, 1.0)]
    if direction == 'lr':
        stops = [(0, color, 1.0), (50, color, 0.55), (100, color, 1.0)]
    cv.shape(prst, x, y, w, h, grad=stops, grad_angle=ang, name='deco:barrow')
    if label:
        if direction in ('up', 'down'):
            cv.text(x + w + 0.05, y, 1.6, h, label, size=size, color=label_color, role='title', anchor='middle',
                    wrap=True, fit=True, min_size=8)
        else:
            cv.text(x, y - size / 72 * 1.5, w, size / 72 * 1.5, label, size=size, color=label_color, role='title',
                    align='center', wrap=False, fit=True, min_size=8)


def axis(cv, x, y, w, nodes=0, h=0.16, color='primary'):
    """Gradient arrow bar (light -> navy) with white nodes at given x positions (list) or n evenly spaced."""
    cv.shape('rightArrow', x, y - h * 0.9, w, h * 1.8, grad=[(0, color + '+80', 1.0), (100, color, 1.0)],
             grad_angle=0, adj={'adj1': 45000, 'adj2': 90000}, name='deco:axis')
    xs = nodes if isinstance(nodes, (list, tuple)) else [x + w * (i + 0.5) / nodes for i in range(nodes)]
    for nx in xs:
        cv.circle(nx, y, 0.085, fill='FFFFFF', line=color, line_w=1.5, name='deco:node')


def dots_divider(cv, x, y, w, color='primary'):
    """Row of small squares (▪▪▪) used as a centered ornament."""
    for k in range(3):
        cv.rect(x + k * 0.16, y, 0.075, 0.075, fill=color, alpha=1 - 0.3 * k, name='deco:dot')


def stat(cv, box, value, unit='', label='', color='emph', size=None, align='center', label_size=None, prefix=None):
    """Achievement number: big red value + unit, small label under it. prefix: small word before the value
    ('小于' / '大于' / '减少', 科技奖 效益页)."""
    t = cv.t
    size = size or min(34, box.h * 72 * 0.5)
    from . import oxml as XX
    tb = cv.slide.shapes.add_textbox(*[int(v * 914400) for v in (box.x, box.y, box.w, box.h * 0.6)])
    XX.set_body(tb, 0, 0, 0, 0, anchor='b', wrap=False)
    p = tb.text_frame.paragraphs[0]
    XX.set_para(p, align=align, bullet='')
    ea, lat, _ = t.font('number')
    if prefix:
        r0 = p.add_run()
        r0.text = prefix + ' '
        XX.style_run(r0, size=size * 0.42, bold=True, hexclr=t.c(color), ea=t.f_body, latin=lat)
    r = p.add_run()
    r.text = str(value)
    XX.style_run(r, size=size, bold=True, hexclr=t.c(color), ea=ea, latin=lat)
    if unit:
        r2 = p.add_run()
        r2.text = unit
        XX.style_run(r2, size=size * 0.5, bold=True, hexclr=t.c(color), ea=t.f_body, latin=lat)
    tb.name = 'txt:stat'
    if label:
        cv.text(box.x, box.y + box.h * 0.62, box.w, box.h * 0.38, label, size=label_size or t.size_small,
                color='dark', role='medium', align=align, fit=True, min_size=8, name='txt:statlabel')


def figure(cv, box, image=None, caption=None, frame=True, cap_style='band', placeholder='示意图', fit='contain'):
    """Image inside a thin frame with a caption band below. Without image draws a labeled placeholder."""
    t = cv.t
    cap_h = 0.34 if caption else 0
    if frame:
        cv.rect(box.x, box.y, box.w, box.h, fill='FFFFFF', line='panel_line', line_w=0.75, name='deco:figframe')
    ib = Box(box.x + 0.06, box.y + 0.06, box.w - 0.12, box.h - cap_h - 0.12)
    pic = None
    if image:
        pic = cv.image(image, ib.x, ib.y, ib.w, ib.h, fit=fit, name='img:figure')
    else:
        cv.rect(ib.x, ib.y, ib.w, ib.h, fill='panel', name='deco:placeholder')
        cv.icon('image', ib.cx - 0.25, ib.cy - 0.35, 0.5, 'primary+50')
        cv.text(ib.x, ib.cy + 0.2, ib.w, 0.3, placeholder, size=11, color='muted', align='center', wrap=False,
                fit=True)
    if caption:
        if cap_style == 'band':
            cv.rect(box.x, box.b - cap_h, box.w, cap_h, fill='panel', name='deco:capband')
        cv.text(box.x + 0.05, box.b - cap_h, box.w - 0.1, cap_h, caption, size=11.5, color='primary_deep',
                role='title', align='center', anchor='middle', wrap=False, fit=True, min_size=8, name='txt:caption')
    return pic


def pic_box(pic):
    """Box (inches) actually covered by a picture shape (e.g. after fit='contain' letterboxing)."""
    from .units import EMU_PER_IN as E
    return Box(pic.left / E, pic.top / E, pic.width / E, pic.height / E)


# ---------------------------------------------------------------- research figures: formulas, zoom, callouts
def formula(cv, box, tex, num=None, size=None, color='text', align='center', note=None, note_size=None):
    """One display equation centred (or left) in `box`, optional '(n)' number at the right edge and a one-line note
    under it (Chinese explanation of the symbols). Returns the Box covered by the equation."""
    size = size or cv.t.size_body + 4
    num_w = 0.55 if num is not None else 0
    note_h = 0.3 if note else 0
    eb = cv.equation(tex, box.x, box.y, size=size, color=color, w=box.w - num_w, h=box.h - note_h, align=align,
                     anchor='middle')
    if num is not None:
        cv.text(box.r - num_w, eb.y, num_w, eb.h, f'({num})', size=cv.t.size_body, color='muted', align='right',
                anchor='middle', wrap=False, fit=False, name='txt:eqnum')
    if note:
        cv.text(box.x, eb.b + 0.04, box.w, note_h, note, size=note_size or cv.t.size_small, color='muted',
                align=align, wrap=False, fit=True, min_size=9, name='txt:eqnote')
    return eb


def zoom_inset(cv, image, pic, src, dst, color='emph', label=None, line_w=1.5, connect=True, frame_fill='FFFFFF'):
    """'局部放大' — mark region `src` of a placed figure and show it enlarged in `dst` (better than a bare red box).
    image: source file; pic: the picture shape returned by cv.image / figure() (or its Box);
    src: (x0, y0, x1, y1) fractions of the image; dst: Box for the enlarged view. Returns the Box of the inset image."""
    from PIL import Image
    from . import images as IMG
    pb = pic if isinstance(pic, Box) else pic_box(pic)
    x0, y0, x1, y1 = src
    sx, sy, sw, sh = pb.x + x0 * pb.w, pb.y + y0 * pb.h, (x1 - x0) * pb.w, (y1 - y0) * pb.h
    import os
    out = IMG._out(image, 'zoom' + IMG._key(os.path.abspath(image), os.path.getmtime(image), tuple(src)))
    if not os.path.exists(out):
        with Image.open(image) as im:
            W, H = im.size
            im.convert('RGB').crop((int(x0 * W), int(y0 * H), int(x1 * W), int(y1 * H))).save(out)
    with Image.open(out) as im:
        iw, ih = im.size
    s = min((dst.w - 0.1) / iw, (dst.h - 0.1) / ih)
    w, h = iw * s, ih * s
    ib = Box(dst.x + (dst.w - w) / 2, dst.y + (dst.h - h) / 2, w, h)
    if connect:  # connectors from the marked region to the inset (the two corners facing each other)
        if ib.x >= sx + sw:      # inset to the right
            pairs = [((sx + sw, sy), (ib.x, ib.y)), ((sx + sw, sy + sh), (ib.x, ib.b))]
        elif ib.r <= sx:         # left
            pairs = [((sx, sy), (ib.r, ib.y)), ((sx, sy + sh), (ib.r, ib.b))]
        elif ib.y >= sy + sh:    # below
            pairs = [((sx, sy + sh), (ib.x, ib.y)), ((sx + sw, sy + sh), (ib.r, ib.y))]
        else:                    # above
            pairs = [((sx, sy), (ib.x, ib.b)), ((sx + sw, sy), (ib.r, ib.b))]
        for (ax, ay), (bx, by) in pairs:
            cv.line(ax, ay, bx, by, color, 1.0, dash='sysDash', name='deco:zoomline')
    cv.rect(sx, sy, sw, sh, fill=None, line=color, line_w=line_w, name='deco:zoomsrc')
    cv.rect(ib.x - 0.04, ib.y - 0.04, ib.w + 0.08, ib.h + 0.08, fill=frame_fill, line=color, line_w=line_w,
            shadow='soft', name='deco:zoomframe')
    cv.image(out, ib.x, ib.y, ib.w, ib.h, fit='stretch', name='img:zoom')
    if label:  # tag sits on top of the frame (outside), so it never hides the figure's own panel title
        lw = cv.width_of(label, 10.5, role='title') + 0.24
        ty = ib.y - 0.04 - 0.28
        cv.rect(ib.x - 0.04, ty, lw, 0.28, fill=color, name='deco:zoomtag')
        cv.text(ib.x - 0.04, ty, lw, 0.28, label, size=10.5, color='FFFFFF', role='title', align='center',
                anchor='middle', wrap=False, fit=True, name='txt:zoomtag')
    return ib


def callout(cv, tx, ty, x, y, w, h, text, color='emph', size=None, dot=True):
    """Annotation for a figure: dot at target (tx, ty) + leader line + framed label at (x, y, w, h)."""
    size = size or cv.t.size_small
    lx = x if tx < x else (x + w if tx > x + w else min(max(tx, x), x + w))
    ly = y + h / 2 if (tx < x or tx > x + w) else (y if ty < y else y + h)
    cv.line(tx, ty, lx, ly, color, 1.25, name='deco:callline')
    if dot:
        cv.circle(tx, ty, 0.055, fill=color, name='deco:calldot')
    cv.rect(x, y, w, h, fill='FFFFFF', line=color, line_w=1.0, radius=0.05, name='deco:callbox')
    cv.text(x + 0.06, y, w - 0.12, h, text, size=size, color=color, role='title', align='center', anchor='middle',
            fit=True, min_size=8, name='txt:callout')


def brace(cv, x, y, h, side='left', color='primary', w=0.18):
    prst = 'leftBrace' if side == 'left' else 'rightBrace'
    sh = cv.shape(prst, x, y, w, h, fill=None, line=color, line_w=1.25, name='deco:brace')
    return sh


def num_square(cv, x, y, n, size=0.46, fill='primary'):
    cv.rect(x, y, size, size, fill=fill, name='deco:numsq')
    cv.text(x, y, size, size, f'{n:02d}' if isinstance(n, int) else str(n), size=size * 72 * 0.42, color='FFFFFF',
            role='number', bold=True, align='center', anchor='middle', wrap=False, fit=False)


def red_marker(cv, x, y, text, w=1.25, h=0.42, size=None):
    """'问题一' style red label with double chevron after it. Returns right edge x."""
    tag(cv, x, y, w, h, text, style='red', size=size)
    for k in range(2):
        cx = x + w + 0.14 + k * 0.14
        pts = [(cx, y + h * 0.28), (cx + 0.1, y + h / 2), (cx, y + h * 0.72)]
        cv.poly(pts, fill=None, line='emph', line_w=2.0, closed=False, name='deco:chev')
    return x + w + 0.45



def flow_chain(cv, box, nodes, style='box', arrow='chevron', size=None, colors=None, sub_size=None):
    """Horizontal chain of nodes joined by arrows (process / system composition).
    nodes: [{'title': str, 'sub': str (optional 2nd line), 'icon': lucide name (optional)}].
    style: box (navy boxes, white text) | light (light panels, navy text) | grad (light->navy progression)."""
    t = cv.t
    n = len(nodes)
    size = size or t.size_body
    gap = 0.42
    w = (box.w - gap * (n - 1)) / n
    for i, nd in enumerate(nodes):
        x = box.x + i * (w + gap)
        if style == 'grad':
            k = i / max(1, n - 1)
            fill = 'primary+' + str(int(70 - 70 * k)) if k < 1 else 'primary_deep'
            fg = 'primary_deep' if k < 0.45 else 'FFFFFF'
        elif style == 'light':
            fill, fg = 'panel', 'primary_deep'
        else:
            fill, fg = 'primary', 'FFFFFF'
        if colors and i < len(colors):
            fill = colors[i]
        cv.rect(x, box.y, w, box.h, fill=fill, line='panel_line' if style == 'light' else None, line_w=0.75,
                radius=0.05, name='deco:flownode')
        y = box.y + 0.1
        if nd.get('icon'):
            isz = min(0.5, box.h * 0.32)
            cv.icon(nd['icon'], x + (w - isz) / 2, y + 0.02, isz, fg)
            y += isz + 0.08
        th = (box.b - y - 0.08) * (0.55 if nd.get('sub') else 1.0)
        cv.text(x + 0.06, y, w - 0.12, th, nd.get('title', ''), size=size + 1, color=fg, role='title',
                align='center', anchor='middle' if not nd.get('sub') else 'bottom', fit=True, min_size=9,
                max_lines=2, name='txt:flowtitle')
        if nd.get('sub'):
            cv.text(x + 0.06, y + th + 0.02, w - 0.12, box.b - y - th - 0.1, nd['sub'], size=sub_size or size - 2,
                    color=fg, role='medium', align='center', fit=True, min_size=8, alpha=0.9, name='txt:flowsub')
        if i < n - 1:
            ax = x + w + 0.07
            if arrow == 'block':
                block_arrow(cv, ax, box.cy - 0.16, gap - 0.14, 0.32, 'right', color='primary')
            else:
                for k in range(2):
                    cx = ax + 0.06 + k * 0.13
                    pts = [(cx, box.cy - 0.13), (cx + 0.1, box.cy), (cx, box.cy + 0.13)]
                    cv.poly(pts, fill=None, line='emph' if arrow == 'red' else 'primary', line_w=2.2, closed=False,
                            name='deco:chev')


def mini_table(cv, box, columns, rows, size=None, emph_cols=(), first_col_color='primary_deep', header_fill='primary',
               zebra=True, align=None):
    """Compact navy-header table drawn with native table object (editable). Returns graphic frame."""
    from .tables import table as _table
    t = cv.t
    fs = size or t.size_body - 1
    rows2 = []
    for r in rows:
        rr = []
        for ci, c in enumerate(r):
            c = str(c)
            if ci in emph_cols and not c.startswith('[['):
                c = '[[' + c + ']]'
            rr.append(c)
        rows2.append(rr)
    gf, geo = _table(cv, box.x, box.y, box.w, box.h, columns, rows2, style='header', font_size=fs, header_size=fs,
                     zebra=zebra, align=align, first_col_bold=True, max_row_h=0.6)
    return gf, geo



def icon_badge_ac(cv, cx, cy, d, icon, color='primary'):
    """Navy gradient circle with a white line icon + thin outer ring (defense style)."""
    cv.circle(cx, cy, d / 2 + 0.06, fill=None, line=color + '+55', line_w=1.0, name='deco:badgering')
    cv.circle(cx, cy, d / 2, grad=[(0, color + '+15', 1.0), (100, 'primary_deep', 1.0)], grad_angle=45,
              name='deco:badge')
    s = d * 0.52
    cv.icon(icon, cx - s / 2, cy - s / 2, s, 'FFFFFF')


# ---------------------------------------------------------------- diagram helpers (see diagrams.py)
from .diagrams import (card_box, card_title, symbol_strip, formula_block, formula_card, cycle,  # noqa: E402,F401
                       stat_grid, progress_bars, vs_badge, hbracket, water_waves)
from .parts import (LEVELS, level_key, level_color, chip, level_chip, chevrons, silhouette, person,  # noqa: E402,F401
                    stars, laurel, certificate, metric_box, converge, vchain, arc_text, hub_node, cylinder)
