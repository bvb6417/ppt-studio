"""Styled native tables.

style:
  'header'     header row in main color + white bold text, very light zebra rows, hairline row rules (business)
  'three_line' academic 三线表: thick top rule, thin header rule, thick bottom rule, no fills / verticals
  'minimal'    header text in main color, hairline rules only
  'card'       like header but placed on a white shadow card (call card() yourself or use layouts.table_page)
highlight_col: column index (or list of indices) to emphasize; highlight_mode 'fill' (pale tint + bold main-color text) or
  'raised' (a main-color gradient card with shadow behind that column, white text) — the '凸起' trick.
"""
from __future__ import annotations

from lxml import etree

from . import oxml as X
from .canvas import plain
from .units import emu

NO_STYLE = '{2D5ABB26-0587-4C30-8999-92F81FD0307C}'
TCPR_ORDER = ['lnL', 'lnR', 'lnT', 'lnB', 'lnTlToBr', 'lnBlToTr', 'cell3D', 'noFill', 'solidFill', 'gradFill',
              'blipFill', 'pattFill', 'grpFill', 'headers', 'extLst']


def _border(tcPr, side, hexclr=None, width_pt=0.75):
    tag = {'L': 'lnL', 'R': 'lnR', 'T': 'lnT', 'B': 'lnB'}[side]
    X.remove_children(tcPr, [tag])
    ln = etree.Element(X.qn('a:' + tag), w=str(int(width_pt * 12700)), cap='flat', cmpd='sng', algn='ctr')
    if hexclr:
        ln.append(X.solid_fill_el(hexclr))
        etree.SubElement(ln, X.qn('a:prstDash'), val='solid')
    else:
        etree.SubElement(ln, X.qn('a:noFill'))
    X.insert_ordered(tcPr, ln, TCPR_ORDER)


def _cell_fill(tcPr, hexclr=None, alpha=1.0):
    X.remove_children(tcPr, ['noFill', 'solidFill', 'gradFill'])
    el = X.solid_fill_el(hexclr, alpha) if hexclr else etree.Element(X.qn('a:noFill'))
    X.insert_ordered(tcPr, el, TCPR_ORDER)


_BREAK_AFTER = set('/、，,；;：:）)] ')


def _balanced_break(text, width_pt, size, ea, lat, bold=False):
    """If the cell text wraps leaving a <= 2-char last line, return an index that splits it into two balanced
    lines at a natural boundary (after / 、 ， or between Latin and CJK); else None."""
    from . import fonts as F
    lines = F.wrap(text, width_pt, size, ea, lat, bold)
    if len(lines) != 2 or len(lines[-1].strip()) > 2:
        return None
    n = len(text)
    best, best_score = None, 1e9
    for i in range(2, n - 1):
        a, b = text[i - 1], text[i]
        natural = a in _BREAK_AFTER or (a.isascii() and a.isalnum() and F.is_cjk(b)) or \
            (F.is_cjk(a) and b.isascii() and b.isalnum())
        inside_word = a.isascii() and a.isalnum() and b.isascii() and b.isalnum()
        if inside_word or b in F.NO_START:
            continue
        if not (natural or (F.is_cjk(a) and F.is_cjk(b))):
            continue
        # both halves must fit on one line
        if F.text_width(text[:i], size, ea, lat, bold) > width_pt or F.text_width(text[i:], size, ea, lat, bold) > width_pt:
            continue
        score = abs(i - n / 2) - (1.5 if natural else 0)
        if score < best_score:
            best, best_score = i, score
    return best


def _fix_orphans(cv, cws, columns, rows, fs, pad_x, rounds=12):
    """Widen columns whose cells wrap leaving <= 2 characters on the last line, taking width from columns
    with slack (width beyond their longest single-line cell)."""
    from . import fonts as F
    from .canvas import plain
    ea, lat, _ = cv.t.font('body')
    ncol = len(cws)
    allrows = ([columns] if columns else []) + [list(map(str, r)) for r in rows]

    def single(ci):
        return max(cv.width_of(r[ci], fs) for r in allrows) + 2 * pad_x

    for _ in range(rounds):
        bad = None
        for ci in range(ncol):
            for r in allrows:
                lines = F.wrap(plain(r[ci]), (cws[ci] - 2 * pad_x) * 72 * 0.97, fs, ea, lat)
                if len(lines) > 1 and len(lines[-1].strip()) <= 2:
                    bad = ci
                    break
            if bad is not None:
                break
        if bad is None:
            break
        step = fs / 72 * 1.2
        slack = [(cws[cj] - single(cj), cj) for cj in range(ncol) if cj != bad]
        slack.sort(reverse=True)
        if not slack or slack[0][0] < step * 0.5:
            break
        give = min(step, slack[0][0])
        cws[slack[0][1]] -= give
        cws[bad] += give
    return cws


def table(cv, x, y, w, h, columns, rows, style='header', col_widths=None, align=None, font_size=None,
          header_size=None, highlight_col=None, highlight_mode='fill', highlight_rows=None, first_col_bold=False,
          zebra=True, fit=True, max_row_h=None, name='table', header=True):
    """columns: header labels; rows: list of lists (strings; '**x**'/'[[x]]' markup ok).
    Returns (graphicframe, geometry dict with col x-positions and row y-positions)."""
    t = cv.t
    ncol = len(columns) if columns else len(rows[0])
    nrow = len(rows) + (1 if header else 0)
    fs = font_size or max(t.size_min, t.size_body - 2)
    hs = header_size or fs
    ea, lat, _ = t.font('body')
    pad_x, pad_y = 0.1, 0.05
    # --- column widths proportional to content
    if col_widths:
        tot = sum(col_widths)
        cws = [w * c / tot for c in col_widths]
    else:
        need = []
        for ci in range(ncol):
            cells = ([columns[ci]] if header else []) + [str(r[ci]) for r in rows]
            m = max(cv.width_of(c, fs, bold=(header and c == columns[ci])) for c in cells) * 1.04 + 2 * pad_x
            need.append(max(m, 0.7))
        if sum(need) <= w:
            # everything fits on one line: give each column what it needs, spread the rest evenly-ish
            extra = w - sum(need)
            cws = [c + extra * (0.5 / ncol + 0.5 * c / sum(need)) for c in need]
        else:
            need = [min(c, w * 0.55) for c in need]
            tot = sum(need)
            cws = [w * c / tot for c in need]
            avg = w / ncol
            cws = [0.75 * c + 0.25 * avg for c in cws]
            s_ = sum(cws)
            cws = [c * w / s_ for c in cws]
        cws = _fix_orphans(cv, cws, columns if header else None, rows, fs, pad_x)

    def heights(size, hsize):
        hh = []
        for ri in range(nrow):
            is_head = header and ri == 0
            cells = columns if is_head else rows[ri - (1 if header else 0)]
            sz = hsize if is_head else size
            mh = 0
            for ci in range(ncol):
                txt = str(cells[ci])
                mh = max(mh, cv.measure(txt, cws[ci] - 2 * pad_x, sz, bold=is_head, ls=1.1))
            hh.append(mh + 2 * pad_y + 0.06)
        return hh

    hh = heights(fs, hs)
    while fit and sum(hh) > h and fs > max(9, t.size_min - 3):
        fs -= 0.5
        hs = min(hs, fs + 1)
        hh = heights(fs, hs)
    # distribute spare height (cap row height)
    spare = h - sum(hh)
    if spare > 0:
        cap = max_row_h or 0.62
        add = spare / nrow
        hh = [min(max(v, v + add), max(v, cap)) for v in hh]
    total_h = sum(hh)
    # --- raised highlight card behind column
    col_x = [x]
    for cw in cws:
        col_x.append(col_x[-1] + cw)
    row_y = [y]
    for v in hh:
        row_y.append(row_y[-1] + v)
    hcols = set()
    if highlight_col is not None:   # one column index or several (fill mode)
        hcols = {c_ % ncol for c_ in (highlight_col if isinstance(highlight_col, (list, tuple, set)) else [highlight_col])}
    if hcols and highlight_mode == 'raised':
        hc = min(hcols)
        cv.rect(col_x[hc] + 0.02, y - 0.1, cws[hc] - 0.04, total_h + 0.2, radius=0.08,
                grad=[('secondary', 1.0), ('primary', 1.0)], grad_angle=90, shadow='strong', name='deco:colcard')
    gf = cv.slide.shapes.add_table(nrow, ncol, emu(x), emu(y), emu(w), emu(total_h))
    gf.name = 'table:' + name
    tbl = gf.table
    tblPr = tbl._tbl.tblPr
    for k in ('firstRow', 'bandRow', 'firstCol', 'lastRow', 'lastCol', 'bandCol'):
        tblPr.set(k, '0')
    sid = tblPr.find(X.qn('a:tableStyleId'))
    if sid is None:
        sid = etree.SubElement(tblPr, X.qn('a:tableStyleId'))
    sid.text = NO_STYLE
    for ci, cw in enumerate(cws):
        tbl.columns[ci].width = emu(cw)
    for ri, rh in enumerate(hh):
        tbl.rows[ri].height = emu(rh)
    prim, pale, bg = t.c('primary'), t.c('primary_bg'), t.c('surface')
    line = t.c('line')
    dark = t.c('dark')
    hl_rows = set(highlight_rows or [])
    for ri in range(nrow):
        is_head = header and ri == 0
        data_i = ri - (1 if header else 0)
        cells = columns if is_head else rows[data_i]
        for ci in range(ncol):
            cell = tbl.cell(ri, ci)
            tcPr = cell._tc.get_or_add_tcPr()
            tcPr.set('anchor', 'ctr')
            for k, v in (('marL', pad_x), ('marR', pad_x), ('marT', pad_y), ('marB', pad_y)):
                tcPr.set(k, str(emu(v)))
            hc = ci in hcols
            # fills
            fill, fcol, fbold = None, t.c('text'), False
            if style in ('header', 'card'):
                if is_head:
                    fill, fcol, fbold = prim, 'FFFFFF', True
                elif zebra and data_i % 2 == 1:
                    fill = pale
                else:
                    fill = bg if not t.is_dark else None
            elif style == 'minimal':
                if is_head:
                    fcol, fbold = prim, True
            elif style == 'three_line':
                if is_head:
                    fcol, fbold = dark, True
            if data_i in hl_rows and not is_head:
                fill = t.c('primary+82') if not t.is_dark else t.c('line')
                fbold = True
            if hc:
                if highlight_mode == 'raised':
                    fill, fcol, fbold = None, 'FFFFFF', True
                elif not is_head:
                    fill, fcol, fbold = t.c('primary+84') if not t.is_dark else t.c('line'), prim, True
            if first_col_bold and ci == 0 and not is_head:
                fbold = True
            _cell_fill(tcPr, fill)
            # borders
            for side in 'LR':
                _border(tcPr, side, None)
            if style == 'three_line':
                _border(tcPr, 'T', dark if ri == 0 else (dark if ri == 1 and header else None), 1.5 if ri == 0 else 0.75)
                _border(tcPr, 'B', dark if ri == nrow - 1 else (dark if is_head else None),
                        1.5 if ri == nrow - 1 else 0.75)
            elif style in ('header', 'card', 'minimal'):
                _border(tcPr, 'T', None)
                _border(tcPr, 'B', (prim if (is_head and style == 'minimal') else line) if not hc or highlight_mode != 'raised' else None,
                        1.0 if is_head else 0.75)
            # text
            tf = cell.text_frame
            tf.word_wrap = True
            txt = str(cells[ci])
            p = tf.paragraphs[0]
            al = (align[ci] if align else ('left' if ci == 0 else 'center'))
            X.set_para(p, align=al, line_spacing=1.1, bullet='')
            from .canvas import parse_markup, plain as _plain
            csz = hs if is_head else fs
            brk = _balanced_break(_plain(txt), (cws[ci] - 2 * pad_x) * 72 * 0.97, csz, ea, lat, fbold)
            offset = 0
            for seg, kind in parse_markup(txt):
                col = fcol if kind != 'emph' else (t.c('emph') if not (hc and highlight_mode == 'raised') else 'FFFFFF')
                if kind and kind.startswith('color:'):
                    col = t.c(kind[6:])
                pieces = [seg]
                if brk is not None and offset < brk < offset + len(seg):
                    pieces = [seg[:brk - offset], None, seg[brk - offset:]]
                elif brk is not None and brk == offset and offset > 0:
                    pieces = [None, seg]
                offset += len(seg)
                for piece in pieces:
                    if piece is None:
                        p.add_line_break()
                        continue
                    if not piece:
                        continue
                    r = p.add_run()
                    r.text = piece
                    X.style_run(r, size=csz, bold=fbold or bool(kind),
                                hexclr=col if col.startswith('#') is False and len(col) == 6 else t.c(col),
                                ea=ea, latin=lat)
    geo = dict(col_x=col_x, row_y=row_y, font_size=fs, height=total_h)
    return gf, geo
