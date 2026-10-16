"""Color utilities: parsing, tint/shade/mix, contrast, palette derivation."""
from __future__ import annotations

import colorsys


def norm(c: str) -> str:
    """'#1e66f5' / '1E66F5' / 'abc' -> '1E66F5'"""
    c = c.strip().lstrip('#').upper()
    if len(c) == 3:
        c = ''.join(ch * 2 for ch in c)
    if len(c) != 6 or any(ch not in '0123456789ABCDEF' for ch in c):
        raise ValueError(f'bad color: {c!r}')
    return c


def rgb(c: str):
    c = norm(c)
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def hexs(r, g, b) -> str:
    return '%02X%02X%02X' % tuple(max(0, min(255, int(round(v)))) for v in (r, g, b))


def mix(a: str, b: str, t: float) -> str:
    """t=0 -> a, t=1 -> b"""
    ra, rb = rgb(a), rgb(b)
    return hexs(*[x + (y - x) * t for x, y in zip(ra, rb)])


def tint(c: str, t: float) -> str:
    """Mix toward white. t=0.9 -> very pale."""
    return mix(c, 'FFFFFF', t)


def shade(c: str, t: float) -> str:
    """Mix toward black."""
    return mix(c, '000000', t)


def hls(c: str):
    r, g, b = [v / 255 for v in rgb(c)]
    return colorsys.rgb_to_hls(r, g, b)


def from_hls(h, l, s) -> str:
    r, g, b = colorsys.hls_to_rgb(h % 1.0, max(0, min(1, l)), max(0, min(1, s)))
    return hexs(r * 255, g * 255, b * 255)


def rotate(c: str, degrees: float, l=None, s=None) -> str:
    h, ll, ss = hls(c)
    return from_hls(h + degrees / 360.0, ll if l is None else l, ss if s is None else s)


def luminance(c: str) -> float:
    def ch(v):
        v = v / 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = rgb(c)
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a: str, b: str) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def is_dark(c: str) -> bool:
    return luminance(c) < 0.35


def readable(bg: str, dark='1F2329', light='FFFFFF') -> str:
    """Text color with the better contrast on bg."""
    return light if contrast(bg, light) >= contrast(bg, dark) else dark


def harmonize_accent(primary: str) -> str:
    """A warm/cool accent that pops against primary (split-complement, controlled lightness)."""
    h, l, s = hls(primary)
    acc = from_hls(h + 0.5 - 0.08, 0.55, min(0.85, max(0.6, s)))
    return acc
