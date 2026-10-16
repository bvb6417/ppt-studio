"""数据示意图（matplotlib，白底 / 透明底）：细胞图谱 UMAP、肝小叶分区、拟时序分岔、基因模块热图、空间图。

Run:  python make_figs.py   -> figs/*.png
虚构论文 + 模拟数据，PPT 中统一标注“示意 / 模拟数据”。数据图一律用代码画，不交给生图模型。
"""
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt                       # noqa: E402
import numpy as np                                    # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from matplotlib.patches import Polygon, Circle, FancyArrowPatch  # noqa: E402
import matplotlib.patheffects as pe  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'figs')
os.makedirs(OUT, exist_ok=True)

INK, TEAL, CORAL, MUTED = '#24282E', '#14665E', '#E07A3F', '#8A8F98'
plt.rcParams.update({'font.family': ['Microsoft YaHei', 'SimHei', 'DejaVu Sans'], 'axes.unicode_minus': False,
                     'font.size': 9, 'axes.linewidth': 0.7, 'axes.edgecolor': '#555555', 'legend.frameon': False,
                     'xtick.direction': 'out', 'ytick.direction': 'out', 'text.color': INK,
                     'axes.labelcolor': INK, 'xtick.color': '#555555', 'ytick.color': '#555555'})

# 细胞类型：名称、颜色、占比（%）
TYPES = [('门周肝细胞 Z1', '#2A9D8F', 21.4), ('中间带肝细胞 Z2', '#4C8DCB', 18.6), ('中央周肝细胞 Z3', '#7A6BC9', 16.9),
         ('增殖肝细胞', '#E07A3F', 7.8), ('内皮细胞', '#58B4AE', 12.1), ('库普弗细胞', '#E9A23B', 9.3),
         ('星状细胞', '#C9727E', 5.6), ('胆管细胞', '#8BB174', 3.9), ('淋巴细胞', '#9AA3AE', 4.4)]
COL = {n: c for n, c, _ in TYPES}


def save(fig, name, transparent=True):
    fig.savefig(os.path.join(OUT, name), dpi=260, bbox_inches='tight', pad_inches=0.04, transparent=transparent)
    plt.close(fig)


def _umap(seed=5, scale=1.0):
    """模拟 UMAP：肝细胞 Z1→Z2→Z3 连续带 + 从 Z2 伸出的增殖分支 + 其他细胞岛。返回 [(type, xy)]。"""
    rng = np.random.default_rng(seed)
    out = []
    n = int(5200 * scale)
    t = rng.uniform(0, 1, n)
    cx, cy = -4.6 + 8.4 * t, 2.1 * np.sin(np.pi * t) - 0.6
    nx, ny = np.cos(np.pi * t) * 0.6, -1.0
    w = rng.normal(0, 0.55, n) * (0.8 + 0.4 * np.sin(np.pi * t))
    xy = np.c_[cx + w * 0.35 * nx + rng.normal(0, 0.18, n), cy + w * 0.7 + rng.normal(0, 0.12, n)]
    zone = np.where(t < 0.36, 0, np.where(t < 0.66, 1, 2))
    for k in range(3):
        out.append((TYPES[k][0], xy[zone == k]))
    m = int(900 * scale)                                       # 增殖分支：从 Z2 中部向上弯出
    s = rng.uniform(0, 1, m) ** 0.8
    bx, by = -0.2 + 1.6 * s - 1.2 * s ** 2, 1.6 + 2.9 * s
    out.append((TYPES[3][0], np.c_[bx + rng.normal(0, 0.28, m), by + rng.normal(0, 0.22, m)]))
    blobs = [(TYPES[4][0], (5.6, -3.4), (0.9, 0.55), 1500), (TYPES[5][0], (-5.4, -3.6), (0.75, 0.6), 1150),
             (TYPES[6][0], (1.0, -4.6), (0.75, 0.45), 700), (TYPES[7][0], (-6.3, 1.9), (0.45, 0.6), 480),
             (TYPES[8][0], (6.6, 2.6), (0.5, 0.65), 550)]
    for name, (mx, my), (sx, sy), k in blobs:
        k = int(k * scale)
        th = rng.uniform(0, 2 * np.pi, k)
        r = np.abs(rng.normal(0, 1, k)) ** 0.8
        out.append((name, np.c_[mx + sx * r * np.cos(th) * 1.3, my + sy * r * np.sin(th) * 1.3]))
    return out


# ------------------------------------------------------------------ 1 细胞图谱 UMAP
def umap():
    fig, ax = plt.subplots(figsize=(6.2, 4.6))
    data = _umap()
    for name, xy in data:
        ax.scatter(xy[:, 0], xy[:, 1], s=2.2, color=COL[name], alpha=0.75, lw=0, rasterized=True)
    labels = {TYPES[0][0]: (-4.6, 0.55), TYPES[1][0]: (-2.3, 2.35), TYPES[2][0]: (4.6, 0.55),
              TYPES[3][0]: (2.5, 4.7), TYPES[4][0]: (5.6, -5.25), TYPES[5][0]: (-5.4, -5.45),
              TYPES[6][0]: (1.0, -5.7), TYPES[7][0]: (-6.3, 3.35), TYPES[8][0]: (6.6, 4.4)}
    for name, (lx, ly) in labels.items():
        ax.text(lx, ly, name, ha='center', va='center', fontsize=7.8, color=COL[name], fontweight='bold',
                path_effects=[pe.withStroke(linewidth=2.6, foreground='white')])
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ('top', 'right'):
        ax.spines[sp].set_visible(False)
    ax.set_xlabel('UMAP 1', fontsize=8, color=MUTED)
    ax.set_ylabel('UMAP 2', fontsize=8, color=MUTED)
    ax.set_xlim(-7.6, 8.0)
    ax.set_ylim(-6.1, 5.4)
    save(fig, 'umap.png')


# ------------------------------------------------------------------ 2 肝小叶分区示意
def lobule():
    fig, ax = plt.subplots(figsize=(4.0, 4.0))
    ax.set_aspect('equal')
    ax.axis('off')
    ang = np.deg2rad(np.arange(0, 360, 60) + 30)
    zones = [(1.0, '#BFE3DD'), (0.68, '#C9D8F0'), (0.36, '#DCD4F3')]
    for r, c in zones:
        ax.add_patch(Polygon(np.c_[r * np.cos(ang), r * np.sin(ang)], closed=True, fc=c, ec='white', lw=1.6))
    for a in np.deg2rad(np.arange(0, 360, 20)):
        ax.plot([0.1 * np.cos(a), 0.9 * np.cos(a)], [0.1 * np.sin(a), 0.9 * np.sin(a)], color='white', lw=0.8,
                alpha=0.8)
    ax.add_patch(Circle((0, 0), 0.085, fc='#7A6BC9', ec='white', lw=1.2))
    for a in ang:
        px, py = 1.0 * np.cos(a), 1.0 * np.sin(a)
        for dx, dy, c in ((-0.05, 0.03, '#2A9D8F'), (0.05, 0.03, CORAL), (0, -0.05, '#8BB174')):
            ax.add_patch(Circle((px + dx, py + dy), 0.045, fc=c, ec='white', lw=0.8))
        ax.add_patch(FancyArrowPatch((px * 0.86, py * 0.86), (px * 0.58, py * 0.58), arrowstyle='-|>',
                                     mutation_scale=8, color=TEAL, lw=1.0, alpha=0.8))
    ax.text(0, -0.2, '中央静脉', ha='center', fontsize=7.5, color='#5A4E9C')
    ax.text(0.76, 0.0, 'Z1', ha='center', va='center', fontsize=9, color='#1F6F66', fontweight='bold')
    ax.text(0.46, 0.0, 'Z2', ha='center', va='center', fontsize=9, color='#2F5F9A', fontweight='bold')
    ax.text(0.2, 0.0, 'Z3', ha='center', va='center', fontsize=9, color='#5A4E9C', fontweight='bold')
    ax.text(1.08, 0.66, '门管区', fontsize=7.5, color='#1F6F66')
    ax.set_xlim(-1.15, 1.45)
    ax.set_ylim(-1.1, 1.1)
    save(fig, 'lobule.png')


# ------------------------------------------------------------------ 3 拟时序分岔
def trajectory():
    rng = np.random.default_rng(8)
    fig, ax = plt.subplots(figsize=(4.6, 3.8))
    n = 2600
    s = rng.uniform(0, 1, n)                                   # 主干：静息 Z2 → 激活
    trunk = np.c_[-3 + 3.0 * s + rng.normal(0, 0.22, n), -1.6 + 1.4 * s + rng.normal(0, 0.2, n)]
    m = 1500
    u = rng.uniform(0, 1, m)                                   # 分支 A：增殖
    ba = np.c_[0 + 1.8 * u + rng.normal(0, 0.2, m), -0.2 + 2.6 * u + rng.normal(0, 0.18, m)]
    u2 = rng.uniform(0, 1, m)                                  # 分支 B：功能维持
    bb = np.c_[0 + 3.0 * u2 + rng.normal(0, 0.2, m), -0.2 - 0.9 * u2 + rng.normal(0, 0.18, m)]
    pts = np.r_[trunk, ba, bb]
    pt = np.r_[0.5 * s, 0.5 + 0.5 * u, 0.5 + 0.5 * u2]
    cmap = LinearSegmentedColormap.from_list('pt', ['#C9D8F0', '#4C8DCB', '#14665E', '#E07A3F'])
    sc = ax.scatter(pts[:, 0], pts[:, 1], c=pt, cmap=cmap, s=2.4, lw=0, alpha=0.85, rasterized=True)
    for path, col in (([(-3, -1.6), (-1.5, -0.9), (0, -0.2)], INK), ([(0, -0.2), (0.9, 1.1), (1.8, 2.4)], CORAL),
                      ([(0, -0.2), (1.5, -0.65), (3.0, -1.1)], TEAL)):
        p = np.array(path)
        ax.plot(p[:, 0], p[:, 1], color=col, lw=1.6)
        ax.annotate('', xy=p[-1], xytext=p[-2], arrowprops=dict(arrowstyle='-|>', color=col, lw=1.6))
    ax.plot(0, -0.2, 'o', ms=7, mfc='white', mec=INK, mew=1.4)
    ax.text(-0.95, 0.25, '分岔点', fontsize=8, color=INK,
            bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='none', alpha=0.9))
    ax.text(1.95, 2.55, '增殖态', fontsize=8.5, color=CORAL, fontweight='bold')
    ax.text(2.0, -1.95, '功能维持态', fontsize=8.5, color=TEAL, fontweight='bold')
    ax.text(-3.1, -2.15, '静息 Z2 肝细胞', fontsize=8, color='#2F5F9A')
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    cb = fig.colorbar(sc, ax=ax, fraction=0.035, pad=0.06)
    cb.set_label('拟时序', fontsize=7.5)
    cb.set_ticks([])
    cb.outline.set_visible(False)
    save(fig, 'trajectory.png')


# ------------------------------------------------------------------ 4 基因模块热图
def heatmap():
    rng = np.random.default_rng(4)
    x = np.linspace(0, 1, 120)
    mods = [('应激早反应', ['Jun', 'Fos', 'Atf3'], 0.12, 0.10), ('细胞周期', ['Mki67', 'Top2a', 'Ccnb1'], 0.55, 0.12),
            ('代谢重编程', ['Hmgcs2', 'Pck1', 'G6pc'], 0.38, 0.16), ('成熟功能', ['Alb', 'Cyp2e1', 'Apoa1'], 0.92, 0.18)]
    rows, ylabels = [], []
    for name, genes, mu, sd in mods:
        for g in genes:
            prof = np.exp(-((x - mu - rng.normal(0, 0.02)) / sd) ** 2) + rng.normal(0, 0.025, x.size)
            if name == '成熟功能':
                prof = np.clip(0.8 - 0.7 * np.exp(-((x - 0.45) / 0.2) ** 2), 0, 1) + rng.normal(0, 0.025, x.size)
            rows.append(np.convolve(prof, np.ones(9) / 9, mode='same'))
            ylabels.append(g)
    Z = np.array(rows)
    Z = (Z - Z.min(1, keepdims=True)) / (Z.max(1, keepdims=True) - Z.min(1, keepdims=True))
    fig, ax = plt.subplots(figsize=(4.6, 3.4))
    cmap = LinearSegmentedColormap.from_list('h', ['#F7F7F5', '#BFE3DD', '#2A9D8F', '#14665E', '#E07A3F'])
    ax.imshow(Z, aspect='auto', cmap=cmap, interpolation='bilinear')
    ax.set_yticks(range(len(ylabels)))
    ax.set_yticklabels(ylabels, fontsize=7, style='italic')
    ax.set_xticks([0, 59, 119])
    ax.set_xticklabels(['静息', '分岔', '终末'], fontsize=7.5)
    for k in range(1, 4):
        ax.axhline(k * 3 - 0.5, color='white', lw=2)
    for k, (name, *_rest) in enumerate(mods):
        ax.text(121.5, k * 3 + 1, name, va='center', fontsize=7.8, color=INK)
    ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_xlabel('拟时序 →', fontsize=8, color=MUTED)
    save(fig, 'heatmap.png')


# ------------------------------------------------------------------ 5 空间转录组：增殖评分
def spatial():
    rng = np.random.default_rng(12)
    R = 1.0
    cvs = []
    for i in range(-3, 4):
        for j in range(-3, 4):
            cvs.append((i * 1.5 * R * 1.15, j * np.sqrt(3) * R + (np.sqrt(3) / 2 * R if i % 2 else 0)))
    cvs = np.array(cvs) + rng.normal(0, 0.16, (len(cvs), 2))      # 小叶不规则
    gain = rng.uniform(0.55, 1.0, len(cvs))
    step = 0.075
    gx, gy = np.meshgrid(np.arange(-4.2, 4.2, step), np.arange(-3.4, 3.4, step * 0.87))
    gx = gx + (np.arange(gx.shape[0])[:, None] % 2) * step / 2
    P = np.c_[gx.ravel(), gy.ravel()]
    ang = np.arctan2(P[:, 1], P[:, 0])
    edge = 3.2 + 0.35 * np.sin(3 * ang + 0.6) + 0.2 * np.cos(5 * ang)
    keep = np.hypot(P[:, 0] * 0.85, P[:, 1]) < edge
    P = P[keep]
    D = np.hypot(P[:, None, 0] - cvs[None, :, 0], P[:, None, 1] - cvs[None, :, 1])
    near = np.argmin(D, axis=1)
    r = np.clip(D[np.arange(len(P)), near] / R, 0, 1.1)
    wav = 0.08 * np.sin(P[:, 0] * 2.3 + 1.0) * np.cos(P[:, 1] * 1.9)             # 平滑扰动，避免完美圆环
    score = np.exp(-((r + wav - 0.5) / 0.22) ** 2) * gain[near] * (0.7 + 0.3 * rng.random(r.size))         + rng.normal(0, 0.06, r.size)
    fig, ax = plt.subplots(figsize=(4.8, 3.9))
    cmap = LinearSegmentedColormap.from_list('s', ['#EEF1F2', '#CFE8E3', '#5DB3A7', '#E9A23B', '#E07A3F'])
    sc = ax.scatter(P[:, 0], P[:, 1], c=np.clip(score, 0, 1), cmap=cmap, s=4.2, lw=0, rasterized=True)
    inside = np.hypot(cvs[:, 0] * 0.85, cvs[:, 1]) < 2.9
    ax.scatter(cvs[inside, 0], cvs[inside, 1], s=22, facecolor='white', edgecolor='#7A6BC9', lw=1.1, zorder=3)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.plot([2.2, 3.2], [-3.25, -3.25], color=INK, lw=1.6)
    ax.text(2.7, -3.12, '200 μm', ha='center', fontsize=7, color=INK)
    cb = fig.colorbar(sc, ax=ax, fraction=0.035, pad=0.01)
    cb.set_label('增殖评分（48 h）', fontsize=7.5)
    cb.outline.set_visible(False)
    cb.ax.tick_params(labelsize=6.5)
    save(fig, 'spatial.png')


if __name__ == '__main__':
    for f in (umap, lobule, trajectory, heatmap, spatial):
        f()
        print('ok', f.__name__)
