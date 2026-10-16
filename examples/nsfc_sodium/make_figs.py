"""示意图（matplotlib）：硬碳储钠机理、充放电曲线、循环、孔结构—容量关系、吸附能分布、原位 XRD。

Run:  python make_figs.py   -> figs/*.png
全部为示例数据（虚构项目），在 PPT 中统一标注“示意 / 示例数据”。
"""
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt                       # noqa: E402
import numpy as np                                    # noqa: E402
from matplotlib.collections import LineCollection     # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'figs')
os.makedirs(OUT, exist_ok=True)

NAVY, BLUE, LIGHT, RED, GOLD, GRAY = '#0B3C8C', '#1E6FE0', '#9CC2F2', '#C00000', '#E8A317', '#8A93A6'
plt.rcParams.update({'font.family': ['Microsoft YaHei', 'SimHei', 'DejaVu Sans'], 'axes.unicode_minus': False,
                     'font.size': 9, 'axes.linewidth': 0.8, 'axes.edgecolor': '#444444', 'legend.frameon': False,
                     'xtick.direction': 'in', 'ytick.direction': 'in', 'mathtext.fontset': 'stix'})


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=240, bbox_inches='tight', pad_inches=0.05, facecolor='white')
    plt.close(fig)


# ------------------------------------------------------------------ 1 储钠机理示意
def mechanism():
    rng = np.random.default_rng(7)
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.add_patch(plt.Rectangle((0, 0), 16, 10, color='#F4F7FC', zorder=0))
    pores = [(4.2, 6.6, 1.25), (11.6, 3.4, 1.45), (12.6, 7.7, 0.9)]

    def in_pore(x, y, m=0.9):
        return any((x - px) ** 2 + (y - py) ** 2 < (pr + m) ** 2 for px, py, pr in pores)

    segs, golds, reds = [], [], []
    for gx in np.arange(0.9, 16, 1.55):
        for gy in np.arange(0.9, 10, 1.35):
            cx, cy = gx + rng.uniform(-0.35, 0.35), gy + rng.uniform(-0.3, 0.3)
            if in_pore(cx, cy) or not (0.6 < cx < 15.4 and 0.6 < cy < 9.4):
                continue
            th = rng.uniform(-0.9, 0.9) + (np.pi / 2 if rng.random() < 0.35 else 0)
            L, k, n = rng.uniform(1.0, 1.5), rng.uniform(-0.18, 0.18), rng.integers(3, 5)
            t = np.linspace(-L / 2, L / 2, 24)
            u, v = np.cos(th), np.sin(th)
            for j in range(n):
                off = (j - (n - 1) / 2) * 0.27
                px, py = t, k * t ** 2 + off
                segs.append(np.c_[cx + px * u - py * v, cy + px * v + py * u])
            if rng.random() < 0.5:   # 层间嵌入的钠
                for tt in (-0.35, 0.05, 0.42):
                    off = 0.135
                    golds.append((cx + tt * u - (k * tt ** 2 + off) * v, cy + tt * v + (k * tt ** 2 + off) * u))
            if rng.random() < 0.35:  # 边缘缺陷吸附
                ex, ey = cx + (L / 2 + 0.12) * u, cy + (L / 2 + 0.12) * v
                reds.append((ex, ey))
                golds.append((ex + 0.18 * u, ey + 0.18 * v))
    ax.add_collection(LineCollection(segs, colors='#3B4B66', linewidths=1.25, alpha=0.85, zorder=2))
    for px, py, pr in pores:                       # 闭孔：外圈弯曲碳层 + 内部准金属钠团簇
        for rr, a in ((pr + 0.06, 0.95), (pr + 0.33, 0.75)):
            th = np.linspace(0, 2 * np.pi, 160)
            wob = 1 + 0.03 * np.sin(5 * th + px)
            ax.plot(px + rr * wob * np.cos(th), py + rr * wob * np.sin(th), color='#3B4B66', lw=1.3, alpha=a, zorder=2)
        ax.add_patch(plt.Circle((px, py), pr - 0.05, color='#FFF4D6', zorder=1))
        s = 0.25
        for ix in np.arange(-pr, pr + 0.01, s):
            for iy in np.arange(-pr, pr + 0.01, s * 0.87):
                xx = ix + (s / 2 if int(round(iy / (s * 0.87))) % 2 else 0)
                if xx ** 2 + iy ** 2 < (pr - 0.22) ** 2:
                    ax.add_patch(plt.Circle((px + xx, py + iy), 0.085, color=GOLD, ec='#B07A0A', lw=0.4, zorder=3))
    for gx, gy in golds:
        ax.add_patch(plt.Circle((gx, gy), 0.085, color=GOLD, ec='#B07A0A', lw=0.4, zorder=3))
    for rx, ry in reds:
        ax.plot(rx, ry, marker='x', ms=4.5, mew=1.3, color=RED, zorder=4)

    def label(x, y, tx, ty, num, text):
        ax.annotate('', xy=(x, y), xytext=(tx, ty), arrowprops=dict(arrowstyle='-', color=NAVY, lw=0.9), zorder=5)
        ax.add_patch(plt.Circle((tx, ty), 0.36, color=NAVY, zorder=6))
        ax.text(tx, ty, num, color='white', ha='center', va='center', fontsize=9, fontweight='bold', zorder=7)
        ax.text(tx + 0.5, ty, text, color=NAVY, ha='left', va='center', fontsize=9.5, fontweight='bold', zorder=7,
                bbox=dict(boxstyle='round,pad=0.25', fc='white', ec='none', alpha=0.92))

    rx, ry = reds[2] if len(reds) > 2 else (8, 5)
    label(rx, ry, 6.4, 9.35, '①', '缺陷 / 边缘吸附')
    gx, gy = golds[0]
    label(gx, gy, 0.75, 0.6, '②', '类石墨层间嵌入')
    label(11.6, 3.4 - 1.0, 9.6, 0.6, '③', '闭孔填充（准金属钠团簇）')
    save(fig, 'mechanism.png')


# ------------------------------------------------------------------ 2 恒流充放电曲线
def gcd():
    fig, ax = plt.subplots(figsize=(4.6, 3.2))
    q = np.linspace(0, 1, 400)

    def discharge(cap, slope_cap):
        x = q * cap
        v = np.where(x < slope_cap, 1.25 * np.exp(-x / 18) + 0.95 * (1 - x / slope_cap) + 0.1,
                     0.1 - 0.085 * np.clip((x - slope_cap) / (cap - slope_cap), 0, 1) ** 1.8)
        v[0] = 2.0
        return x, np.clip(v, 0.005, 2.0)

    for i, (cap, sc, a, lab) in enumerate([(372, 128, 1.0, '第 2 圈'), (366, 126, 0.55, '第 50 圈'),
                                           (358, 124, 0.3, '第 200 圈')]):
        x, v = discharge(cap, sc)
        ax.plot(x, v, color=BLUE, lw=1.6, alpha=a, label=lab)
        ax.plot(x * 0.985, np.clip(v + 0.05 + 0.04 * (v > 0.15), 0, 2.05), color=RED, lw=1.4, alpha=a)  # 充电
    ax.axvspan(0, 128, color=LIGHT, alpha=0.28, lw=0)
    ax.axvspan(128, 372, color='#FCE3B0', alpha=0.45, lw=0)
    ax.text(64, 1.72, '斜坡区\n≈ 128 mAh g$^{-1}$', ha='center', va='center', fontsize=8.5, color=NAVY)
    ax.text(250, 0.62, '平台区（< 0.1 V）\n≈ 244 mAh g$^{-1}$', ha='center', va='center', fontsize=8.5, color='#9A5B00')
    ax.set_xlim(0, 390)
    ax.set_ylim(0, 2.1)
    ax.set_xlabel('比容量 / mAh g$^{-1}$')
    ax.set_ylabel('电压 / V（vs. Na$^+$/Na）')
    ax.plot([], [], color=RED, lw=1.4, label='充电（脱钠）')
    ax.legend(loc='upper right', fontsize=7.5)
    save(fig, 'gcd.png')


# ------------------------------------------------------------------ 3 循环稳定性
def cycle():
    rng = np.random.default_rng(3)
    n = np.arange(1, 1001, 8)
    ours = 318 * (1 - 0.075 * (n / 1000) ** 0.9) + rng.normal(0, 1.6, n.size)
    ref = 286 * (1 - 0.31 * (n / 1000) ** 0.8) + rng.normal(0, 2.0, n.size)
    ce = 99.92 - 0.6 * np.exp(-n / 12) + rng.normal(0, 0.03, n.size)
    fig, ax = plt.subplots(figsize=(4.6, 3.2))
    ax.scatter(n, ours, s=7, color=BLUE, label='本项目 HC-3', zorder=3)
    ax.scatter(n, ref, s=7, color=GRAY, label='对照硬碳', zorder=3)
    ax.set_ylim(150, 360)
    ax.set_xlim(0, 1010)
    ax.set_xlabel('循环次数')
    ax.set_ylabel('放电比容量 / mAh g$^{-1}$')
    ax.annotate('保持率 92.6%', xy=(980, ours[-1]), xytext=(560, 262), fontsize=8.5, color=NAVY,
                arrowprops=dict(arrowstyle='->', color=NAVY, lw=0.8))
    ax.annotate('保持率 68.9%', xy=(980, ref[-1]), xytext=(620, 175), fontsize=8.5, color='#555555',
                arrowprops=dict(arrowstyle='->', color='#777777', lw=0.8))
    ax2 = ax.twinx()
    ax2.plot(n, ce, color=RED, lw=0.9, alpha=0.8)
    ax2.set_ylim(90, 101)
    ax2.set_ylabel('库伦效率 / %', color=RED)
    ax2.tick_params(axis='y', colors=RED, direction='in')
    ax.legend(loc='lower left', fontsize=7.5, markerscale=2)
    ax.text(1000, 157, '2 C（1 C = 300 mA g$^{-1}$）', ha='right', fontsize=7.5, color='#666666')
    save(fig, 'cycle.png')


# ------------------------------------------------------------------ 4 闭孔体积—平台容量
def pore():
    rng = np.random.default_rng(11)
    x = np.array([0.031, 0.045, 0.058, 0.066, 0.079, 0.088, 0.097, 0.112, 0.121, 0.135])
    y = 72 + 1420 * x + rng.normal(0, 9, x.size)
    fig, ax = plt.subplots(figsize=(4.4, 3.2))
    k, b = np.polyfit(x, y, 1)
    xx = np.linspace(0.02, 0.145, 50)
    ax.fill_between(xx, k * xx + b - 18, k * xx + b + 18, color=LIGHT, alpha=0.35, lw=0)
    ax.plot(xx, k * xx + b, '--', color=NAVY, lw=1.1)
    ax.scatter(x, y, s=34, c=x, cmap=LinearSegmentedColormap.from_list('b', [LIGHT, NAVY]), edgecolor='white',
               lw=0.6, zorder=3)
    r2 = 1 - np.sum((y - (k * x + b)) ** 2) / np.sum((y - y.mean()) ** 2)
    ax.text(0.03, 0.92, f'$R^2$ = {r2:.2f}', transform=ax.transAxes, fontsize=9, color=NAVY)
    ax.scatter([0.121], [y[8]], s=120, facecolor='none', edgecolor=RED, lw=1.3, zorder=4)
    ax.annotate('HC-3', xy=(0.121, y[8]), xytext=(0.1, y[8] + 34), color=RED, fontsize=8.5,
                arrowprops=dict(arrowstyle='->', color=RED, lw=0.8))
    ax.set_xlabel('闭孔体积 / cm$^3$ g$^{-1}$（SAXS）')
    ax.set_ylabel('平台容量 / mAh g$^{-1}$')
    ax.set_xlim(0.02, 0.145)
    save(fig, 'pore.png')


# ------------------------------------------------------------------ 5 缺陷位点钠吸附能分布
def dft():
    fig, ax = plt.subplots(figsize=(4.6, 3.4))
    a = 1.0
    pts = []
    for i in range(-2, 16):
        for j in range(-2, 12):
            x0, y0 = i * 1.5 * a, j * np.sqrt(3) * a + (np.sqrt(3) / 2 * a if i % 2 else 0)
            pts.append((x0, y0))
            pts.append((x0 + a, y0))
    pts = np.array(pts)
    W, H = 18, 14
    xs, ys = np.meshgrid(np.linspace(0, W, 360), np.linspace(0, H, 280))
    sites = [(4.5, 4.2, -1.15, 1.6, '空位'), (12.5, 9.6, -0.85, 1.4, '吡啶 N'), (13.6, 3.6, -0.6, 1.2, 'C=O'),
             (5.6, 10.6, -0.35, 1.0, '石墨烯 sp$^2$')]
    E = -0.12 + 0.03 * np.sin(xs * 1.4) * np.cos(ys * 1.2)
    for sx, sy, e, r, _ in sites[:3]:
        E += e * np.exp(-((xs - sx) ** 2 + (ys - sy) ** 2) / (2 * r ** 2))
    cmap = LinearSegmentedColormap.from_list('ads', ['#0B3C8C', '#1E6FE0', '#9CC2F2', '#F4F7FC', '#FCE3B0'])
    im = ax.imshow(E, extent=(0, W, 0, H), origin='lower', cmap=cmap, vmin=-1.3, vmax=0.05, interpolation='bicubic')
    keep = (pts[:, 0] > -0.5) & (pts[:, 0] < W + 0.5) & (pts[:, 1] > -0.5) & (pts[:, 1] < H + 0.5)
    p = pts[keep]
    d =np.hypot(p[:, None, 0] - p[None, :, 0], p[:, None, 1] - p[None, :, 1])
    ii, jj = np.where((d > 0.9) & (d < 1.1))
    segs = [[p[i], p[j]] for i, j in zip(ii, jj) if i < j and np.hypot(p[i, 0] - 4.5, p[i, 1] - 4.2) > 0.7]
    ax.add_collection(LineCollection(segs, colors='#4A5D80', linewidths=0.6, alpha=0.3))
    for sx, sy, e, r, name in sites:
        ax.plot(sx, sy, 'o', ms=6, color=GOLD, mec='#7A5200', mew=0.6)
        ax.text(sx + 0.55, sy + 0.55, f'{name}\n{e:+.2f} eV', fontsize=7.5, color='#10213F',
                bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='none', alpha=0.85))
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.set_xticks([])
    ax.set_yticks([])
    cb = fig.colorbar(im, ax=ax, fraction=0.045, pad=0.02)
    cb.set_label('Na 吸附能 / eV', fontsize=8)
    cb.ax.tick_params(labelsize=7)
    save(fig, 'dft.png')


# ------------------------------------------------------------------ 6 原位 XRD 瀑布图
def insitu():
    fig, ax = plt.subplots(figsize=(4.6, 3.4))
    th = np.linspace(15, 32, 500)
    volts = np.r_[np.linspace(2.0, 0.1, 9), np.linspace(0.08, 0.005, 5)]
    cmap = LinearSegmentedColormap.from_list('v', ['#C00000', '#E8A317', '#1E6FE0', '#0B3C8C'])
    for k, v in enumerate(volts):
        c = 23.2 - (0.85 * (2.0 - v) / 1.9 if v >= 0.1 else 0.85)   # 斜坡区 (002) 左移，平台区基本不变
        y = np.exp(-((th - c) / 2.4) ** 2) + 0.18 * np.exp(-((th - 26.4) / 6) ** 2) * 0.4
        ax.plot(th, y + k * 0.32, color=cmap(k / (len(volts) - 1)), lw=1.3)
    ax.axvline(23.2, color='#999999', lw=0.7, ls=':')
    ax.axvline(22.35, color=NAVY, lw=0.7, ls=':')
    ax.annotate('', xy=(22.2, 5.4), xytext=(23.3, 5.4), arrowprops=dict(arrowstyle='->', color=NAVY, lw=1.0))
    ax.text(23.6, 5.4, '(002) 峰左移：层间距增大', ha='left', va='center', fontsize=8, color=NAVY)
    for k, lab, col in ((0, '2.0 V', RED), (8, '0.1 V', '#1E6FE0'), (13, '0.005 V', NAVY)):
        ax.text(31.7, k * 0.32 + 0.2, lab, ha='right', va='center', fontsize=7.5, color=col,
                bbox=dict(boxstyle='round,pad=0.12', fc='white', ec='none', alpha=0.9))
    ax.text(25.4, 3.62, '平台区峰位不变 → 储钠转向闭孔', fontsize=7.5, color=NAVY,
            bbox=dict(boxstyle='round,pad=0.25', fc='white', ec='none', alpha=0.9))
    ax.set_xlim(15, 32)
    ax.set_ylim(-0.1, 5.75)
    ax.set_yticks([])
    ax.set_xlabel('2θ / °（Cu Kα）')
    ax.set_ylabel('强度（偏移）')
    save(fig, 'insitu.png')


# ------------------------------------------------------------------ 7 封面配图（无文字）
def cover_art():
    """深蓝底上的硬碳微结构：白色弯曲碳层 + 发光的金色钠离子 / 闭孔钠团簇，用于封面右上角。"""
    rng = np.random.default_rng(21)
    W, H = 10.0, 10.4
    fig = plt.figure(figsize=(5.0, 5.2))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis('off')
    grad = np.linspace(0, 1, 256)[:, None] * np.ones((1, 256))
    ax.imshow(grad, extent=(0, W, 0, H), origin='lower', aspect='auto', zorder=0,
              cmap=LinearSegmentedColormap.from_list('bg', ['#0A2E78', '#1556C8', '#3B8BF0']))
    pores = [(6.6, 6.9, 1.35), (3.2, 3.0, 1.0), (8.3, 2.4, 0.75)]

    def in_pore(x, y, m=0.8):
        return any((x - px) ** 2 + (y - py) ** 2 < (pr + m) ** 2 for px, py, pr in pores)

    segs, golds = [], []
    for gx in np.arange(0.4, W, 1.25):
        for gy in np.arange(0.4, H, 1.1):
            cx, cy = gx + rng.uniform(-0.3, 0.3), gy + rng.uniform(-0.25, 0.25)
            if in_pore(cx, cy):
                continue
            th = rng.uniform(-0.9, 0.9) + (np.pi / 2 if rng.random() < 0.35 else 0)
            L, k, n = rng.uniform(0.8, 1.25), rng.uniform(-0.2, 0.2), rng.integers(3, 5)
            t = np.linspace(-L / 2, L / 2, 24)
            u, v = np.cos(th), np.sin(th)
            for j in range(n):
                off = (j - (n - 1) / 2) * 0.22
                px, py = t, k * t ** 2 + off
                segs.append(np.c_[cx + px * u - py * v, cy + px * v + py * u])
            if rng.random() < 0.55:
                for tt in (-0.28, 0.1):
                    golds.append((cx + tt * u - (k * tt ** 2 + 0.11) * v, cy + tt * v + (k * tt ** 2 + 0.11) * u))
    ax.add_collection(LineCollection(segs, colors='white', linewidths=1.1, alpha=0.55, zorder=2))
    for px, py, pr in pores:
        for rr, a in ((pr + 0.05, 0.8), (pr + 0.28, 0.5)):
            th = np.linspace(0, 2 * np.pi, 160)
            wob = 1 + 0.03 * np.sin(5 * th + px)
            ax.plot(px + rr * wob * np.cos(th), py + rr * wob * np.sin(th), color='white', lw=1.2, alpha=a, zorder=2)
        for g in range(6):
            ax.add_patch(plt.Circle((px, py), pr * (1.0 - g * 0.12), color='#FFC94A', alpha=0.06, lw=0, zorder=1))
        s = 0.21
        for ix in np.arange(-pr, pr + 0.01, s):
            for iy in np.arange(-pr, pr + 0.01, s * 0.87):
                xx = ix + (s / 2 if int(round(iy / (s * 0.87))) % 2 else 0)
                if xx ** 2 + iy ** 2 < (pr - 0.2) ** 2:
                    ax.add_patch(plt.Circle((px + xx, py + iy), 0.07, color='#FFD15C', lw=0, zorder=3))
    for gx, gy in golds:
        ax.add_patch(plt.Circle((gx, gy), 0.2, color='#FFC94A', alpha=0.18, lw=0, zorder=3))
        ax.add_patch(plt.Circle((gx, gy), 0.075, color='#FFE08A', lw=0, zorder=4))
    fig.savefig(os.path.join(OUT, 'cover_art.png'), dpi=300)
    plt.close(fig)


if __name__ == '__main__':
    for f in (mechanism, gcd, cycle, pore, dft, insitu, cover_art):
        f()
        print('ok', f.__name__)
