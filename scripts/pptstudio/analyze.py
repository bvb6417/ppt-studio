"""Extract design DNA (fonts, sizes, colors, shapes, effects, geometry) from .pptx files.

Parses slide XML directly (fast, no media decoding). Resolves theme fonts (+mj/+mn)
and scheme colors (with lumMod/lumOff/tint/shade) approximately.
Usage: python analyze_pptx.py <pptx> [--json out.json]
"""
import sys, os, re, json, zipfile, colorsys, collections
from lxml import etree

NS = {
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
}
A = '{%s}' % NS['a']
P = '{%s}' % NS['p']
EMU_PER_CM = 360000


def hex_to_rgb(h):
    h = h.strip().lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return '%02X%02X%02X' % tuple(max(0, min(255, int(round(c)))) for c in rgb)


def apply_mods(hexclr, el):
    """Apply DrawingML color transforms (lumMod, lumOff, tint, shade) approximately."""
    r, g, b = [c / 255 for c in hex_to_rgb(hexclr)]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    alpha = 1.0
    for m in el:
        tag = etree.QName(m).localname
        v = m.get('val')
        if v is None:
            continue
        v = int(v) / 100000
        if tag == 'lumMod':
            l = l * v
        elif tag == 'lumOff':
            l = l + v
        elif tag == 'tint':  # move toward white
            r2, g2, b2 = colorsys.hls_to_rgb(h, l, s)
            r2, g2, b2 = [c + (1 - c) * (1 - v) for c in (r2, g2, b2)]
            h, l, s = colorsys.rgb_to_hls(r2, g2, b2)
        elif tag == 'shade':
            r2, g2, b2 = colorsys.hls_to_rgb(h, l, s)
            r2, g2, b2 = [c * v for c in (r2, g2, b2)]
            h, l, s = colorsys.rgb_to_hls(r2, g2, b2)
        elif tag == 'alpha':
            alpha = v
    l = max(0, min(1, l))
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return rgb_to_hex((r * 255, g * 255, b * 255)), alpha


class Theme:
    def __init__(self, xml_bytes):
        t = etree.fromstring(xml_bytes)
        self.colors = {}
        cs = t.find('.//a:clrScheme', NS)
        if cs is not None:
            for c in cs:
                name = etree.QName(c).localname
                srgb = c.find('a:srgbClr', NS)
                sysc = c.find('a:sysClr', NS)
                if srgb is not None:
                    self.colors[name] = srgb.get('val')
                elif sysc is not None:
                    self.colors[name] = sysc.get('lastClr', '000000')
        # map aliases
        self.colors.setdefault('tx1', self.colors.get('dk1', '000000'))
        self.colors.setdefault('bg1', self.colors.get('lt1', 'FFFFFF'))
        self.colors.setdefault('tx2', self.colors.get('dk2', '44546A'))
        self.colors.setdefault('bg2', self.colors.get('lt2', 'E7E6E6'))
        self.fonts = {}
        for kind, tag in (('mj', 'majorFont'), ('mn', 'minorFont')):
            f = t.find('.//a:%s' % tag, NS)
            if f is not None:
                lat = f.find('a:latin', NS)
                ea = f.find('a:ea', NS)
                eat = ea.get('typeface') if ea is not None else ''
                if not eat:
                    hans = f.find("a:font[@script='Hans']", NS)
                    eat = hans.get('typeface') if hans is not None else ''
                self.fonts['+%s-lt' % kind] = lat.get('typeface') if lat is not None else ''
                self.fonts['+%s-ea' % kind] = eat

    def color(self, el):
        """el: an element that contains a color choice (srgbClr/schemeClr/...)."""
        for c in el:
            tag = etree.QName(c).localname
            if tag == 'srgbClr':
                return apply_mods(c.get('val'), c)
            if tag == 'schemeClr':
                base = self.colors.get(c.get('val'), '808080')
                return apply_mods(base, c)
            if tag == 'sysClr':
                return apply_mods(c.get('lastClr', '000000'), c)
            if tag == 'prstClr':
                return ({'black': '000000', 'white': 'FFFFFF'}.get(c.get('val'), '808080'), 1.0)
        return None, 1.0

    def font(self, name):
        if name and name.startswith('+'):
            return self.fonts.get(name, name)
        return name


def luminance(hexclr):
    r, g, b = [c / 255 for c in hex_to_rgb(hexclr)]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def walk_shapes(spTree, xform=(0, 0, 1, 1)):
    """Yield (element, abs_x, abs_y, abs_w, abs_h) for leaf shapes, resolving group transforms."""
    ox, oy, sx, sy = xform
    for el in spTree:
        tag = etree.QName(el).localname
        if tag == 'grpSp':
            g = el.find('p:grpSpPr/a:xfrm', NS)
            if g is None:
                yield from walk_shapes(el, xform)
                continue
            off, ext = g.find('a:off', NS), g.find('a:ext', NS)
            choff, chext = g.find('a:chOff', NS), g.find('a:chExt', NS)
            try:
                gx, gy = int(off.get('x')), int(off.get('y'))
                gw, gh = int(ext.get('cx')), int(ext.get('cy'))
                cx0, cy0 = int(choff.get('x')), int(choff.get('y'))
                cw, ch = int(chext.get('cx')) or 1, int(chext.get('cy')) or 1
            except Exception:
                yield from walk_shapes(el, xform)
                continue
            nsx, nsy = sx * gw / cw, sy * gh / ch
            nox = ox + sx * gx - nsx * cx0
            noy = oy + sy * gy - nsy * cy0
            yield from walk_shapes(el, (nox, noy, nsx, nsy))
        elif tag in ('sp', 'pic', 'cxnSp', 'graphicFrame'):
            x = el.find('.//a:xfrm', NS) if tag != 'graphicFrame' else el.find('p:xfrm', NS)
            if x is None:
                yield el, None, None, None, None
                continue
            off, ext = x.find('a:off', NS), x.find('a:ext', NS)
            if off is None or ext is None:
                yield el, None, None, None, None
                continue
            X = ox + sx * int(off.get('x'))
            Y = oy + sy * int(off.get('y'))
            Wd = sx * int(ext.get('cx'))
            Ht = sy * int(ext.get('cy'))
            yield el, X, Y, Wd, Ht


def analyze(path, max_slides=None):
    z = zipfile.ZipFile(path)
    names = set(z.namelist())
    pres = etree.fromstring(z.read('ppt/presentation.xml'))
    sz = pres.find('p:sldSz', NS)
    SW, SH = int(sz.get('cx')), int(sz.get('cy'))
    theme = Theme(z.read('ppt/theme/theme1.xml')) if 'ppt/theme/theme1.xml' in names else None
    # slide order
    rels = etree.fromstring(z.read('ppt/_rels/presentation.xml.rels'))
    rid2t = {r.get('Id'): r.get('Target') for r in rels}
    order = []
    for s in pres.findall('p:sldIdLst/p:sldId', NS):
        t = rid2t.get(s.get('{%s}id' % NS['r']))
        if t:
            order.append('ppt/' + t.lstrip('/').replace('ppt/', '') if not t.startswith('/') else t.lstrip('/'))
    stats = collections.defaultdict(collections.Counter)
    slides_out = []
    for si, sp in enumerate(order[:max_slides] if max_slides else order, 1):
        if sp not in names:
            continue
        root = etree.fromstring(z.read(sp))
        tree = root.find('.//p:cSld/p:spTree', NS)
        info = dict(idx=si, texts=[], n_pic=0, n_shape=0, full_pic=0, bg=None, geoms=collections.Counter())
        bgc = root.find('.//p:cSld/p:bg//a:solidFill', NS)
        if bgc is not None and theme:
            info['bg'] = theme.color(bgc)[0]
        if root.find('.//p:cSld/p:bg//a:blipFill', NS) is not None:
            info['bg'] = 'IMAGE'
        if root.find('.//p:cSld/p:bg//a:gradFill', NS) is not None:
            info['bg'] = 'GRADIENT'
        for el, X, Y, Wd, Ht in walk_shapes(tree):
            tag = etree.QName(el).localname
            if tag == 'pic':
                info['n_pic'] += 1
                if Wd and Wd * Ht > 0.6 * SW * SH:
                    info['full_pic'] += 1
                stats['pic_area'][round((Wd or 0) * (Ht or 0) / (SW * SH), 1)] += 1
                continue
            if tag == 'graphicFrame':
                if el.find('.//a:tbl', NS) is not None:
                    stats['frame']['table'] += 1
                elif el.find(".//a:graphicData[@uri='http://schemas.openxmlformats.org/drawingml/2006/chart']", NS) is not None:
                    stats['frame']['chart'] += 1
                else:
                    stats['frame']['other'] += 1
                continue
            spPr = el.find('p:spPr', NS)
            geom = None
            if spPr is not None:
                pg = spPr.find('a:prstGeom', NS)
                geom = pg.get('prst') if pg is not None else ('custom' if spPr.find('a:custGeom', NS) is not None else None)
                sf = spPr.find('a:solidFill', NS)
                if sf is not None and theme:
                    c, al = theme.color(sf)
                    if c:
                        stats['fill'][c] += 1
                        if al < 1:
                            stats['effects']['fill_alpha'] += 1
                if spPr.find('a:gradFill', NS) is not None:
                    stats['effects']['gradFill'] += 1
                    for gs in spPr.findall('a:gradFill/a:gsLst/a:gs', NS):
                        c, al = theme.color(gs) if theme else (None, 1)
                        if c:
                            stats['grad_color'][c] += 1
                if spPr.find('a:blipFill', NS) is not None:
                    stats['effects']['blipFill_shape'] += 1
                ln = spPr.find('a:ln', NS)
                if ln is not None and ln.find('a:noFill', NS) is None and ln.find('a:solidFill', NS) is not None:
                    w = int(ln.get('w', '12700')) / 12700
                    stats['line_w'][round(w, 2)] += 1
                    c, _ = theme.color(ln.find('a:solidFill', NS)) if theme else (None, 1)
                    if c:
                        stats['line_color'][c] += 1
                    if ln.find('a:prstDash', NS) is not None and ln.find('a:prstDash', NS).get('val') != 'solid':
                        stats['effects']['dashed_line'] += 1
                ef = spPr.find('a:effectLst', NS)
                if ef is not None:
                    for e in ef:
                        stats['effects'][etree.QName(e).localname] += 1
            if geom:
                stats['geom'][geom] += 1
                info['geoms'][geom] += 1
            info['n_shape'] += 1
            txBody = el.find('p:txBody', NS)
            if txBody is None:
                continue
            bodyPr = txBody.find('a:bodyPr', NS)
            if bodyPr is not None and bodyPr.get('vert') in ('eaVert', 'vert', 'wordArtVertRtl'):
                stats['effects']['vertical_text'] += 1
            for p_ in txBody.findall('a:p', NS):
                algn = None
                pPr = p_.find('a:pPr', NS)
                if pPr is not None:
                    algn = pPr.get('algn')
                    lnspc = pPr.find('a:lnSpc/a:spcPct', NS)
                    if lnspc is not None:
                        stats['line_spacing'][int(lnspc.get('val')) / 100000] += 1
                runs = p_.findall('a:r', NS)
                ptext = ''.join((r.findtext('a:t', default='', namespaces=NS)) for r in runs)
                if not ptext.strip():
                    continue
                stats['align'][algn or 'l'] += 1
                for r in runs:
                    t = r.findtext('a:t', default='', namespaces=NS)
                    if not t.strip():
                        continue
                    rPr = r.find('a:rPr', NS)
                    size = bold = ea = lat = color = None
                    spc = None
                    if rPr is not None:
                        size = int(rPr.get('sz')) / 100 if rPr.get('sz') else None
                        bold = rPr.get('b') == '1'
                        spc = rPr.get('spc')
                        e_ = rPr.find('a:ea', NS)
                        l_ = rPr.find('a:latin', NS)
                        ea = theme.font(e_.get('typeface')) if (e_ is not None and theme) else (e_.get('typeface') if e_ is not None else None)
                        lat = theme.font(l_.get('typeface')) if (l_ is not None and theme) else (l_.get('typeface') if l_ is not None else None)
                        sf = rPr.find('a:solidFill', NS)
                        if sf is not None and theme:
                            color = theme.color(sf)[0]
                        if rPr.find('a:gradFill', NS) is not None:
                            stats['effects']['text_gradient'] += 1
                        if rPr.find('a:effectLst', NS) is not None:
                            stats['effects']['text_effect'] += 1
                    n = len(t)
                    has_cjk = bool(re.search(r'[一-鿿]', t))
                    if has_cjk:
                        stats['font_ea'][ea or '(inherit)'] += n
                    else:
                        stats['font_latin'][lat or '(inherit)'] += n
                    if size:
                        stats['size_chars'][size] += n
                    if color:
                        stats['text_color'][color] += n
                    if spc:
                        stats['char_spacing'][int(spc) / 100] += n
                    info['texts'].append(dict(t=t[:40], sz=size, b=bold, ea=ea, lat=lat, c=color,
                                              x=round(X / EMU_PER_CM, 2) if X is not None else None,
                                              y=round(Y / EMU_PER_CM, 2) if Y is not None else None,
                                              w=round(Wd / EMU_PER_CM, 2) if Wd is not None else None))
        # per-slide: title (largest size) vs body (most chars)
        sizes = [(x['sz'], len(x['t'])) for x in info['texts'] if x['sz']]
        if sizes:
            mx = max(s for s, _ in sizes)
            stats['slide_max_size'][mx] += 1
            body = collections.Counter()
            for s, n in sizes:
                body[s] += n
            stats['slide_body_size'][body.most_common(1)[0][0]] += 1
        xs = [x['x'] for x in info['texts'] if x['x'] is not None and x['x'] >= 0]
        if xs:
            stats['min_text_left_cm'][round(min(xs), 1)] += 1
        stats['bg'][info['bg'] or '(layout)'] += 1
        stats['pics_per_slide'][info['n_pic']] += 1
        slides_out.append(dict(idx=si, n_pic=info['n_pic'], full_pic=info['full_pic'], n_shape=info['n_shape'],
                               bg=info['bg'], geoms=dict(info['geoms']), texts=info['texts'][:60]))
    return dict(file=path, slide_w_cm=SW / EMU_PER_CM, slide_h_cm=SH / EMU_PER_CM,
                theme_fonts=theme.fonts if theme else {}, theme_colors=theme.colors if theme else {},
                stats={k: dict(v.most_common(40)) for k, v in stats.items()}, slides=slides_out)


if __name__ == '__main__':
    src = sys.argv[1]
    res = analyze(src)
    if '--json' in sys.argv:
        out = sys.argv[sys.argv.index('--json') + 1]
        with open(out, 'w', encoding='utf-8') as f:
            json.dump(res, f, ensure_ascii=False, indent=1, default=str)
    else:
        print(json.dumps(res['stats'], ensure_ascii=False, indent=1, default=str)[:6000])
