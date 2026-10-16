"""Native (editable) PowerPoint charts styled like the reference decks:
no chart title (the slide title states the conclusion), faint or no gridlines, data labels on,
key bar/point highlighted in the main color while the rest are light gray / pale tint.
"""
from __future__ import annotations

from lxml import etree
from pptx.chart.data import CategoryChartData, XyChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION, XL_TICK_LABEL_POSITION
from pptx.util import Pt

from . import oxml as X
from .units import emu

KINDS = {
    'column': XL_CHART_TYPE.COLUMN_CLUSTERED, 'bar': XL_CHART_TYPE.BAR_CLUSTERED,
    'stacked': XL_CHART_TYPE.COLUMN_STACKED, 'stacked_bar': XL_CHART_TYPE.BAR_STACKED,
    'stacked100': XL_CHART_TYPE.COLUMN_STACKED_100, 'line': XL_CHART_TYPE.LINE_MARKERS,
    'line_plain': XL_CHART_TYPE.LINE, 'area': XL_CHART_TYPE.AREA, 'pie': XL_CHART_TYPE.PIE,
    'donut': XL_CHART_TYPE.DOUGHNUT, 'scatter': XL_CHART_TYPE.XY_SCATTER, 'radar': XL_CHART_TYPE.RADAR_MARKERS,
}
C_NS = 'http://schemas.openxmlformats.org/drawingml/2006/chart'


def _cq(tag):
    return '{%s}%s' % (C_NS, tag)


def _font(font, size, hexclr, ea, latin, bold=None):
    """Style a python-pptx chart Font (dLbls / tick labels / legend / chart) incl. East-Asian face."""
    font.size = Pt(size)
    if bold is not None:
        font.bold = bold
    font.color.rgb = _rgbc(hexclr)
    rPr = font._rPr
    X.remove_children(rPr, ['latin', 'ea', 'cs'])
    X.insert_ordered(rPr, etree.Element(X.qn('a:latin'), typeface=latin), X.RPR_ORDER)
    X.insert_ordered(rPr, etree.Element(X.qn('a:ea'), typeface=ea), X.RPR_ORDER)


def _sppr_line(el, hexclr=None, width_pt=0.75):
    sp = el.find(_cq('spPr'))
    if sp is None:
        sp = etree.SubElement(el, _cq('spPr'))
    for ch in list(sp):
        sp.remove(ch)
    ln = etree.SubElement(sp, X.qn('a:ln'), w=str(int(width_pt * 12700)))
    if hexclr:
        ln.append(X.solid_fill_el(hexclr))
    else:
        etree.SubElement(ln, X.qn('a:noFill'))
    return sp


def chart(cv, x, y, w, h, kind='column', categories=(), series=None, highlight=None, colors=None,
          labels=True, number_format='General', legend=None, gridlines=False, axis=True, font_size=11,
          gap=70, overlap=None, smooth=True, hole=62, label_pos=None, value_axis=False, max_value=None,
          min_value=None, gradient=True, show_percent=None, label_color=None, name='chart'):
    """series: {'name': [values...]} (ordered) or list of (name, values). highlight: index or list of indices
    of categories to emphasize (single-series bar/column/pie). Returns the python-pptx chart object."""
    t = cv.t
    series = series or {}
    items = list(series.items()) if isinstance(series, dict) else list(series)
    kind_enum = KINDS[kind]
    if kind == 'scatter':
        cd = XyChartData()
        for nm, pts in items:
            s = cd.add_series(nm)
            for px, py in pts:
                s.add_data_point(px, py)
    else:
        cd = CategoryChartData(number_format=number_format)
        cd.categories = list(categories)
        for nm, vals in items:
            cd.add_series(nm, list(vals))
    gf = cv.slide.shapes.add_chart(kind_enum, emu(x), emu(y), emu(w), emu(h), cd)
    gf.name = 'chart:' + name
    ch = gf.chart
    ea, lat, _ = t.font('body')
    ch.has_title = False
    ch.font.size = Pt(font_size)
    txt = t.c('text')
    muted = t.c('muted')
    cs = ch._chartSpace
    # chart-level text props (ea font)
    _font(ch.font, font_size, txt, ea, lat)
    # transparent chart area: spPr goes right after <c:chart>
    old = cs.find(_cq('spPr'))
    if old is not None:
        cs.remove(old)
    sp = etree.Element(_cq('spPr'))
    etree.SubElement(sp, X.qn('a:noFill'))
    ln = etree.SubElement(sp, X.qn('a:ln'))
    etree.SubElement(ln, X.qn('a:noFill'))
    cs.find(_cq('chart')).addnext(sp)
    n_series = len(items)
    colors = colors or t.ramp(max(n_series, len(categories) if kind in ('pie', 'donut') else n_series))
    hl = set([highlight] if isinstance(highlight, int) else (highlight or []))
    hl = {i if i >= 0 else len(categories) + i for i in hl}
    plot = ch.plots[0]
    # legend
    show_legend = legend if legend is not None else (n_series > 1 or kind in ('pie', 'donut'))
    ch.has_legend = bool(show_legend)
    if show_legend:
        ch.legend.position = XL_LEGEND_POSITION.BOTTOM if kind not in ('pie', 'donut') else XL_LEGEND_POSITION.RIGHT
        ch.legend.include_in_layout = False
        _font(ch.legend.font, font_size, muted, ea, lat)
    pale = t.c('primary+78') if not t.is_dark else t.c('line')
    if kind in ('column', 'bar', 'stacked', 'stacked_bar', 'stacked100'):
        plot.gap_width = gap
        if overlap is not None:
            plot.overlap = overlap
        elif n_series > 1 and kind in ('column', 'bar'):
            plot.overlap = -12
        for si, s in enumerate(plot.series):
            base = t.c(colors[si % len(colors)])
            _fill_series(s, base, gradient and n_series == 1, t, kind)
            if n_series == 1 and hl:
                for pi in range(len(categories)):
                    pt = s.points[pi]
                    if pi in hl:
                        _fill_point(pt, base, gradient, t, kind)
                    else:
                        pt.format.fill.solid()
                        pt.format.fill.fore_color.rgb = _rgbc(pale)
    elif kind in ('line', 'line_plain', 'area', 'radar'):
        for si, s in enumerate(plot.series):
            col = t.c(colors[si % len(colors)])
            if kind == 'area':
                _area_fill(s, col)
            else:
                s.format.line.color.rgb = _rgbc(col)
                s.format.line.width = Pt(2.25)
                s.smooth = smooth
                try:
                    from pptx.enum.chart import XL_MARKER_STYLE
                    s.marker.style = XL_MARKER_STYLE.CIRCLE
                    s.marker.size = 7
                    s.marker.format.fill.solid()
                    s.marker.format.fill.fore_color.rgb = _rgbc('FFFFFF' if not t.is_dark else t.bg)
                    s.marker.format.line.color.rgb = _rgbc(col)
                    s.marker.format.line.width = Pt(1.75)
                except Exception:
                    pass
    elif kind in ('pie', 'donut'):
        s = plot.series[0]
        for pi in range(len(categories)):
            pt = s.points[pi]
            pt.format.fill.solid()
            c = t.c(colors[pi % len(colors)])
            if hl and pi not in hl:
                c = pale
            pt.format.fill.fore_color.rgb = _rgbc(c)
            pt.format.line.color.rgb = _rgbc('FFFFFF' if not t.is_dark else t.bg)
            pt.format.line.width = Pt(1.5)
        if kind == 'donut':
            dn = ch._chartSpace.find('.//' + _cq('doughnutChart'))
            hs = dn.find(_cq('holeSize'))
            if hs is None:
                hs = etree.SubElement(dn, _cq('holeSize'))
            hs.set('val', str(hole))
    # data labels
    if labels:
        plot.has_data_labels = True
        dl = plot.data_labels
        dl.font.size = Pt(font_size)
        if kind in ('pie', 'donut'):
            show_pct = True if show_percent is None else show_percent
            dl.show_percentage = show_pct
            dl.show_value = not show_pct
            dl.show_category_name = False
            dl.number_format = '0%' if show_pct else number_format
            dl.number_format_is_linked = False
            if kind == 'pie':  # doughnut charts must NOT carry <c:dLblPos> (PowerPoint rejects the file)
                try:
                    dl.position = label_pos or XL_LABEL_POSITION.OUTSIDE_END
                except Exception:
                    pass
        else:
            dl.show_value = True
            dl.number_format = number_format
            dl.number_format_is_linked = number_format == 'General'
            try:
                if kind in ('column', 'bar'):
                    dl.position = label_pos or XL_LABEL_POSITION.OUTSIDE_END
                elif kind in ('line', 'line_plain'):
                    dl.position = label_pos or XL_LABEL_POSITION.ABOVE
                elif kind.startswith('stacked'):
                    dl.position = XL_LABEL_POSITION.CENTER
            except Exception:
                pass
        lc = label_color or (('FFFFFF' if kind in ('donut',) or kind.startswith('stacked') else txt))
        _font(dl.font, font_size, t.c(lc), ea, lat, bold=False)
        # bold + primary labels on highlighted points
        if hl and kind in ('column', 'bar') and n_series == 1:
            s = plot.series[0]
            # a per-point <c:dLbl> forces a series-level <c:dLbls> whose defaults hide the other values:
            # configure it like the plot-level labels first
            sdl = s.data_labels
            sdl.show_value = True
            sdl.number_format = number_format
            sdl.number_format_is_linked = number_format == 'General'
            try:
                sdl.position = label_pos or XL_LABEL_POSITION.OUTSIDE_END
            except Exception:
                pass
            _font(sdl.font, font_size, t.c(lc), ea, lat, bold=False)
            for pi in hl:
                try:
                    pdl = s.points[pi].data_label
                    pdl.font.bold = True
                    pdl.font.size = Pt(font_size + 1)
                    pdl.font.color.rgb = _rgbc(t.c(colors[0]))
                    pdl.position = label_pos or XL_LABEL_POSITION.OUTSIDE_END
                    pdl._get_or_add_dLbl()
                    d = pdl._dLbl
                    for tag, val in (('showLegendKey', '0'), ('showVal', '1'), ('showCatName', '0'),
                                     ('showSerName', '0'), ('showPercent', '0'), ('showBubbleSize', '0')):
                        e = d.find(_cq(tag))
                        if e is None:
                            e = etree.SubElement(d, _cq(tag))
                        e.set('val', val)
                except Exception:
                    pass
    # axes
    if kind not in ('pie', 'donut'):
        try:
            ca = ch.category_axis
            ca.has_major_gridlines = False
            ca.format.line.color.rgb = _rgbc(t.c('line'))
            _font(ca.tick_labels.font, font_size, txt, ea, lat)
            from pptx.enum.chart import XL_TICK_MARK
            ca.major_tick_mark = XL_TICK_MARK.NONE
            if kind in ('bar', 'stacked_bar'):
                ca.reverse_order = True  # first category on top (reading order)
            va = ch.value_axis
            va.has_major_gridlines = bool(gridlines)
            if gridlines:
                va.major_gridlines.format.line.color.rgb = _rgbc(t.c('line'))
                va.major_gridlines.format.line.width = Pt(0.75)
            va.major_tick_mark = XL_TICK_MARK.NONE
            va.format.line.fill.background()
            if max_value is not None:
                va.maximum_scale = max_value
            if min_value is not None:
                va.minimum_scale = min_value
            if not value_axis:
                va.tick_label_position = XL_TICK_LABEL_POSITION.NONE
            else:
                _font(va.tick_labels.font, font_size - 1, muted, ea, lat)
        except Exception:
            pass
    return ch


def _rgbc(hexclr):
    from pptx.dml.color import RGBColor
    return RGBColor.from_string(hexclr)


def _fill_series(s, base, gradient, t, kind):
    sp = s.format.fill
    if gradient:
        el = s._element
        _grad_sppr(el, base, t, kind)
    else:
        sp.solid()
        sp.fore_color.rgb = _rgbc(base)


def _fill_point(pt, base, gradient, t, kind):
    if gradient:
        _grad_sppr(pt._element, base, t, kind)
    else:
        pt.format.fill.solid()
        pt.format.fill.fore_color.rgb = _rgbc(base)


def _grad_sppr(el, base, t, kind):
    from . import color as C
    sp = el.get_or_add_spPr()
    for ch in list(sp):
        if etree.QName(ch).localname in X.FILL_TAGS:
            sp.remove(ch)
    ang = 0 if kind in ('bar', 'stacked_bar') else 90
    stops = [(0, C.tint(base, 0.35), 1.0), (100, base, 1.0)] if ang == 90 else [(0, base, 1.0), (100, C.tint(base, 0.35), 1.0)]
    X.insert_ordered(sp, X.grad_fill_el(stops, ang), X.SPPR_ORDER)


def _area_fill(s, col):
    sp = s._element.get_or_add_spPr()
    for ch in list(sp):
        sp.remove(ch)
    sp.append(X.grad_fill_el([(0, col, 0.55), (100, col, 0.04)], 90))
    ln = etree.SubElement(sp, X.qn('a:ln'), w=str(int(2.25 * 12700)))
    ln.append(X.solid_fill_el(col))
