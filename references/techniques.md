# Techniques as code

Designer techniques from the reference material, mapped to library calls. `cv` is a `Canvas`
(`cv = d.page(...)` or the return value of any layout), coordinates in inches.

Contents: 1 Text · 2 Emphasis · 3 Shapes & effects · 4 Backgrounds · 5 Images & screenshots · 6 Icons ·
7 Charts · 8 Tables · 9 Diagrams · 10 Transitions & notes · 11 Figures with matplotlib · 12 PowerPoint COM ·
13 Studying a reference deck · 14 Research figures: equations, zoom, callouts, method colors ·
15 Diagram helpers (cards, loops, number grids, bars, brackets, waves) ·
16 Template-family parts (risk chips, people, laurels, certificates, hub diagrams, textures)

---

## 1. Text

```python
cv.text(x, y, w, h, '第一段\n第二段', size=16, color='text', role='body', align='justify', anchor='top',
        ls=1.25, sa=8, fit=True, min_size=12)          # auto-shrinks until it fits the box
h_needed = cv.measure('一段文字', w, size=16)           # inches, same wrapping as PowerPoint (±3 %)
cv.text(..., wrap=False, fit=True)                       # single line shrink-to-width (titles, labels)
cv.text(..., spacing=2)                                  # letter spacing in pt (English captions)
cv.text(..., vert='eaVert')                              # vertical CJK text
cv.text(..., grad=['FFFFFF', 'secondary+40'])            # gradient text (cover titles on dark bg)
cv.text(..., outline=('primary', 1.25))                  # hollow/outlined text (big numbers)
cv.text(..., alpha=0.06, role='heavy', size=120)         # watermark word (or K.watermark)
cv.text(..., bullet='Ø', bullet_font='Wingdings')        # ➢ bullets (A.arrow_list does this for you)
```
Roles pick the font: `title` (bold heading), `heavy` (black weight if installed), `medium`, `light`, `body`,
`number` (Bahnschrift digits), `serif` (思源宋体), `display`. Paragraph dicts override per paragraph:
`[{'text': '小标题', 'size': 18, 'bold': True, 'color': 'primary'}, '正文…']`.
Break Chinese titles by meaning (`'长距离输水工程\n研究方向与前景'`), never mid-word.

## 2. Emphasis (not just red text)

- Markup: `[[关键词]]` → bold + theme `emph` color (red in defense themes); `**粗体**` → bold only.
- Pull the key phrase out into a label: `A.tag(cv, x, y, w, h, '核心阐述', style='chevron')`,
  `A.ribbon(...)`, `A.red_marker(cv, x, y, '问题一')`.
- Pull numbers out: `A.stat(cv, box, '900', '亿m³', '累计调水')` (red), `K.kpi(cv, box, '96', '%', trend='up')`.
- Weaken the rest: secondary text in `muted` gray so the key line stands out.
- Color block behind: `cv.rect(x, y, w, h, fill='emph_pale')` then the text on top; for table columns use
  `highlight_col` / `highlight_mode='raised'`.
- One sentence summary: `A.conclusion(cv, text, y=..., style='yellow', serif=True)` (strongest) or `'navy'`.

## 3. Shapes & effects

```python
cv.rect(x, y, w, h, fill='panel', line='panel_line', line_w=0.75, radius=0.06)   # radius in inches
cv.rect(..., grad=[('primary', 1.0), ('secondary', 1.0)], grad_angle=0)            # linear gradient
cv.circle(cx, cy, r, grad=[(0, 'primary', 0.35), (100, 'primary', 0.0)], grad_kind='radial')  # glow orb
cv.rect(..., shadow='soft')        # 弥散阴影: main-color tinted, ~86 % transparent, 22 pt blur, 5 pt distance
cv.rect(..., shadow={'color': 'primary_deep', 'alpha': 0.08, 'blur': 10, 'dist': 2})
cv.rect(..., alpha=0.6, line='FFFFFF', line_alpha=0.15)                           # glass card (dark themes)
cv.shape('homePlate', x, y, w, h, fill='primary', adj={'adj': 30000})             # any preset (see canvas.PRST)
cv.ring(cx, cy, r, thickness, color='primary', start=0, sweep=270)                 # progress arc (0° = 12 o'clock)
cv.poly([(x1, y1), (x2, y2), ...], fill=None, line='primary', line_w=2, closed=False, smooth=True)  # curve
cv.line(x1, y1, x2, y2, 'primary', 1.5, dash='sysDash', tail='triangle')
A.block_arrow(cv, x, y, w, h, 'up', color='primary')      # gradient thick arrow
A.brace(cv, x, y, h, side='left')                         # { connector
K.waves(cv, y=5.9)                                        # layered bottom waves (modern)
```
Color specs: roles (`primary`, `primary_deep`, `secondary`, `accent`, `emph`, `yellow`, `panel`, `panel_line`,
`panel_light`, `primary_pale`, `primary_bg`, `text`, `dark`, `muted`, `line`, `surface`, `bg`, `bg2`),
tints/shades (`'primary+30'` = 30 % toward white, `'primary-20'` = 20 % toward black) or hex.

## 4. Backgrounds

- Pages get their background automatically (`d.page()`); build your own with `d.new(kind, bg=False)`.
- Soft light gradient: `cv.rect(0, 0, 13.333, 7.5, grad=[(0, 'primary_bg', 1), (100, 'FFFFFF', 1)], grad_angle=35)`.
- `IMG.diffuse(colors, base, blobs=[(cx, cy, r), ...])` → '弥散' color-blob image (modern covers).
- `IMG.dot_map(color, alpha)` → dot-matrix texture (defense cover bands; tech/AI topics).
- `IMG.tech_bg(bg, glow, glow2, grid=True)` → dark glow + perspective grid (tech covers).
- `IMG.gradient_png(stops, size, angle)` → exact gradient image (when a picture is needed instead of a fill).
Insert generated images with `cv.image(path, 0, 0, 13.333, 7.5, fit='stretch')`.

## 5. Images & screenshots

```python
cv.image(path, x, y, w, h, fit='cover', focus=(0.5, 0.35))   # crop to fill (focus = point to keep)
cv.image(path, x, y, w, h, fit='contain')                     # never crop (scientific figures, charts)
cv.image(path, x, y, w, h, shape='ellipse')                   # circle photo; radius=0.12 → rounded corners
cv.image(path, ..., alpha=0.3)                                # faded photo behind text
IMG.fade(path, side='bottom', start=0.4, end=1.0)             # photo fading into the page (no hard edge)
IMG.duotone(path, dark='0B2A5B', light='E8F1FF')              # unify photo colors with the theme
IMG.line_art(path, color='FFFFFF', alpha=0.45)                # building line drawing on color band
IMG.cover_crop(path, aspect=16/9, focus=(0.5, 0.4)); IMG.desaturate(path); IMG.tint(path, '1F57C3', 0.3); IMG.blur(path, 18)
K.screen_frame(cv, box, 'screenshot.png', kind='browser'|'phone'|'laptop', url='...')   # screenshot mockups
A.figure(cv, box, 'fig.png', '图3-1 …')                        # framed figure with caption band
```
Photo over text: add a mask `cv.rect(..., grad=[(0, 'primary_deep', 0.9), (100, 'primary_deep', 0.1)], grad_angle=0)`.
Rows of photos: crop all to the same box size (`image_grid` does it).

## 6. Icons (1,850+ Lucide line icons, ISC license, native vector shapes)

```python
cv.icon('droplets', x, y, 0.5, 'primary')      # exact name
cv.icon('渗漏', x, y, 0.5, 'FFFFFF')            # Chinese/English keyword → best match
K.icon_badge(cv, cx, cy, 0.7, 'radar', style='circle_grad'|'circle_pale'|'square_grad'|'ring'|'plain')
A.icon_badge_ac(cv, cx, cy, 0.7, 'radar')       # defense-style navy badge with ring
```
Find names: `python -m pptstudio icons 水` / `icons pipe`. Keep one icon style per deck; icon size ≈ 0.5–0.9 of
the adjacent text block height.

## 7. Charts (native, editable)

```python
from pptstudio.charts import chart
chart(cv, x, y, w, h, kind='column', categories=[...], series={'名称': [...]}, highlight=-1,
      number_format='0.0', colors=['primary', 'emph'], legend=True, gridlines=False, value_axis=False)
```
Kinds: column, bar, stacked, stacked_bar, stacked100, line, line_plain, area, pie, donut, scatter, radar.
Designer defaults: no chart title (the slide says it), labels on, gridlines off, the highlighted category in the
main color (gradient), others pale. For a single percentage use `kpis(variant='rings')` or `cv.ring(...)`.
The returned object is a python-pptx chart (further tweaks possible).

## 8. Tables

`table_page(...)` / `pptstudio.tables.table(cv, x, y, w, h, columns, rows, style='header'|'three_line'|'minimal',
highlight_col=, highlight_mode='fill'|'raised', highlight_rows=, col_widths=, align=, font_size=)`;
compact in-panel tables: `A.mini_table(cv, box, columns, rows, emph_cols=(3,))`. Text in cells accepts markup.
Keep ≤ 8 rows; move long explanations out of cells into a note (`note=`).

## 9. Diagrams from primitives

- Flow: `A.flow_chain(cv, box, [{'title': '感知', 'icon': 'radar'}, ...], style='grad')`.
- Hub/spoke: `hub(...)` layout or circles + dashed `cv.line`s.
- Layers: `layers(...)` / `pyramid(variant='layers')`.
- Axis with nodes: `A.axis(cv, x, y, w, [node x positions])`.
- Cross-section / schematic drawings: compose circles, rings and arrows (see `tunnel_section()` in
  `examples/nsfc_sodium/build.py`), always keep labels inside the panel box.
- Pass any drawing function as `visual=` to `panels` items / `figure_text` / `text_image`: it receives
  `(cv, box)` and must draw inside `box`.

## 10. Transitions, notes, navigation

`cv.notes('讲稿…')` or `notes=` on any layout; `cv.transition('fade'|'morph'|'push')` (section pages use fade;
consecutive pages with the same objects can use morph). Long decks: `Deck(..., nav='top'|'left')`.

## 11. Schematic figures with matplotlib (when the user has no figure)

Font `Microsoft YaHei`, `axes.unicode_minus=False`, dpi ≥ 200, figure size ≈ panel aspect (6.4×3.6 in), remove
top/right spines, light grid (alpha 0.25), theme colors (navy `#033E9C`, blue `#124CAD`, red `#C00000`, orange
`#F2A33A`), caption “（示意）”. See `examples/nsfc_sodium/make_figs.py`. Real data → prefer native charts.

## 12. PowerPoint COM (Windows + PowerPoint, via pywin32)

| Need | Call |
|---|---|
| PNG previews + contact sheet | `render.export_png(pptx, outdir, width=1600)`, `render.contact_sheet(pngs, out)` / `python -m pptstudio render` |
| Real overflow check (PowerPoint text engine) | `render.check_overflow(pptx)` / `check --com` |
| Auto-shrink overflowing boxes | `render.fix_overflow(pptx)` / `fix` |
| PDF | `render.to_pdf(pptx)` / `pdf` |
| Embed fonts | `render.embed_fonts(pptx)` / `embed` (CJK fonts add ~15–35 MB; fonts whose license forbids embedding are skipped) |

Anything else python-pptx cannot do (animations, 3-D rotation, SmartArt conversion) can be scripted with COM
after saving:
```python
import win32com.client, pythoncom
pythoncom.CoInitialize(); app = win32com.client.DispatchEx('PowerPoint.Application')
pres = app.Presentations.Open(path, False, False, False)
sld = pres.Slides(3); shp = [s for s in sld.Shapes if s.Name == 'txt:title'][0]
sld.TimeLine.MainSequence.AddEffect(shp, 10, 0, 1)   # 10 = msoAnimEffectFade, trigger on click
pres.Save(); pres.Close(); app.Quit()
```
Shape names are stable handles: titles `txt:title`, decorations `deco:*`, backgrounds `bg:*`, images `img:*`.

## 13. Studying a reference deck

`python -m pptstudio analyze ref.pptx [--json out.json]` prints fonts (CJK/Latin), title/body sizes, text and fill
colors, shape types and effects — copy those values into a theme (`Deck('nsfc_blue', primary='…', font_body='…')`)
to match a template. `python -m pptstudio render ref.pptx` gives its thumbnails.

## 14. Research figures: equations, zoom, callouts, method colors

```python
# equations — true point size, consistent style (STIX ≈ Times), numbered like the paper
A.formula(cv, Box(x, y, w, 0.8), r'\dfrac{\partial Q}{\partial t}+gA\dfrac{\partial H}{\partial x}+\dfrac{fQ|Q|}{2DA}=0',
          num=2, size=19, note='f 为Darcy–Weisbach摩阻系数')
cv.equation(r'R_t=T_{\mathrm{sim}}/t_c', x, y, size=17, color='primary_deep', w=1.6, h=0.5, align='center', anchor='middle')

# 局部放大 instead of a bare red box: mark region of a placed figure, enlarged copy in dst
pic = A.figure(cv, Box(x, y, 6.7, 5.0), 'fig3.png', 'Fig. 3 各线程性能曲线')
A.zoom_inset(cv, 'fig3.png', pic, (0.5, 0.5, 1.0, 1.0), Box(7.6, 2.2, 5.0, 2.5), label='B工程 · 3000 s')
A.callout(cv, tx, ty, x, y, 2.6, 0.45, 'WCM 8线程最快：15.9 s')     # dot + leader + framed label

# method colors kept from the paper's figures (色彩指向)
d.add_colors(moc='0072BD', mix='D95319', wcm='77AC30')
A.ribbon(cv, x, y, w, '波特征法 WCM', fill='wcm')
cv.text(..., '相对串行MOC加速：{{wcm|WCM}} [[10.8–91.4]] 倍')          # colored method name + red numbers
table(..., rows=[['B', '{{wcm|WCM}}', '0.031', …]], highlight_col=(5, 6))
```
- Sample the method colors from the figure (most frequent saturated pixels) so slides and figures agree.
- Comparison cards: ours in the method color with soft shadow, literature in gray `F2F2F2`.
- Native chart with one color per bar: set `points[i].format.fill` on the returned chart (see
  `paper-to-slides.md §4`).
- Numeric ranges never wrap mid-range: `4.6–10.5`, `A-50`, `1014–1030` are glued with U+2011 automatically.
- `Deck(nav='mini')` adds chapter chips to every content page title bar; `section(i,
  variant='number', desc=[…])` gives big-number dividers.

## 15. Diagram helpers (cards, loops, number grids, bars, brackets, waves)

```python
from pptstudio import academic as A, Box
inner = A.card_box(cv, Box(x, y, 4, 3), style='shadow')          # 'topline' | 'outline' | 'pale'; returns inner Box
y2 = inner.y + A.card_title(cv, inner.x, inner.y, inner.w, '岩爆倾向判据', icon='activity')
A.formula_card(cv, Box(x, y, 5.6, 3.2), r'W_{et}=\dfrac{\phi_{sp}}{\phi_{st}}', title='储耗比判据',
               meaning='弹性应变能与耗散能之比', symbols=[(r'\phi_{sp}', '弹性应变能'), (r'\phi_{st}', '耗散能')])
segs = A.cycle(cv, cx, cy, 1.8, ['实时感知', '智能诊断', '分级预警', '联动处置'], center='闭环\n预警')
A.stat_grid(cv, box, [{'label': '监测里程', 'value': 32.6, 'unit': 'km'}, {'label': '提前量', 'value': 6, 'unit': 'd',
                                                                     'color': 'emph'}], cols=3)
A.progress_bars(cv, box, [{'label': '机理试验', 'value': 100}, {'label': '工程示范', 'value': 80}], highlight=1)
A.hbracket(cv, x0, x1, y, '基础研究')                            # phase bracket over several columns
A.vs_badge(cv, cx, cy)                                            # round VS between two comparison cards
A.water_waves(cv, 0, 13.333, 6.4, 1.1, colors=('primary+70', 'primary+45', 'primary+25'), alphas=(0.7, 0.55, 0.5))
```
`A.cycle` returns each segment's mid angle and color — place detail blocks or leader lines with them. Labels follow
the ring tangent and stay upright; keep them ≤ 4 CJK characters.

## 16. Template-family parts (risk chips, people, laurels, certificates, hub diagrams, textures)

```python
from pptstudio import academic as A, images as IMG, Box
A.level_chip(cv, x, y, 1.6, 0.4, '高')                    # grey chip '级别高' with the level word in red
A.chip(cv, x, y, 1.6, 0.4, '涉及课题二', style='fill', color=A.level_color('中'))   # orange filled chip
A.person(cv, Box(x, y, 1.2, 1.7), '李四', '课题1负责人', photo=None)     # silhouette until a real photo is given
A.laurel(cv, cx, cy, 2.4, 1.4, '省科技进步奖', '一等奖')               # wreath badge; titles ≤ 8 chars
A.certificate(cv, Box(x, y, 1.5, 2.0), image='cert1.jpg')          # framed scan; image=None → drawn placeholder
A.metric_box(cv, Box(x, y, 4.2, 0.6), '复杂场景决策准确率降低', '25.6', '%', arrow='down')
A.converge(cv, Box(x, y, 12.4, 1.5), '左侧论点', '右侧论点', '科学机遇', '红色结论句')
A.vchain(cv, Box(x, y, 3.0, 4.2), ['发挥体制机制优势', '顺应建设海洋强国', '开发装备研究'], header='实施路径', highlight=(1,))
A.hub_node(cv, cx, cy, 0.62, '治理体系', ['诉求', '张力'], color='1E6B7F')
A.arc_text(cv, cx, cy, 2.4, '机理约束', 30, 60, size=13)                # upper half: start < end (clockwise)
A.arc_text(cv, cx, cy, 2.4, '分级预警', 240, 210, size=13)              # lower half: start > end keeps it upright
A.cylinder(cv, x, y, 2.0, 0.5, '数据融合', color='1E6B7F')
cv.image(IMG.skyline(cv.t.c('primary+48'), fade='both', motif='city'), 0, 3.2, 13.333, 2.3)   # faint city line
cv.image(IMG.hexgrid(cv.t.c('primary+30'), fade='center'), 0, 0, 13.333, 7.5)                 # 科学技术奖 texture
cv.image(IMG.dot_wave(cv.t.c('primary+25')), 0, 5.0, 13.333, 2.5)                            # halftone wave
```
Risk colors are fixed (低 green · 中 orange · 高 red) and only ever used on small chips; keep everything else in the
theme's navy + red. People photos must come from the user; `silhouette` keeps the layout while they are missing.
