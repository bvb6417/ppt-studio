"""Synthetic research figures for galleries, demos and layout tests (never for real decks).

Each function renders one realistic-looking scientific figure with Chinese labels (matplotlib, cached PNG) for a
fictional project “深埋长隧洞围岩灾变机理与智能预警” — so sample pages look like real NSFC / 科技奖 slides instead
of grey placeholders. All data are made up; captions in the gallery say “示例”.

    from pptstudio import samples
    paths = samples.all_figures()          # dict name -> png path
"""
from __future__ import annotations

import os

import numpy as np

from .images import cache_dir

VERSION = 'v4'
NAVY, BLUE, LIGHT, RED, ORANGE, TEAL, GRAY = '#0B3C8C', '#1F6FD1', '#8DB8EA', '#C00000', '#F2A33A', '#159A8C', '#8A93A6'


def _setup():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family': ['Microsoft YaHei', 'SimHei', 'DejaVu Sans'], 'axes.unicode_minus': False,
                         'font.size': 9, 'axes.linewidth': 0.8, 'axes.edgecolor': '#444444',
                         'axes.titlesize': 10, 'legend.frameon': False})
    return plt


def _path(name):
    return os.path.join(cache_dir(), f'sample_{name}_{VERSION}.png')


def _save(fig, name):
    p = _path(name)
    fig.savefig(p, dpi=220, bbox_inches='tight', pad_inches=0.06, facecolor='white')
    import matplotlib.pyplot as plt
    plt.close(fig)
    return p


def _smooth_noise(shape, sigma, seed):
    rng = np.random.default_rng(seed)
    z = rng.standard_normal(shape)
    fy = np.fft.fftfreq(shape[0])[:, None]
    fx = np.fft.fftfreq(shape[1])[None, :]
    g = np.exp(-2 * (np.pi * sigma) ** 2 * (fx ** 2 + fy ** 2))
    out = np.real(np.fft.ifft2(np.fft.fft2(z) * g))
    return (out - out.min()) / (out.max() - out.min())


def route_map():
    """Terrain hillshade + contours with a tunnel route, stations, scale bar and north arrow."""
    p = _path('route_map')
    if os.path.exists(p):
        return p
    plt = _setup()
    from matplotlib.colors import LightSource
    z = 0.65 * _smooth_noise((300, 480), 18, 3) + 0.35 * _smooth_noise((300, 480), 6, 5)
    z = 400 + 2600 * z
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    ls = LightSource(azdeg=315, altdeg=40)
    rgb = ls.shade(z, cmap=plt.get_cmap('gist_earth'), vert_exag=0.02, blend_mode='soft', vmin=0, vmax=3400)
    ax.imshow(rgb, extent=(0, 48, 0, 30), origin='lower')
    ax.contour(np.linspace(0, 48, 480), np.linspace(0, 30, 300), z, levels=12, colors='k', linewidths=0.25,
               alpha=0.35)
    t = np.linspace(0, 1, 200)
    x = 3 + 42 * t
    y = 8 + 14 * t + 3.2 * np.sin(2.6 * np.pi * t)
    ax.plot(x, y, color='white', lw=4.2, solid_capstyle='round')
    ax.plot(x, y, color=RED, lw=2.2, solid_capstyle='round', label='隧洞轴线')
    for f, lab in ((0.0, '进口'), (0.32, '1#支洞'), (0.63, '2#支洞'), (1.0, '出口')):
        i = int(f * 199)
        ax.plot(x[i], y[i], marker='o', ms=7, mfc='white', mec=NAVY, mew=1.6)
        ax.annotate(lab, (x[i], y[i]), xytext=(0, 9), textcoords='offset points', ha='center', fontsize=9,
                    color='white', fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.2', fc=NAVY, ec='none', alpha=0.85))
    ax.plot([34, 44], [2.2, 2.2], color='white', lw=3)
    ax.plot([34, 44], [2.2, 2.2], color='k', lw=1.2)
    ax.text(39, 3.0, '10 km', ha='center', fontsize=8, color='white', fontweight='bold')
    ax.annotate('N', xy=(2.6, 28.4), xytext=(2.6, 25.0), ha='center', fontsize=10, color='white',
                fontweight='bold', arrowprops=dict(arrowstyle='-|>', color='white', lw=1.6))
    leg = ax.legend(loc='lower left', fontsize=8, labelcolor='white', frameon=True, facecolor=NAVY,
                    edgecolor='none', framealpha=0.75)
    ax.set_xticks([]), ax.set_yticks([])
    return _save(fig, 'route_map')


def stress_field():
    """Kirsch-type tangential stress around a circular opening (filled contours + colorbar)."""
    p = _path('stress_field')
    if os.path.exists(p):
        return p
    plt = _setup()
    a, sv, sh = 1.0, 52.0, 34.0
    X, Y = np.meshgrid(np.linspace(-4, 4, 400), np.linspace(-4, 4, 400))
    r = np.hypot(X, Y)
    th = np.arctan2(Y, X)
    rr = np.maximum(r, a)
    s_t = (sv + sh) / 2 * (1 + a ** 2 / rr ** 2) - (sv - sh) / 2 * (1 + 3 * a ** 4 / rr ** 4) * np.cos(2 * th)
    s_t = np.where(r < a, np.nan, s_t)
    fig, ax = plt.subplots(figsize=(4.6, 4.0))
    cf = ax.contourf(X, Y, s_t, levels=18, cmap='RdYlBu_r')
    ax.contour(X, Y, s_t, levels=9, colors='k', linewidths=0.3, alpha=0.4)
    ax.add_patch(plt.Circle((0, 0), a, fc='white', ec='k', lw=1.2))
    ax.text(0, 0, '隧洞', ha='center', va='center', fontsize=10, fontweight='bold', color=NAVY)
    for s in (-1, 1):
        ax.annotate('', xy=(0, s * 3.2), xytext=(0, s * 4.1),
                    arrowprops=dict(arrowstyle='-|>', color='k', lw=1.4, shrinkA=0, shrinkB=0))
        ax.annotate('', xy=(s * 3.2, 0), xytext=(s * 4.1, 0),
                    arrowprops=dict(arrowstyle='-|>', color='k', lw=1.0, shrinkA=0, shrinkB=0))
    ax.text(0.25, 3.55, 'σv = 52 MPa', fontsize=8)
    ax.text(2.45, 0.25, 'σh = 34 MPa', fontsize=8)
    ax.set_aspect('equal'), ax.set_xticks([]), ax.set_yticks([])
    cb = fig.colorbar(cf, ax=ax, fraction=0.046, pad=0.03)
    cb.set_label('切向应力 / MPa')
    return _save(fig, 'stress_field')


def microseismic():
    """Synthetic microseismic waveform (top) + spectrogram (bottom)."""
    p = _path('microseismic')
    if os.path.exists(p):
        return p
    plt = _setup()
    fs = 6000
    t = np.arange(0, 0.5, 1 / fs)
    rng = np.random.default_rng(11)
    sig = 0.04 * rng.standard_normal(t.size)
    for t0, f0, amp in ((0.08, 420, 1.0), (0.21, 260, 0.6), (0.33, 650, 0.45)):
        env = np.where(t > t0, np.exp(-(t - t0) * 38), 0)
        sig += amp * env * np.sin(2 * np.pi * f0 * (t - t0) * (1 + 0.4 * (t - t0)))
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(5.6, 3.8), sharex=True, gridspec_kw={'height_ratios': [1, 1.4]})
    a1.plot(t * 1000, sig, color=NAVY, lw=0.6)
    a1.set_ylabel('幅值 / mm·s⁻¹')
    for t0, lab in ((0.08, 'P'), (0.21, 'S')):
        a1.axvline(t0 * 1000, color=RED, lw=1, ls='--')
        a1.text(t0 * 1000 + 4, 0.9, lab + '波初至', color=RED, fontsize=8)
    a1.spines[['top', 'right']].set_visible(False)
    a2.specgram(sig, NFFT=256, Fs=fs, noverlap=200, cmap='magma', xextent=(0, 500))
    a2.set_ylim(0, 1200)
    a2.set_ylabel('频率 / Hz'), a2.set_xlabel('时间 / ms')
    fig.tight_layout()
    return _save(fig, 'microseismic')


def section():
    """Tunnel cross-section schematic: rock mass, lining, monitoring instruments, crack zones."""
    p = _path('section')
    if os.path.exists(p):
        return p
    plt = _setup()
    from matplotlib.patches import Polygon, Wedge, Rectangle
    fig, ax = plt.subplots(figsize=(5.2, 4.0))
    ax.add_patch(Rectangle((-6, -5), 12, 10, fc='#D9D2C3', ec='none'))
    rng = np.random.default_rng(2)
    for _ in range(260):
        x, y = rng.uniform(-6, 6), rng.uniform(-5, 5)
        ax.plot([x, x + rng.uniform(0.1, 0.4)], [y, y + rng.uniform(-0.1, 0.1)], color='#A79F8D', lw=0.6)
    arch = [(np.cos(a) * 2.6, np.sin(a) * 2.6 + 0.2) for a in np.linspace(0, np.pi, 60)]
    shape = [(2.6, -2.2)] + arch + [(-2.6, -2.2)]
    ax.add_patch(Polygon([(x * 1.18, y * 1.12) for x, y in shape], fc='#BFC6D1', ec='#6E7787', lw=1))
    ax.add_patch(Polygon(shape, fc='white', ec=NAVY, lw=1.6))
    ax.add_patch(Wedge((0, 0.2), 4.4, 25, 70, width=1.3, fc=RED, alpha=0.18, ec='none'))
    ax.add_patch(Wedge((0, 0.2), 4.4, 110, 155, width=1.3, fc=RED, alpha=0.18, ec='none'))
    for ang in (35, 48, 61, 120, 136):
        a = np.radians(ang)
        r0 = 3.15
        ax.plot([np.cos(a) * r0, np.cos(a) * (r0 + 1.0) + 0.2], [np.sin(a) * r0 + 0.2, np.sin(a) * (r0 + 1.0) + 0.45],
                color=RED, lw=1.1)
    instr = [((-1.6, 3.6), 's', TEAL, '多点位移计'), ((1.9, 3.5), '^', ORANGE, '微震传感器'),
             ((3.6, 0.6), 'D', BLUE, '应力计'), ((-3.6, 0.4), 'o', NAVY, '渗压计')]
    for (x, y), mk, c, lab in instr:
        ax.plot(x, y, marker=mk, ms=9, mfc=c, mec='white', mew=1.2)
        ax.annotate(lab, (x, y), xytext=(8, 4), textcoords='offset points', fontsize=8.5, color='#1A1A1A',
                    bbox=dict(boxstyle='round,pad=0.25', fc='white', ec=c, lw=0.8))
    ax.text(0, -1.0, '开挖断面\nD = 7.2 m', ha='center', va='center', fontsize=9, color=NAVY, fontweight='bold')
    ax.text(3.1, 4.4, '损伤区', color=RED, fontsize=9, fontweight='bold')
    ax.set_xlim(-6, 6), ax.set_ylim(-5, 5), ax.set_aspect('equal'), ax.axis('off')
    return _save(fig, 'section')


def network():
    """Monitoring network along the tunnel: sensors → gateways → cloud platform."""
    p = _path('network')
    if os.path.exists(p):
        return p
    plt = _setup()
    from matplotlib.patches import FancyBboxPatch
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    ax.add_patch(FancyBboxPatch((0.3, 0.6), 9.4, 0.7, boxstyle='round,pad=0.02,rounding_size=0.3', fc='#E6EBF2',
                                ec='#8A93A6', lw=1))
    ax.text(5.0, 0.95, '隧洞（长 32.6 km）', ha='center', va='center', fontsize=9, color='#4A5468')
    xs = np.linspace(0.8, 9.2, 12)
    gws = [2.2, 5.0, 7.8]
    for i, x in enumerate(xs):
        c = [TEAL, ORANGE, BLUE][i % 3]
        ax.plot(x, 1.55, marker='o', ms=6.5, mfc=c, mec='white', mew=1)
        g = min(gws, key=lambda v: abs(v - x))
        ax.plot([x, g], [1.62, 2.45], color='#9AA6BC', lw=0.7, ls='--')
    for g in gws:
        ax.add_patch(FancyBboxPatch((g - 0.45, 2.45), 0.9, 0.5, boxstyle='round,pad=0.02,rounding_size=0.08',
                                    fc=NAVY, ec='none'))
        ax.text(g, 2.7, '边缘网关', ha='center', va='center', fontsize=7.5, color='white')
        ax.annotate('', xy=(5.0, 3.55), xytext=(g, 2.98), arrowprops=dict(arrowstyle='-|>', color=NAVY, lw=1.2))
    ax.add_patch(FancyBboxPatch((3.4, 3.55), 3.2, 0.75, boxstyle='round,pad=0.02,rounding_size=0.15', fc=BLUE,
                                ec='none'))
    ax.text(5.0, 3.92, '智能预警云平台', ha='center', va='center', fontsize=10, color='white', fontweight='bold')
    for x, lab, c in ((0.9, '位移', TEAL), (2.0, '微震', ORANGE), (3.1, '应力', BLUE)):
        ax.plot(x, 0.18, marker='o', ms=6, mfc=c, mec='white')
        ax.text(x + 0.15, 0.18, lab, va='center', fontsize=8)
    ax.set_xlim(0, 10), ax.set_ylim(0, 4.5), ax.axis('off')
    return _save(fig, 'network')


def risk3d():
    """3-D risk surface: rockburst index vs burial depth and lateral pressure coefficient."""
    p = _path('risk3d')
    if os.path.exists(p):
        return p
    plt = _setup()
    d = np.linspace(500, 2500, 60)
    k = np.linspace(0.6, 1.8, 60)
    D, K = np.meshgrid(d, k)
    R = 0.25 + 0.55 * (D - 500) / 2000 + 0.18 * np.cos(2.6 * (K - 1.1)) + 0.06 * np.sin(D / 230)
    fig = plt.figure(figsize=(5.4, 4.0))
    ax = fig.add_subplot(projection='3d')
    sf = ax.plot_surface(D, K, R, cmap='turbo', linewidth=0, antialiased=True, alpha=0.95)
    ax.contour(D, K, R, zdir='z', offset=R.min() - 0.1, cmap='turbo', levels=10, linewidths=0.8)
    ax.set_xlabel('埋深 / m', labelpad=6), ax.set_ylabel('侧压系数', labelpad=6), ax.set_zlabel('岩爆风险指数', labelpad=4)
    ax.set_zlim(R.min() - 0.1, R.max())
    ax.view_init(elev=26, azim=-128)
    fig.colorbar(sf, ax=ax, shrink=0.6, pad=0.08)
    return _save(fig, 'risk3d')


def curves():
    """Displacement monitoring curves with warning thresholds and an alarm window."""
    p = _path('curves')
    if os.path.exists(p):
        return p
    plt = _setup()
    t = np.arange(0, 120)
    rng = np.random.default_rng(4)
    fig, ax = plt.subplots(figsize=(6.0, 3.4))
    for c, s, lab in ((NAVY, 1.0, 'K12+350'), (BLUE, 0.72, 'K12+410'), (TEAL, 0.5, 'K12+470')):
        base = 26 * s * (1 - np.exp(-t / 30)) + 0.04 * s * np.maximum(t - 70, 0) ** 1.6
        ax.plot(t, base + rng.normal(0, 0.35, t.size), color=c, lw=1.4, label=lab)
    ax.axhline(35, color=ORANGE, ls='--', lw=1.2)
    ax.axhline(45, color=RED, ls='--', lw=1.2)
    ax.text(2, 35.8, '黄色预警 35 mm', color=ORANGE, fontsize=8)
    ax.text(2, 45.8, '红色预警 45 mm', color=RED, fontsize=8)
    ax.axvspan(88, 102, color=RED, alpha=0.08)
    ax.annotate('提前 6 d 发出预警', xy=(90, 39), xytext=(52, 52), fontsize=8.5, color=RED,
                arrowprops=dict(arrowstyle='->', color=RED, lw=1))
    ax.set_xlabel('时间 / d'), ax.set_ylabel('累计位移 / mm')
    ax.set_xlim(0, 120), ax.set_ylim(0, 60)
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(alpha=0.25)
    ax.legend(loc='upper left', fontsize=8, ncol=3)
    return _save(fig, 'curves')


def scatter():
    """Predicted vs measured with 1:1 line and ±10 % band."""
    p = _path('scatter')
    if os.path.exists(p):
        return p
    plt = _setup()
    rng = np.random.default_rng(8)
    m = rng.uniform(5, 60, 140)
    pr = m * (1 + rng.normal(0, 0.05, m.size))
    pb = m * (1 + rng.normal(0.08, 0.16, m.size))
    fig, ax = plt.subplots(figsize=(4.4, 4.0))
    xx = np.array([0, 65])
    ax.fill_between(xx, xx * 0.9, xx * 1.1, color=BLUE, alpha=0.1, label='±10% 误差带')
    ax.plot(xx, xx, color='k', lw=1, ls='--')
    ax.scatter(m, pb, s=12, color=GRAY, alpha=0.6, label='经验模型  R²=0.71')
    ax.scatter(m, pr, s=14, color=RED, alpha=0.8, label='本文模型  R²=0.96')
    ax.set_xlim(0, 65), ax.set_ylim(0, 65)
    ax.set_xlabel('实测位移 / mm'), ax.set_ylabel('预测位移 / mm')
    ax.legend(loc='upper left', fontsize=8)
    ax.spines[['top', 'right']].set_visible(False)
    ax.set_aspect('equal')
    return _save(fig, 'scatter')


def all_figures():
    """Render (or reuse) every sample figure. Returns {name: png path}."""
    return {f.__name__: f() for f in (route_map, stress_field, microseismic, section, network, risk3d, curves,
                                      scatter)}
