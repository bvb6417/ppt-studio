"""Layouts distilled from 新参考 (2026-10-02): 国家科技进步奖 · 国家科学技术奖 · 国家重点研发计划 (项目 / 申报) ·
长江学者 · 全国重点实验室 · 万人计划青年拔尖 template families and 科研架构图 hub diagrams (design-rules §14).
Style-aware (skin chrome + theme colors), dense and figure-rich like the rest of the defense layouts.

    risks        风险分析: cards (2×2: arrow tag + summary, 负面影响, 级别 / 涉及课题 chips) | tabs (2×3: tab header, red
                 label + dashed summary, bullets, colored 涉及课题 chip + level word) | rows (level badge, impact, 应对)
    outcomes     预期成果: centre figure card flanked by 2+2 outline pills with number circles, figure row, conclusion
    topics       课题分解: 2×2 topic panels joined by labeled arrows, top banner, side bracket labels
    lab_team     实验室 / 团队人员构成: stats + leader card + member photos | roster table (key rows red)
    leader       项目负责人: photo + honour strip + achievements + laurel award badges + sub-team photo groups
    need_cards   需求 / 背景四卡: tab-header image cards, chevrons, V-convergence to a red conclusion
    framework    科研架构图 (hub): centre hexagon, ring nodes, accent dots, curved phrases, side columns, bottom chain
    history      发展历程: year pills on a gradient arrow, event titles, ★ ratings, photos
    awards       科研团队获奖: banner with counts, award table (key rows red), certificate shelf
"""
from __future__ import annotations

import math

from . import academic as A
from . import parts as P
from .canvas import Box, plain
from .layouts import layout
from .layouts_ac import _fill_panel
from .layouts_rs import _frame, _done

W, H = 13.333, 7.5
_SOFT = {'color': 'primary_deep', 'alpha': 0.09, 'blur': 10, 'dist': 2}


def _ribbon_shape(cv, default='rect'):
    hs = A.header_shape(cv)
    return hs if hs in ('rect', 'fade', 'pale', 'notch', 'pill', 'tab') else default


def _placeholder(cv, b, label='示意图'):
    cv.rect(b.x, b.y, b.w, b.h, fill='panel', name='deco:placeholder')
    s = min(0.5, b.h * 0.3)
    cv.icon('image', b.cx - s / 2, b.cy - s * 0.8, s, 'primary+50')
    cv.text(b.x, b.cy + s * 0.3, b.w, 0.3, label, size=10.5, color='muted', align='center', wrap=False, fit=True,
            name='txt:placeholder')


# =========================================================================== 风险分析
@layout
def risks(deck, title, risks, variant='cards', cols=None, impact_label='负面影响：', topic_prefix='涉及',
          statement=None, stmt_style=None, stmt_label=None, conclusion=None, conclusion_style='navy', num=None,
          en=None, source=None, notes=None, section=None):
    """风险分析 (万人计划 / 重点研发申报). risks: [{'name': '案例不足', 'summary': '忽略城市规模的影响',
    'impact': '研究结论难以推广…', 'level': '高' | '中' | '低', 'topic': '课题三', 'label': '智能计算' (tabs),
    'points': [str], 'measure': '应对措施' (rows)}].
    variant: cards (2 columns: navy arrow tag + summary, 负面影响 line, chips 级别 / 涉及课题) | tabs (3 columns:
    tab header, red label + dashed summary, ➤ bullets, 涉及课题 chip in the level color + level word) | rows (one
    row per risk: level badge, name, impact, 应对措施). Level colors: 低 green · 中 orange · 高 red."""
    cv, area = _frame(deck, title, statement, stmt_style, stmt_label, conclusion, conclusion_style, num, en, source,
                      section)
    n = len(risks)
    if variant == 'rows':
        _risk_rows(cv, area, risks, impact_label, topic_prefix)
        return _done(cv, notes)
    cols = cols or (2 if (variant == 'cards' and n <= 4) or n <= 2 else 3)
    boxes = area.grid(n, cols=cols, gap=0.24, row_gap=0.22 if variant == 'cards' else 0.16)
    for b, r in zip(boxes, risks):
        if variant == 'tabs':
            _risk_tab(cv, b, r, topic_prefix)
        else:
            _risk_card(cv, b, r, impact_label, topic_prefix)
    return _done(cv, notes)


def _risk_card(cv, b, r, impact_label, topic_prefix):
    t = cv.t
    size = t.size_body
    cv.rect(b.x, b.y, b.w, b.h, fill='FFFFFF', line='primary+40', line_w=1.0, name='deco:riskcard', shadow=_SOFT)
    hh = min(0.5, max(0.4, b.h * 0.2))
    name = r.get('name', '')
    tw = min(b.w * 0.42, cv.width_of(name, size + 2, role='title', bold=True) + 0.62)
    cv.shape('homePlate', b.x + 0.14, b.y + 0.14, tw, hh, grad=[(0, 'primary', 1.0), (100, 'primary_deep', 1.0)],
             grad_angle=0, adj={'adj': 32000}, name='deco:risktag')
    cv.text(b.x + 0.2, b.y + 0.14, tw - 0.34, hh, name, size=size + 2, color='FFFFFF', role='title', bold=True,
            align='center', anchor='middle', wrap=False, fit=True, min_size=9, name='txt:riskname')
    x = b.x + 0.14 + tw + 0.14
    if r.get('summary'):
        w_ = P.chevrons(cv, x, b.y + 0.14 + hh / 2, 'primary+20', n=1, size=0.22)
        cv.text(x + w_ + 0.1, b.y + 0.14, b.r - x - w_ - 0.25, hh, r['summary'], size=size, color='primary_deep',
                role='title', bold=True, anchor='middle', wrap=False, fit=True, min_size=8, name='txt:risksum')
    has_chips = bool(r.get('level') or r.get('topic'))
    ch = 0.4 if has_chips else 0
    yc = b.b - 0.16 - ch
    y = b.y + 0.14 + hh + 0.14
    body_b = (yc - 0.26) if has_chips else b.b - 0.14
    if r.get('impact'):
        txt = '{{emph|' + impact_label + '}}' + r['impact']
        sz = size + 1 if cv.measure(txt, b.w - 0.44, size + 1, role='medium', ls=1.2) < (body_b - y) * 0.6 else size
        cv.text(b.x + 0.22, y, b.w - 0.44, body_b - y, txt, size=sz, color='dark', role='medium', fit=True,
                min_size=9, ls=1.2, anchor='middle', name='txt:riskimpact')
    elif r.get('points'):
        A.arrow_list(cv, Box(b.x + 0.22, y, b.w - 0.44, body_b - y), r['points'], size=size, anchor='middle')
    if has_chips:
        cv.line(b.x + 0.3, yc - 0.14, b.r - 0.3, yc - 0.14, 'primary+30', 1.0, name='deco:risksep')
        cw = min(1.7, (b.w - 1.0) / 2)
        both = bool(r.get('level') and r.get('topic'))
        xs = [b.cx - cw - 0.25, b.cx + 0.25] if both else [b.cx - cw / 2]
        k = 0
        if r.get('level'):
            P.level_chip(cv, xs[k], yc, cw, ch, r['level'])
            k += 1
        if r.get('topic'):
            P.chip(cv, xs[k], yc, cw, ch, topic_prefix + r['topic'])


def _risk_tab(cv, b, r, topic_prefix):
    t = cv.t
    size = t.size_body
    tab_h = 0.42
    name = r.get('name', '')
    tw = min(b.w - 0.6, cv.width_of(name, size + 2, role='title', bold=True) + 1.0)
    cv.rect(b.x, b.y + tab_h / 2, b.w, b.h - tab_h / 2, fill='FFFFFF', line='primary+50', line_w=0.75,
            name='deco:riskcard', shadow=_SOFT)
    A.ribbon(cv, b.x + (b.w - tw) / 2, b.y, tw, name, h=tab_h, size=size + 2, shape='tab')
    y = b.y + tab_h + 0.14
    lab, summ = r.get('label'), r.get('summary')
    rh = 0.38
    if lab or summ:
        x = b.x + 0.16
        if lab:
            lw = min(b.w * 0.42, cv.width_of(lab, size, role='title', bold=True) + 0.36)
            cv.rect(x, y, lw, rh, fill='FFFFFF', line='emph', line_w=1.0, radius=0.03, name='deco:risklabel')
            cv.text(x, y, lw, rh, lab, size=size, color='emph', role='title', bold=True, align='center',
                    anchor='middle', wrap=False, fit=True, min_size=8, name='txt:risklabel')
            x += lw + 0.1
        if summ:
            cv.rect(x, y, b.r - 0.16 - x, rh, fill='primary_bg', line='primary+35', line_w=0.75, dash='dash',
                    name='deco:risksum')
            cv.text(x + 0.08, y, b.r - 0.24 - x - 0.08, rh, summ, size=size, color='primary_deep', role='title',
                    bold=True, anchor='middle', wrap=False, fit=True, min_size=8, name='txt:risksum')
        y += rh + 0.14
    level, topic = r.get('level'), r.get('topic')
    ch = 0.38 if (level or topic) else 0
    yc = b.b - 0.14 - ch
    pts = r.get('points') or ([r['impact']] if r.get('impact') else [])
    if pts:
        A.arrow_list(cv, Box(b.x + 0.2, y, b.w - 0.4, yc - 0.1 - y), pts, size=size, anchor='middle')
    if level or topic:
        col = P.level_color(level) if level else 'primary'
        cw = min(1.8, b.w * 0.5)
        x0 = b.cx - (cw + (0.6 if level else 0)) / 2
        if topic:
            P.chip(cv, x0, yc, cw, ch, topic_prefix + topic, style='fill', color=col)
        if level:
            cv.text(x0 + (cw + 0.12 if topic else 0), yc, 0.5, ch, P.level_key(level), size=size + 4, color=col,
                    role='title', bold=True, anchor='middle', wrap=False, fit=False, name='txt:risklevel')


def _risk_rows(cv, area, risks, impact_label, topic_prefix):
    t = cv.t
    n = len(risks)
    gap = 0.14
    rh = min(1.15, (area.h - gap * (n - 1)) / n)
    y0 = area.y + (area.h - rh * n - gap * (n - 1)) / 2
    has_measure = any(r.get('measure') for r in risks)
    for i, r in enumerate(risks):
        y = y0 + i * (rh + gap)
        col = P.level_color(r.get('level')) if r.get('level') else t.c('primary')
        cv.rect(area.x, y, area.w, rh, fill='FFFFFF', line='panel_line', line_w=0.75, name='deco:riskrow',
                shadow=_SOFT)
        bs = min(rh - 0.24, 0.62)
        cv.rect(area.x + 0.16, y + (rh - bs) / 2, bs, bs, fill=col, radius=0.06, name='deco:risklevel')
        cv.text(area.x + 0.16, y + (rh - bs) / 2, bs, bs, P.level_key(r.get('level')) if r.get('level') else
                str(i + 1), size=bs * 72 * 0.5, color='FFFFFF', role='title', bold=True, align='center',
                anchor='middle', wrap=False, fit=False, name='txt:risklevel')
        nx = area.x + 0.16 + bs + 0.2
        nw = 2.3
        sub = topic_prefix + r['topic'] if r.get('topic') else r.get('summary')
        cv.text(nx, y + 0.06, nw, (rh - 0.12) * (0.55 if sub else 1), r.get('name', ''), size=t.size_body + 2,
                color='primary_deep', role='title', bold=True, anchor='bottom' if sub else 'middle', wrap=False,
                fit=True, min_size=9, name='txt:riskname')
        if sub:
            cv.text(nx, y + 0.06 + (rh - 0.12) * 0.57, nw, (rh - 0.12) * 0.43, sub, size=t.size_small, color='muted',
                    role='medium', wrap=False, fit=True, min_size=8, name='txt:risksub')
        ix = nx + nw + 0.15
        cv.line(ix - 0.08, y + 0.16, ix - 0.08, y + rh - 0.16, 'panel_line', 0.75, name='deco:riskdiv')
        iw = (area.r - ix - 0.2) * (0.56 if has_measure else 1.0)
        if r.get('impact'):
            cv.text(ix, y + 0.06, iw, rh - 0.12, '{{emph|' + impact_label + '}}' + r['impact'], size=t.size_body,
                    color='dark', role='medium', anchor='middle', fit=True, min_size=8.5, name='txt:riskimpact')
        if has_measure and r.get('measure'):
            mx = ix + iw + 0.15
            cv.rect(mx, y + 0.1, area.r - mx - 0.14, rh - 0.2, fill='primary_bg', line='primary+60', line_w=0.5,
                    radius=0.04, name='deco:riskmeasure')
            cv.text(mx + 0.12, y + 0.1, area.r - mx - 0.38, rh - 0.2, '{{primary|应对：}}' + r['measure'],
                    size=t.size_body - 0.5, color='dark', role='medium', anchor='middle', fit=True, min_size=8,
                    name='txt:riskmeasure')


# =========================================================================== 预期成果
@layout
def outcomes(deck, title, items, center=None, figures=None, statement=None, stmt_style=None, stmt_label=None,
             conclusion=None, conclusion_style='navy', num=None, en=None, source=None, notes=None, section=None):
    """预期成果 (万人计划): a navy centre card (header + figure + caption) flanked by outline pills with number
    circles (left 01 02 …, right … 04), an optional figure row and a conclusion bar.
    items: 2–6 dicts {'title', 'text' | 'points'}; center: {'header': '预期成果', 'image', 'caption'};
    figures: [path | {'image', 'caption'}] (≤ 4)."""
    t = deck.theme
    cv, area = _frame(deck, title, statement, stmt_style, stmt_label, conclusion, conclusion_style, num, en, source,
                      section)
    figs = [f if isinstance(f, dict) else {'image': f} for f in (figures or [])]
    fig_h = min(1.8, area.h * 0.36) if figs else 0
    top = Box(area.x, area.y, area.w, area.h - (fig_h + 0.18 if figs else 0))
    left, right = items[:(len(items) + 1) // 2], items[(len(items) + 1) // 2:]
    cw = min(3.5, top.w * 0.27)
    cb = Box(top.cx - cw / 2, top.y, cw, top.h)
    for side, group in ((-1, left), (1, right)):
        k = len(group)
        if not k:
            continue
        gap = 0.2
        ph = min(1.4, (top.h - gap * (k - 1)) / k)
        y0 = top.y + (top.h - ph * k - gap * (k - 1)) / 2
        for j, it in enumerate(group):
            idx = j + 1 if side < 0 else len(left) + j + 1
            y = y0 + j * (ph + gap)
            x0, x1 = (top.x, cb.x + 0.45) if side < 0 else (cb.r - 0.45, top.r)
            cv.rect(x0, y, x1 - x0, ph, fill='FFFFFF', line='primary', line_w=1.5, radius=ph / 2, name='deco:outpill',
                    shadow=_SOFT)
            r_ = min(0.32, ph * 0.27)
            ccx = x0 + ph * 0.42 if side < 0 else x1 - ph * 0.42
            cv.circle(ccx, y + ph / 2, r_, grad=[(0, 'primary', 1.0), (100, 'primary_deep', 1.0)], grad_angle=45,
                      name='deco:outnum')
            cv.text(ccx - r_, y + ph / 2 - r_, 2 * r_, 2 * r_, f'{idx:02d}', size=r_ * 72 * 0.72, color='FFFFFF',
                    role='number', bold=True, align='center', anchor='middle', wrap=False, fit=False,
                    name='txt:outnum')
            tx0, tx1 = (ccx + r_ + 0.2, cb.x - 0.15) if side < 0 else (cb.r + 0.15, ccx - r_ - 0.2)
            al = 'left' if side < 0 else 'right'
            th = min(0.5, ph * 0.36)
            cv.text(tx0, y + 0.1, tx1 - tx0, th, it.get('title', ''), size=t.size_body + 3, color='primary_deep',
                    role='title', bold=True, align=al, anchor='middle', wrap=False, fit=True, min_size=10,
                    name='txt:outtitle')
            bb = Box(tx0, y + 0.1 + th + 0.02, tx1 - tx0, ph - th - 0.22)
            if it.get('points') and side < 0:
                A.arrow_list(cv, bb, it['points'], size=t.size_body, gap=2)
            elif it.get('points') or it.get('text'):
                body = '\n'.join(it['points']) if it.get('points') else it['text']
                cv.text(bb.x, bb.y, bb.w, bb.h, body, size=t.size_body, color='dark', role='medium', align=al,
                        fit=True, min_size=8.5, ls=1.15, sa=2, name='txt:outtext')
    center = center or {}
    cv.rect(cb.x, cb.y, cb.w, cb.h, grad=[(0, 'primary', 1.0), (100, 'primary_deep', 1.0)], grad_angle=90,
            name='deco:outcenter', shadow={'color': 'primary_deep', 'alpha': 0.3, 'blur': 14, 'dist': 4})
    hh = 0.5
    cv.text(cb.x, cb.y + 0.04, cb.w, hh, center.get('header', '预期成果'), size=t.size_body + 4, color='FFFFFF',
            role='title', bold=True, align='center', anchor='middle', wrap=False, fit=True, min_size=10,
            name='txt:outheader')
    cap = center.get('caption')
    cap_h = min(0.78, cv.measure(cap, cb.w - 0.3, t.size_body - 0.5, role='medium') + 0.12) if cap else 0
    ib = Box(cb.x + 0.12, cb.y + hh + 0.06, cb.w - 0.24, cb.h - hh - 0.18 - cap_h)
    cv.rect(ib.x, ib.y, ib.w, ib.h, fill='FFFFFF', name='deco:outframe')
    if center.get('image'):
        cv.image(center['image'], ib.x + 0.03, ib.y + 0.03, ib.w - 0.06, ib.h - 0.06, fit='cover', name='img:outcome')
    else:
        _placeholder(cv, Box(ib.x + 0.03, ib.y + 0.03, ib.w - 0.06, ib.h - 0.06), '成果示意图')
    if cap:
        cv.text(cb.x + 0.15, ib.b + 0.04, cb.w - 0.3, cap_h, cap, size=t.size_body - 0.5, color='FFFFFF',
                role='medium', align='center', anchor='middle', fit=True, min_size=8, name='txt:outcaption')
    if figs:
        fb = Box(area.x, area.b - fig_h, area.w, fig_h)
        for b, f in zip(fb.cols(len(figs), gap=0.16), figs):
            A.figure(cv, b, f.get('image'), f.get('caption'), placeholder=f.get('placeholder', '成果图'))
    return _done(cv, notes)


# =========================================================================== 课题分解
@layout
def topics(deck, title, topics, banner=None, links=None, side_left=None, side_right=None, statement=None,
           stmt_style=None, stmt_label=None, conclusion=None, conclusion_style='navy', num=None, en=None, source=None,
           notes=None, section=None):
    """课题分解 (重点研发): 2×2 topic panels (red '课题k' + title, then figure / points via the usual panel keys)
    joined by labeled arrows, an optional top banner and side bracket labels.
    topics: 4 dicts {'name': '课题1', 'title': str, 'image' | 'points' | 'text' | 'chart' | …}.
    links: {(1, 2): ('认知', '感知') — two opposite arrows | (1, 3): '协同认知' — block arrow | (2, 3): '条件支撑' —
    diagonal double arrow | (3, 4): '迭代优化闭环'}; keys are 1-based topic pairs (1 2 / 3 4 = top / bottom row).
    side_left / side_right: labels on the outer brackets (e.g. '提供感知输入', '依赖认知反馈')."""
    t = deck.theme
    cv, area = _frame(deck, title, statement, stmt_style, stmt_label, conclusion, conclusion_style, num, en, source,
                      section)
    y = area.y
    if banner:
        bh = 0.48
        cv.rect(area.x, y, area.w, bh, grad=[(0, 'primary_bg', 1.0), (50, 'primary+80', 1.0), (100, 'primary_bg', 1.0)],
                grad_angle=0, line='primary+55', line_w=0.75, name='deco:topicbanner')
        cv.text(area.x + 0.2, y, area.w - 0.4, bh, banner, size=t.size_body + 2, color='primary_deep', role='title',
                bold=True, align='center', anchor='middle', wrap=False, fit=True, min_size=10, name='txt:topicbanner')
        y += bh + 0.2
    links = {tuple(sorted(k)): v for k, v in (links or {}).items()}
    sl = 0.62 if side_left else 0
    sr = 0.62 if side_right else 0
    grid = Box(area.x + sl, y, area.w - sl - sr, area.b - y)
    hgap = 1.3 if any(k in links for k in ((1, 2), (3, 4))) else 0.3
    vgap = 0.62 if any(k in links for k in ((1, 3), (2, 4))) else 0.24
    if (2, 3) in links or (1, 4) in links:
        hgap, vgap = max(hgap, 1.3), max(vgap, 0.62)
    cw, rh = (grid.w - hgap) / 2, (grid.h - vgap) / 2
    boxes = [Box(grid.x, grid.y, cw, rh), Box(grid.x + cw + hgap, grid.y, cw, rh),
             Box(grid.x, grid.y + rh + vgap, cw, rh), Box(grid.x + cw + hgap, grid.y + rh + vgap, cw, rh)]
    for i, (b, tp) in enumerate(zip(boxes, topics)):
        cv.rect(b.x, b.y, b.w, b.h, fill='FFFFFF', line='panel_line', line_w=0.75, name='deco:topic',
                shadow={'color': 'primary_deep', 'alpha': 0.1, 'blur': 10, 'dist': 3})
        hh = min(0.8, max(0.55, b.h * 0.26))
        cv.rect(b.x, b.y, b.w, hh, grad=[(0, 'primary_bg', 1.0), (100, 'FFFFFF', 1.0)], grad_angle=0,
                name='deco:topichead')
        nm = tp.get('name', f'课题{i + 1}')
        nw = cv.width_of(nm, t.size_body + 4, role='title', bold=True) + 0.25
        cv.text(b.x + 0.15, b.y, nw, hh, nm, size=t.size_body + 4, color='emph', role='title', bold=True,
                anchor='middle', wrap=False, fit=False, name='txt:topicname')
        cv.line(b.x + 0.15 + nw, b.y + hh * 0.26, b.x + 0.15 + nw, b.y + hh * 0.74, 'primary+40', 1.0,
                name='deco:topicdiv')
        cv.text(b.x + 0.3 + nw, b.y + 0.04, b.w - nw - 0.45, hh - 0.08, tp.get('title', ''), size=t.size_body + 2,
                color='primary_deep', role='title', bold=True, anchor='middle', fit=True, min_size=9, max_lines=2,
                ls=1.1, name='txt:topictitle')
        _fill_panel(cv, Box(b.x + 0.14, b.y + hh + 0.08, b.w - 0.28, b.h - hh - 0.18), tp)

    def label(x, y_, w, h, text, anchor='middle'):
        cv.text(x, y_, w, h, text, size=t.size_body + 1, color='primary_deep', role='title', bold=True,
                align='center', anchor=anchor, fit=True, min_size=8, ls=1.0, max_lines=2, name='txt:topiclink')

    for (a, b_), val in links.items():
        if not (1 <= a <= len(boxes) and 1 <= b_ <= len(boxes)):
            continue
        A_, B_ = boxes[a - 1], boxes[b_ - 1]
        pair = isinstance(val, (list, tuple)) and len(val) == 2
        if (a, b_) in ((1, 2), (3, 4)):                      # horizontal
            x0, x1 = A_.r + 0.08, B_.x - 0.08
            cy = A_.y + A_.h * 0.5
            if pair:
                cv.line(x0, cy - 0.15, x1, cy - 0.15, 'primary', 2.0, tail='triangle', name='deco:link')
                cv.line(x0, cy + 0.15, x1, cy + 0.15, 'primary', 2.0, head='triangle', name='deco:link')
                label(x0, cy - 0.85, x1 - x0, 0.62, val[0], 'bottom')
                label(x0, cy + 0.23, x1 - x0, 0.62, val[1], 'top')
            else:
                cv.shape('leftRightArrow', x0, cy - 0.2, x1 - x0, 0.4, grad=[(0, 'primary', 1.0), (50, 'primary_deep', 1.0),
                         (100, 'primary', 1.0)], grad_angle=0, adj={'adj1': 50000, 'adj2': 45000}, name='deco:linkblock')
                label(x0, cy - 0.88, x1 - x0, 0.62, val if isinstance(val, str) else val[0], 'bottom')
        elif (a, b_) in ((1, 3), (2, 4)):                    # vertical
            cx = A_.cx
            y0, y1 = A_.b + 0.06, B_.y - 0.06
            if pair:
                A.block_arrow(cv, cx - 0.4, y0, 0.26, y1 - y0, 'down', color='primary')
                A.block_arrow(cv, cx + 0.14, y0, 0.26, y1 - y0, 'up', color='primary')
                label(cx - 2.1, y0, 1.6, y1 - y0, val[0])
                label(cx + 0.5, y0, 1.6, y1 - y0, val[1])
            else:
                A.block_arrow(cv, cx - 0.14, y0, 0.28, y1 - y0, 'down', color='primary')
                cv.text(cx + 0.24, y0, 2.0, y1 - y0, val if isinstance(val, str) else val[0], size=t.size_body + 1,
                        color='primary_deep', role='title', bold=True, anchor='middle', wrap=False, fit=True,
                        min_size=8, name='txt:topiclink')
        else:                                                # diagonal (2, 3) or (1, 4)
            if (a, b_) == (2, 3):
                p0, p1 = (B_.r + 0.1, B_.y - 0.08), (A_.x - 0.1, A_.b + 0.08)
            else:
                p0, p1 = (A_.r + 0.1, A_.b + 0.08), (B_.x - 0.1, B_.y - 0.08)
            cv.line(p0[0], p0[1], p1[0], p1[1], 'primary', 1.75, head='triangle', tail='triangle', name='deco:link')
            ang = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
            if ang > 90:
                ang -= 180
            elif ang < -90:
                ang += 180
            mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
            txt = val if isinstance(val, str) else val[0]
            tw = cv.width_of(txt, t.size_body, role='title', bold=True) + 0.2
            nx, ny = math.sin(math.radians(ang)) * 0.2, -math.cos(math.radians(ang)) * 0.2
            cv.text(mx + nx - tw / 2, my + ny - 0.17, tw, 0.34, txt, size=t.size_body, color='primary_deep',
                    role='title', bold=True, align='center', anchor='middle', wrap=False, fit=False, rot=ang % 360,
                    name='txt:topiclink')
    for side, text in ((-1, side_left), (1, side_right)):
        if not text:
            continue
        ya, yb = boxes[0].cy, boxes[2].cy
        lx = area.x + 0.42 if side < 0 else area.r - 0.42
        tgt = (boxes[0].x - 0.05, boxes[2].x - 0.05) if side < 0 else (boxes[1].r + 0.05, boxes[3].r + 0.05)
        cv.line(lx, ya, lx, yb, 'primary+30', 1.5, name='deco:bracket')
        cv.line(lx, ya, tgt[0], ya, 'primary+30', 1.5, tail='triangle', name='deco:bracket')
        cv.line(lx, yb, tgt[1], yb, 'primary+30', 1.5, tail='triangle', name='deco:bracket')
        tx = lx - 0.4 if side < 0 else lx + 0.08
        cv.rect(tx, ya + 0.35, 0.32, yb - ya - 0.7, fill='FFFFFF', name='deco:bracketbg')
        cv.text(tx, ya + 0.35, 0.32, yb - ya - 0.7, '\n'.join(plain(text)), size=t.size_body, color='primary_deep',
                role='title', bold=True, align='center', anchor='middle', ls=1.0, sa=0, fit=True, min_size=8,
                name='txt:bracket')
    return _done(cv, notes)


# =========================================================================== 人员构成
@layout
def lab_team(deck, title, stats=None, headline=None, leader=None, members=None, columns=None, rows=None,
         highlight_rows=(), left_header='成员组成', right_header='团队骨干成员', statement=None, stmt_style=None,
         stmt_label=None, conclusion=None, conclusion_style='navy', num=None, en=None, source=None, notes=None,
         section=None):
    """实验室 / 团队人员构成 (重点研发): left = header strip, headline ('固定人员，共计[[168]]人…'), stat numbers with
    pill labels, leader card (photo + name + titles + bullets), member photo row; right = header strip + roster table
    (highlight_rows -> red). stats: [('136', '人', '研发人员')]; leader: {'name', 'label': '实验室主任',
    'titles': [str], 'points': [str], 'photo'}; members: [{'name', 'role', 'photo'}]. Missing photos -> silhouettes."""
    t = deck.theme
    cv, area = _frame(deck, title, statement, stmt_style, stmt_label, conclusion, conclusion_style, num, en, source,
                      section)
    has_tab = bool(rows)
    L = Box(area.x, area.y, area.w * (0.53 if has_tab else 1.0), area.h)
    shape = _ribbon_shape(cv)
    hh = 0.46
    y = L.y
    if left_header:
        A.ribbon(cv, L.x, y, L.w, left_header, h=hh, size=t.size_body + 3, shape=shape)
        y += hh
    if headline or stats:
        sb_h = (0.5 if headline else 0) + (1.0 if stats else 0) + 0.16
        cv.rect(L.x, y, L.w, sb_h, fill='FFFFFF', line='primary+50', line_w=0.75, name='deco:teamstats')
        yy = y + 0.06
        if headline:
            cv.text(L.x + 0.15, yy, L.w - 0.3, 0.42, headline, size=t.size_body + 2, color='primary_deep',
                    role='title', bold=True, align='center', anchor='middle', wrap=False, fit=True, min_size=9,
                    name='txt:teamhead')
            yy += 0.46
            if stats:
                cv.line(L.x + 0.25, yy, L.r - 0.25, yy, 'primary+45', 0.75, dash='dash', name='deco:teamdash')
            yy += 0.04
        if stats:
            cells = Box(L.x + 0.2, yy, L.w - 0.4, 0.96).cols(len(stats), gap=0.3)
            for c, st in zip(cells, stats):
                v, u, lb = (st.get('value'), st.get('unit', ''), st.get('label', '')) if isinstance(st, dict) else \
                    (list(st) + ['', '', ''])[:3]
                A.stat(cv, Box(c.x, c.y, c.w, 0.8), v, u, '', size=24)
                cv.rect(c.x + 0.1, c.y + 0.52, c.w - 0.2, 0.38, fill='FFFFFF', line='primary+50', line_w=0.75,
                        radius=0.19, name='deco:statpill', shadow=_SOFT)
                cv.text(c.x + 0.1, c.y + 0.52, c.w - 0.2, 0.38, lb, size=t.size_body, color='primary_deep',
                        role='title', bold=True, align='center', anchor='middle', wrap=False, fit=True, min_size=8,
                        name='txt:statpill')
        y += sb_h + 0.14
    mem_h = min(1.75, (L.b - y) * 0.47) if members else 0
    if leader:
        lh = L.b - y - (mem_h + 0.14 if members else 0)
        lb = Box(L.x, y, L.w, lh)
        cv.rect(lb.x, lb.y, lb.w, lb.h, grad=[(0, 'FFFFFF', 1.0), (100, 'primary_bg', 1.0)], grad_angle=0,
                line='primary+60', line_w=0.75, name='deco:leadercard')
        pw = min(lh * 0.8, 1.6)
        P.person(cv, Box(lb.x, lb.y, pw, lh), name=leader.get('label', '负责人'), photo=leader.get('photo'))
        tx = lb.x + pw + 0.2
        nm = leader.get('name', '')
        ns = t.size_body + 6
        nw = cv.width_of(nm, ns, role='title', bold=True) + 0.15
        cv.text(tx, lb.y + 0.08, nw, 0.5, nm, size=ns, color='primary', role='title', bold=True, anchor='middle',
                wrap=False, fit=False, name='txt:leadername')
        if leader.get('titles'):
            cv.text(tx + nw + 0.1, lb.y + 0.08, lb.r - tx - nw - 0.2, 0.5, '  |  '.join(leader['titles']),
                    size=t.size_body, color='emph', role='title', bold=True, anchor='middle', wrap=False, fit=True,
                    min_size=8, name='txt:leadertitles')
        if leader.get('points'):
            A.arrow_list(cv, Box(tx, lb.y + 0.62, lb.r - tx - 0.15, lh - 0.7), leader['points'],
                         size=t.size_body - 0.5)
        y += lh + 0.14
    if members:
        k = len(members)
        mb = Box(L.x, L.b - mem_h, L.w, mem_h)
        pw = min(1.3, (mb.w - 0.14 * (k - 1)) / k, mem_h * 0.78)
        x0 = mb.x + (mb.w - (pw * k + 0.14 * (k - 1))) / 2
        for i, mm in enumerate(members):
            P.person(cv, Box(x0 + i * (pw + 0.14), mb.y, pw, mb.h), mm.get('name'), mm.get('role'), mm.get('photo'))
    if has_tab:
        from .tables import table
        R = Box(L.r + 0.25, area.y, area.r - L.r - 0.25, area.h)
        A.ribbon(cv, R.x, R.y, R.w, right_header, h=hh, size=t.size_body + 3, shape=shape)
        cv.rect(R.x, R.y + hh, R.w, R.h - hh, fill='FFFFFF', line='primary+50', line_w=0.75, name='deco:roster')
        hl = set(highlight_rows or ())
        rows2 = [[('[[' + str(c) + ']]') if i in hl else str(c) for c in r] for i, r in enumerate(rows)]
        table(cv, R.x + 0.12, R.y + hh + 0.1, R.w - 0.24, R.h - hh - 0.2, columns, rows2, style='minimal',
              zebra=False, align=['center'] * len(columns), font_size=t.size_body - 0.5, max_row_h=0.62)
    return _done(cv, notes)


# =========================================================================== 项目负责人
@layout
def leader(deck, title, name, photo=None, honors=None, points=None, awards=None, groups=None, statement=None,
           stmt_style=None, stmt_label=None, conclusion=None, conclusion_style='navy', num=None, en=None, source=None,
           notes=None, section=None):
    """科研项目负责人 (重点研发): photo with a navy name band | honour strip (first honour in yellow), ➤ achievement
    lines, laurel award badges; below: sub-team groups (tab header + photo cards, name + red role).
    honors: [str]; points: [str] ([[red]] numbers); awards: [{'title': '国家科技进步奖', 'level': '一等奖'}];
    groups: [{'name': '课题一负责人', 'members': [{'name', 'role', 'photo'}]}]."""
    t = deck.theme
    cv, area = _frame(deck, title, statement, stmt_style, stmt_label, conclusion, conclusion_style, num, en, source,
                      section)
    gh = min(2.3, area.h * 0.45) if groups else 0
    top = Box(area.x, area.y, area.w, area.h - (gh + 0.2 if groups else 0))
    pw = min(top.h * 0.82, 2.6)
    P.person(cv, Box(top.x, top.y, pw, top.h), name=name, photo=photo, size=t.size_body + 5)
    R = Box(top.x + pw, top.y, top.w - pw, top.h)
    cv.rect(R.x, R.y, R.w, R.h, fill='FFFFFF', line='panel_line', line_w=0.75, name='deco:leaderbox')
    hh = 0.55 if honors else 0
    if honors:
        cv.rect(R.x, R.y, R.w, hh, grad=[(0, 'primary_deep', 1.0), (100, 'primary', 1.0)], grad_angle=0,
                name='deco:honors')
        txt = '{{yellow|' + honors[0] + '}}' + ''.join('  |  ' + h_ for h_ in honors[1:])
        cv.text(R.x + 0.3, R.y, R.w - 0.45, hh, txt, size=t.size_body + 3, color='FFFFFF', role='title', bold=True,
                anchor='middle', wrap=False, fit=True, min_size=9, name='txt:honors')
    aw_h = min(1.65, R.h * 0.46) if awards else 0
    if points:
        A.arrow_list(cv, Box(R.x + 0.3, R.y + hh + 0.12, R.w - 0.45, R.h - hh - aw_h - 0.24), points,
                     size=t.size_body + 1, anchor='middle')
    if awards:
        ab = Box(R.x, R.b - aw_h, R.w, aw_h)
        cv.rect(ab.x, ab.y, ab.w, ab.h, grad=[(0, 'primary_bg', 1.0), (100, 'primary+82', 1.0)], grad_angle=90,
                name='deco:awardstrip')
        for c, a in zip(ab.cols(len(awards), gap=0.1), awards):
            P.laurel(cv, c.cx, c.cy, min(c.w * 0.92, 2.7), c.h * 0.92, a.get('title', ''), a.get('level') or a.get('sub'))
    if groups:
        gb = Box(area.x, area.b - gh, area.w, gh)
        counts = [max(1, len(g.get('members', []))) for g in groups]
        gap = 0.18
        avail = gb.w - gap * (len(groups) - 1)
        x = gb.x
        tab_h = 0.4
        for g, cnt in zip(groups, counts):
            w_ = avail * cnt / sum(counts)
            cv.rect(x, gb.y + tab_h / 2, w_, gb.h - tab_h / 2, fill='FFFFFF', line='primary+50', line_w=0.75,
                    name='deco:group')
            tw = min(w_ - 0.3, cv.width_of(g.get('name', ''), t.size_body + 1, role='title', bold=True) + 0.7)
            A.ribbon(cv, x + (w_ - tw) / 2, gb.y, tw, g.get('name', ''), h=tab_h, size=t.size_body + 1, shape='tab')
            mems = g.get('members', [])
            inner = Box(x + 0.12, gb.y + tab_h + 0.1, w_ - 0.24, gb.h - tab_h - 0.18)
            k = max(1, len(mems))
            pw2 = min(1.25, (inner.w - 0.12 * (k - 1)) / k, inner.h * 0.78)
            x0 = inner.x + (inner.w - (pw2 * k + 0.12 * (k - 1))) / 2
            for i, mm in enumerate(mems):
                P.person(cv, Box(x0 + i * (pw2 + 0.12), inner.y, pw2, inner.h), mm.get('name'), mm.get('role'),
                         mm.get('photo'), band=False)
            x += w_ + gap
    return _done(cv, notes)


# =========================================================================== 需求四卡 + 汇聚
@layout
def need_cards(deck, title, cards, statement=None, stmt_style=None, stmt_label=None, converge=None, conclusion=None,
               conclusion_style='navy', num=None, en=None, source=None, notes=None, section=None):
    """需求 / 背景四卡 (长江学者): 3–5 cards with a tab header (科学挑战 / 国家需求 / 国际竞争 / 技术发展), an image with a
    caption ribbon over its lower edge, a colored heading + bold sub-heading and a grey footer note; chevron circles
    between cards; optional V-convergence under them.
    cards: [{'tab', 'image', 'caption', 'head', 'sub', 'foot'}]; converge: {'left', 'right', 'center', 'conclusion'}."""
    t = deck.theme
    cv, area = _frame(deck, title, statement, stmt_style, stmt_label, conclusion, conclusion_style, num, en, source,
                      section)
    cv_h = min(1.6, area.h * 0.3) if converge else 0
    cb = Box(area.x, area.y, area.w, area.h - (cv_h + 0.08 if converge else 0))
    n = len(cards)
    gap = 0.42
    cw = (cb.w - gap * (n - 1)) / n
    tab_h = 0.44
    for i, cd in enumerate(cards):
        x = cb.x + i * (cw + gap)
        b = Box(x, cb.y, cw, cb.h)
        cv.rect(b.x, b.y + tab_h / 2, b.w, b.h - tab_h / 2, fill='FFFFFF', line='primary+50', line_w=0.75,
                name='deco:needcard', shadow=_SOFT)
        tab = cd.get('tab', '')
        tw = min(b.w - 0.4, cv.width_of(tab, t.size_body + 3, role='title', bold=True) + 0.9)
        A.ribbon(cv, b.x + (b.w - tw) / 2, b.y, tw, tab, h=tab_h, size=t.size_body + 3, shape='tab')
        y = b.y + tab_h + 0.1
        foot = cd.get('foot')
        fh = min(0.85, cv.measure(foot, b.w - 0.4, t.size_body - 1, role='medium') + 0.2) if foot else 0
        head_h = 0.42 if cd.get('head') else 0
        sub_h = 0.36 if cd.get('sub') else 0
        img_h = b.b - y - 0.1 - head_h - sub_h - (fh + 0.1 if foot else 0) - 0.08
        ib = Box(b.x + 0.12, y, b.w - 0.24, img_h)
        if cd.get('image'):
            cv.image(cd['image'], ib.x, ib.y, ib.w, ib.h, fit='cover', name='img:needcard')
        else:
            _placeholder(cv, ib)
        if cd.get('caption'):
            ch = min(0.38, ib.h * 0.25)
            cv.rect(ib.x, ib.b - ch, ib.w, ch, grad=[(0, 'primary_deep', 0.15), (50, 'primary_deep', 0.75),
                    (100, 'primary_deep', 0.15)], grad_angle=0, name='deco:needcap')
            cv.text(ib.x, ib.b - ch, ib.w, ch, cd['caption'], size=t.size_body, color='FFFFFF', role='title',
                    bold=True, align='center', anchor='middle', spacing=2, wrap=False, fit=True, min_size=8,
                    name='txt:needcap')
        y = ib.b + 0.08
        if cd.get('head'):
            cv.text(b.x + 0.1, y, b.w - 0.2, head_h, cd['head'], size=t.size_body + 3, color='primary', role='title',
                    bold=True, align='center', anchor='middle', wrap=False, fit=True, min_size=9, name='txt:needhead')
            y += head_h
        if cd.get('sub'):
            cv.text(b.x + 0.1, y, b.w - 0.2, sub_h, cd['sub'], size=t.size_body + 1, color='dark', role='title',
                    bold=True, align='center', anchor='middle', wrap=False, fit=True, min_size=8, name='txt:needsub')
        if foot:
            cv.rect(b.x + 0.12, b.b - fh - 0.1, b.w - 0.24, fh, fill='panel', name='deco:needfoot')
            cv.text(b.x + 0.2, b.b - fh - 0.1, b.w - 0.4, fh, foot, size=t.size_body - 1, color='dark', role='medium',
                    align='center', anchor='middle', fit=True, min_size=8, name='txt:needfoot')
        if i < n - 1:
            ccx = x + cw + gap / 2
            ccy = b.y + tab_h / 2 + (b.h - tab_h / 2) * 0.5
            cv.circle(ccx, ccy, 0.17, fill='FFFFFF', line='primary+40', line_w=1.0, name='deco:needchev', shadow=_SOFT)
            P.chevrons(cv, ccx - 0.05, ccy, 'primary', n=1, size=0.18)
    if converge:
        P.converge(cv, Box(area.x, area.b - cv_h, area.w, cv_h), converge.get('left'), converge.get('right'),
                   converge.get('center', '科学机遇'), converge.get('conclusion'))
    return _done(cv, notes)


# =========================================================================== 科研架构图 (hub)
@layout
def framework(deck, title, center, ring, accents=None, arcs=None, left=None, right=None, bottom=None, banner=None,
              palette=None, highlight=None, statement=None, stmt_style=None, stmt_label=None, conclusion=None,
              conclusion_style='navy', num=None, en=None, source=None, notes=None, section=None):
    """科研架构图 (hub, 佑泽学长 / 科研绘图 style): centre hexagon keyword; 4 ring nodes on a dashed circle (top / right /
    bottom / left) with sub bubbles; accent dots on the diagonals; curved phrases + arc arrows on the ring; side
    columns (circles + dashed boxes); a bottom chain of cylinders pointing at the highlighted middle item; a banner.
    center: str ('结构性\\n矛盾'); ring: up to 4 dicts {'title', 'subs': [a, b] | 'one label'}; accents: 4 chars;
    arcs: up to 4 phrases (clockwise from the top-right quadrant); left / right: {'circles': [str], 'boxes':
    [{'title', 'text'}]}; bottom: [str]; highlight: index in bottom (default middle);
    palette: None (theme navy + red) | 'teal' (teal 1E6B7F + maroon A0323C)."""
    t = deck.theme
    cv, area = _frame(deck, title, statement, stmt_style, stmt_label, conclusion, conclusion_style, num, en, source,
                      section)
    main, acc = ('1E6B7F', 'A0323C') if palette == 'teal' else ('primary_deep', 'emph')
    y = area.y
    if banner:
        bh = 0.46
        bw = min(area.w * 0.7, cv.width_of(banner, t.size_body + 3, role='title', bold=True) + 1.4)
        cv.rect(area.cx - bw / 2, y, bw, bh, grad=[(0, 'primary_deep', 1.0), (100, 'primary', 1.0)], grad_angle=0,
                name='deco:fwbanner')
        cv.text(area.cx - bw / 2, y, bw, bh, banner, size=t.size_body + 3, color='FFFFFF', role='title', bold=True,
                align='center', anchor='middle', wrap=False, fit=True, min_size=10, name='txt:fwbanner')
        y += bh + 0.1
    bot_h = 0.5 if bottom else 0
    hub = Box(area.x, y, area.w, area.b - y - (bot_h + 0.16 if bottom else 0))
    R = max(1.2, min(hub.h / 2 - 0.62, 2.0))
    cx, cy = hub.cx, hub.cy
    cv.circle(cx, cy, R + 0.5, fill=main + '+88' if palette == 'teal' else 'primary_bg', alpha=0.9, name='deco:fwdisc')
    cv.circle(cx, cy, R, fill=None, line=main + '+30', line_w=1.25, dash='dash', name='deco:fwring')
    # arcs + curved phrases, one per quadrant (clockwise from top-right)
    for k, phrase in enumerate((arcs or [])[:4]):
        mid = 45 + 90 * k
        cv.ring(cx, cy, R + 0.2, 0.06, color=acc, start=mid - 22, sweep=44, name='deco:fwarc')
        ex = mid + 22
        px, py = cx + (R + 0.2) * math.sin(math.radians(ex)), cy - (R + 0.2) * math.cos(math.radians(ex))
        cv.shape('triangle', px - 0.1, py - 0.1, 0.2, 0.2, fill=acc, rot=(ex + 90) % 360, name='deco:fwarrow')
        size = max(10, min(14, R * 6.5))
        n = len(plain(phrase))
        step = math.degrees((size / 72 * 1.15) / (R + 0.48))
        span = step * (n - 1)
        if 90 < mid < 270:      # lower half: counter-clockwise so the characters stay upright
            P.arc_text(cv, cx, cy, R + 0.48, phrase, mid + span / 2, mid - span / 2, size=size, color=acc)
        else:
            P.arc_text(cv, cx, cy, R + 0.48, phrase, mid - span / 2, mid + span / 2, size=size, color=acc)
    for k, ch in enumerate((accents or [])[:4]):
        th = math.radians(45 + 90 * k)
        px, py = cx + R * 0.64 * math.sin(th), cy - R * 0.64 * math.cos(th)
        cv.circle(px, py, 0.24, fill=acc, name='deco:fwaccent')
        cv.text(px - 0.24, py - 0.24, 0.48, 0.48, ch, size=15, color='FFFFFF', role='title', bold=True,
                align='center', anchor='middle', wrap=False, fit=False, name='txt:fwaccent')
    hw = R * 0.56
    hh_ = hw * 0.88
    cv.shape('hexagon', cx - hw, cy - hh_, 2 * hw, 2 * hh_, grad=[(0, main + '+18', 1.0), (100, main, 1.0)],
             grad_angle=90, adj={'adj': 25000, 'vf': 115470}, name='deco:fwcenter',
             shadow={'color': main, 'alpha': 0.3, 'blur': 12, 'dist': 3})
    cv.text(cx - hw * 0.8, cy - hh_ * 0.8, hw * 1.6, hh_ * 1.6, center, size=max(16, min(28, R * 13)),
            color='FFFFFF', role='serif', bold=True, align='center', anchor='middle', fit=True, min_size=12, ls=1.05,
            name='txt:fwcenter')
    rn = min(0.66, R * 0.36)
    for k, nd in enumerate((ring or [])[:4]):
        th = math.radians(90 * k)
        nd = nd if isinstance(nd, dict) else {'title': nd}
        P.hub_node(cv, cx + R * math.sin(th), cy - R * math.cos(th), rn, nd.get('title', ''), nd.get('subs'),
                   color=main)
    # side columns: circles near the hub, dashed boxes outside
    for side, spec in ((-1, left), (1, right)):
        if not spec:
            continue
        circles = spec.get('circles', [])
        boxes_ = spec.get('boxes', [])
        ccx = cx + side * (R + 1.35)
        if circles:
            cr = min(0.5, hub.h / (2.4 * len(circles)))
            ys = [hub.y + hub.h * (i + 0.5) / len(circles) for i in range(len(circles))]
            for yy, txt in zip(ys, circles):
                cv.circle(ccx, yy, cr, grad=[(0, main + '+15', 1.0), (100, main, 1.0)], grad_angle=90,
                          name='deco:fwcircle', shadow={'color': main, 'alpha': 0.25, 'blur': 8, 'dist': 2})
                cv.text(ccx - cr * 0.8, yy - cr * 0.8, cr * 1.6, cr * 1.6, txt, size=max(10, cr * 72 * 0.34),
                        color='FFFFFF', role='title', bold=True, align='center', anchor='middle', fit=True,
                        min_size=8, ls=1.0, name='txt:fwcircle')
        if boxes_:
            x0 = area.x if side < 0 else ccx + 0.65
            x1 = ccx - 0.65 if side < 0 else area.r
            bw = x1 - x0
            bxs = Box(x0, hub.y + 0.1, bw, hub.h - 0.2).rows(len(boxes_), gap=0.3)
            for bb, spec_b in zip(bxs, boxes_):
                cv.rect(bb.x, bb.y, bb.w, bb.h, fill='FFFFFF', line=main + '+30', line_w=1.0, dash='dash',
                        name='deco:fwbox')
                hb = min(0.42, bb.h * 0.36)
                tw = min(bb.w - 0.3, cv.width_of(spec_b.get('title', ''), t.size_body + 1, role='title', bold=True) + 0.5)
                cv.rect(bb.x + (bb.w - tw) / 2, bb.y + 0.1, tw, hb, fill=main, name='deco:fwboxhead')
                cv.text(bb.x + (bb.w - tw) / 2, bb.y + 0.1, tw, hb, spec_b.get('title', ''), size=t.size_body + 1,
                        color='FFFFFF', role='title', bold=True, align='center', anchor='middle', wrap=False,
                        fit=True, min_size=8, name='txt:fwboxhead')
                cv.text(bb.x + 0.12, bb.y + 0.16 + hb, bb.w - 0.24, bb.h - hb - 0.24, spec_b.get('text', ''),
                        size=t.size_body + 1, color='dark', role='title', bold=True, align='center',
                        anchor='middle', fit=True, min_size=8, name='txt:fwboxtext')
    if bottom:
        n = len(bottom)
        hi = n // 2 if highlight is None else highlight
        gap = 0.42
        cw = min(2.3, (area.w - gap * (n - 1)) / n)
        x0 = area.cx - (cw * n + gap * (n - 1)) / 2
        by = area.b - bot_h
        for i, txt in enumerate(bottom):
            x = x0 + i * (cw + gap)
            if i == hi:
                cv.shape('leftRightArrow', x - 0.12, by - 0.04, cw + 0.24, bot_h + 0.08, fill=acc,
                         adj={'adj1': 70000, 'adj2': 30000}, name='deco:fwhi')
                cv.text(x + 0.2, by, cw - 0.4, bot_h, txt, size=t.size_body + 2, color='FFFFFF', role='title',
                        bold=True, align='center', anchor='middle', wrap=False, fit=True, min_size=9, name='txt:fwhi')
            else:
                P.cylinder(cv, x, by, cw, bot_h, txt, color=main)
            if i < n - 1:
                ax = x + cw + 0.08
                right_ = i < hi
                cv.shape('rightArrow' if right_ else 'leftArrow', ax, by + bot_h / 2 - 0.12, gap - 0.16, 0.24,
                         fill=main + '+25', name='deco:fwchain')
    return _done(cv, notes)


# =========================================================================== 发展历程
@layout
def history(deck, title, events, banner=None, subtitle=None, statement=None, stmt_style=None, stmt_label=None,
            conclusion=None, conclusion_style='navy', num=None, en=None, source=None, notes=None, section=None):
    """发展历程 (重点实验室): navy pill title + one-line summary, a gradient arrow with navy year pills, one column per
    event: title (key=True -> red), ★ rating, framed photo. events: [{'year', 'title', 'stars': 1–3, 'image',
    'key': bool}]."""
    t = deck.theme
    cv, area = _frame(deck, title, statement, stmt_style, stmt_label, conclusion, conclusion_style, num, en, source,
                      section)
    y = area.y
    if banner:
        bw = cv.width_of(banner, t.size_body + 3, role='title', bold=True) + 1.2
        cv.rect(area.cx - bw / 2, y, bw, 0.44, radius=0.22, grad=[(0, 'primary_deep', 1.0), (100, 'primary', 1.0)],
                grad_angle=0, name='deco:histbanner')
        cv.text(area.cx - bw / 2, y, bw, 0.44, banner, size=t.size_body + 3, color='FFFFFF', role='title', bold=True,
                align='center', anchor='middle', wrap=False, fit=True, min_size=9, name='txt:histbanner')
        y += 0.52
    if subtitle:
        cv.text(area.x, y, area.w, 0.4, subtitle, size=t.size_body + 2, color='dark', role='title', bold=True,
                align='center', anchor='middle', wrap=False, fit=True, min_size=9, name='txt:histsub')
        y += 0.48
    ay = y + 0.24
    cv.shape('rightArrow', area.x, ay - 0.13, area.w, 0.26, grad=[(0, 'primary+75', 1.0), (100, 'primary', 1.0)],
             grad_angle=0, adj={'adj1': 36000, 'adj2': 70000}, name='deco:histaxis')
    n = len(events)
    cols = Box(area.x + 0.1, ay + 0.34, area.w - 0.45, area.b - ay - 0.34).cols(n, gap=0.22)
    any_img = any(e.get('image') is not None or e.get('placeholder') for e in events)
    title_h = min(1.1, max(cv.measure(e.get('title', ''), cols[0].w, t.size_body + 2, role='title') for e in events)
                  + 0.12) if events else 0
    star_h = 0.36 if any(e.get('stars') for e in events) else 0
    img_h = min(cols[0].h - title_h - star_h - 0.2, cols[0].w * 0.92) if any_img else 0
    blk = title_h + star_h + (img_h + 0.14 if any_img else 0)
    top_y = cols[0].y + max(0.0, (cols[0].h - blk) * 0.35)
    for c, e in zip(cols, events):
        pw = min(1.35, c.w * 0.72)
        cv.rect(c.cx - pw / 2, ay - 0.2, pw, 0.4, radius=0.06, grad=[(0, 'primary', 1.0), (100, 'primary_deep', 1.0)],
                grad_angle=90, name='deco:histyear')
        cv.text(c.cx - pw / 2, ay - 0.2, pw, 0.4, e.get('year', ''), size=t.size_body + 2, color='FFFFFF',
                role='number', bold=True, align='center', anchor='middle', wrap=False, fit=True, min_size=9,
                name='txt:histyear')
        cv.text(c.x, top_y, c.w, title_h, e.get('title', ''), size=t.size_body + 2, color='emph' if e.get('key')
                else 'primary_deep', role='title', bold=True, align='center', anchor='middle', fit=True, min_size=8.5,
                ls=1.12, name='txt:histtitle')
        yy = top_y + title_h
        if e.get('stars'):
            P.stars(cv, c.cx, yy + star_h / 2, int(e['stars']), size=0.22, color='emph', gap=0.08, center_big=False)
        yy += star_h + 0.14
        if any_img:
            A.figure(cv, Box(c.x, yy, c.w, img_h), e.get('image'), None, placeholder=e.get('placeholder', '照片'))
    return _done(cv, notes)


# =========================================================================== 科研团队获奖
@layout
def awards(deck, title, columns=None, rows=None, banner=None, highlight_rows=(), certificates=None, cert_aspect=0.74,
           statement=None, stmt_style=None, stmt_label=None, conclusion=None, conclusion_style='navy', num=None,
           en=None, source=None, notes=None, section=None):
    """科研团队获奖 (重点研发): navy banner ('获得国家奖共[[12]]项，其中第一完成单位[[8]]项' — [[..]] in yellow), award
    table (highlight_rows -> red), certificate shelf. certificates: [path | {'image', 'title'} | 'title text'];
    entries without an image are drawn as certificate placeholders. cert_aspect: width / height (0.74 portrait)."""
    t = deck.theme
    cv, area = _frame(deck, title, statement, stmt_style, stmt_label, conclusion, conclusion_style, num, en, source,
                      section)
    y = area.y
    if banner:
        A.conclusion(cv, banner, y=y, x=area.x, w=area.w, h=0.5, style='navy')
        y += 0.62
    certs = [c if isinstance(c, dict) else ({'image': c} if isinstance(c, str) and ('/' in c or '\\' in c or '.' in c[-5:])
                                            else {'title': c}) for c in (certificates or [])]
    tb_h = min(area.b - y - 1.7, (len(rows) + 1) * 0.52) if (rows and certs) else area.b - y
    cert_h = min(3.4, area.b - y - (tb_h + 0.25 if rows else 0)) if certs else 0
    if rows:
        from .tables import table
        hl = set(highlight_rows or ())
        rows2 = [[('[[' + str(c) + ']]') if i in hl else str(c) for c in r] for i, r in enumerate(rows)]
        table(cv, area.x, y, area.w, tb_h, columns, rows2, style='minimal', zebra=False, align=['center'] * len(columns),
              font_size=t.size_body, max_row_h=0.48)
    if certs:
        cb = Box(area.x, area.b - cert_h, area.w, cert_h)
        cv.rect(cb.x, cb.b - 0.2, cb.w, 0.2, grad=[(0, 'panel', 1.0), (100, 'primary+78', 1.0)], grad_angle=90,
                name='deco:shelf')
        n = len(certs)
        slot = cb.w / n
        ch = cert_h - 0.3
        cw = min(slot - 0.25, ch * cert_aspect)
        ch = cw / cert_aspect
        for i, c in enumerate(certs):
            x = cb.x + i * slot + (slot - cw) / 2
            P.certificate(cv, Box(x, cb.b - 0.12 - ch, cw, ch), image=c.get('image'),
                          title=c.get('title') or ('荣誉证书' if i % 2 == 0 else 'CERTIFICATE'))
    return _done(cv, notes)
