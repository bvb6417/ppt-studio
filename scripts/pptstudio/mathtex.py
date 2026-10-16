"""Equations for research slides: LaTeX-style math (matplotlib mathtext, STIX = Times-like) rendered to a transparent
PNG whose physical size matches the requested point size, so formulas sit next to body text at a consistent scale.

    from pptstudio import mathtex
    png, w, h = mathtex.render(r'\\dfrac{\\partial H}{\\partial t}+\\dfrac{a^2}{gA}\\dfrac{\\partial Q}{\\partial x}=0', 20)
    cv.equation(r'R_t=T_{\\mathrm{sim}}/t_c', x, y, size=20)          # Canvas helper (places at true size)

Supported: the mathtext subset of TeX (\\frac \\dfrac \\sum_{}^{} \\left( \\right) \\lfloor \\hat \\mathrm \\mathcal
\\partial, Greek, sub/superscripts). Not supported: \\begin{align}, \\text{中文} — put Chinese in a text box instead.
"""
from __future__ import annotations

import hashlib
import os

from .images import cache_dir

DPI = 600


def render(tex, size=20.0, color='1A1A1A', fontset='stix', dpi=DPI):
    """Typeset `tex` (with or without surrounding $…$) at `size` pt. Returns (png_path, width_in, height_in)."""
    s = tex.strip()
    if not (s.startswith('$') and s.endswith('$')):
        s = f'${s}$'
    color = color.lstrip('#')
    key = hashlib.md5(f'{s}|{size}|{color}|{fontset}|{dpi}'.encode('utf-8')).hexdigest()[:16]
    path = os.path.join(cache_dir(), f'eq_{key}.png')
    if not os.path.exists(path):
        import matplotlib
        matplotlib.use('Agg')
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_agg import FigureCanvasAgg
        rc = {'mathtext.fontset': fontset, 'font.family': 'STIXGeneral' if fontset == 'stix' else 'serif'}
        with matplotlib.rc_context(rc):
            fig = Figure(figsize=(14, 3))
            FigureCanvasAgg(fig)
            fig.text(0.0, 0.5, s, fontsize=size, color='#' + color, va='center')
            fig.savefig(path, dpi=dpi, transparent=True, bbox_inches='tight', pad_inches=0.02)
    from PIL import Image
    with Image.open(path) as im:
        w, h = im.size
    return path, w / dpi, h / dpi
