"""SVG path/primitive -> list of subpaths of absolute segments (M, L, C, Z), arcs converted to cubic beziers."""
import math, re


class _Scanner:
    _num = re.compile(r'\s*,?\s*([-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?)')
    _cmd = re.compile(r'\s*,?\s*([MmLlHhVvCcSsQqTtAaZz])')
    _flag = re.compile(r'\s*,?\s*([01])')
    def __init__(self, d):
        self.d = d; self.i = 0
    def cmd(self):
        m = self._cmd.match(self.d, self.i)
        if m: self.i = m.end(); return m.group(1)
        return None
    def has_num(self):
        return self._num.match(self.d, self.i) is not None
    def num(self):
        m = self._num.match(self.d, self.i)
        if not m: raise ValueError('number expected at %d in %r' % (self.i, self.d))
        self.i = m.end(); return float(m.group(1))
    def flag(self):
        m = self._flag.match(self.d, self.i)
        if not m: raise ValueError('flag expected at %d' % self.i)
        self.i = m.end(); return int(m.group(1))
    def done(self):
        return self.d[self.i:].strip(' ,\t\n') == ''


def _arc_to_beziers(x1, y1, rx, ry, phi, fa, fs, x2, y2):
    """Endpoint arc -> list of cubic bezier (c1x,c1y,c2x,c2y,x,y). SVG spec F.6."""
    if rx == 0 or ry == 0:
        return [(x1, y1, x2, y2, x2, y2)]
    rx, ry = abs(rx), abs(ry)
    cphi, sphi = math.cos(math.radians(phi)), math.sin(math.radians(phi))
    dx, dy = (x1 - x2) / 2, (y1 - y2) / 2
    x1p = cphi * dx + sphi * dy
    y1p = -sphi * dx + cphi * dy
    lam = (x1p ** 2) / (rx ** 2) + (y1p ** 2) / (ry ** 2)
    if lam > 1:
        s = math.sqrt(lam)
        rx, ry = rx * s, ry * s
    num = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
    den = rx * rx * y1p * y1p + ry * ry * x1p * x1p
    co = math.sqrt(max(0, num / den)) if den else 0
    if fa == fs:
        co = -co
    cxp = co * rx * y1p / ry
    cyp = -co * ry * x1p / rx
    cx = cphi * cxp - sphi * cyp + (x1 + x2) / 2
    cy = sphi * cxp + cphi * cyp + (y1 + y2) / 2

    def ang(ux, uy, vx, vy):
        a = math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)
        return a
    t1 = ang(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dt = ang((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not fs and dt > 0:
        dt -= 2 * math.pi
    elif fs and dt < 0:
        dt += 2 * math.pi
    n = max(1, int(math.ceil(abs(dt) / (math.pi / 2) - 1e-9)))
    seg = dt / n
    k = 4 / 3 * math.tan(seg / 4)
    out = []
    t = t1
    for _ in range(n):
        c1, s1 = math.cos(t), math.sin(t)
        c2, s2 = math.cos(t + seg), math.sin(t + seg)
        p1 = (c1 - k * s1, s1 + k * c1)
        p2 = (c2 + k * s2, s2 - k * c2)
        p3 = (c2, s2)
        pts = []
        for (ux, uy) in (p1, p2, p3):
            X = cx + rx * (cphi * ux) - ry * (sphi * uy)
            Y = cy + rx * (sphi * ux) + ry * (cphi * uy)
            pts += [X, Y]
        out.append(tuple(pts))
        t += seg
    return out


def parse_path(d):
    """Return list of subpaths; each subpath = {'start':(x,y), 'segs':[('L',x,y)|('C',x1,y1,x2,y2,x,y)], 'closed':bool}."""
    sc = _Scanner(d)
    cx = cy = sx = sy = 0.0
    last_c2 = last_q = None
    subs = []; cur = None; cmd = None
    while not sc.done():
        c = sc.cmd()
        if c is not None:
            cmd = c
        elif cmd is None or not sc.has_num():
            break
        if cmd in 'Zz':
            if cur is not None:
                cur['closed'] = True
            cx, cy = sx, sy; cur = None; last_c2 = last_q = None
            continue
        rel = cmd.islower(); C = cmd.upper()
        if C == 'M':
            x, y = sc.num(), sc.num()
            if rel: x += cx; y += cy
            cur = {'start': (x, y), 'segs': [], 'closed': False}; subs.append(cur)
            cx, cy = sx, sy = x, y
            cmd = 'l' if rel else 'L'; last_c2 = last_q = None
            continue
        if cur is None:
            cur = {'start': (cx, cy), 'segs': [], 'closed': False}; subs.append(cur); sx, sy = cx, cy
        if C == 'L':
            x, y = sc.num(), sc.num()
            if rel: x += cx; y += cy
            cur['segs'].append(('L', x, y)); cx, cy = x, y; last_c2 = last_q = None
        elif C == 'H':
            x = sc.num()
            if rel: x += cx
            cur['segs'].append(('L', x, cy)); cx = x; last_c2 = last_q = None
        elif C == 'V':
            y = sc.num()
            if rel: y += cy
            cur['segs'].append(('L', cx, y)); cy = y; last_c2 = last_q = None
        elif C == 'C':
            x1, y1, x2, y2, x, y = [sc.num() for _ in range(6)]
            if rel: x1 += cx; y1 += cy; x2 += cx; y2 += cy; x += cx; y += cy
            cur['segs'].append(('C', x1, y1, x2, y2, x, y)); cx, cy = x, y; last_c2 = (x2, y2); last_q = None
        elif C == 'S':
            x2, y2, x, y = [sc.num() for _ in range(4)]
            if rel: x2 += cx; y2 += cy; x += cx; y += cy
            x1, y1 = (2 * cx - last_c2[0], 2 * cy - last_c2[1]) if last_c2 else (cx, cy)
            cur['segs'].append(('C', x1, y1, x2, y2, x, y)); cx, cy = x, y; last_c2 = (x2, y2); last_q = None
        elif C == 'Q':
            qx, qy, x, y = [sc.num() for _ in range(4)]
            if rel: qx += cx; qy += cy; x += cx; y += cy
            cur['segs'].append(('C', cx + 2/3*(qx-cx), cy + 2/3*(qy-cy), x + 2/3*(qx-x), y + 2/3*(qy-y), x, y))
            cx, cy = x, y; last_q = (qx, qy); last_c2 = None
        elif C == 'T':
            x, y = sc.num(), sc.num()
            if rel: x += cx; y += cy
            qx, qy = (2 * cx - last_q[0], 2 * cy - last_q[1]) if last_q else (cx, cy)
            cur['segs'].append(('C', cx + 2/3*(qx-cx), cy + 2/3*(qy-cy), x + 2/3*(qx-x), y + 2/3*(qy-y), x, y))
            cx, cy = x, y; last_q = (qx, qy); last_c2 = None
        elif C == 'A':
            rx, ry, phi = sc.num(), sc.num(), sc.num()
            fa, fs = sc.flag(), sc.flag()
            x, y = sc.num(), sc.num()
            if rel: x += cx; y += cy
            for b in _arc_to_beziers(cx, cy, rx, ry, phi, fa, fs, x, y):
                cur['segs'].append(('C',) + tuple(b))
            cx, cy = x, y; last_c2 = last_q = None
    return subs


def circle_path(cx, cy, r):
    return ellipse_path(cx, cy, r, r)


def ellipse_path(cx, cy, rx, ry):
    k = 0.5522847498
    return [{'start': (cx + rx, cy), 'closed': True, 'segs': [
        ('C', cx + rx, cy + k * ry, cx + k * rx, cy + ry, cx, cy + ry),
        ('C', cx - k * rx, cy + ry, cx - rx, cy + k * ry, cx - rx, cy),
        ('C', cx - rx, cy - k * ry, cx - k * rx, cy - ry, cx, cy - ry),
        ('C', cx + k * rx, cy - ry, cx + rx, cy - k * ry, cx + rx, cy)]}]


def rect_path(x, y, w, h, rx=0, ry=None):
    ry = rx if ry is None else ry
    rx, ry = min(rx, w / 2), min(ry, h / 2)
    if rx <= 0:
        return [{'start': (x, y), 'closed': True, 'segs': [('L', x + w, y), ('L', x + w, y + h), ('L', x, y + h)]}]
    k = 0.5522847498
    return [{'start': (x + rx, y), 'closed': True, 'segs': [
        ('L', x + w - rx, y), ('C', x + w - rx + k * rx, y, x + w, y + ry - k * ry, x + w, y + ry),
        ('L', x + w, y + h - ry), ('C', x + w, y + h - ry + k * ry, x + w - rx + k * rx, y + h, x + w - rx, y + h),
        ('L', x + rx, y + h), ('C', x + rx - k * rx, y + h, x, y + h - ry + k * ry, x, y + h - ry),
        ('L', x, y + ry), ('C', x, y + ry - k * ry, x + rx - k * rx, y, x + rx, y)]}]


def node_to_subpaths(tag, a):
    f = lambda k, dflt=0: float(a.get(k, dflt))
    if tag == 'path':
        return parse_path(a['d'])
    if tag == 'circle':
        return circle_path(f('cx'), f('cy'), f('r'))
    if tag == 'ellipse':
        return ellipse_path(f('cx'), f('cy'), f('rx'), f('ry'))
    if tag == 'rect':
        rx = f('rx', a.get('ry', 0)); ry = f('ry', a.get('rx', 0))
        return rect_path(f('x'), f('y'), f('width'), f('height'), rx, ry)
    if tag == 'line':
        return [{'start': (f('x1'), f('y1')), 'closed': False, 'segs': [('L', f('x2'), f('y2'))]}]
    if tag in ('polyline', 'polygon'):
        pts = [float(v) for v in re.findall(r'[-+]?(?:\d*\.\d+|\d+\.?)', a['points'])]
        xy = list(zip(pts[0::2], pts[1::2]))
        return [{'start': xy[0], 'closed': tag == 'polygon', 'segs': [('L', x, y) for x, y in xy[1:]]}]
    return []
