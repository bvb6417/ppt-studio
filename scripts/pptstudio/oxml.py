"""Low-level DrawingML helpers for python-pptx elements (schema-ordered inserts).

Everything python-pptx does not expose: alpha fills, alpha/radial gradients, tinted soft shadows, glow,
soft edges, gradient text, character spacing, East-Asian fonts, picture transparency, custom geometry,
morph/fade transitions.
"""
from __future__ import annotations

from lxml import etree

NS = {
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
    'p14': 'http://schemas.microsoft.com/office/powerpoint/2010/main',
    'p159': 'http://schemas.microsoft.com/office/powerpoint/2015/09/main',
}


def qn(tag: str) -> str:
    pfx, local = tag.split(':')
    return '{%s}%s' % (NS[pfx], local)


def _local(el):
    return etree.QName(el).localname


FILL_TAGS = ['noFill', 'solidFill', 'gradFill', 'blipFill', 'pattFill', 'grpFill']
SPPR_ORDER = ['xfrm', 'custGeom', 'prstGeom'] + FILL_TAGS + ['ln', 'effectLst', 'effectDag', 'scene3d', 'sp3d', 'extLst']
LN_ORDER = ['noFill', 'solidFill', 'gradFill', 'pattFill', 'prstDash', 'custDash', 'round', 'bevel', 'miter',
            'headEnd', 'tailEnd', 'extLst']
EFFECT_ORDER = ['blur', 'fillOverlay', 'glow', 'innerShdw', 'outerShdw', 'prstShdw', 'reflection', 'softEdge']
RPR_ORDER = ['ln'] + FILL_TAGS + ['effectLst', 'effectDag', 'highlight', 'uLnTx', 'uLn', 'uFillTx', 'uFill',
                                  'latin', 'ea', 'cs', 'sym', 'hlinkClick', 'hlinkMouseOver', 'rtl', 'extLst']
PPR_ORDER = ['lnSpc', 'spcBef', 'spcAft', 'buClrTx', 'buClr', 'buSzTx', 'buSzPct', 'buSzPts', 'buFontTx', 'buFont',
             'buNone', 'buAutoNum', 'buChar', 'buBlip', 'tabLst', 'defRPr', 'extLst']
BODYPR_ORDER = ['prstTxWarp', 'noAutofit', 'normAutofit', 'spAutoFit', 'scene3d', 'sp3d', 'flatTx', 'extLst']


def insert_ordered(parent, child, order):
    name = _local(child)
    idx = order.index(name) if name in order else len(order)
    for i, existing in enumerate(parent):
        en = _local(existing)
        if en in order and order.index(en) > idx:
            existing.addprevious(child)
            return child
    parent.append(child)
    return child


def remove_children(parent, names):
    for ch in list(parent):
        if _local(ch) in names:
            parent.remove(ch)


def sub(parent, tag, **attrs):
    el = etree.SubElement(parent, qn(tag))
    for k, v in attrs.items():
        el.set(k, str(v))
    return el


# ---------------------------------------------------------------- colors
def color_el(hexclr: str, alpha: float = 1.0, lum_mod=None, lum_off=None):
    c = etree.Element(qn('a:srgbClr'))
    c.set('val', hexclr)
    if lum_mod is not None:
        sub(c, 'a:lumMod', val=int(lum_mod * 100000))
    if lum_off is not None:
        sub(c, 'a:lumOff', val=int(lum_off * 100000))
    if alpha is not None and alpha < 0.999:
        sub(c, 'a:alpha', val=int(max(0.0, alpha) * 100000))
    return c


def solid_fill_el(hexclr, alpha=1.0):
    f = etree.Element(qn('a:solidFill'))
    f.append(color_el(hexclr, alpha))
    return f


def grad_fill_el(stops, angle=90, kind='linear', rot_with_shape=True, center=(50, 50)):
    """stops: [(pos 0-100, hex, alpha 0-1), ...]; angle in degrees (0 = left->right, 90 = top->bottom).
    kind: 'linear' | 'radial' (circle from center) | 'rect' | 'shape'."""
    g = etree.Element(qn('a:gradFill'))
    g.set('rotWithShape', '1' if rot_with_shape else '0')
    gl = sub(g, 'a:gsLst')
    for pos, col, al in stops:
        gs = sub(gl, 'a:gs', pos=int(round(pos * 1000)))
        gs.append(color_el(col, al))
    if kind == 'linear':
        sub(g, 'a:lin', ang=int(round(angle * 60000)) % 21600000, scaled='0')
    else:
        p = sub(g, 'a:path', path={'radial': 'circle', 'circle': 'circle', 'rect': 'rect', 'shape': 'shape'}[kind])
        cx, cy = center
        sub(p, 'a:fillToRect', l=int(cx * 1000), t=int(cy * 1000), r=int((100 - cx) * 1000), b=int((100 - cy) * 1000))
    return g


# ---------------------------------------------------------------- shape props
def spPr(shape):
    el = shape._element
    for tag in ('p:spPr', 'p:grpSpPr'):
        x = el.find(qn(tag))
        if x is not None:
            return x
    raise ValueError('no spPr')


def strip_style(shape):
    """Remove <p:style> so theme line/fill/effect/font refs do not leak (e.g. default shadows)."""
    st = shape._element.find(qn('p:style'))
    if st is not None:
        shape._element.remove(st)


def set_fill(shape, hexclr=None, alpha=1.0):
    sp = spPr(shape)
    remove_children(sp, FILL_TAGS)
    if hexclr is None:
        insert_ordered(sp, etree.Element(qn('a:noFill')), SPPR_ORDER)
    else:
        insert_ordered(sp, solid_fill_el(hexclr, alpha), SPPR_ORDER)


def set_grad(shape, stops, angle=90, kind='linear', center=(50, 50)):
    sp = spPr(shape)
    remove_children(sp, FILL_TAGS)
    insert_ordered(sp, grad_fill_el(stops, angle, kind, center=center), SPPR_ORDER)


def set_line(shape, hexclr=None, width_pt=1.0, alpha=1.0, dash=None, cap=None, join='round',
             head=None, tail=None, grad_stops=None, grad_angle=0):
    sp = spPr(shape)
    remove_children(sp, ['ln'])
    ln = etree.Element(qn('a:ln'))
    if hexclr is None and not grad_stops:
        sub(ln, 'a:noFill')
    else:
        ln.set('w', str(int(round(width_pt * 12700))))
        if cap:
            ln.set('cap', {'round': 'rnd', 'flat': 'flat', 'square': 'sq', 'rnd': 'rnd'}[cap])
        if grad_stops:
            ln.append(grad_fill_el(grad_stops, grad_angle))
        else:
            ln.append(solid_fill_el(hexclr, alpha))
        if dash:
            sub(ln, 'a:prstDash', val=dash)  # 'dash','sysDash','sysDot','lgDash','dashDot'
        if join == 'round':
            sub(ln, 'a:round')
        elif join == 'miter':
            sub(ln, 'a:miter', lim='800000')
        if head:
            sub(ln, 'a:headEnd', type=head, w='med', len='med')
        if tail:
            sub(ln, 'a:tailEnd', type=tail, w='med', len='med')
    insert_ordered(sp, ln, SPPR_ORDER)
    return ln


def _effect_lst(sp):
    ef = sp.find(qn('a:effectLst'))
    if ef is None:
        ef = insert_ordered(sp, etree.Element(qn('a:effectLst')), SPPR_ORDER)
    return ef


def clear_effects(shape):
    sp = spPr(shape)
    remove_children(sp, ['effectLst', 'effectDag'])
    insert_ordered(sp, etree.Element(qn('a:effectLst')), SPPR_ORDER)


def set_shadow(shape, hexclr='000000', alpha=0.15, blur_pt=20, dist_pt=4, dir_deg=90, size=1.0):
    """Soft outer shadow (designer '弥散阴影': high transparency, big blur, tinted with main color)."""
    ef = _effect_lst(spPr(shape))
    remove_children(ef, ['outerShdw'])
    o = etree.Element(qn('a:outerShdw'))
    o.set('blurRad', str(int(blur_pt * 12700)))
    o.set('dist', str(int(dist_pt * 12700)))
    o.set('dir', str(int(dir_deg * 60000)))
    if size != 1.0:
        o.set('sx', str(int(size * 100000)))
        o.set('sy', str(int(size * 100000)))
    o.set('algn', 'ctr')
    o.set('rotWithShape', '0')
    o.append(color_el(hexclr, alpha))
    insert_ordered(ef, o, EFFECT_ORDER)


def set_glow(shape, hexclr, alpha=0.4, radius_pt=10):
    ef = _effect_lst(spPr(shape))
    remove_children(ef, ['glow'])
    g = etree.Element(qn('a:glow'))
    g.set('rad', str(int(radius_pt * 12700)))
    g.append(color_el(hexclr, alpha))
    insert_ordered(ef, g, EFFECT_ORDER)


def set_soft_edge(shape, radius_pt=10):
    ef = _effect_lst(spPr(shape))
    remove_children(ef, ['softEdge'])
    insert_ordered(ef, etree.Element(qn('a:softEdge'), rad=str(int(radius_pt * 12700))), EFFECT_ORDER)


def set_blur(shape, radius_pt=10):
    ef = _effect_lst(spPr(shape))
    remove_children(ef, ['blur'])
    insert_ordered(ef, etree.Element(qn('a:blur'), rad=str(int(radius_pt * 12700)), grow='1'), EFFECT_ORDER)


def set_rotation(shape, degrees):
    x = spPr(shape).find(qn('a:xfrm'))
    if x is not None:
        x.set('rot', str(int(degrees * 60000)))


def set_flip(shape, h=False, v=False):
    x = spPr(shape).find(qn('a:xfrm'))
    if x is not None:
        if h:
            x.set('flipH', '1')
        if v:
            x.set('flipV', '1')


def set_adj(shape, **vals):
    """Set preset geometry adjust values, e.g. set_adj(sh, adj=16667) or adj1=..., adj2=..."""
    pg = spPr(shape).find(qn('a:prstGeom'))
    if pg is None:
        return
    av = pg.find(qn('a:avLst'))
    if av is None:
        av = sub(pg, 'a:avLst')
    for k, v in vals.items():
        for gd in av.findall(qn('a:gd')):
            if gd.get('name') == k:
                av.remove(gd)
        sub(av, 'a:gd', name=k, fmla=f'val {int(v)}')


def set_prst(shape, prst):
    pg = spPr(shape).find(qn('a:prstGeom'))
    if pg is not None:
        pg.set('prst', prst)


def set_custgeom(shape, subpaths, vb_w, vb_h, scale=100, fill_mode='norm', filled_idx=None):
    """Replace geometry by custom paths. subpaths from svgpath: {'start','segs','closed'}.
    fill_mode: 'norm' (filled) or 'none' (stroke only); filled_idx: set of subpath indices to fill."""
    sp = spPr(shape)
    remove_children(sp, ['prstGeom', 'custGeom'])
    cg = etree.Element(qn('a:custGeom'))
    for t in ('a:avLst', 'a:gdLst', 'a:ahLst', 'a:cxnLst'):
        sub(cg, t)
    sub(cg, 'a:rect', l='0', t='0', r='r', b='b')
    pl = sub(cg, 'a:pathLst')
    W, H = int(round(vb_w * scale)), int(round(vb_h * scale))
    for i, spth in enumerate(subpaths):
        p = sub(pl, 'a:path', w=W, h=H)
        fm = 'norm' if (filled_idx and i in filled_idx) else fill_mode
        if fm == 'none':
            p.set('fill', 'none')
        if spth.get('nostroke'):
            p.set('stroke', '0')

        def pt(parent, x, y):
            sub(parent, 'a:pt', x=int(round(x * scale)), y=int(round(y * scale)))
        m = sub(p, 'a:moveTo')
        pt(m, *spth['start'])
        for seg in spth['segs']:
            if seg[0] == 'L':
                pt(sub(p, 'a:lnTo'), seg[1], seg[2])
            else:
                c = sub(p, 'a:cubicBezTo')
                pt(c, seg[1], seg[2]); pt(c, seg[3], seg[4]); pt(c, seg[5], seg[6])
        if spth.get('closed'):
            sub(p, 'a:close')
    insert_ordered(sp, cg, SPPR_ORDER)


# ---------------------------------------------------------------- text
def body_pr(shape):
    return shape.text_frame._txBody.find(qn('a:bodyPr'))


def set_body(shape, l=0.0, t=0.0, r=0.0, b=0.0, anchor='t', wrap=True, autofit='none', vert=None,
             anchor_ctr=False, warp=None):
    """Insets in points. anchor: t|ctr|b. autofit: none|shape|shrink. vert: None|'eaVert'."""
    bp = body_pr(shape)
    for k, v in (('lIns', l), ('tIns', t), ('rIns', r), ('bIns', b)):
        bp.set(k, str(int(v * 12700)))
    bp.set('anchor', anchor)
    bp.set('wrap', 'square' if wrap else 'none')
    bp.set('rtlCol', '0')
    if anchor_ctr:
        bp.set('anchorCtr', '1')
    if vert:
        bp.set('vert', vert)
    remove_children(bp, ['noAutofit', 'normAutofit', 'spAutoFit', 'prstTxWarp'])
    if warp:
        w = etree.Element(qn('a:prstTxWarp'), prst=warp)
        sub(w, 'a:avLst')
        insert_ordered(bp, w, BODYPR_ORDER)
    insert_ordered(bp, etree.Element(qn({'none': 'a:noAutofit', 'shape': 'a:spAutoFit',
                                         'shrink': 'a:normAutofit'}[autofit])), BODYPR_ORDER)


def set_para(p, align=None, line_spacing=None, space_before=None, space_after=None,
             indent=None, margin_left=None, bullet=None, bullet_color=None, bullet_font=None,
             east_asian_break=True, hanging_punct=True):
    """p: python-pptx _Paragraph. line_spacing: multiple (1.0 = single). spaces in pt. indent/margin in pt.
    bullet: None (inherit) | '' (none) | '•' / '■' / '▶' etc."""
    pPr = p._p.get_or_add_pPr()
    if align:
        pPr.set('algn', {'left': 'l', 'center': 'ctr', 'right': 'r', 'justify': 'just', 'dist': 'dist',
                         'l': 'l', 'ctr': 'ctr', 'r': 'r', 'just': 'just'}[align])
    if margin_left is not None:
        pPr.set('marL', str(int(margin_left * 12700)))
    if indent is not None:
        pPr.set('indent', str(int(indent * 12700)))
    if east_asian_break:
        pPr.set('eaLnBrk', '1')
    if hanging_punct:
        pPr.set('hangingPunct', '1')
    if line_spacing is not None:
        remove_children(pPr, ['lnSpc'])
        ls = etree.Element(qn('a:lnSpc'))
        sub(ls, 'a:spcPct', val=int(line_spacing * 100000))
        insert_ordered(pPr, ls, PPR_ORDER)
    for tag, v in (('spcBef', space_before), ('spcAft', space_after)):
        if v is not None:
            remove_children(pPr, [tag])
            e = etree.Element(qn('a:' + tag))
            sub(e, 'a:spcPts', val=int(v * 100))
            insert_ordered(pPr, e, PPR_ORDER)
    if bullet is not None:
        remove_children(pPr, ['buNone', 'buAutoNum', 'buChar', 'buBlip', 'buClr', 'buClrTx', 'buFont', 'buFontTx'])
        if bullet == '':
            insert_ordered(pPr, etree.Element(qn('a:buNone')), PPR_ORDER)
        else:
            if bullet_color:
                bc = etree.Element(qn('a:buClr'))
                bc.append(color_el(bullet_color))
                insert_ordered(pPr, bc, PPR_ORDER)
            bf = etree.Element(qn('a:buFont'), typeface=bullet_font or 'Arial')
            insert_ordered(pPr, bf, PPR_ORDER)
            insert_ordered(pPr, etree.Element(qn('a:buChar'), char=bullet), PPR_ORDER)
    return pPr


def style_run(r, size=None, bold=None, italic=None, hexclr=None, alpha=1.0, ea=None, latin=None,
              spacing=None, underline=None, grad_stops=None, grad_angle=0, baseline=None, outline=None,
              lang='zh-CN'):
    """r: python-pptx _Run. spacing: character spacing in pt. outline: (hex, width_pt) for hollow text."""
    rPr = r._r.get_or_add_rPr()
    rPr.set('lang', lang)
    rPr.set('altLang', 'en-US')
    if size is not None:
        rPr.set('sz', str(int(round(size * 100))))
    if bold is not None:
        rPr.set('b', '1' if bold else '0')
    if italic is not None:
        rPr.set('i', '1' if italic else '0')
    if underline is not None:
        rPr.set('u', 'sng' if underline else 'none')
    if spacing is not None:
        rPr.set('spc', str(int(round(spacing * 100))))
    if baseline is not None:
        rPr.set('baseline', str(int(baseline * 1000)))
    if outline is not None:
        remove_children(rPr, ['ln'])
        ln = etree.Element(qn('a:ln'), w=str(int(outline[1] * 12700)))
        ln.append(solid_fill_el(outline[0]))
        insert_ordered(rPr, ln, RPR_ORDER)
    if grad_stops:
        remove_children(rPr, FILL_TAGS)
        insert_ordered(rPr, grad_fill_el(grad_stops, grad_angle, rot_with_shape=True), RPR_ORDER)
    elif hexclr is not None:
        remove_children(rPr, FILL_TAGS)
        insert_ordered(rPr, solid_fill_el(hexclr, alpha), RPR_ORDER)
    elif outline is not None:
        remove_children(rPr, FILL_TAGS)
        insert_ordered(rPr, etree.Element(qn('a:noFill')), RPR_ORDER)
    if latin:
        remove_children(rPr, ['latin'])
        insert_ordered(rPr, etree.Element(qn('a:latin'), typeface=latin), RPR_ORDER)
    if ea:
        remove_children(rPr, ['ea'])
        insert_ordered(rPr, etree.Element(qn('a:ea'), typeface=ea), RPR_ORDER)
        remove_children(rPr, ['cs'])
        insert_ordered(rPr, etree.Element(qn('a:cs'), typeface=latin or ea), RPR_ORDER)
    return rPr


def set_end_para_font(p, size, ea=None, latin=None):
    """Keep empty-paragraph height consistent (endParaRPr)."""
    e = p._p.find(qn('a:endParaRPr'))
    if e is None:
        e = sub(p._p, 'a:endParaRPr')
    e.set('lang', 'zh-CN')
    e.set('sz', str(int(size * 100)))
    if latin:
        sub(e, 'a:latin', typeface=latin)
    if ea:
        sub(e, 'a:ea', typeface=ea)


# ---------------------------------------------------------------- pictures
def pic_alpha(pic, alpha):
    blip = pic._element.find('.//' + qn('a:blip'))
    if blip is not None:
        remove_children(blip, ['alphaModFix'])
        el = etree.Element(qn('a:alphaModFix'), amt=str(int(alpha * 100000)))
        blip.insert(0, el)


def pic_geom(pic, prst='roundRect', adj=None):
    sp = spPr(pic)
    pg = sp.find(qn('a:prstGeom'))
    if pg is None:
        pg = insert_ordered(sp, etree.Element(qn('a:prstGeom')), SPPR_ORDER)
    pg.set('prst', prst)
    remove_children(pg, ['avLst'])
    av = sub(pg, 'a:avLst')
    if adj is not None:
        sub(av, 'a:gd', name='adj', fmla=f'val {int(adj)}')


def pic_crop(pic, l=0.0, t=0.0, r=0.0, b=0.0):
    """Crop fractions 0..1 (python-pptx has crop_left etc. too, this sets all at once)."""
    pic.crop_left, pic.crop_top, pic.crop_right, pic.crop_bottom = l, t, r, b


# ---------------------------------------------------------------- slide-level
def set_transition(slide, kind='fade', duration_ms=700):
    """kind: 'fade' | 'morph' | 'push' | None. Morph written with AlternateContent + fade fallback."""
    sld = slide._element
    for old in sld.findall(qn('p:transition')) + sld.findall(qn('mc:AlternateContent')):
        if old.tag == qn('p:transition') or old.find('.//' + qn('p:transition')) is not None:
            sld.remove(old)
    if not kind:
        return
    # transition must come after clrMapOvr and before timing / extLst
    anchor = sld.find(qn('p:timing'))
    if anchor is None:
        anchor = sld.find(qn('p:extLst'))
    if kind == 'morph':
        ac = etree.Element(qn('mc:AlternateContent'), nsmap={'mc': NS['mc'], 'p159': NS['p159'], 'p14': NS['p14']})
        ch = sub(ac, 'mc:Choice', Requires='p159')
        tr = sub(ch, 'p:transition', spd='slow')
        tr.set(qn('p14:dur'), str(duration_ms))
        sub(tr, 'p159:morph', option='byObject')
        fb = sub(ac, 'mc:Fallback')
        tr2 = sub(fb, 'p:transition', spd='slow')
        sub(tr2, 'p:fade')
        el = ac
    else:
        el = etree.Element(qn('p:transition'), spd='med')
        sub(el, {'fade': 'p:fade', 'push': 'p:push'}[kind])
    if anchor is not None:
        anchor.addprevious(el)
    else:
        sld.append(el)
