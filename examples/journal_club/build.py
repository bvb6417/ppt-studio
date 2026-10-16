"""示例：期刊杂志风 · 组会文献汇报（浅色，衬线标题 + 墨绿 / 暖橙）。

虚构论文“肝脏再生的单细胞时空图谱”，11 页：封面 / 目录 / 背景 / 研究设计 / 三个主要发现 / 空间验证 /
亮点与局限 / 总结与启发 / 结束页。
- 配图分两类：数据图（UMAP、曲线、热图、空间图）由 make_figs.py 用 matplotlib 生成；氛围图 / 插画按
  img/图片提示词.md 用生图模型生成，放进 img/ 后重新运行即自动替换占位图。
- 页眉页脚是自定义的“期刊风”chrome：替换 d.page 之后，skill 自带版式（chart_page、compare）也套用同一套页眉。

Run:  python make_figs.py   (figs/*.png)
      python build.py       -> out/期刊风文献汇报_示例.pptx + out/期刊风文献汇报_示例_preview/
"""
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'scripts'))
sys.path.insert(0, HERE)

from PIL import Image, ImageDraw, ImageFilter, ImageFont      # noqa: E402
from pptstudio import Deck, Box                              # noqa: E402
from pptstudio import images as IMG                          # noqa: E402
import make_figs as MF                                       # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].endswith('.pptx') else \
    os.path.join(HERE, 'out', '期刊风文献汇报_示例.pptx')
W, H = 13.333, 7.5
INK, TEAL, TEAL2, CORAL, MUTED, RULE, PAPER = '1E2227', '14665E', '2A9D8F', 'E07A3F', '8A8F98', 'E2E4E7', 'F6F5F1'
NOTE = '示例论文（虚构）· 模拟数据，仅用于版式演示'
SEC = ['研究背景', '研究设计', '主要发现', '总结与启发']
SEC_EN = ['BACKGROUND', 'STUDY DESIGN', 'FINDINGS', 'TAKEAWAYS']

# ------------------------------------------------------------------ 图片：img/ 下有同名文件就用，否则画占位图
FIG = lambda n: os.path.join(HERE, 'figs', n)               # noqa: E731
GEN = os.path.join(HERE, '_gen')
MISSING = []
if not os.path.exists(FIG('spatial.png')):
    for f in (MF.umap, MF.lobule, MF.trajectory, MF.heatmap, MF.spatial):
        f()


def placeholder(name, size):
    """生图前的占位：白底 + 柔和墨绿 / 暖橙光斑 + 虚线框 + 文件名提示。"""
    os.makedirs(GEN, exist_ok=True)
    p = os.path.join(GEN, f'ph_{name}_{size[0]}x{size[1]}.png')
    if os.path.exists(p):
        return p
    w, h = size
    im = Image.new('RGB', size, (255, 255, 255))
    glow = Image.new('RGB', size, (255, 255, 255))
    g = ImageDraw.Draw(glow)
    for (fx, fy, fr, col) in ((0.62, 0.45, 0.32, (201, 228, 223)), (0.42, 0.62, 0.22, (248, 214, 192)),
                              (0.78, 0.7, 0.18, (214, 226, 242))):
        r = fr * min(w, h)
        g.ellipse([fx * w - r, fy * h - r, fx * w + r, fy * h + r], fill=col)
    im = Image.blend(im, glow.filter(ImageFilter.GaussianBlur(min(w, h) * 0.12)), 0.9)
    d = ImageDraw.Draw(im)
    m = int(min(w, h) * 0.04)
    for x in range(m, w - m, 28):
        d.line([(x, m), (x + 14, m)], fill=(170, 190, 186), width=3)
        d.line([(x, h - m), (x + 14, h - m)], fill=(170, 190, 186), width=3)
    for y in range(m, h - m, 28):
        d.line([(m, y), (m, y + 14)], fill=(170, 190, 186), width=3)
        d.line([(w - m, y), (w - m, y + 14)], fill=(170, 190, 186), width=3)
    try:
        font = ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc', int(min(w, h) * 0.06))
    except OSError:
        font = ImageFont.load_default()
    txt = f'配图位：{name}\n见 img/图片提示词.md'
    bb = d.multiline_textbbox((0, 0), txt, font=font, align='center', spacing=10)
    d.multiline_text(((w - bb[2]) / 2, (h - bb[3]) / 2), txt, fill=(20, 102, 94), font=font, align='center',
                     spacing=10)
    im.save(p)
    return p


def whiten(path, white=244):
    """生图的“白底”常是 #F5F5F5 左右，放在纯白页面上会露出浅灰方框：把白点拉到 255。"""
    os.makedirs(GEN, exist_ok=True)
    out = os.path.join(GEN, 'w_' + os.path.splitext(os.path.basename(path))[0] + '.png')
    if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(path):
        Image.open(path).convert('RGB').point(lambda v: min(255, round(v * 255 / white))).save(out)
    return out


def img(name, size, white_bg=True):
    for ext in ('png', 'jpg', 'jpeg', 'webp'):
        p = os.path.join(HERE, 'img', f'{name}.{ext}')
        if os.path.exists(p):
            return whiten(p) if white_bg else p
    MISSING.append(name)
    return placeholder(name, size)


COVER = img('cover', (1920, 1080))
LIVER = img('liver', (1200, 1600))
STEPS = [img(f'step_{i}', (1024, 1024)) for i in (1, 2, 3, 4)]
TISSUE = img('tissue', (2520, 1080), white_bg=False)
ENDING = img('ending', (1920, 1080))


# ------------------------------------------------------------------ 期刊风 chrome
def kicker(cv, x, y, en, zh=None, color=TEAL, size=10.5):
    cv.rect(x, y + 0.07, 0.32, 0.045, fill=color, name='deco:kickbar')
    tx = x + 0.45
    ew = len(en) * (0.66 * size + 3) / 72              # 字距 3 pt 的大写英文宽度（估算偏保守）
    cv.text(tx, y - 0.04, ew, 0.3, en, size=size, color=color, role='number', spacing=3, wrap=False, fit=False,
            name='txt:kicker')
    if zh:
        cv.text(tx + ew + 0.1, y - 0.04, 3.0, 0.3, '·  ' + zh, size=size, color=MUTED, wrap=False, fit=False,
                name='txt:kicker_zh')


KICK = {'en': '', 'zh': ''}


def chrome(d, title):
    cv = d.new(bg=False)
    cv.rect(0, 0, W, H, fill='FFFFFF', name='bg:paper')
    n = len(d.prs.slides)
    kicker(cv, 0.75, 0.42, KICK['en'], KICK['zh'])
    cv.text(0.75, 0.66, 9.6, 0.62, title, size=26, color=INK, role='serif', bold=True, anchor='middle', wrap=False,
            fit=True, min_size=18, name='txt:title')
    cv.text(W - 0.75 - 4.2, 0.38, 4.2, 0.3, 'Journal Club  ·  肝脏再生单细胞图谱', size=9.5, color=MUTED,
            align='right', wrap=False, fit=True, name='txt:runner')
    cv.line(0.75, 1.42, W - 0.75, 1.42, RULE, 0.75)
    cv.rect(0.75, 1.405, 0.9, 0.035, fill=TEAL, name='deco:rulemark')
    cv.line(0.75, H - 0.5, W - 0.75, H - 0.5, RULE, 0.5)
    cv.text(0.75, H - 0.44, 7, 0.26, NOTE, size=8.5, color=MUTED, wrap=False, fit=True, name='txt:note')
    cv.text(W - 0.75 - 1.4, H - 0.46, 1.4, 0.3, f'{n:02d}  /  11', size=10, color=MUTED, role='number',
            align='right', wrap=False, fit=False, name='txt:page')
    cv.content = Box(0.75, 1.7, W - 1.5, H - 1.7 - 0.72)
    return cv


def journal_page(self, title, en=None, source=None, bg=True, section=None, nav=True, num=None):
    """替换 Deck.page：skill 版式（chart_page / compare …）照常调用 d.page()，拿到的是期刊风页眉页脚。"""
    cv = chrome(self, title)
    self.pages[-1] = ('content', title)
    return cv


def caption(cv, x, y, w, letter, text):
    cv.text(x, y, 0.3, 0.3, letter, size=12, color=INK, role='number', bold=True, wrap=False, fit=False,
            name='txt:figletter')
    cv.text(x + 0.3, y + 0.01, w - 0.3, 0.3, text, size=11, color='text', wrap=False, fit=True, min_size=9,
            name='txt:caption')


def stmt(cv, x, y, w, h, text, size=15):
    """结论条：浅米底 + 暖橙竖线 + 衬线粗体。"""
    cv.rect(x, y, w, h, fill=PAPER, name='deco:stmt')
    cv.rect(x, y, 0.06, h, fill=CORAL, name='deco:stmtbar')
    cv.text(x + 0.3, y, w - 0.45, h, text, size=size, color=INK, role='serif', bold=True, anchor='middle',
            fit=True, min_size=11, name='txt:stmt')


# ------------------------------------------------------------------ 1 封面
def cover(d):
    cv = d.new(bg=False)
    cv.rect(0, 0, W, H, fill='FFFFFF', name='bg:paper')
    pic = IMG.fade(IMG.cover_crop(COVER, W / H, focus=(0.7, 0.5)), side='left', start=0.4, end=0.56)
    cv.image(pic, 0, 0, W, H, fit='stretch', name='img:cover')         # 生图左侧本就留白，整张铺满
    x = 0.85
    kicker(cv, x, 0.95, 'JOURNAL CLUB', '组会文献汇报', size=11)
    cv.text(x, 1.45, 6.4, 2.3, '肝脏再生的\n{{primary|单细胞时空图谱}}', size=50, color=INK, role='serif', bold=True,
            ls=1.12, sa=0, fit=True, min_size=36, name='txt:cover_title')
    cv.text(x, 3.85, 6.0, 0.4, 'A single-cell spatiotemporal atlas of liver regeneration', size=14,
            color=MUTED, role='display', italic=True, wrap=False, fit=True, name='txt:cover_en')
    cv.line(x, 4.55, x + 4.6, 4.55, RULE, 1.0)
    cv.rect(x, 4.535, 0.9, 0.035, fill=CORAL, name='deco:coverrule')
    cv.text(x, 4.75, 6.0, 0.62, ['示例论文（虚构）  |  Example Journal, 2026', '模拟数据，仅用于版式演示'], size=11.5,
            color=MUTED, ls=1.15, sa=4, fit=True, name='txt:cite')
    cv.text(x, 6.15, 6.0, 0.4, '汇报人：张三　　　组会  ·  2026.10', size=14, color=INK, role='medium', wrap=False,
            fit=True, name='txt:presenter')
    cv.transition('fade')
    cv.notes('封面：左侧期刊式文字栏（栏目名 + 衬线标题 + 英文题名 + 引文），右侧生图主视觉渐隐进白底。')


# ------------------------------------------------------------------ 2 目录
DESC = ['肝脏再生的分区之谜', '时间序列 × 单细胞 × 空间', '图谱、接力与命运分岔', '结论与对本课题的启发']


def agenda(d):
    cv = d.new(bg=False)
    cv.rect(0, 0, W, H, fill='FFFFFF', name='bg:paper')
    px, py, pw, ph = 0.75, 0.75, 3.7, H - 1.5
    cv.image(TISSUE, px, py, pw, ph, fit='cover', focus=(0.35, 0.5), radius=0.08, name='img:agenda')
    cv.rect(px, py, pw, ph, fill=None, radius=0.08, grad=[(0, TEAL, 0.0), (45, TEAL, 0.15), (100, '0D3F3A', 0.9)],
            grad_angle=90, name='deco:agendamask')
    cv.text(px + 0.4, py + ph - 1.75, pw - 0.8, 0.9, '目录', size=48, color='FFFFFF', role='serif', bold=True,
            wrap=False, fit=False, name='txt:mulu')
    cv.text(px + 0.42, py + ph - 0.85, pw - 0.8, 0.3, 'CONTENTS', size=11, color='FFFFFF', role='number',
            spacing=6, alpha=0.85, wrap=False, fit=False, name='txt:contents')
    rx0, rx1 = 5.3, W - 0.85
    top, rh = 1.0, 1.38
    for i in range(4):
        y = top + i * rh
        cv.text(rx0, y + 0.18, 1.2, 0.9, f'0{i + 1}', size=40, color=TEAL if i != 2 else CORAL, role='number',
                anchor='middle', wrap=False, fit=False, name='txt:agnum')
        cv.text(rx0 + 1.35, y + 0.2, 2.6, 0.5, SEC[i], size=22, color=INK, role='serif', bold=True,
                anchor='middle', wrap=False, fit=True, name='txt:agsec')
        cv.text(rx0 + 1.37, y + 0.72, 2.6, 0.3, SEC_EN[i], size=9.5, color=MUTED, role='number', spacing=2.5,
                wrap=False, fit=True, name='txt:agen')
        cv.text(rx1 - 3.3, y + 0.3, 3.3, 0.6, DESC[i], size=12.5, color='text', align='right', anchor='middle',
                fit=True, name='txt:agdesc')
        cv.line(rx0, y + rh, rx1, y + rh, RULE, 0.75)
    cv.transition('fade')


# ------------------------------------------------------------------ 3 背景
def page_background(d):
    KICK.update(en='BACKGROUND', zh=SEC[0])
    cv = d.page('肝脏如何“长回来”？')
    b = cv.content
    cv.image(LIVER, b.x, b.y - 0.05, 3.6, b.h + 0.05, fit='contain', name='img:liver')
    rx = b.x + 4.0
    rw = b.r - rx
    stats = [('70', '%', '部分肝切除（PHx）', '切除约 2/3 肝脏体积'), ('≈7', '天', '体积基本恢复', '小鼠肝脏迅速再生')]
    for k, (v, u, lab, sub) in enumerate(stats):
        sx = rx + k * (rw / 2)
        vw = cv.width_of(v, 54, role='number') * 1.05
        cv.text(sx, b.y - 0.1, vw + 0.1, 1.0, v, size=54, color=TEAL if k == 0 else CORAL, role='number',
                anchor='bottom', wrap=False, fit=False, name='txt:stat')
        cv.text(sx + vw + 0.12, b.y + 0.3, 0.8, 0.5, u, size=20, color=INK, role='medium', anchor='bottom',
                wrap=False, fit=False, name='txt:statunit')
        cv.text(sx, b.y + 0.95, rw / 2 - 0.3, 0.35, lab, size=15, color=INK, role='serif', bold=True, wrap=False,
                fit=True, name='txt:statlabel')
        cv.text(sx, b.y + 1.32, rw / 2 - 0.3, 0.3, sub, size=11.5, color=MUTED, wrap=False, fit=True,
                name='txt:statsub')
    cv.line(rx, b.y + 1.85, b.r, b.y + 1.85, RULE, 0.75)
    ly = b.y + 2.05
    cv.image(MF_FIG('lobule.png'), rx - 0.1, ly - 0.05, 2.55, 2.55, fit='contain', name='img:lobule')
    tx = rx + 2.65
    cv.text(tx, ly, rw - 2.65, 0.4, '肝小叶的“分区分工”', size=16, color=INK, role='serif', bold=True,
            wrap=False, fit=True, name='txt:subhead')
    pts = ['血液从门管区流向中央静脉，形成 [[Z1–Z3]] 三个代谢分区',
           'Z1 偏重糖异生与尿素合成，Z3 偏重药物代谢',
           '长期争论：再生的新肝细胞[[主要来自哪个分区]]？']
    cv.text(tx, ly + 0.5, rw - 2.65, 1.9, pts, size=13, color='text', bullet='•', bullet_color=TEAL, ls=1.25, sa=7,
            fit=True, name='txt:bgpoints')
    stmt(cv, rx, b.b - 0.62, rw, 0.62, '核心问题：再生由哪些细胞驱动？各分区按什么[[顺序]]进入增殖？')
    cv.transition('fade')


def MF_FIG(n):
    return FIG(n)


# ------------------------------------------------------------------ 4 研究设计
STEP_TXT = [('2/3 部分肝切除', '成年雄性小鼠模型'), ('6 个时间点取样', '0 h 至 7 d，组织解离'),
            ('单细胞转录组', '液滴法，约 86k 个细胞'), ('空间转录组', '12 张切片，原位验证')]


def page_design(d):
    KICK.update(en='STUDY DESIGN', zh=SEC[1])
    cv = d.page('时间序列 × 单细胞 × 空间')
    b = cv.content
    cols = Box(b.x, b.y, b.w, 2.95).cols(4, gap=0.3)
    for k, (c, p, (t1, t2)) in enumerate(zip(cols, STEPS, STEP_TXT)):
        cv.rect(c.x, c.y, c.w, c.h, fill='FFFFFF', line=RULE, line_w=0.75, radius=0.06, name='deco:stepcard')
        s = min(c.w - 0.5, 1.75)
        cv.image(p, c.cx - s / 2, c.y + 0.12, s, s, fit='contain', name=f'img:step{k + 1}')
        cv.text(c.x + 0.25, c.y + 0.15, 0.6, 0.35, f'0{k + 1}', size=13, color=CORAL, role='number', wrap=False,
                fit=False, name='txt:stepnum')
        cv.text(c.x + 0.2, c.y + 2.0, c.w - 0.4, 0.4, t1, size=15, color=INK, role='serif', bold=True,
                align='center', wrap=False, fit=True, name='txt:steptitle')
        cv.text(c.x + 0.2, c.y + 2.42, c.w - 0.4, 0.3, t2, size=11.5, color=MUTED, align='center', wrap=False,
                fit=True, name='txt:stepsub')
        if k < 3:
            cv.shape('chevron', c.r + 0.08, c.y + 1.0, 0.14, 0.26, fill=TEAL2, alpha=0.7, name='deco:stepchev')
    # 取样时间轴
    ty = b.y + 3.45
    tx0, tx1 = b.x + 1.5, b.r - 0.2
    cv.text(b.x, ty - 0.17, 1.4, 0.34, '取样时间点', size=12, color=INK, role='medium', wrap=False, fit=True,
            name='txt:tlabel')
    cv.line(tx0, ty, tx1, ty, RULE, 2.0)
    xa, xb = tx0 + (tx1 - tx0) * 0.4, tx0 + (tx1 - tx0) * 0.6
    cv.line(xa, ty, xb, ty, CORAL, 3.0)                  # 24–48 h 增殖高峰窗口
    pts = ['0 h', '12 h', '24 h', '48 h', '72 h', '7 d']
    for i, lab in enumerate(pts):
        x = tx0 + (tx1 - tx0) * i / (len(pts) - 1)
        key = lab in ('24 h', '48 h')
        cv.circle(x, ty, 0.11 if key else 0.08, fill=CORAL if key else TEAL, line='FFFFFF', line_w=1.5,
                  name='deco:tdot')
        cv.text(x - 0.5, ty + 0.16, 1.0, 0.3, lab, size=11.5, color=CORAL if key else 'text', role='number',
                align='center', wrap=False, fit=False, name='txt:tlab')
    cv.text((xa + xb) / 2 - 1.0, ty - 0.46, 2.0, 0.28, '增殖高峰窗口', size=10, color=CORAL,
            align='center', wrap=False, fit=False, name='txt:twin')
    # 数据规模
    ky = b.b - 1.05
    kcols = Box(b.x, ky, b.w, 1.05).cols(4, gap=0.3)
    kp = [('86', 'k', '单细胞转录组'), ('6', '个', '时间点'), ('23', '个', '细胞亚群'), ('12', '张', '空间切片')]
    for c, (v, u, lab) in zip(kcols, kp):
        cv.line(c.x, c.y, c.r, c.y, INK, 1.0)
        vw = cv.width_of(v, 34, role='number') * 1.05
        cv.text(c.x, c.y + 0.08, vw + 0.1, 0.6, v, size=34, color=TEAL, role='number', anchor='bottom', wrap=False,
                fit=False, name='txt:kv')
        cv.text(c.x + vw + 0.1, c.y + 0.28, 0.6, 0.38, u, size=14, color=TEAL, role='medium', anchor='bottom',
                wrap=False, fit=False, name='txt:ku')
        cv.text(c.x, c.y + 0.7, c.w, 0.3, lab, size=12, color=MUTED, wrap=False, fit=True, name='txt:kl')
    cv.transition('fade')


# ------------------------------------------------------------------ 5 发现一：细胞图谱
def page_atlas(d):
    KICK.update(en='FINDING 01', zh='细胞图谱')
    cv = d.page('9 大类、23 个亚群的再生细胞图谱')
    b = cv.content
    fw = 7.3
    cv.image(FIG('umap.png'), b.x - 0.1, b.y - 0.05, fw, b.h - 0.35, fit='contain', name='img:umap')
    caption(cv, b.x, b.b - 0.3, fw - 0.2, 'a', '全部时间点细胞的 UMAP 降维（模拟数据，n ≈ 86k）')
    rx = b.x + fw + 0.35
    rw = b.r - rx
    cv.text(rx, b.y, rw - 0.9, 0.4, '细胞组成', size=16, color=INK, role='serif', bold=True, wrap=False, fit=True,
            name='txt:subhead')
    cv.text(b.r - 0.8, b.y + 0.02, 0.8, 0.4, '占比 %', size=10.5, color=MUTED, align='right', wrap=False, fit=False,
            name='txt:unit')
    y0, rh = b.y + 0.55, 0.36
    mx = max(p for _, _, p in MF.TYPES)
    for i, (name, col, pct) in enumerate(MF.TYPES):
        y = y0 + i * rh
        cv.circle(rx + 0.07, y + rh / 2, 0.065, fill=col.lstrip('#'), name='deco:dot')
        cv.text(rx + 0.25, y, 1.9, rh, name, size=11.5, color=INK if i != 3 else CORAL, bold=(i == 3),
                anchor='middle', wrap=False, fit=True, min_size=9, name='txt:ctype')
        bx, bw = rx + 2.2, rw - 2.2 - 0.55
        cv.rect(bx, y + rh / 2 - 0.05, bw, 0.1, fill='EEF0F1', name='deco:bartrack')
        cv.rect(bx, y + rh / 2 - 0.05, bw * pct / mx, 0.1, fill=col.lstrip('#'), name='deco:bar')
        cv.text(b.r - 0.5, y, 0.5, rh, f'{pct:.1f}', size=11, color='text', role='number', align='right',
                anchor='middle', wrap=False, fit=False, name='txt:pct')
    stmt(cv, rx, b.b - 1.15, rw, 1.0, '肝细胞沿 Z1→Z3 连续分布，增殖肝细胞从[[中间带 Z2]] 分支伸出', size=14)
    cv.transition('fade')


# ------------------------------------------------------------------ 6 发现二：分区接力（skill 版式 chart_page）
def page_relay(d):
    KICK.update(en='FINDING 02', zh='分区接力')
    d.chart_page('中间带 Z2 率先进入增殖',
                 chart={'kind': 'line', 'categories': ['0 h', '12 h', '24 h', '48 h', '72 h', '7 d'],
                        'series': {'Z1 门周': [0.5, 1.2, 6.8, 18.5, 9.6, 1.4],
                                   'Z2 中间带': [0.6, 3.5, 21.4, 27.9, 8.1, 1.2],
                                   'Z3 中央周': [0.4, 0.8, 2.6, 9.7, 12.3, 1.8]},
                        'colors': [TEAL2, CORAL, '7A6BC9'], 'legend': True, 'labels': False, 'value_axis': True,
                        'gridlines': True, 'number_format': '0', 'smooth': True},
                 chart_title='图 b  各分区增殖肝细胞比例', unit='单位：%（模拟数据）',
                 points=['Z2 在 [[24 h]] 已达峰值的 3/4，明显领先 Z1、Z3',
                         'Z1 于 48 h 跟进，Z3 在 72 h 才出现增殖高峰',
                         '再生呈“中间带先行、两侧接力”的[[分区接力]]模式'],
                 notes='skill 自带 chart_page：原生折线图（可在 PowerPoint 中编辑数据）+ 关键发现。')


# ------------------------------------------------------------------ 7 发现三：命运分岔
def page_fate(d):
    KICK.update(en='FINDING 03', zh='命运分岔')
    cv = d.page('Z2 肝细胞的命运分岔')
    b = cv.content
    l, r = Box(b.x, b.y, b.w, b.h - 0.95).split(0.5, gap=0.45)
    cv.image(FIG('trajectory.png'), l.x, l.y, l.w, l.h - 0.4, fit='contain', name='img:traj')
    caption(cv, l.x, l.b - 0.3, l.w, 'c', '拟时序轨迹：静息 Z2 → 分岔 → 增殖态 / 功能维持态')
    cv.image(FIG('heatmap.png'), r.x, r.y, r.w, r.h - 0.4, fit='contain', name='img:heat')
    caption(cv, r.x, r.b - 0.3, r.w, 'd', '沿拟时序的基因模块动态（行归一化）')
    stmt(cv, b.x, b.b - 0.68, b.w, 0.68,
         '分岔前“代谢重编程”先行，随后细胞周期程序开启——约 [[38%]] 的 Z2 细胞走向增殖态')
    cv.transition('fade')


# ------------------------------------------------------------------ 8 空间验证
def page_spatial(d):
    KICK.update(en='VALIDATION', zh='空间验证')
    cv = d.page('空间转录组：增殖集中于中间带')
    b = cv.content
    fw = 5.9
    cv.image(FIG('spatial.png'), b.x - 0.1, b.y - 0.05, fw, b.h - 0.35, fit='contain', name='img:spatial')
    caption(cv, b.x, b.b - 0.3, fw, 'e', '48 h 切片的增殖评分（○ 为中央静脉）')
    rx = b.x + fw + 0.5
    rw = b.r - rx
    items = [('01', '增殖信号呈环带分布', '高分 spot 围绕中央静脉、距其约 [[1/2]] 小叶半径，恰为 Z2 所在'),
             ('02', '与单细胞结论一致', '空间去卷积估计的增殖肝细胞比例与 scRNA-seq 结果相关系数 r = 0.91'),
             ('03', '谱系示踪佐证', 'Z2 标记细胞 7 d 后的克隆占新生肝细胞的 [[61%]]（模拟数据）')]
    y = b.y + 0.05
    ih = (b.h - 0.1) / 3
    for k, (n, t1, t2) in enumerate(items):
        yy = y + k * ih
        cv.text(rx, yy, 0.8, 0.5, n, size=26, color=CORAL, role='number', wrap=False, fit=False, name='txt:num')
        cv.text(rx + 0.85, yy + 0.04, rw - 0.85, 0.45, t1, size=17, color=INK, role='serif', bold=True,
                wrap=False, fit=True, name='txt:itemhead')
        cv.text(rx + 0.85, yy + 0.55, rw - 0.85, ih - 0.75, t2, size=13, color='text', ls=1.3, fit=True,
                name='txt:itembody')
        if k < 2:
            cv.line(rx, yy + ih - 0.12, b.r, yy + ih - 0.12, RULE, 0.75)
    cv.transition('fade')


# ------------------------------------------------------------------ 9 亮点与局限（skill 版式 compare）
def page_discussion(d):
    KICK.update(en='DISCUSSION', zh='亮点与局限')
    d.compare('亮点与局限',
              left={'title': '局限', 'subtitle': '值得继续追问的地方', 'icon': 'circle-help',
                    'points': ['仅覆盖雄性成年小鼠，[[性别与年龄]]效应未知', '7 d 之后的组织重塑阶段未取样',
                               '空间分辨率约 55 μm，单个 spot 含多个细胞', '仅一种损伤模型（部分肝切除）']},
              right={'title': '亮点', 'subtitle': '这篇文章做得漂亮的地方', 'icon': 'sparkles',
                     'points': ['[[时间 × 单细胞 × 空间]]三维数据互相印证', '拟时序 + 谱系示踪，结论不止于相关',
                                '把“谁在再生”细化到[[分区与时序]]', '数据与代码全部公开，便于复用']},
              summary='组会讨论：Z2 的“先发优势”在毒性损伤模型中是否依然成立？',
              notes='skill 自带 compare：左右卡片对比，右侧高亮。')


# ------------------------------------------------------------------ 10 总结与启发
def page_takeaways(d):
    KICK.update(en='TAKEAWAYS', zh=SEC[3])
    cv = d.page('总结与启发')
    b = cv.content
    bh = 2.1
    cv.image(TISSUE, 0, b.y - 0.05, W, bh, fit='cover', focus=(0.5, 0.5), name='img:band')
    cv.rect(0, b.y - 0.05, W, bh, fill=None, grad=[(0, 'FFFFFF', 0.97), (48, 'FFFFFF', 0.82), (100, 'FFFFFF', 0.0)],
            grad_angle=0, name='deco:bandmask')
    cv.text(b.x, b.y + 0.2, 7.6, 0.4, 'ONE-SENTENCE SUMMARY', size=10, color=TEAL, role='number', spacing=3,
            wrap=False, fit=False, name='txt:oss')
    cv.text(b.x, b.y + 0.6, 7.8, 1.2, '肝脏再生是一场由[[中间带]]发起的“分区接力”', size=26, color=INK, role='serif',
            bold=True, ls=1.15, fit=True, min_size=18, name='txt:summary')
    cols = Box(b.x, b.y + bh + 0.35, b.w, b.b - (b.y + bh + 0.35)).cols(3, gap=0.4)
    data = [('方法', '时间序列 + 单细胞 + 空间', '三类数据交叉验证，比单一测序更有说服力'),
            ('结论', 'Z2 是再生的“发起者”', '先代谢重编程、再进入细胞周期，Z1、Z3 依次接力'),
            ('启发', '对本课题', '可借鉴“拟时序 + 空间”的分析框架，验证我们体系中的分区差异')]
    for k, (c, (tag, head, body)) in enumerate(zip(cols, data)):
        hi = k == 2
        cv.rect(c.x, c.y, c.w, c.h, fill='FFFFFF' if not hi else PAPER, line=RULE if not hi else None,
                radius=0.06, name='deco:tcard')
        cv.rect(c.x, c.y, c.w, 0.05, fill=TEAL if not hi else CORAL, name='deco:tcardtop')
        cv.text(c.x + 0.3, c.y + 0.25, c.w - 0.6, 0.3, tag, size=11, color=TEAL if not hi else CORAL,
                role='medium', spacing=2, wrap=False, fit=False, name='txt:ttag')
        cv.text(c.x + 0.3, c.y + 0.6, c.w - 0.6, 0.45, head, size=17, color=INK, role='serif', bold=True,
                wrap=False, fit=True, name='txt:thead')
        cv.text(c.r - 1.55, c.b - 1.05, 1.35, 0.95, f'0{k + 1}', size=54, color='E9E4DC' if hi else 'EEF0F1',
                role='number', align='right', anchor='bottom', wrap=False, fit=False, name='deco:bignum')
        cv.text(c.x + 0.3, c.y + 1.12, c.w - 0.6, c.h - 1.25, body, size=13.5, color='text', ls=1.3, fit=True,
                name='txt:tbody')
    cv.transition('fade')


# ------------------------------------------------------------------ 11 结束页
def ending(d):
    cv = d.new(bg=False)
    cv.rect(0, 0, W, H, fill='FFFFFF', name='bg:paper')
    cv.image(IMG.fade(ENDING, side='left', start=0.62, end=0.8), 0, 0, W, H, fit='cover', name='img:ending')
    cv.text(0.95, 2.35, 6, 1.6, '谢谢', size=80, color=INK, role='serif', bold=True, wrap=False, fit=False,
            name='txt:thanks')
    cv.line(1.0, 4.15, 3.2, 4.15, RULE, 1.0)
    cv.rect(1.0, 4.135, 0.7, 0.035, fill=CORAL, name='deco:endrule')
    cv.transition('fade')


# ------------------------------------------------------------------ build
def build():
    d = Deck(dict(base='academic_green', primary=TEAL, secondary=TEAL2, accent=CORAL, emph=CORAL, dark=INK,
                  text='3A3F47', muted=MUTED, line=RULE, bg='FFFFFF', bg2=PAPER, panel=PAPER,
                  font_display='Georgia', card_style='outline'), scenario='research', page_numbers=False)
    d.page = types.MethodType(journal_page, d)
    d.set_sections(SEC, en=SEC_EN)
    d.meta(title='肝脏再生的单细胞时空图谱', author='张三', date='2026.10')
    cover(d)
    agenda(d)
    page_background(d)
    page_design(d)
    page_atlas(d)
    page_relay(d)
    page_fate(d)
    page_spatial(d)
    page_discussion(d)
    page_takeaways(d)
    ending(d)
    path = d.save(OUT, render='--no-render' not in sys.argv)
    print('saved:', path)
    if MISSING:
        print('占位图（待生图替换，放入 img/）：', ', '.join(sorted(set(MISSING))))


if __name__ == '__main__':
    build()
