"""Font discovery, font stacks, text measurement and wrapping (PowerPoint-compatible estimates).

PowerPoint facts (calibrated via COM on Office 365):
  * single line spacing (spcPct 100%) -> line pitch = 1.2 x font size for EVERY font;
  * CJK glyph advance ~= 1.0 em;  Latin widths come from the real font metrics.
We measure with Pillow using the actual installed font files so wrapping matches PowerPoint closely.
"""
from __future__ import annotations

import json
import os
import re
import sys
from functools import lru_cache

LINE_PITCH = 1.2  # PowerPoint single spacing = 1.2 x size

# ---------------------------------------------------------------- font stacks
# First installed family wins. "portable" stacks only use fonts shipped with Windows+Office.
STACKS = {
    'sans': ['HarmonyOS Sans SC', '思源黑体 CN', 'Source Han Sans CN', 'Source Han Sans SC', 'Noto Sans SC',
             '阿里巴巴普惠体 2.0', 'Alibaba PuHuiTi 2.0', '阿里巴巴普惠体', 'OPPOSans', 'MiSans',
             'Microsoft YaHei', 'DengXian', 'SimHei'],
    'serif': ['思源宋体 CN', 'Source Han Serif CN', 'Source Han Serif SC', 'Noto Serif SC', '方正小标宋简体',
              'STZhongsong', '华文中宋', 'SimSun'],
    'kai': ['方正楷体简体', 'STKaiti', '华文楷体', 'KaiTi'],
    'latin': ['Montserrat', 'Segoe UI', 'Arial'],
    'number': ['Bahnschrift SemiBold', 'Bahnschrift', 'DIN Alternate', 'Montserrat SemiBold', 'Arial'],
    'portable_sans': ['Microsoft YaHei'],
    'portable_serif': ['SimSun'],
    'portable_latin': ['Arial'],
}

# weights available as separate family names for some variable / multi-weight fonts
WEIGHT_NAMES = {
    'Noto Sans SC': {'light': 'Noto Sans SC Light', 'medium': 'Noto Sans SC Medium', 'bold': 'Noto Sans SC Bold',
                     'black': 'Noto Sans SC Black'},
    'Noto Serif SC': {'light': 'Noto Serif SC Light', 'medium': 'Noto Serif SC Medium', 'bold': 'Noto Serif SC Bold',
                      'black': 'Noto Serif SC Black'},
    'Microsoft YaHei': {'light': 'Microsoft YaHei Light'},
    'DengXian': {'light': 'DengXian Light'},
    'HarmonyOS Sans SC': {'light': 'HarmonyOS Sans SC Light', 'medium': 'HarmonyOS Sans SC Medium',
                          'bold': 'HarmonyOS Sans SC Bold', 'black': 'HarmonyOS Sans SC Black'},
    'Bahnschrift': {'light': 'Bahnschrift Light', 'medium': 'Bahnschrift SemiBold', 'bold': 'Bahnschrift SemiBold'},
}

_CACHE_DIR = os.path.join(os.environ.get('LOCALAPPDATA') or os.path.expanduser('~'), 'pptstudio')
_INDEX_FILE = os.path.join(_CACHE_DIR, 'font_index.json')


def _font_dirs():
    dirs = []
    if sys.platform == 'win32':
        windir = os.environ.get('WINDIR', r'C:\Windows')
        dirs.append(os.path.join(windir, 'Fonts'))
        la = os.environ.get('LOCALAPPDATA')
        if la:
            dirs.append(os.path.join(la, 'Microsoft', 'Windows', 'Fonts'))
    elif sys.platform == 'darwin':
        dirs += ['/System/Library/Fonts', '/Library/Fonts', os.path.expanduser('~/Library/Fonts')]
    else:
        dirs += ['/usr/share/fonts', '/usr/local/share/fonts', os.path.expanduser('~/.fonts')]
    return [d for d in dirs if os.path.isdir(d)]


def _scan_fonts():
    """Map lower-case family name -> list of {path, index, weight, italic, variable}."""
    from fontTools.ttLib import TTFont, TTCollection
    idx = {}

    def add(name, rec):
        if not name:
            return
        idx.setdefault(name.strip().lower(), []).append(rec)

    for d in _font_dirs():
        for root, _, files in os.walk(d):
            for fn in files:
                if not fn.lower().endswith(('.ttf', '.otf', '.ttc', '.otc')):
                    continue
                path = os.path.join(root, fn)
                try:
                    if fn.lower().endswith(('.ttc', '.otc')):
                        fonts = TTCollection(path, lazy=True).fonts
                    else:
                        fonts = [TTFont(path, lazy=True)]
                except Exception:
                    continue
                for i, f in enumerate(fonts):
                    try:
                        name = f['name']
                        os2 = f['OS/2'] if 'OS/2' in f else None
                        weight = getattr(os2, 'usWeightClass', 400) if os2 else 400
                        italic = bool(getattr(os2, 'fsSelection', 0) & 1) if os2 else False
                        variable = 'fvar' in f
                        rec = dict(path=path, index=i, weight=weight, italic=italic, variable=variable)
                        fams = set()
                        for rn in name.names:
                            if rn.nameID in (1, 4, 16):
                                try:
                                    fams.add(rn.toUnicode())
                                except Exception:
                                    pass
                        for fam in fams:
                            add(fam, rec)
                        if variable:
                            # named instances e.g. "Noto Sans SC Black"
                            base = None
                            for rn in name.names:
                                if rn.nameID == 1:
                                    try:
                                        base = rn.toUnicode(); break
                                    except Exception:
                                        pass
                            for inst in f['fvar'].instances:
                                try:
                                    sub = name.getDebugName(inst.subfamilyNameID)
                                except Exception:
                                    sub = None
                                if base and sub:
                                    r2 = dict(rec); r2['weight'] = int(inst.coordinates.get('wght', 400))
                                    r2['instance'] = sub
                                    add(f'{base} {sub}', r2)
                    except Exception:
                        continue
    return idx


@lru_cache(maxsize=1)
def font_index():
    try:
        if os.path.exists(_INDEX_FILE):
            data = json.load(open(_INDEX_FILE, encoding='utf-8'))
            if data.get('_dirs') == _font_dirs() and data.get('_n') == _count_font_files():
                return data['fonts']
    except Exception:
        pass
    try:
        fonts = _scan_fonts()
    except Exception:
        fonts = {}
    try:
        os.makedirs(_CACHE_DIR, exist_ok=True)
        json.dump({'_dirs': _font_dirs(), '_n': _count_font_files(), 'fonts': fonts},
                  open(_INDEX_FILE, 'w', encoding='utf-8'), ensure_ascii=False)
    except Exception:
        pass
    return fonts


def _count_font_files():
    n = 0
    for d in _font_dirs():
        for _, _, files in os.walk(d):
            n += sum(1 for f in files if f.lower().endswith(('.ttf', '.otf', '.ttc', '.otc')))
    return n


def is_installed(family: str) -> bool:
    return family.strip().lower() in font_index()


def pick(stack, portable=False) -> str:
    """Return the first installed family from a stack name or list."""
    if isinstance(stack, str):
        key = ('portable_' + stack) if portable and ('portable_' + stack) in STACKS else stack
        cands = STACKS.get(key, [stack])
    else:
        cands = list(stack)
    for c in cands:
        if is_installed(c):
            return c
    return cands[-1]


def weight_family(family: str, weight: str) -> str | None:
    """Family name for a weight ('light'|'medium'|'bold'|'black') if such a named face is installed."""
    name = WEIGHT_NAMES.get(family, {}).get(weight)
    if name and is_installed(name):
        return name
    cand = f'{family} {weight.capitalize()}'
    if is_installed(cand):
        return cand
    return None


# ---------------------------------------------------------------- measurement
_PIL_SIZE = 100


@lru_cache(maxsize=64)
def _pil_font(family: str, bold: bool):
    from PIL import ImageFont
    recs = font_index().get(family.strip().lower())
    if not recs:
        return None
    target = 700 if bold else 400
    rec = min(recs, key=lambda r: (r.get('italic', False), abs(r.get('weight', 400) - target)))
    try:
        f = ImageFont.truetype(rec['path'], _PIL_SIZE, index=rec.get('index', 0))
        if rec.get('variable'):
            try:
                inst = rec.get('instance') or ('Bold' if bold else 'Regular')
                f.set_variation_by_name(inst)
            except Exception:
                pass
        return f
    except Exception:
        return None


_CJK_RE = re.compile(r'[\u2e80-\u2fdf\u3000-\u303f\u3040-\u30ff\u3100-\u312f\u3190-\u31ff\u3400-\u4dbf'
                     r'\u4e00-\u9fff\uf900-\ufaff\ufe30-\ufe4f\uff00-\uffef]')


def is_cjk(ch: str) -> bool:
    return bool(_CJK_RE.match(ch))


def _fallback_width(text, bold):
    w = 0.0
    for ch in text:
        if is_cjk(ch):
            w += 1.0
        elif ch == ' ':
            w += 0.28
        elif ch.isdigit():
            w += 0.56
        elif ch.isupper():
            w += 0.66
        elif ch in 'il.,;:!|\'`':
            w += 0.26
        else:
            w += 0.52
    return w * (1.06 if bold else 1.0)


@lru_cache(maxsize=20000)
def text_width(text: str, size: float, ea: str = 'Microsoft YaHei', latin: str | None = None,
               bold: bool = False, spacing: float = 0.0) -> float:
    """Width in points of a single-line string. spacing = extra character spacing in pt."""
    latin = latin or ea
    total = 0.0
    # split into script runs
    for m in re.finditer(r'([\u2e80-\u9fff\uf900-\ufaff\ufe30-\ufe4f\uff00-\uffef\u3000-\u303f]+)|([^\u2e80-\u9fff\uf900-\ufaff\ufe30-\ufe4f\uff00-\uffef\u3000-\u303f]+)', text):
        seg = m.group(0)
        if m.group(1):  # CJK ideographs / full-width punctuation: fixed 1 em advance in every CJK font
            total += len(seg) * size * 1.0
            continue
        fam = latin
        f = _pil_font(fam, bold)
        if f is None and fam != ea:
            f = _pil_font(ea, bold)
        if f is not None:
            try:
                total += f.getlength(seg) * size / _PIL_SIZE
                continue
            except Exception:
                pass
        total += _fallback_width(seg, bold) * size
    return total + spacing * len(text)


# kinsoku: characters that must not start / end a line
NO_START = set('，。、；：！？）》」』】〕〗〉”’%‰℃°,.;:!?)]}…—～·')
NO_END = set('（《「『【〔〖〈“‘([{')


def _units(text):
    """Split a paragraph into breakable units (CJK char, latin word incl. trailing space)."""
    return re.findall(r'[A-Za-z0-9\-\+\.\,/%°_@#&\'"$€¥²³]+ ?|\s|.', text)


def wrap(text: str, width: float, size: float, ea='Microsoft YaHei', latin=None, bold=False, spacing=0.0):
    """Greedy PowerPoint-like wrapping. Returns list of lines (for one paragraph)."""
    if width <= 0:
        return [text]
    units = _units(text)
    lines, cur = [], ''
    for u in units:
        cand = cur + u
        if text_width(cand.rstrip(), size, ea, latin, bold, spacing) <= width or not cur:
            cur = cand
            continue
        # overflow: break before u (respect kinsoku)
        if u and u[0] in NO_START and len(cur) > 1:
            # move last char of cur down with the punctuation
            lines.append(cur[:-1].rstrip())
            cur = cur[-1] + u
        elif cur and cur[-1] in NO_END and len(cur) > 1:
            lines.append(cur[:-1].rstrip())
            cur = cur[-1] + u
        else:
            lines.append(cur.rstrip())
            cur = u.lstrip() if u.strip() else ''
        # very long single unit (e.g. URL) -> hard split
        while text_width(cur, size, ea, latin, bold, spacing) > width and len(cur) > 1:
            k = len(cur)
            while k > 1 and text_width(cur[:k], size, ea, latin, bold, spacing) > width:
                k -= 1
            lines.append(cur[:k]); cur = cur[k:]
    if cur or not lines:
        lines.append(cur.rstrip())
    return lines


def layout_height(paragraphs, width, size, ea='Microsoft YaHei', latin=None, bold=False,
                  line_spacing=1.0, space_after=0.0, space_before=0.0, spacing=0.0):
    """Height (pt) and line count for a list of paragraphs rendered in a box of given width (pt)."""
    n = 0
    h = 0.0
    widest = 0.0
    for i, p in enumerate(paragraphs):
        ls = wrap(p, width, size, ea, latin, bold, spacing) if p else ['']
        n += len(ls)
        for l in ls:
            widest = max(widest, text_width(l, size, ea, latin, bold, spacing))
        h += len(ls) * size * LINE_PITCH * line_spacing
        if i > 0:
            h += space_before
        if i < len(paragraphs) - 1:
            h += space_after
    return h, n, widest


def fit_size(paragraphs, width, height, size_max, size_min=10, ea='Microsoft YaHei', latin=None, bold=False,
             line_spacing=1.0, space_after_ratio=0.0, spacing=0.0, max_lines=None, step=0.5):
    """Largest font size (<= size_max) for which the text fits the box. Returns (size, fits)."""
    s = size_max
    while s >= size_min - 1e-6:
        h, n, widest = layout_height(paragraphs, width, s, ea, latin, bold, line_spacing,
                                     space_after=space_after_ratio * s, spacing=spacing)
        if h <= height + 0.5 and (max_lines is None or n <= max_lines):
            return s, True
        s -= step
    return size_min, False


def available_report():
    """Human readable report of which stack fonts are installed."""
    out = []
    for k, fams in STACKS.items():
        got = [f for f in fams if is_installed(f)]
        out.append(f'{k:15s} -> {pick(k)}   (installed: {", ".join(got) or "none"})')
    return '\n'.join(out)
