"""Unit helpers. The public API works in inches (floats); python-pptx wants EMU ints."""
EMU_PER_IN = 914400
EMU_PER_PT = 12700
EMU_PER_CM = 360000
SLIDE_W = 13.333  # 16:9 widescreen, inches
SLIDE_H = 7.5


def emu(inches: float) -> int:
    return int(round(inches * EMU_PER_IN))


def pt_emu(points: float) -> int:
    return int(round(points * EMU_PER_PT))


def in2pt(inches: float) -> float:
    return inches * 72.0


def pt2in(points: float) -> float:
    return points / 72.0


def cm(v: float) -> float:
    """centimetres -> inches"""
    return v / 2.54
