"""科研答辩风 layouts (NSFC / 国省科技奖 / 毕业答辩 / 开题 / 竞赛答辩).

Dense, figure-rich, formal. Every content page = title bar (section-numbered) + statement + panels + (conclusion bar).
Deck methods dispatch here automatically when theme.style == 'defense'.
"""
from __future__ import annotations

from . import academic as A
from . import components as K
from . import covers as COV
from . import images as IMG
from .canvas import Box, plain
from .layouts import layout, REGISTRY  # noqa: F401

W, H = 13.333, 7.5


def _info(deck, info):
    m = deck._meta
    if info is not None:
        return list(info)
    out = []
    if m.get('unit'):
        out.append(f"申报单位：{m['unit']}")
    elif m.get('org'):
        out.append(f"汇报单位：{m['org']}")
    if m.get('lab'):
        out.append(f"所在实验室：{m['lab']}")
    return out


# =========================================================================== structure pages
def cover(deck, title=None, subtitle=None, en=None, tag=None, info=None, variant=None, image=None,
          project=None, presenter=None, notes=None, motif=None, **kw):
    """Defense cover. variant (default from the skin): band (navy band + serif title) | sky (light, navy serif
    title) | award (科技奖: white, serif title, completers line, bottom navy band with units) | left (亮蓝白:
    left-aligned white title on a slanted blue block, corner arcs) | tech (重点研发: circuit-pattern tech
    background, serif title, bottom band with units) | plaque (科技进步奖: huge blue serif title, presenter pill on
    a bottom band with units + date) | midband (科学技术奖 / 万人: full-width blue band holding the title, pill,
    牵头单位, units grid) | arc (重点研发: navy block with a bowed lower edge, pill on the arc) | tag (长江学者:
    white card with a navy tag, chevron subtitle band, split pill, bottom swoosh) | lab (全国重点实验室: navy pill,
    lab name between rules, » 实验室主任 « band). Meta used: logo, units (list), date, lab, completers.
    motif='wave': layered water waves (水利 / 流域 / 海洋 topics) along the band's lower edge (band) or the
    page bottom (sky / award)."""
    t = deck.theme
    m = deck._meta
    title = title or m.get('title') or '项目答辩汇报'
    subtitle = subtitle if subtitle is not None else m.get('subtitle')
    project = project if project is not None else (m.get('project') or tag)
    presenter = presenter or (f"汇报人：{m['author']}" if m.get('author') else None)
    variant = variant or (t.extras or {}).get('cover', 'band')
    if variant in COV.COVERS:
        cv = COV.cover(deck, variant, title, subtitle, project, presenter, _info(deck, info), image, motif)
        if notes:
            cv.notes(notes)
        return cv
    if variant in ('left', 'tech'):
        cv = _cover_extra(deck, variant, title, subtitle, project, presenter, _info(deck, info), image)
        if notes:
            cv.notes(notes)
        return cv
    cv = deck.new('cover', bg=False)
    infos = _info(deck, info)
    serif = 'serif'
    if variant == 'band':
        bh = 4.75
        cv.rect(0, 0, W, H, fill='FFFFFF', name='bg:base')
        if image:
            cv.image(image, 0, 0, W, bh, fit='cover', name='bg:photo')
            cv.rect(0, 0, W, bh, grad=[(0, 'primary_deep', 0.92), (100, 'primary', 0.80)], grad_angle=90, name='bg:mask')
        else:
            cv.rect(0, 0, W, bh, grad=[(0, 'primary_deep', 1.0), (100, 'primary', 1.0)], grad_angle=100,
                    name='bg:band')
            p = IMG.dot_map(t.c('secondary+40'), alpha=0.35, size=(1600, 570), step=12, seed=11)
            cv.image(p, 0, 0, W, bh, fit='stretch', name='bg:dots')
            K.glow_orb(cv, W * 0.82, 0.3, 3.2, 'secondary', 0.35)
        if motif == 'wave':
            A.water_waves(cv, 0, W, bh - 0.5, 0.8, colors=('secondary+25', 'primary+45', 'FFFFFF'),
                          alphas=(0.55, 0.5, 1.0), amp=0.11)
        else:
            cv.rect(0, bh - 0.06, W, 0.06, fill='secondary', alpha=0.9, name='deco:bandedge')
        y = 0.7
        if project:
            cv.text(1.0, y, W - 2.0, 0.42, project, size=15, color='FFFFFF', role='medium', align='center',
                    wrap=False, fit=True, min_size=10, alpha=0.92, name='txt:project')
            y += 0.55
        ts = 46 if len(plain(title)) <= 26 else 40
        th = min(2.35, cv.measure(title, W - 1.6, ts, role=serif) + 0.1)
        cv.text(0.8, y, W - 1.6, th, title, size=ts, color='FFFFFF', role='serif', bold=True, align='center',
                anchor='middle', fit=True, min_size=28, max_lines=2, ls=1.1, name='txt:cover_title')
        y += th + 0.12
        if subtitle:
            cv.text(1.0, y, W - 2.0, 0.55, subtitle, size=22, color='FFFFFF', role='medium', align='center',
                    wrap=False, fit=True, min_size=14, alpha=0.95)
            y += 0.6
        if presenter:
            pw = cv.width_of(presenter, 17, role='title') + 0.9
            py = min(bh - (1.08 if motif == 'wave' else 0.78), y + 0.1)
            cv.rect((W - pw) / 2, py, pw, 0.5, fill=None, line='FFFFFF', line_w=1.25, radius=0.25, name='deco:pill')
            cv.text((W - pw) / 2, py, pw, 0.5, presenter, size=17, color='FFFFFF', role='title', align='center',
                    anchor='middle', wrap=False, fit=True)
            for side in (-1, 1):
                for k in range(3):
                    x0 = W / 2 + side * (pw / 2 + 0.25 + k * 0.17) - (0.1 if side < 0 else 0)
                    cv.shape('parallelogram', x0, py + 0.14, 0.1, 0.22, fill='FFFFFF', alpha=0.9 - 0.25 * k,
                             adj={'adj': 50000}, name='deco:slash')
        yy = bh + 0.55
        for line in infos:
            cv.text(1.0, yy, W - 2.0, 0.45, line, size=18, color='dark', role='title', align='center',
                    wrap=False, fit=True, min_size=11)
            yy += 0.52
    elif variant == 'sky':
        cv.rect(0, 0, W, H, grad=[(0, 'primary+80', 1.0), (60, 'FFFFFF', 1.0), (100, 'panel', 1.0)], grad_angle=90,
                name='bg:base')
        if motif == 'wave':
            A.water_waves(cv, 0, W, H - 1.05, 1.05, colors=('primary+72', 'primary+50', 'primary+28'),
                          alphas=(0.7, 0.55, 0.5), amp=0.1)
        if image:
            cv.image(IMG.fade(image, side='top', start=0.0, end=0.7), 0, H * 0.45, W, H * 0.55, fit='cover',
                     name='bg:photo')
        y = 0.55
        if m.get('logo'):
            K.logo(cv, m['logo'], x=(W - 2.2) / 2, y=y, h=0.5, align='left')
            y += 0.7
        if project:
            cv.text(1.0, y, W - 2.0, 0.4, project, size=14, color='primary_deep', role='medium', align='center',
                    wrap=False, fit=True, min_size=9)
            y += 0.5
        ts = 50 if len(plain(title)) <= 24 else 42
        th = min(2.5, cv.measure(title, W - 1.6, ts, role=serif) + 0.1)
        cv.text(0.8, y + 0.1, W - 1.6, th, title, size=ts, color='primary_deep', role='serif', bold=True,
                align='center', anchor='middle', fit=True, min_size=28, max_lines=2, ls=1.12, name='txt:cover_title')
        y += th + 0.35
        if subtitle:
            cv.text(1.0, y, W - 2.0, 0.5, subtitle, size=20, color='primary', role='medium', align='center',
                    wrap=False, fit=True)
            y += 0.6
        if presenter:
            pw = cv.width_of(presenter, 16, role='title') + 0.8
            cv.rect((W - pw) / 2, y, pw, 0.48, fill='primary', radius=0.24, name='deco:pill')
            cv.text((W - pw) / 2, y, pw, 0.48, presenter, size=16, color='FFFFFF', role='title', align='center',
                    anchor='middle', wrap=False, fit=True)
            y += 0.7
        for line in infos:
            cv.text(1.0, y, W - 2.0, 0.4, line, size=15, color='dark', role='title', align='center', wrap=False,
                    fit=True, min_size=10)
            y += 0.44
    else:  # award
        cv.rect(0, 0, W, H, fill='FFFFFF', name='bg:base')
        if motif == 'wave':
            A.water_waves(cv, 0, W, H - 1.85, 0.75, colors=('primary+75', 'primary+55'), alphas=(0.7, 0.55), amp=0.09)
        cv.rect(0, 0, W, H * 0.62, grad=[(0, 'panel', 1.0), (100, 'FFFFFF', 1.0)], grad_angle=90, name='bg:fade')
        if project:
            cv.text(0.55, 0.4, 8.0, 0.35, project, size=12, color='dark', role='medium', wrap=False, fit=True)
        if m.get('logo'):
            K.logo(cv, m['logo'], y=0.35, h=0.45)
        nl = len(title.split('\n'))
        ts = 54 if nl == 1 else 44
        th = 1.1 if nl == 1 else nl * ts / 72 * 1.45 + 0.12
        cv.text(0.8, 1.2, W - 1.6, th, title, size=ts, color='primary_deep', role='serif', bold=True,
                align='center', anchor='middle', wrap=False, fit=True, min_size=28, name='txt:cover_title',
                spacing=2 if nl == 1 else 0, ls=1.1)
        y = 1.2 + th + 0.12
        if subtitle:
            cv.text(0.8, y, W - 1.6, 0.6, subtitle, size=26, color='primary_deep', role='serif', bold=True,
                    align='center', wrap=False, fit=True, min_size=14)
            y += 0.75
        cv.line(2.2, y + 0.05, W - 2.2, y + 0.05, 'primary+60', 1.0)
        y += 0.3
        if presenter:
            cv.text(1.0, y, W - 2.0, 0.5, '》 ' + presenter + ' 《', size=19, color='primary', role='title',
                    align='center', wrap=False, fit=True)
            y += 0.6
        if m.get('completers'):
            cv.text(1.0, y, W - 2.0, 0.4, '主要完成人：' + m['completers'], size=14, color='dark', role='medium',
                    align='center', wrap=False, fit=True, min_size=9)
        units = m.get('units') or infos
        by = H - 1.25
        cv.rect(0, by, W, 1.25, grad=[(0, 'primary_deep', 1.0), (100, 'primary', 1.0)], grad_angle=0,
                name='deco:bottomband')
        if units:
            half = (len(units) + 1) // 2
            rows = [units[:half], units[half:]] if len(units) > 3 else [units]
            for i, row in enumerate(rows):
                cv.text(0.6, by + 0.18 + i * 0.45, W - 1.2, 0.42, '  |  '.join(row), size=13, color='FFFFFF',
                        role='medium', align='center', wrap=False, fit=True, min_size=8)
    if notes:
        cv.notes(notes)
    return cv


def _cover_extra(deck, variant, title, subtitle, project, presenter, infos, image):
    t = deck.theme
    m = deck._meta
    cv = deck.new('cover', bg=False)
    cv.rect(0, 0, W, H, fill='FFFFFF', name='bg:base')
    if variant == 'left':                       # 亮蓝白: slanted bright block, left title, corner arcs
        bh = H * 0.7
        cv.poly([(0, 0), (W * 0.7, 0), (W * 0.6, bh), (0, bh)], grad=[(0, 'primary', 1.0), (100, 'secondary', 1.0)],
                grad_angle=20, name='bg:block')
        p = IMG.dot_map(t.c('FFFFFF'), alpha=0.16, size=(1300, 700), step=13, seed=21)
        cv.image(p, 0, 0, W * 0.66, bh, fit='stretch', name='bg:dots')
        if image:
            cv.image(image, W * 0.62, 0, W * 0.38, bh, fit='cover', name='bg:photo')
            cv.poly([(W * 0.6, 0), (W * 0.72, 0), (W * 0.62, bh), (W * 0.5, bh)], fill='FFFFFF', name='bg:cut')
        for k, (r, a_) in enumerate(((2.6, 0.9), (2.05, 0.4))):
            cv.shape('blockArc', W - r, -r, 2 * r, 2 * r, fill='primary' if k == 0 else 'secondary', alpha=a_,
                     adj={'adj1': 5400000, 'adj2': 10800000, 'adj3': 5200}, name=f'bg:arc{k}')
            cv.shape('blockArc', -r * 0.6, H - r * 0.6, 1.2 * r, 1.2 * r, fill='primary', alpha=0.25 * a_,
                     adj={'adj1': 16200000, 'adj2': 0, 'adj3': 6000}, name=f'bg:arcb{k}')
        x0, y = 0.75, 0.7
        tw = W * (0.46 if image else 0.56)       # with a photo the white diagonal cut starts at ~0.52 W
        if project:
            cv.rect(x0, y + 0.08, 0.08, 0.3, fill='FFFFFF', name='deco:projbar')
            cv.text(x0 + 0.2, y, tw, 0.46, project, size=15, color='FFFFFF', role='medium', wrap=False,
                    fit=True, min_size=10, anchor='middle', alpha=0.95)
            y += 0.7
        longest = max(len(plain(ln)) for ln in title.split('\n'))
        ts = max(26, min(44, tw * 72 / max(1, longest) * 0.96))   # keep each manual line on one line
        th = min(2.5, cv.measure(title, tw, ts, role='title') + 0.1)
        cv.text(x0, y, tw, th, title, size=ts, color='FFFFFF', role='title', bold=True, fit=True, min_size=26,
                max_lines=3, ls=1.12, name='txt:cover_title')
        y += th + 0.1
        if subtitle:
            cv.text(x0, y, W * 0.55, 0.5, subtitle, size=18, color='FFFFFF', role='medium', wrap=False, fit=True,
                    min_size=11, alpha=0.92)
            y += 0.6
        if presenter:
            pw = cv.width_of(presenter, 16, role='title') + 0.8
            cv.rect(x0, min(bh - 0.75, y + 0.05), pw, 0.48, fill=None, line='FFFFFF', line_w=1.25, radius=0.24,
                    name='deco:pill')
            cv.text(x0, min(bh - 0.75, y + 0.05), pw, 0.48, presenter, size=16, color='FFFFFF', role='title',
                    align='center', anchor='middle', wrap=False, fit=True)
        yy = bh + 0.42
        for line in infos[:3]:
            cv.text(x0, yy, W * 0.7, 0.4, line, size=15, color='dark', role='title', wrap=False, fit=True, min_size=9)
            yy += 0.46
        return cv
    # tech: 重点研发 / 科研报告 — circuit pattern on the right, serif title, bottom band with units
    cv.rect(0, 0, W, H, grad=[(0, 'FFFFFF', 1.0), (100, 'primary_bg', 1.0)], grad_angle=0, name='bg:grad')
    cv.image(IMG.circuit(t.c('primary'), size=(1600, 900), seed=7, alpha=0.5, fade='left'), 0, 0, W, H - 1.3,
             fit='stretch', name='bg:circuit')
    K.glow_orb(cv, W * 0.86, 1.6, 3.0, 'secondary', 0.22)
    x0, y = 0.85, 0.75
    if project:
        cv.rect(x0, y + 0.06, 0.6, 0.06, fill='primary', name='deco:projbar')
        cv.text(x0, y + 0.18, W * 0.62, 0.42, project, size=15, color='primary_deep', role='medium', wrap=False,
                fit=True, min_size=10)
        y += 0.85
    th = min(2.6, cv.measure(title, W * 0.66, 46, role='serif') + 0.1)
    cv.text(x0, y, W * 0.66, th, title, size=46, color='primary_deep', role='serif', bold=True, fit=True, min_size=28,
            max_lines=3, ls=1.1, name='txt:cover_title')
    y += th + 0.12
    if subtitle:
        cv.text(x0, y, W * 0.66, 0.5, subtitle, size=20, color='primary', role='medium', wrap=False, fit=True,
                min_size=12)
        y += 0.62
    if presenter:
        pw = cv.width_of(presenter, 16, role='title') + 0.8
        cv.rect(x0, y + 0.05, pw, 0.48, fill='primary', radius=0.24, name='deco:pill')
        cv.text(x0, y + 0.05, pw, 0.48, presenter, size=16, color='FFFFFF', role='title', align='center',
                anchor='middle', wrap=False, fit=True)
    units = m.get('units') or infos
    by = H - 1.3
    cv.rect(0, by, W, 1.3, grad=[(0, 'primary_deep', 1.0), (100, 'primary', 1.0)], grad_angle=0,
            name='deco:bottomband')
    cv.rect(0, by - 0.06, W, 0.06, fill='secondary', alpha=0.85, name='deco:bandedge')
    if units:
        half = (len(units) + 1) // 2
        rows = [units[:half], units[half:]] if len(units) > 3 else [units]
        for i, row in enumerate(rows):
            cv.text(0.6, by + 0.22 + i * 0.45, W - 1.2, 0.42, '  |  '.join(row), size=13, color='FFFFFF',
                    role='medium', align='center', wrap=False, fit=True, min_size=8)
    return cv


def agenda(deck, items=None, current=None, title='汇报提纲', en='CONTENTS', variant=None, descs=None, notes=None,
           **kw):
    """Vertical-title agenda (navy block with vertical serif '汇报提纲' + numbered pill rows).
    current: 0-based index to highlight in red (used for section dividers).
    variant: vertical | split | card | corner (重点研发: white card with diagonal corner sashes, vertical serif
    title + faint vertical CONTENTS, rows on fading bars) | band (科技奖: navy title band + a row of numbered cards)."""
    t = deck.theme
    items = list(items or deck.sections)
    n = len(items)
    variant = variant or t.extras.get('agenda', 'vertical')
    cv = deck.new('content', bg=False)
    cv.rect(0, 0, W, H, grad=[(0, 'FFFFFF', 1.0), (100, 'panel', 1.0)], grad_angle=90, name='bg:base')
    if variant == 'corner':
        COV.agenda_corner(deck, cv, items, current, title if title != '汇报提纲' else '汇报目录', en, descs)
    elif variant == 'band':
        COV.agenda_band(deck, cv, items, current, title, en, descs)
    elif variant == 'split':
        pw = 4.6
        cv.rect(0, 0, pw, H, grad=[(0, 'primary_deep', 1.0), (100, 'primary', 1.0)], grad_angle=90, name='deco:panel')
        if deck._meta.get('logo'):
            K.logo(cv, deck._meta['logo'], x=0.7, y=0.6, h=0.55, align='left')
        cv.text(0.7, 2.5, pw - 1.2, 1.2, title if len(title) <= 3 else '目录', size=54, color='FFFFFF', role='serif',
                bold=True, wrap=False, fit=True)
        cv.text(0.72, 3.65, pw - 1.2, 0.45, en, size=16, color='FFFFFF', alpha=0.75, spacing=3, wrap=False, fit=True)
        area = Box(pw + 0.9, 0.9, W - pw - 1.6, H - 1.8)
        rh = min(0.95, area.h / n)
        y0 = area.y + (area.h - rh * n) / 2
        for i, it in enumerate(items):
            on = current is not None and i == current
            col = 'emph' if on else 'primary_deep'
            y = y0 + i * rh
            cv.text(area.x, y, 1.0, rh, f'{i + 1:02d}', size=30, color=col, role='number', bold=True,
                    anchor='middle', wrap=False, fit=False)
            cv.text(area.x + 1.05, y, area.w - 1.05, rh * (0.62 if descs else 1), it, size=22, color=col,
                    role='title', anchor='middle' if not descs else 'bottom', wrap=False, fit=True, min_size=12)
            if descs and i < len(descs) and descs[i]:
                cv.text(area.x + 1.07, y + rh * 0.6, area.w - 1.1, rh * 0.36, descs[i], size=11, color='muted',
                        wrap=False, fit=True, spacing=0.4)
    elif variant == 'card':   # 深蓝白 / 红 / 绿 templates: white card over a split background, vertical title
        cv.rect(0, H * 0.56, W, H * 0.44, grad=[(0, 'primary_deep', 1.0), (100, 'primary', 1.0)], grad_angle=0,
                name='bg:band')
        card = Box(1.15, 0.75, W - 2.3, H - 1.5)
        cv.rect(card.x, card.y, card.w, card.h, fill='FFFFFF', radius=0.12, name='deco:card',
                shadow={'color': 'primary_deep', 'alpha': 0.18, 'blur': 22, 'dist': 6})
        tw = 2.4
        chars = list(title if len(title) <= 4 else '目录')
        cv.text(card.x + 0.45, card.y + 0.5, tw * 0.62, card.h - 1.0, '\n'.join(chars), size=50, color='primary_deep',
                role='serif', bold=True, align='center', anchor='middle', ls=1.0, sa=4, fit=True, min_size=26,
                name='txt:agenda_title')
        cv.text(card.x + 0.45 + tw * 0.62, card.y + 0.6, 0.45, card.h - 1.2, en, size=13, color='primary', alpha=0.35,
                vert='eaVert', spacing=4, wrap=False, fit=False, align='center', name='deco:agenda_en')
        cv.line(card.x + tw + 0.55, card.y + 0.55, card.x + tw + 0.55, card.b - 0.55, 'primary+65', 1.25)
        area = Box(card.x + tw + 0.95, card.y + 0.45, card.w - tw - 1.4, card.h - 0.9)
        rh = min(0.8, area.h / max(n, 1))
        y0 = area.y + (area.h - rh * n) / 2
        for i, it in enumerate(items):
            on = current is not None and i == current
            dim = current is not None and not on
            y = y0 + i * rh
            if on:
                cv.rect(area.x - 0.15, y + 0.06, area.w + 0.15, rh - 0.12, fill='primary_bg', line='primary+60',
                        line_w=0.75, radius=(rh - 0.12) / 2, name='deco:agenda_on')
            cv.text(area.x, y, 0.85, rh, f'{i + 1:02d}', size=24, color='primary' if not dim else 'B8C2D6',
                    role='number', bold=True, anchor='middle', wrap=False, fit=False)
            cv.text(area.x + 0.95, y, area.w - 1.0, rh * (0.6 if descs else 1), it, size=21,
                    color='primary_deep' if not dim else 'A3ADBF', role='title', anchor='middle' if not descs else 'bottom',
                    wrap=False, fit=True, min_size=12, name='txt:agenda_item')
            if descs and i < len(descs) and descs[i]:
                cv.text(area.x + 0.97, y + rh * 0.6, area.w - 1.1, rh * 0.36, descs[i], size=11,
                        color='muted' if not dim else 'B8C2D6', wrap=False, fit=True)
    else:  # vertical
        bx, bw = 1.25, 1.75
        cv.rect(bx, 0.85, bw, H - 1.7, radius=0.12, grad=[(0, 'primary', 1.0), (100, 'primary_deep', 1.0)],
                grad_angle=90, name='deco:vblock', shadow={'color': 'primary_deep', 'alpha': 0.25, 'blur': 18, 'dist': 4})
        chars = list(title)
        cv.text(bx, 1.2, bw * 0.62, H - 2.4, '\n'.join(chars), size=40, color='FFFFFF', role='serif', bold=True,
                align='center', anchor='middle', ls=1.0, sa=6, fit=True, min_size=24, name='txt:agenda_title')
        cv.text(bx + bw * 0.62, 1.3, bw * 0.3, H - 2.6, en, size=13, color='FFFFFF', alpha=0.45, vert='eaVert',
                spacing=4, wrap=False, fit=False, align='center', name='deco:agenda_en')
        area = Box(bx + bw + 1.0, 1.0, W - bx - bw - 2.2, H - 2.0)
        rh = min(1.0, area.h / n)
        gap = 0.22
        y0 = area.y + (area.h - rh * n) / 2
        for i, it in enumerate(items):
            on = current is not None and i == current
            y = y0 + i * rh + gap / 2
            hh = rh - gap
            cv.rect(area.x + hh / 2, y, area.w - hh / 2, hh, fill='FFFFFF', radius=hh / 2,
                    line='emph' if on else 'primary+65', line_w=1.25, name='deco:row',
                    shadow={'color': 'primary_deep', 'alpha': 0.08, 'blur': 10, 'dist': 2})
            d = hh * 0.86
            cv.circle(area.x + hh / 2 + 0.05, y + hh / 2, d / 2,
                      grad=[(0, ('emph' if on else 'primary') + '+15', 1.0), (100, 'emph' if on else 'primary_deep', 1.0)],
                      grad_angle=45, name='deco:num')
            cv.text(area.x + hh / 2 + 0.05 - d / 2, y + hh / 2 - d / 2, d, d, str(i + 1), size=min(24, d * 72 * 0.5),
                    color='FFFFFF', role='number', bold=True, align='center', anchor='middle', wrap=False, fit=False)
            cv.text(area.x + hh + 0.35, y, area.w - hh - 0.6, hh, it, size=min(24, hh * 72 * 0.46),
                    color='emph' if on else 'primary_deep', role='title', anchor='middle', wrap=False, fit=True,
                    min_size=12, name='txt:agenda_item')
    if notes:
        cv.notes(notes)
    return cv


def section(deck, index, title=None, en=None, desc=None, variant=None, notes=None, **kw):
    """Section divider = the agenda again with the current chapter in red (NSFC convention).
    variant (default from the skin): None (agenda) | number (大序号过渡页) | band (full navy page)."""
    deck.cur_section = index - 1
    deck._sub_counter[index - 1] = 0
    variant = variant or (deck.theme.extras or {}).get('section')
    if variant == 'number':
        # 大序号过渡页: navy block with a huge chapter number, serif title + what this part shows, chapter progress
        t = deck.theme
        cv = deck.new('section', bg=False)
        cv.rect(0, 0, W, H, grad=[(0, 'FFFFFF', 1.0), (100, 'panel', 1.0)], grad_angle=90, name='bg:base')
        lw = W * 0.36
        cv.rect(0, 0, lw, H, grad=[(0, 'primary_deep', 1.0), (100, 'primary', 1.0)], grad_angle=100, name='bg:band')
        p = IMG.dot_map(t.c('secondary+40'), alpha=0.3, size=(700, 900), step=12, seed=5 + index)
        cv.image(p, 0, 0, lw, H, fit='stretch', name='bg:dots')
        cv.text(0.3, 1.45, lw - 0.6, 0.5, 'PART', size=20, color='FFFFFF', role='number', bold=True, align='center',
                spacing=8, alpha=0.75, wrap=False, fit=False, name='txt:part')
        cv.text(0.1, 1.85, lw - 0.2, 2.9, f'{index:02d}', size=170, color='FFFFFF', role='number', bold=True,
                align='center', anchor='middle', wrap=False, fit=False, name='txt:bignum')
        cv.rect(lw - 0.08, 0, 0.08, H, fill='secondary', alpha=0.9, name='deco:bandedge')
        x = lw + 0.85
        w = W - x - 0.8
        ttl = title or deck.sections[index - 1]
        en = en or (deck.section_en[index - 1] if getattr(deck, 'section_en', None) else None)
        cv.text(x, 1.55, w, 1.0, ttl, size=40, color='primary_deep', role='serif', bold=True, anchor='bottom',
                wrap=False, fit=True, min_size=24, name='txt:sectitle')
        y = 2.65
        if en:
            cv.text(x, y, w, 0.4, en.upper(), size=13, color='muted', spacing=1.2, wrap=False, fit=True, min_size=8)
            y += 0.5
        cv.rect(x, y + 0.05, 1.1, 0.07, fill='emph', name='deco:secrule')
        y += 0.4
        if desc:
            items = desc if isinstance(desc, (list, tuple)) else [desc]
            A.arrow_list(cv, Box(x, y, w, 2.5), items, size=t.size_body + 3, gap=10, anchor='top')
        # chapter progress (past / current / future)
        n = len(deck.sections)
        if n > 1:
            cw = min(2.3, w / n)
            for i, s_ in enumerate(deck.sections):
                cx = x + i * cw
                on = i == index - 1
                col = 'primary' if on else ('primary+45' if i < index - 1 else 'line')
                cv.rect(cx, H - 1.05, cw - 0.08, 0.06, fill=col, name=f'deco:prog{i}')
                cv.text(cx, H - 0.95, cw - 0.08, 0.32, f'{i + 1:02d} ' + (getattr(deck, 'section_short', None)
                                                                       or deck.sections)[i],
                        size=11, color='primary_deep' if on else 'muted', role='title' if on else 'medium',
                        wrap=False, fit=True, min_size=8, name=f'txt:prog{i}')
        if notes:
            cv.notes(notes)
        cv.transition('fade')
        return cv
    if variant == 'band':
        t = deck.theme
        cv = deck.new('section', bg=False)
        cv.rect(0, 0, W, H, grad=[(0, 'primary_deep', 1.0), (100, 'primary', 1.0)], grad_angle=100, name='bg:band')
        p = IMG.dot_map(t.c('secondary+40'), alpha=0.3, size=(1600, 900), step=12, seed=7)
        cv.image(p, 0, 0, W, H, fit='stretch', name='bg:dots')
        ttl = title or deck.sections[index - 1]
        cv.text(0, 2.3, W, 1.2, f'第{"一二三四五六七八九十"[index - 1] if index <= 10 else index}部分', size=24,
                color='FFFFFF', role='medium', align='center', wrap=False, fit=True, alpha=0.85)
        cv.text(0.8, 3.1, W - 1.6, 1.2, ttl, size=46, color='FFFFFF', role='serif', bold=True, align='center',
                anchor='middle', wrap=False, fit=True)
        if notes:
            cv.notes(notes)
        return cv
    cv = agenda(deck, current=index - 1, notes=notes)
    cv.transition('fade')
    return cv


def ending(deck, title=None, subtitle=None, en=None, variant=None, info=None, notes=None, presenter=False, **kw):
    """Closing page. Default = just “谢谢” (no “感谢各位专家 / 敬请批评指正”, no presenter or unit lines).
    Extra text appears only when passed explicitly: subtitle=, en= (small English line), info=[lines],
    presenter=True (汇报人 from meta) or a string. variant (default from the skin): band (navy page) | sky (light
    page) | split (white page with a navy bottom band) | plaque (white page, faint skyline, blue serif word, bottom
    gradient band) | midband (word on a full-width blue band across a hexagon-textured page)."""
    t = deck.theme
    m = deck._meta
    title = title or '谢谢'
    variant = variant or (t.extras or {}).get('ending', 'band')
    pres = presenter if isinstance(presenter, str) else (
        f"汇报人：{m['author']}" if presenter and m.get('author') else None)
    infos = list(info) if info else []
    big = len(plain(title).replace('\n', '')) <= 4
    size = 110 if big else 54
    cv = deck.new('cover', bg=False)
    dark = variant in ('band', 'midband')
    fg = 'FFFFFF' if dark else ('primary' if variant == 'plaque' else 'primary_deep')
    th = size / 72 * (1.25 if big else 2.5)
    extra = (0.55 if subtitle else 0) + (0.4 if en else 0) + (0.7 if pres else 0) + 0.46 * len(infos)
    bottom_band = {'split': 1.25, 'plaque': 1.15}.get(variant, 0)
    top = (H - bottom_band - th - extra) / 2 - 0.1
    if variant == 'plaque':
        cv.rect(0, 0, W, H, grad=[(0, 'FFFFFF', 1.0), (100, 'primary_bg', 1.0)], grad_angle=90, name='bg:base')
        cv.image(IMG.skyline(t.c('primary+48'), size=(1600, 280), seed=5, alpha=0.42, fade='both', motif='city'),
                 0, H - 1.15 - 2.3, W, 2.3, fit='stretch', name='bg:skyline')
        cv.rect(0, H - 1.15, W, 1.15, grad=[(0, 'primary', 1.0), (100, 'primary_deep', 1.0)], grad_angle=0,
                name='deco:bottomband')
    elif variant == 'midband':
        cv.rect(0, 0, W, H, grad=[(0, 'FFFFFF', 1.0), (100, 'panel', 1.0)], grad_angle=90, name='bg:base')
        cv.image(IMG.hexgrid(t.c('primary+30'), size=(1600, 900), alpha=0.22, fade='center'), 0, 0, W, H,
                 fit='stretch', name='bg:hex')
        band_y, band_h = top - 0.35, th + extra + (0.35 if big else 0) + 0.75
        cv.rect(0, band_y, W, band_h, grad=[(0, 'primary', 1.0), (100, 'primary-12', 1.0)], grad_angle=0,
                name='bg:midband', shadow={'color': 'primary_deep', 'alpha': 0.28, 'blur': 16, 'dist': 5})
        cv.image(IMG.skyline('FFFFFF', size=(1600, 300), seed=9, alpha=0.14, fade='both', motif='city'),
                 0, band_y + band_h * 0.25, W, band_h * 0.75, fit='stretch', name='bg:bandsky')
    elif variant == 'band':
        cv.rect(0, 0, W, H, grad=[(0, 'primary_deep', 1.0), (100, 'primary', 1.0)], grad_angle=100, name='bg:band')
        p = IMG.dot_map(t.c('secondary+40'), alpha=0.32, size=(1600, 900), step=12, seed=11)
        cv.image(p, 0, 0, W, H, fit='stretch', name='bg:dots')
        K.glow_orb(cv, W * 0.82, 0.6, 3.4, 'secondary', 0.3)
    elif variant == 'split':
        cv.rect(0, 0, W, H, grad=[(0, 'FFFFFF', 1.0), (100, 'panel', 1.0)], grad_angle=90, name='bg:base')
        cv.rect(0, H - 1.25, W, 1.25, grad=[(0, 'primary_deep', 1.0), (100, 'primary', 1.0)], grad_angle=0,
                name='deco:bottomband')
        cv.rect(0, H - 1.31, W, 0.06, fill='secondary', alpha=0.85, name='deco:bandedge')
    else:  # sky
        cv.rect(0, 0, W, H, grad=[(0, 'primary+80', 1.0), (60, 'FFFFFF', 1.0), (100, 'panel', 1.0)], grad_angle=90,
                name='bg:base')
        p = IMG.dot_map(t.c('primary+30'), alpha=0.12, size=(1600, 900), step=14, seed=5)
        cv.image(p, 0, 0, W, H, fit='stretch', name='bg:dots')
    cv.text(0.8, top, W - 1.6, th, title, size=size, color=fg, role='serif', bold=True, align='center',
            anchor='middle', fit=True, min_size=30, ls=1.15, spacing=12 if big else 0, name='txt:end_title')
    y = top + th
    if big:   # quiet ornament under the word (no extra text)
        for side in (-1, 1):
            cv.line(W / 2 + side * 0.25, y + 0.12, W / 2 + side * 1.5, y + 0.12, fg, 1.25, alpha=0.55,
                    name='deco:endline')
        cv.shape('diamond', W / 2 - 0.07, y + 0.05, 0.14, 0.14, fill='yellow' if dark else 'emph', name='deco:enddot')
        y += 0.35
    if en:
        cv.text(1, y, W - 2, 0.38, en.upper(), size=14, color=fg, alpha=0.8, spacing=4, align='center', wrap=False,
                fit=True, min_size=9)
        y += 0.42
    if subtitle:
        cv.text(1, y, W - 2, 0.5, subtitle, size=20, color=fg, role='medium', align='center', wrap=False, fit=True,
                min_size=11)
        y += 0.56
    if pres:
        pw = cv.width_of(pres, 16, role='title') + 0.8
        cv.rect((W - pw) / 2, y + 0.1, pw, 0.48, fill=None if dark else 'primary', line='FFFFFF' if dark else None,
                line_w=1.25, radius=0.24, name='deco:pill')
        cv.text((W - pw) / 2, y + 0.1, pw, 0.48, pres, size=16, color='FFFFFF', role='title', align='center',
                anchor='middle', wrap=False, fit=True)
        y += 0.7
    for line in infos:
        cv.text(1, y, W - 2, 0.42, line, size=15, color=fg, role='title', align='center', wrap=False, fit=True,
                min_size=9)
        y += 0.46
    if notes:
        cv.notes(notes)
    return cv


# =========================================================================== content pages
@layout
def panels(deck, title, panels, statement=None, stmt_style=None, stmt_label=None, conclusion=None,
           conclusion_style='navy', cols=None, num=None, en=None, source=None, notes=None, section=None,
           header_style=None, weights=None):
    """Workhorse dense page: statement bar + N ribbon-headed panels (+ conclusion bar).
    panels: [{'header': str, 'image': path|None, 'caption': str, 'points': [str], 'text': str,
              'image_h': fraction of panel height for the image (default 0.55 when points exist),
              'tags': [str] (small light tags row), 'chart': dict (native chart spec)}]
    statement: key sentence with [[red]] emphasis; stmt_style: bar | label (needs stmt_label e.g. '核心阐述') |
    centered | pink. conclusion: bottom navy bar text (conclusion_style: navy | yellow | red | light)."""
    t = deck.theme
    cv = deck.page(title, en, source=source, section=section, num=num)
    box = cv.content
    y = box.y
    if statement:
        y += A.statement(cv, box.x, y, box.w, statement, style=stmt_style, label=stmt_label) + 0.18
    bottom = box.b
    if conclusion:
        cy = A.conclusion(cv, conclusion, y=box.b - 0.55, x=box.x, w=box.w, h=0.55, style=conclusion_style,
                          serif=conclusion_style == 'yellow')
        bottom = cy - 0.16
    area = Box(box.x, y, box.w, bottom - y)
    n = len(panels)
    ncol = cols or (n if n <= 4 else (3 if n in (5, 6) else 4))
    nrow = (n + ncol - 1) // ncol
    rows = area.rows(nrow, gap=0.16)
    idx = 0
    for r in rows:
        k = min(ncol, n - idx)
        cells = r.cols(k, gap=0.18, weights=(weights if weights and len(weights) == k else None))
        for c in cells:
            p = panels[idx]
            idx += 1
            inner = A.panel(cv, c, header=p.get('header'), header_style=header_style)
            _fill_panel(cv, inner, p)
    _unify_lists(cv)
    if notes:
        cv.notes(notes)
    return cv


def _unify_lists(cv, name='txt:arrowlist'):
    """Give every sibling list on the slide the same (smallest) font size, scaling spacing accordingly."""
    from . import oxml as X
    shapes = [sh for sh in cv.slide.shapes if sh.name == name]
    if len(shapes) < 2:
        return

    def size_of(sh):
        szs = [int(r._r.get_or_add_rPr().get('sz') or 0) for p in sh.text_frame.paragraphs for r in p.runs]
        return max(szs) if szs else 0
    sizes = [size_of(sh) for sh in shapes]
    valid = [v for v in sizes if v > 0]
    if not valid:
        return
    target = min(valid)
    for sh, sz in zip(shapes, sizes):
        if sz <= target:
            continue
        k = target / sz
        for p in sh.text_frame.paragraphs:
            for r in p.runs:
                rPr = r._r.get_or_add_rPr()
                if rPr.get('sz'):
                    rPr.set('sz', str(int(round(int(rPr.get('sz')) * k))))
            pPr = p._p.pPr
            if pPr is not None:
                for tag in ('marL', 'indent'):
                    if pPr.get(tag):
                        pPr.set(tag, str(int(int(pPr.get(tag)) * k)))
                sa = pPr.find(X.qn('a:spcAft'))
                if sa is not None:
                    pts = sa.find(X.qn('a:spcPts'))
                    if pts is not None:
                        pts.set('val', str(int(int(pts.get('val')) * k)))


def _list_h(cv, items, w, size):
    """Height (in) of a ➢ list at size (hanging indent ~1.05 em, para gap 0.45 em)."""
    ind = size / 72 * 1.05
    return sum(cv.measure(it, w - ind, size, role='medium', ls=1.12) for it in items) + size / 72 * 0.45 * (len(items) - 1)


def _fill_panel(cv, inner, p):
    """Place content inside a panel's / card's inner box (top->bottom): subtitle · image | chart | visual |
    placeholder | formula (+symbols) · table · stats · stat_grid · bars · flow · tags · points | text."""
    t = cv.t
    y = inner.y
    has_text = bool(p.get('points') or p.get('text'))
    t = cv.t
    tags = p.get('tags')
    tag_h = 0.42 if tags else 0
    if p.get('subtitle'):
        cv.text(inner.x, y, inner.w, 0.4, p['subtitle'], size=t.size_body + 1, color='primary_deep', role='title',
                align='center', wrap=False, fit=True, min_size=10, emph='emph')
        y += 0.46
    visual = p.get('image') or p.get('chart') or p.get('visual') or p.get('placeholder') or p.get('formula')
    if p.get('icon') and not visual and not (p.get('stat_grid') or p.get('bars') or p.get('table')):
        free_h = inner.b - y
        d = max(0.6, min(1.05, free_h * 0.26))
        items = p.get('points', [])
        sz = t.size_body + 1
        while items and sz < t.size_body + 4 and \
                d + 0.25 + _list_h(cv, items, inner.w - 0.2, sz + 0.5) < free_h * 0.72:
            sz += 0.5
        pts_h = _list_h(cv, items, inner.w - 0.2, sz) if items else 0
        block = d + 0.25 + pts_h
        y0 = y + max(0, (free_h - block) * 0.42)
        A.icon_badge_ac(cv, inner.cx, y0 + d / 2, d, p['icon'])
        y = y0 + d + 0.25
        if items:
            A.arrow_list(cv, Box(inner.x + 0.1, y, inner.w - 0.2, inner.b - y), items, size=sz,
                         gap=sz * 0.6)
        return
    if visual:
        frac = p.get('image_h', 0.62 if has_text else 1.0)
        vh = (inner.b - y - tag_h) * frac if has_text else (inner.b - y - tag_h)
        if p.get('image') and has_text and 'image_h' not in p:
            # size the frame from the picture's aspect ratio so the figure fills it
            try:
                from PIL import Image as _I
                with _I.open(p['image']) as _im:
                    ar = _im.width / _im.height
                cap_h = 0.34 if p.get('caption') else 0
                natural = (inner.w - 0.12) / ar + cap_h + 0.12
                vh = min(natural, (inner.b - y - tag_h) * 0.72)
            except Exception:
                pass
        if p.get('formula') and not (p.get('image') or p.get('chart') or p.get('visual')):
            syms = p.get('symbols') or ()
            nrow = (len(syms) + 3) // 4 if syms else 0
            natural = 0.95 + 0.76 * nrow + (0.1 if syms else 0)
            vh = min(natural, (inner.b - y - tag_h) * 0.72) if has_text else (inner.b - y - tag_h)
        vb = Box(inner.x, y, inner.w, vh)
        if p.get('formula') and not (p.get('image') or p.get('chart') or p.get('visual')):
            A.formula_block(cv, vb, p['formula'], symbols=p.get('symbols') or (), num=p.get('num'),
                            size=p.get('formula_size') or (t.size_body + (4 if has_text else 7)))
        elif p.get('chart'):
            from .charts import chart as _chart
            spec = dict(p['chart'])
            kind = spec.pop('kind', 'column')
            cv.rect(vb.x, vb.y, vb.w, vb.h, fill='FFFFFF', line='panel_line', line_w=0.5, name='deco:chartbg')
            _chart(cv, vb.x + 0.05, vb.y + 0.05, vb.w - 0.1, vb.h - 0.1, kind=kind, font_size=11, **spec)
        elif p.get('visual'):
            p['visual'](cv, vb)
        else:
            A.figure(cv, vb, p.get('image'), p.get('caption'), frame=True,
                     placeholder=p.get('placeholder') or '示意图')
        y += vh + 0.12
    if p.get('table'):
        tb = p['table']
        after = 1.15 if p.get('stats') else 0   # keep room for a stats row that follows the table
        th_ = (inner.b - y - after) * (tb.get('h', 1.0) if has_text else 1.0)
        A.mini_table(cv, Box(inner.x, y, inner.w, th_), tb['columns'], tb['rows'], size=tb.get('size'),
                     emph_cols=tb.get('emph_cols', ()), align=tb.get('align'))
        y += th_ + 0.1
    if p.get('stats'):
        st = p['stats']
        sh = min(1.05, (inner.b - y) * (0.45 if has_text else 1.0))
        cells = Box(inner.x, y, inner.w, sh).cols(len(st), gap=0.1)
        for c, s_ in zip(cells, st):
            A.stat(cv, c, s_.get('value'), s_.get('unit', ''), s_.get('label', ''), size=s_.get('size'))
        y += sh + 0.1
    pts_need = (_list_h(cv, p['points'], inner.w, t.size_body) + 0.25) if p.get('points') else         ((cv.measure(p['text'], inner.w, t.size_body, role='medium') + 0.2) if p.get('text') else 0)
    if p.get('stat_grid'):
        sg = p['stat_grid']
        gc = p.get('grid_cols') or (len(sg) if len(sg) <= 4 else (3 if len(sg) in (5, 6, 9) else 4))
        nr = (len(sg) + gc - 1) // gc
        room = (inner.b - y) - (pts_need if has_text else 0) - (0.5 if p.get('bars') else 0)
        sh = max(min(0.86 * nr, (inner.b - y) * 0.6), min(1.15 * nr, room)) if has_text else (inner.b - y)
        A.stat_grid(cv, Box(inner.x, y, inner.w, sh), sg, cols=gc)
        y += sh + 0.1
    if p.get('bars'):
        bars = p['bars']
        room = (inner.b - y) - (pts_need if has_text else 0)
        bh = max(min(0.46 * len(bars), (inner.b - y) * 0.62), min(0.58 * len(bars), room)) if has_text             else min(0.62 * len(bars), inner.b - y)
        A.progress_bars(cv, Box(inner.x, y, inner.w, bh), bars, highlight=p.get('bars_highlight'),
                        max_value=p.get('bars_max', 100.0))
        y += bh + 0.1
    if p.get('flow'):
        fh = min(1.3, (inner.b - y) * (0.5 if has_text else 1.0))
        A.flow_chain(cv, Box(inner.x, y, inner.w, fh), p['flow'], style=p.get('flow_style', 'grad'))
        y += fh + 0.12
    if tags:
        n = len(tags)
        tw = (inner.w - 0.12 * (n - 1)) / n
        for i, tg in enumerate(tags):
            A.tag(cv, inner.x + i * (tw + 0.12), y, tw, 0.36, tg, style='light', size=12)
        y += tag_h
    if p.get('points'):
        rest = Box(inner.x, y, inner.w, inner.b - y)
        sz = p.get('size')
        if sz is None:  # grow text to use the free room (<= body+2), then center the block vertically
            sz = t.size_body
            items = p['points']
            while sz < t.size_body + 2 and _list_h(cv, items, rest.w, sz + 0.5) < rest.h * 0.8:
                sz += 0.5
        blocky = p.get('stat_grid') or p.get('bars') or p.get('table') or p.get('stats') or p.get('flow')
        A.arrow_list(cv, rest, p['points'], size=sz,
                     anchor=p.get('anchor') or ('middle' if (p.get('image') or not (visual or blocky)) else 'top'))
    elif p.get('text'):
        cv.text(inner.x, y, inner.w, inner.b - y, p['text'], size=p.get('size') or t.size_body, color='dark',
                role='medium', fit=True, min_size=10, align='justify')


@layout
def columns(deck, title, cols, statement=None, axis=True, bottom=None, conclusion=None, num=None, en=None,
            source=None, notes=None, section=None, arrow_between=True):
    """'卡脖子问题' layout: statement + N navy header boxes, each over a light card (centered navy subheading +
    ➢ points), an optional gradient axis with nodes under the cards, and a bottom zone.
    cols: [{'header','subtitle','points'}]. bottom: [{'tag': '算法算力', 'title': '...', 'text': '...'}] rows
    (chevron-tag blocks) or a string (conclusion bar)."""
    t = deck.theme
    cv = deck.page(title, en, source=source, section=section, num=num)
    box = cv.content
    y = box.y
    if statement:
        y += A.statement(cv, box.x, y, box.w, statement) + 0.2
    n = len(cols)
    bottom_h = 0
    if bottom:
        bottom_h = 0.62 if isinstance(bottom, str) else min(2.2, 0.95 * len(bottom) + 0.1)
    if conclusion:
        bottom_h += 0.7
    axis_h = 0.45 if axis else 0
    area = Box(box.x, y, box.w, box.b - y - bottom_h - axis_h - (0.12 if bottom_h else 0))
    cells = area.cols(n, gap=0.22)
    hh = 0.5
    for c, col in zip(cells, cols):
        A.ribbon(cv, c.x, c.y, c.w, col.get('header', ''), h=hh, size=t.size_body + 2, shape=A.header_shape(cv))
        if arrow_between:
            A.block_arrow(cv, c.cx - 0.09, c.y + hh + 0.02, 0.18, 0.22, 'lr' if False else 'down', color='emph',
                          light=True)
        cb = Box(c.x, c.y + hh + 0.26, c.w, c.h - hh - 0.26)
        cv.rect(cb.x, cb.y, cb.w, cb.h, grad=[(0, 'panel', 1.0), (100, 'FFFFFF', 1.0)], grad_angle=90,
                line='panel_line', line_w=0.5, name='deco:colcard')
        yy = cb.y + 0.12
        if col.get('subtitle'):
            cv.text(cb.x + 0.1, yy, cb.w - 0.2, 0.42, col['subtitle'], size=t.size_body + 1, color='primary',
                    role='title', align='center', wrap=False, fit=True, min_size=10, emph='emph')
            yy += 0.5
        if col.get('points'):
            A.arrow_list(cv, Box(cb.x + 0.12, yy, cb.w - 0.22, cb.b - yy - 0.08), col['points'])
    if axis:
        A.axis(cv, area.x, area.b + 0.22, area.w, [c.cx for c in cells])
    if bottom:
        by = area.b + axis_h + 0.12
        if isinstance(bottom, str):
            A.conclusion(cv, bottom, y=by, x=box.x, w=box.w, h=0.55)
        else:
            rows = Box(box.x, by, box.w, bottom_h - 0.05).rows(len(bottom), gap=0.12)
            for r, b in zip(rows, bottom):
                A.tag(cv, r.x, r.y, 1.55, min(r.h, 1.0), b.get('tag', ''), style='chevron', size=14)
                cv.rect(r.x + 1.65, r.y, r.w - 1.65, r.h, grad=[(0, 'panel', 1.0), (100, 'FFFFFF', 1.0)], grad_angle=0,
                        name='deco:blk')
                cv.text(r.x + 1.85, r.y, 3.6, r.h, b.get('title', ''), size=t.size_body + 1, color='primary',
                        role='title', anchor='middle', fit=True, min_size=10, max_lines=2)
                if b.get('text'):
                    cv.text(r.x + 5.55, r.y, r.w - 5.7, r.h, b['text'], size=t.size_body, color='dark', role='medium',
                            anchor='middle', fit=True, min_size=10)
    if conclusion:
        A.conclusion(cv, conclusion, y=box.b - 0.55, x=box.x, w=box.w, h=0.55, style='yellow', serif=True)
    _unify_lists(cv)
    if notes:
        cv.notes(notes)
    return cv


@layout
def problems(deck, title, items, lead=None, conclusion=None, num=None, en=None, source=None, notes=None,
             section=None, variant=None):
    """'问题一/问题二' layout. items: [{'label': '问题一', 'question': '...', 'image': path, 'caption': str,
    'tag': '研究重点', 'points': [...]}]. variant: rows (default for <=2 items) | columns (default for 3-4 items)."""
    t = deck.theme
    cv = deck.page(title, en, source=source, section=section, num=num)
    box = cv.content
    y = box.y
    if lead:
        cv.rect(box.x, y, 0.07, 0.42, fill='primary', name='deco:leadbar')
        cv.text(box.x + 0.2, y, box.w - 0.2, 0.42, lead, size=t.size_body + 1, color='primary_deep', role='title',
                anchor='middle', wrap=False, fit=True, min_size=10, emph='emph')
        y += 0.55
    bottom = box.b - (0.7 if conclusion else 0)
    n = len(items)
    variant = variant or ('columns' if n >= 3 else 'rows')
    if variant == 'columns':
        cols = Box(box.x, y, box.w, bottom - y).cols(n, gap=0.2)
        for c, it in zip(cols, items):
            A.tag(cv, c.x, c.y, c.w, 0.44, it.get('label', ''), style='red', size=15)
            qh = 0.82
            cv.rect(c.x, c.y + 0.44, c.w, qh, grad=[(0, 'panel', 1.0), (100, 'FFFFFF', 1.0)], grad_angle=90,
                    line='panel_line', line_w=0.5, name='deco:qbar')
            cv.text(c.x + 0.12, c.y + 0.44, c.w - 0.24, qh, it.get('question', ''), size=t.size_body + 1,
                    color='primary_deep', role='title', align='center', anchor='middle', fit=True, min_size=10,
                    max_lines=2, emph='emph')
            yy = c.y + 0.44 + qh + 0.12
            if it.get('image') or it.get('caption') or it.get('placeholder'):
                ih = _aspect_h(it.get('image'), c.w, it.get('caption'), max_h=(c.b - yy) * 0.55)
                A.figure(cv, Box(c.x, yy, c.w, ih), it.get('image'), it.get('caption'),
                         placeholder=it.get('placeholder') or '示意图')
                yy += ih + 0.12
            if it.get('points'):
                pb = Box(c.x, yy, c.w, c.b - yy)
                cv.rect(pb.x, pb.y, pb.w, pb.h, fill='panel_light', line='panel_line', line_w=0.5, name='deco:ptsbg')
                ty = pb.y + 0.08
                if it.get('tag'):
                    A.ribbon(cv, pb.x + (pb.w - 1.8) / 2, ty, 1.8, it['tag'], h=0.38, size=13, shape=A.header_shape(cv))
                    ty += 0.48
                A.arrow_list(cv, Box(pb.x + 0.14, ty, pb.w - 0.26, pb.b - ty - 0.06), it['points'],
                             size=t.size_body, anchor='middle')
    else:
        rows = Box(box.x, y, box.w, bottom - y).rows(n, gap=0.16)
        for r, it in zip(rows, items):
            qh = 0.44
            x2 = A.red_marker(cv, r.x, r.y, it.get('label', ''), w=1.3, h=qh)
            cv.rect(x2, r.y, r.r - x2, qh, grad=[(0, 'panel', 1.0), (100, 'FFFFFF', 1.0)], grad_angle=0,
                    name='deco:qbar')
            cv.text(x2 + 0.15, r.y, r.r - x2 - 0.25, qh, it.get('question', ''), size=t.size_body + 1,
                    color='primary_deep', role='title', anchor='middle', wrap=False, fit=True, min_size=10, emph='emph')
            body = Box(r.x, r.y + qh + 0.12, r.w, r.h - qh - 0.12)
            fw = 0
            if it.get('image') or it.get('caption') or it.get('placeholder'):
                fw = _aspect_w(it.get('image'), body.h, it.get('caption'), max_w=body.w * 0.45)
                A.figure(cv, Box(body.x, body.y, fw, body.h), it.get('image'), it.get('caption'),
                         placeholder=it.get('placeholder') or '示意图')
            if it.get('points'):
                tb = Box(body.x + fw + (0.15 if fw else 0), body.y, body.w - fw - (0.15 if fw else 0), body.h)
                cv.rect(tb.x, tb.y, tb.w, tb.h, fill='panel_light', line='panel_line', line_w=0.5, name='deco:ptsbg')
                ty = tb.y + 0.08
                if it.get('tag'):
                    A.ribbon(cv, tb.x + 0.12, ty, min(2.2, tb.w - 0.24), it['tag'], h=0.38, size=13,
                             shape=A.header_shape(cv))
                    ty += 0.48
                A.arrow_list(cv, Box(tb.x + 0.14, ty, tb.w - 0.26, tb.b - ty - 0.06), it['points'],
                             size=t.size_body + 1, anchor='middle')
    if conclusion:
        A.conclusion(cv, conclusion, y=box.b - 0.55, x=box.x, w=box.w, h=0.55)
    _unify_lists(cv)
    if notes:
        cv.notes(notes)
    return cv


def _img_ar(path):
    try:
        from PIL import Image as _I
        with _I.open(path) as im:
            return im.width / im.height
    except Exception:
        return 16 / 9


def _aspect_h(path, w, caption, max_h):
    cap = 0.34 if caption else 0
    return min(max_h, (w - 0.12) / _img_ar(path) + cap + 0.12) if path else min(max_h, 1.6)


def _aspect_w(path, h, caption, max_w):
    cap = 0.34 if caption else 0
    return min(max_w, (h - cap - 0.12) * _img_ar(path) + 0.12) if path else min(max_w, 3.0)


@layout
def figure_text(deck, title, image=None, caption=None, blocks=None, points=None, statement=None, side='left',
                frac=0.52, header=None, conclusion=None, num=None, en=None, source=None, notes=None, section=None,
                visual=None, stmt_style='label', stmt_label='核心阐述', placeholder=None):
    """Figure panel + explanation. blocks: [{'tag': '算法算力', 'title': '...', 'text': '...'}] (chevron-tag rows)
    or points (➢ list under an optional header ribbon). statement: top key sentence (default '核心阐述' label style)."""
    t = deck.theme
    kw_placeholder = placeholder
    cv = deck.page(title, en, source=source, section=section, num=num)
    box = cv.content
    y = box.y
    if statement:
        y += A.statement(cv, box.x, y, box.w, statement, style=stmt_style, label=stmt_label) + 0.18
    bottom = box.b - (0.7 if conclusion else 0)
    area = Box(box.x, y, box.w, bottom - y)
    fb, tb = area.split(frac, gap=0.25)
    if side == 'right':
        tb, fb = area.split(1 - frac, gap=0.25)
    if visual:
        visual(cv, fb)
    else:
        A.figure(cv, fb, image, caption, placeholder=kw_placeholder or '示意图')
    if blocks:
        n = len(blocks)
        rows = tb.rows(n, gap=0.14)
        for r, b in zip(rows, blocks):
            tw = 1.25
            th_ = min(r.h, 1.0)
            A.tag(cv, r.x, r.y + (r.h - th_) / 2, tw, th_, b.get('tag', ''), style='chevron', size=14)
            cv.rect(r.x + tw + 0.1, r.y, r.w - tw - 0.1, r.h, grad=[(0, 'panel', 1.0), (100, 'FFFFFF', 1.0)],
                    grad_angle=0, line='panel_line', line_w=0.5, name='deco:blk')
            ty = r.y + 0.08
            if b.get('title'):
                cv.text(r.x + tw + 0.25, ty, r.w - tw - 0.35, 0.42, b['title'], size=t.size_body + 1, color='primary',
                        role='title', wrap=False, fit=True, min_size=10, emph='emph')
                ty += 0.44
                cv.line(r.x + tw + 0.25, ty, r.r - 0.15, ty, 'panel_line', 0.75)
                ty += 0.06
            if b.get('text'):
                cv.text(r.x + tw + 0.25, ty, r.w - tw - 0.4, r.b - ty - 0.05, b['text'], size=t.size_body,
                        color='dark', role='medium', anchor='middle' if not b.get('title') else 'top', fit=True,
                        min_size=10)
    elif points:
        inner = A.panel(cv, tb, header=header, header_style='strip' if header else 'ribbon')
        A.arrow_list(cv, inner, points, size=t.size_body + 1, gap=t.size_body * 0.7)
    if conclusion:
        A.conclusion(cv, conclusion, y=box.b - 0.55, x=box.x, w=box.w, h=0.55)
    if notes:
        cv.notes(notes)
    return cv


@layout
def route(deck, title, target, top, questions, topics, left_image=None, right_image=None, labels=('', ''),
          num=None, en=None, source=None, notes=None, section=None, left_caption=None, right_caption=None):
    """技术路线: '科学目标' line, a top goal box, an up arrow, key questions (left) linked by braces to topics (right),
    optional images on both sides. questions: [{'title','focus'}] (bottom -> top order as drawn top -> bottom);
    topics: list of lists — topics[i] belongs to questions[i]."""
    t = deck.theme
    cv = deck.page(title, en, source=source, section=section, num=num)
    box = cv.content
    y = box.y
    A.statement(cv, box.x, y, box.w, target, style='centered', size=t.size_body + 3)
    y += 0.62
    side_w = 2.55 if (left_image or right_image) else 0
    mid = Box(box.x + side_w + (0.2 if side_w else 0), y, box.w - 2 * side_w - (0.4 if side_w else 0), box.b - y)
    for img, cap, x in ((left_image, left_caption, box.x), (right_image, right_caption, box.r - side_w)):
        if side_w:   # frame sized from the picture's aspect, centred in the side column
            fh = box.b - y
            if img:
                fh = min(fh, (side_w - 0.12) / _img_ar(img) + 0.12 + (0.34 if cap else 0))
            A.figure(cv, Box(x, y + (box.b - y - fh) / 2, side_w, fh), img, cap)
    # top goal
    th = 0.62
    cv.rect(mid.x + 0.2, mid.y, mid.w - 0.4, th, grad=[(0, 'primary_deep', 1.0), (100, 'primary', 1.0)], grad_angle=0,
            name='deco:goal')
    cv.text(mid.x + 0.35, mid.y, mid.w - 0.7, th, top, size=t.size_body + 3, color='FFFFFF', role='title',
            align='center', anchor='middle', wrap=False, fit=True, min_size=11)
    ay = mid.y + th + 0.05
    A.block_arrow(cv, mid.cx - 0.28, ay, 0.56, 0.55, 'up', color='primary')
    if labels and any(labels):
        cv.text(mid.cx - 2.8, ay + 0.1, 2.3, 0.4, labels[0], size=t.size_body + 1, color='emph', role='title',
                align='right', wrap=False, fit=True)
        cv.text(mid.cx + 0.5, ay + 0.1, 2.3, 0.4, labels[1], size=t.size_body + 1, color='emph', role='title',
                wrap=False, fit=True)
    body = Box(mid.x, ay + 0.68, mid.w, mid.b - (ay + 0.68))
    cv.rect(body.x, body.y, body.w, body.h, fill='FFFFFF', line='panel_line', line_w=0.75, name='deco:routebody')
    nq = len(questions)
    qrows = body.inset(0.15, 0.12).rows(nq, gap=0.14)
    qw = min(2.6, body.w * 0.32)
    for r, q, tp in zip(qrows, questions, topics):
        qb = Box(r.x, r.y + 0.08, qw, r.h - 0.16)
        cv.rect(qb.x, qb.y, qb.w, qb.h, fill='FFFFFF', line='panel_line', line_w=0.75, name='deco:qbox',
                shadow={'color': 'primary_deep', 'alpha': 0.08, 'blur': 8, 'dist': 2})
        cv.text(qb.x + 0.12, qb.y + 0.06, qb.w - 0.24, 0.42, q.get('title', ''), size=t.size_body + 1,
                color='primary', role='title', align='center', wrap=False, fit=True, min_size=10)
        cv.line(qb.x + 0.2, qb.y + 0.5, qb.r - 0.2, qb.y + 0.5, 'panel_line', 0.75, dash='sysDash')
        if q.get('focus'):
            cv.text(qb.x + 0.14, qb.y + 0.56, qb.w - 0.26, qb.h - 0.6, '[[聚焦：]]' + q['focus'], size=t.size_body,
                    color='dark', role='medium', fit=True, min_size=9)
        A.brace(cv, qb.r + 0.18, r.y + 0.05, r.h - 0.1, side='left', color='primary+20')
        tb = Box(qb.r + 0.45, r.y, r.r - qb.r - 0.45, r.h)
        trs = tb.rows(len(tp), gap=0.1)
        for trr, tx in zip(trs, tp):
            cv.rect(trr.x, trr.y, trr.w, trr.h, grad=[(0, 'panel', 1.0), (100, 'FFFFFF', 1.0)], grad_angle=0,
                    name='deco:topic')
            cv.text(trr.x + 0.15, trr.y, trr.w - 0.25, trr.h, tx, size=t.size_body, color='dark', role='medium',
                    anchor='middle', fit=True, min_size=9, emph='emph')
    if notes:
        cv.notes(notes)
    return cv


@layout
def innovations(deck, title, items, subtitle=None, footer=None, num=None, en=None, source=None, notes=None,
                section=None, visual=None, image=None, caption=None):
    """创新点 / 项目特色: numbered rows (navy '01' square + navy tab label + text with [[red]] emphasis).
    items: [{'tag': '技术创新', 'text': '...'}]. footer: bottom light line (e.g. '为...提供创新的技术解决方案').
    image/visual: optional figure on the right third."""
    t = deck.theme
    cv = deck.page(title, en, source=source, section=section, num=num)
    box = cv.content
    y = box.y
    if subtitle:
        A.statement(cv, box.x, y, box.w, subtitle, style='centered', size=t.size_body + 2)
        y += 0.6
    bottom = box.b - (0.6 if footer else 0)
    area = Box(box.x, y, box.w, bottom - y)
    if image or visual:
        area, fb = area.split(0.64, gap=0.25)
        if visual:
            visual(cv, fb)
        else:
            A.figure(cv, fb, image, caption)
    n = len(items)
    rows = area.rows(n, gap=0.18)
    for i, (r, it) in enumerate(zip(rows, items)):
        cv.rect(r.x + 0.3, r.y + 0.22, r.w - 0.3, r.h - 0.22, fill='FFFFFF', line='panel_line', line_w=0.75,
                name='deco:innov', shadow={'color': 'primary_deep', 'alpha': 0.08, 'blur': 10, 'dist': 2})
        A.num_square(cv, r.x, r.y + 0.22 + (r.h - 0.22) / 2 - 0.25, i + 1, size=0.5)
        tw = max(1.6, cv.width_of(it.get('tag', ''), 15, role='title', bold=True) + 0.5)
        A.ribbon(cv, r.x + 0.75, r.y, tw, it.get('tag', ''), h=0.42, size=15, shape=A.header_shape(cv))
        cv.text(r.x + 0.75, r.y + 0.5, r.w - 1.0, r.h - 0.58, it.get('text', ''), size=t.size_body + 1, color='dark',
                role='medium', anchor='middle', fit=True, min_size=10, emph='emph')
    if footer:
        cv.rect(box.x, box.b - 0.48, box.w, 0.48, grad=[(0, 'panel', 0.3), (50, 'panel', 1.0), (100, 'panel', 0.3)],
                grad_angle=0, name='deco:footer')
        cv.text(box.x, box.b - 0.48, box.w, 0.48, footer, size=t.size_body + 1, color='primary', role='title',
                align='center', anchor='middle', wrap=False, fit=True, min_size=10, emph='emph')
    if notes:
        cv.notes(notes)
    return cv


@layout
def achievements(deck, title, stats, images=None, headline=None, footer=None, num=None, en=None,
                 source=None, notes=None, section=None, captions=None):
    """成果/进度: headline (centered ▪▪▪ line), a row of images (papers/certificates) with red stat numbers under
    them, optional schedule strip (see schedule())."""
    t = deck.theme
    cv = deck.page(title, en, source=source, section=section, num=num)
    box = cv.content
    y = box.y
    if headline:
        A.statement(cv, box.x, y, box.w, headline, style='centered', size=t.size_body + 2)
        y += 0.6
    bottom = box.b - (0.6 if footer else 0)
    stats_h = 1.0
    img_h = (bottom - y - stats_h - 0.1) if images else 0
    if images:
        cells = Box(box.x, y, box.w, img_h).cols(len(images), gap=0.18)
        for i, (c, im) in enumerate(zip(cells, images)):
            A.figure(cv, c, im, (captions[i] if captions and i < len(captions) else None), frame=True)
        y += img_h + 0.1
    scells = Box(box.x, y, box.w, stats_h).cols(len(stats), gap=0.15)
    for c, s in zip(scells, stats):
        A.stat(cv, c, s.get('value'), s.get('unit', ''), s.get('label', ''))
    if footer:
        A.conclusion(cv, footer, y=box.b - 0.5, x=box.x, w=box.w, h=0.5)
    if notes:
        cv.notes(notes)
    return cv


@layout
def schedule(deck, title, periods, tasks, statement=None, num=None, en=None, source=None, notes=None, section=None,
             sub_periods=None):
    """Gantt-style research schedule. periods: ['2026', '2027', ...]; sub_periods: e.g. ['1-6月', '7-12月'];
    tasks: [{'name': '研究内容一', 'desc': '...', 'span': (start, end) in sub-period units (0-based, end exclusive),
    'color': optional}]."""
    t = deck.theme
    cv = deck.page(title, en, source=source, section=section, num=num)
    box = cv.content
    y = box.y
    if statement:
        y += A.statement(cv, box.x, y, box.w, statement) + 0.2
    sp = sub_periods or ['']
    ns = len(periods) * len(sp)
    lw = 2.9
    gx, gw = box.x + lw, box.w - lw
    cw = gw / ns
    hh1, hh2 = 0.44, (0.36 if sub_periods else 0)
    cv.rect(box.x, y, lw, hh1 + hh2, fill='primary_deep', name='deco:gh')
    cv.text(box.x, y, lw, hh1 + hh2, '研究内容', size=15, color='FFFFFF', role='title', align='center',
            anchor='middle', wrap=False, fit=True)
    for i, pnm in enumerate(periods):
        x = gx + i * len(sp) * cw
        cv.rect(x, y, len(sp) * cw, hh1, fill='primary', line='FFFFFF', line_w=0.75, name='deco:gh')
        cv.text(x, y, len(sp) * cw, hh1, pnm, size=14, color='FFFFFF', role='title', align='center', anchor='middle',
                wrap=False, fit=True)
        if sub_periods:
            for j, s in enumerate(sp):
                xx = x + j * cw
                cv.rect(xx, y + hh1, cw, hh2, fill='primary+25', line='FFFFFF', line_w=0.75, name='deco:gh2')
                cv.text(xx, y + hh1, cw, hh2, s, size=11.5, color='FFFFFF', role='medium', align='center',
                        anchor='middle', wrap=False, fit=True)
    y += hh1 + hh2
    n = len(tasks)
    rh = min(0.95, (box.b - y) / max(1, n))
    palette = ['primary', 'secondary', 'accent', 'emph', 'primary+30']
    for i, tk in enumerate(tasks):
        yy = y + i * rh
        cv.rect(box.x, yy, box.w, rh, fill='panel_light' if i % 2 == 0 else 'FFFFFF', line='panel_line', line_w=0.5,
                name='deco:grow')
        cv.text(box.x + 0.12, yy, lw - 0.2, rh * (0.55 if tk.get('desc') else 1), tk.get('name', ''), size=14,
                color='primary_deep', role='title', anchor='middle' if not tk.get('desc') else 'bottom', wrap=False,
                fit=True, min_size=9)
        if tk.get('desc'):
            cv.text(box.x + 0.12, yy + rh * 0.55, lw - 0.2, rh * 0.42, tk['desc'], size=11, color='text',
                    role='medium', wrap=False, fit=True, min_size=8)
        s0, s1 = tk.get('span', (0, ns))
        col = tk.get('color') or palette[i % len(palette)]
        bx = gx + s0 * cw + 0.05
        cv.rect(bx, yy + rh * 0.25, (s1 - s0) * cw - 0.1, rh * 0.5, radius=0.06,
                grad=[(0, col + '+35' if '#' not in col else col, 1.0), (100, col, 1.0)], grad_angle=0,
                name='deco:gbar')
        if tk.get('label'):
            cv.text(bx, yy + rh * 0.25, (s1 - s0) * cw - 0.1, rh * 0.5, tk['label'], size=11.5, color='FFFFFF',
                    role='title', align='center', anchor='middle', wrap=False, fit=True, min_size=8)
    if notes:
        cv.notes(notes)
    return cv


@layout
def profile(deck, title, name, groups, role=None, photo=None, direction=None, conclusion=None, num=None, en=None,
            source=None, notes=None, section=None):
    """个人基本情况: photo card left; right: 研究方向 row + grouped rows with vertical navy labels.
    groups: [{'label': '教育经历', 'rows': [('2023-至今', '科研科技大学', '集成电路科学与工程', '博士'), ...]}]
    (first cell navy bold, last cell red bold)."""
    t = deck.theme
    cv = deck.page(title, en, source=source, section=section, num=num)
    box = cv.content
    bottom = box.b - (0.72 if conclusion else 0)
    lb, rb = Box(box.x, box.y, box.w, bottom - box.y).split(0.24, gap=0.3)
    cv.rect(lb.x, lb.y, lb.w, lb.h, fill='FFFFFF', line='panel_line', line_w=0.75, name='deco:photocard',
            shadow={'color': 'primary_deep', 'alpha': 0.1, 'blur': 12, 'dist': 3})
    ph = Box(lb.x + 0.2, lb.y + 0.2, lb.w - 0.4, lb.h * 0.62)
    if photo:
        cv.image(photo, ph.x, ph.y, ph.w, ph.h, fit='cover', name='img:photo')
    else:
        cv.rect(ph.x, ph.y, ph.w, ph.h, fill='panel', name='deco:photo')
        cv.icon('user', ph.cx - 0.5, ph.cy - 0.5, 1.0, 'primary+50')
    cv.text(lb.x, ph.b + 0.15, lb.w, 0.6, name, size=28, color='primary_deep', role='serif', bold=True,
            align='center', anchor='middle', wrap=False, fit=True)
    if role:
        cv.line(lb.x + 0.5, ph.b + 0.82, lb.r - 0.5, ph.b + 0.82, 'primary+40', 1.0)
        cv.text(lb.x, ph.b + 0.9, lb.w, 0.4, role, size=14, color='dark', role='title', align='center', wrap=False,
                fit=True)
    cv.rect(rb.x, rb.y, rb.w, rb.h, fill='FFFFFF', line='panel_line', line_w=0.75, name='deco:infocard')
    y = rb.y + 0.15
    if direction:
        cv.rect(rb.x + 0.15, y, rb.w - 0.3, 0.55, fill='panel', name='deco:dirbar')
        cv.icon('circle-play', rb.x + 0.3, y + 0.12, 0.32, 'primary')
        cv.text(rb.x + 0.8, y, rb.w - 1.0, 0.55, '研究方向：' + direction, size=t.size_body + 1, color='dark',
                role='title', anchor='middle', wrap=False, fit=True, min_size=10)
        y += 0.72
    ng = len(groups)
    tot_rows = sum(len(g['rows']) for g in groups)
    avail = rb.b - 0.15 - y - 0.15 * (ng - 1)
    rh = min(0.62, avail / max(1, tot_rows))
    for g in groups:
        gh = rh * len(g['rows'])
        A.vlabel(cv, rb.x + 0.15, y, 0.55, gh, g['label'])
        for i, row in enumerate(g['rows']):
            yy = y + i * rh
            cells = list(row)
            xs = [0.95, 2.85, 5.3]
            cv.text(rb.x + 0.85, yy, 0.3, rh, '➢', size=13, color='primary', wrap=False, fit=False, anchor='middle')
            widths = [1.9, 2.4, rb.w - 0.85 - 5.3 - 1.4]
            for k, cell in enumerate(cells[:3]):
                cv.text(rb.x + xs[k] + 0.15, yy, widths[k], rh, cell, size=t.size_body,
                        color='primary' if k == 0 else 'dark', role='title', anchor='middle', wrap=False, fit=True,
                        min_size=9)
            if len(cells) > 3:
                cv.text(rb.r - 1.45, yy, 1.3, rh, cells[3], size=t.size_body, color='emph', role='title',
                        align='right', anchor='middle', wrap=False, fit=True, min_size=9)
            if i < len(g['rows']) - 1:
                cv.line(rb.x + 0.85, yy + rh, rb.r - 0.15, yy + rh, 'panel_line', 0.75, dash='dash')
        y += gh + 0.15
    if conclusion:
        A.conclusion(cv, conclusion, y=box.b - 0.6, x=box.x, w=box.w, h=0.6, style='yellow', serif=True)
    if notes:
        cv.notes(notes)
    return cv


@layout
def layers(deck, title, levels, statement=None, side=None, conclusion=None, num=None, en=None, source=None,
           notes=None, section=None):
    """Layered architecture (e.g. 数字孪生水网: 感知层/数据层/模型层/应用层). levels (top -> bottom):
    [{'label': '应用层', 'items': ['智能调度', '安全预警', ...]}]. side: optional right column
    {'header': '支撑体系', 'points': [...]} drawn as a tall panel."""
    t = deck.theme
    cv = deck.page(title, en, source=source, section=section, num=num)
    box = cv.content
    y = box.y
    if statement:
        y += A.statement(cv, box.x, y, box.w, statement) + 0.18
    bottom = box.b - (0.7 if conclusion else 0)
    area = Box(box.x, y, box.w, bottom - y)
    if side:
        area, sb = area.split(0.78, gap=0.2)
        inner = A.panel(cv, sb, header=side.get('header'), header_style='strip')
        A.arrow_list(cv, inner, side.get('points', []), size=t.size_body)
    n = len(levels)
    rows = area.rows(n, gap=0.14)
    for i, (r, lv) in enumerate(zip(rows, levels)):
        lw = 1.75
        k = i / max(1, n - 1)
        cv.rect(r.x, r.y, lw, r.h, grad=[(0, 'primary_deep', 1.0), (100, 'primary', 1.0)], grad_angle=90,
                name='deco:layerlab')
        cv.text(r.x + 0.05, r.y, lw - 0.1, r.h, lv.get('label', ''), size=t.size_body + 2, color='FFFFFF',
                role='title', align='center', anchor='middle', wrap=True, fit=True, min_size=10)
        body = Box(r.x + lw + 0.12, r.y, r.w - lw - 0.12, r.h)
        cv.rect(body.x, body.y, body.w, body.h, fill='panel', line='panel_line', line_w=0.5, name='deco:layerbody')
        items = lv.get('items', [])
        if items:
            cells = body.inset(0.14, 0.12).cols(len(items), gap=0.12)
            for c, it in zip(cells, items):
                cv.rect(c.x, c.y, c.w, c.h, fill='FFFFFF', line='primary+55', line_w=0.75, radius=0.04,
                        name='deco:chip')
                cv.text(c.x + 0.05, c.y, c.w - 0.1, c.h, it, size=t.size_body, color='primary_deep', role='title',
                        align='center', anchor='middle', fit=True, min_size=9, max_lines=2)
        if i < n - 1:
            A.block_arrow(cv, r.x + lw / 2 - 0.12, r.b - 0.02, 0.24, 0.18, 'up', color='primary+30')
    if conclusion:
        A.conclusion(cv, conclusion, y=box.b - 0.55, x=box.x, w=box.w, h=0.55)
    if notes:
        cv.notes(notes)
    return cv


@layout
def milestones(deck, title, events, statement=None, highlight=None, conclusion=None, num=None, en=None,
               source=None, notes=None, section=None, stats=None):
    """Milestone timeline: gradient axis with nodes, navy year pills, event boxes alternating above/below.
    events: [{'date': '2014.12', 'title': '...', 'text': '...'}]. stats: optional red-number row on top."""
    t = deck.theme
    cv = deck.page(title, en, source=source, section=section, num=num)
    box = cv.content
    y = box.y
    if statement:
        y += A.statement(cv, box.x, y, box.w, statement) + 0.15
    if stats:
        sh = 1.0
        cells = Box(box.x, y, box.w, sh).cols(len(stats), gap=0.12)
        for c, s_ in zip(cells, stats):
            cv.rect(c.x, c.y, c.w, c.h, fill='panel_light', line='panel_line', line_w=0.5, name='deco:statbg')
            A.stat(cv, c.inset(0.05, 0.06), s_.get('value'), s_.get('unit', ''), s_.get('label', ''))
        y += sh + 0.15
    bottom = box.b - (0.7 if conclusion else 0)
    area = Box(box.x, y, box.w, bottom - y)
    n = len(events)
    hl = (highlight % n) if highlight is not None else None
    ay = area.y + area.h / 2
    slot = area.w / n
    xs = [area.x + slot * (i + 0.5) for i in range(n)]
    A.axis(cv, area.x, ay, area.w, xs, h=0.14)
    eh = area.h / 2 - 0.5
    for i, e in enumerate(events):
        cx = xs[i]
        on = i == hl
        pw = min(slot - 0.1, max(1.1, cv.width_of(e.get('date', ''), 14, role='number', bold=True) + 0.4))
        up = i % 2 == 0
        py = ay - 0.62 if up else ay + 0.24
        cv.rect(cx - pw / 2, py, pw, 0.38, fill='emph' if on else 'primary_deep', radius=0.19, name='deco:yearpill')
        cv.text(cx - pw / 2, py, pw, 0.38, e.get('date', ''), size=14, color='FFFFFF', role='number', bold=True,
                align='center', anchor='middle', wrap=False, fit=True, min_size=9)
        bw = min(slot * 1.9, 3.3)
        bx = min(max(cx - bw / 2, area.x), area.r - bw)
        need = 0.52 + (cv.measure(e.get('text', ''), bw - 0.24, t.size_body - 1, role='medium') + 0.12
                       if e.get('text') else 0)
        avail = eh - 0.2 if up else area.b - (ay + 0.72)
        bh = min(avail, max(need, 0.9))
        by = (ay - 0.72 - bh) if up else ay + 0.72
        cv.rect(bx, by, bw, bh, fill='FFFFFF', line='emph' if on else 'panel_line', line_w=1.0 if on else 0.75,
                name='deco:eventbox', shadow={'color': 'primary_deep', 'alpha': 0.06, 'blur': 8, 'dist': 2})
        cv.text(bx + 0.1, by + 0.06, bw - 0.2, 0.4, e.get('title', ''), size=t.size_body + 1,
                color='emph' if on else 'primary', role='title', align='center', wrap=False, fit=True, min_size=9)
        if e.get('text'):
            cv.text(bx + 0.12, by + 0.48, bw - 0.24, bh - 0.55, e['text'], size=t.size_body - 1, color='dark',
                    role='medium', align='center', fit=True, min_size=9)
        cv.line(cx, (by + bh) if up else by, cx, py if up else py + 0.38, 'primary+40', 1.0, dash='sysDash')
    if conclusion:
        A.conclusion(cv, conclusion, y=box.b - 0.55, x=box.x, w=box.w, h=0.55)
    if notes:
        cv.notes(notes)
    return cv


# =========================================================================== registry for defense-only pages
for _fn in (panels, columns, problems, figure_text, route, innovations, achievements, schedule, profile, layers,
            milestones):
    REGISTRY[_fn.__name__] = _fn
