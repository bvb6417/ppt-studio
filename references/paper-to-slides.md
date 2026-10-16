# Paper → defense / report deck (论文转答辩·汇报PPT)

Use when the user hands over a paper (docx / pdf / markdown) and wants slides. Base style: defense
(`Deck('nsfc_blue', nav='mini')`). Guiding rule from the tutorials: **论文是用来“读”的，PPT是用来“看”的**
— every page states one finding, shows the evidence (figure / table / numbers) and drops prose.

Contents: 1 Extract · 2 Storyline · 3 Page rules · 4 Code patterns · 5 QA for paper decks

---

## 1. Extract everything first (keep a facts table)

**docx** — walk the body in order with python-docx; record headings (style names `Heading 1/2/3`, `论文标题`),
paragraphs, tables, inline images and equations:

```python
import docx, os
from docx.oxml.ns import qn
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
A_ = 'http://schemas.openxmlformats.org/drawingml/2006/main'
R_ = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
V_ = 'urn:schemas-microsoft-com:vml'
d = docx.Document(path); rels = d.part.rels
for el in d.element.body.iterchildren():
    if el.tag == qn('w:p'):            # text + markers
        for n in el.iter():
            if n.tag == qn('w:t'): ...                                   # text (skip if inside m:oMath)
            elif n.tag == f'{{{M}}}oMath': ''.join(t.text for t in n.iter(f'{{{M}}}t'))   # OMML equation
            elif n.tag == f'{{{A_}}}blip': rels[n.get(f'{{{R_}}}embed')].target_ref   # figure
            elif n.tag == f'{{{V_}}}imagedata': ...                          # MathType OLE → WMF preview
    elif el.tag == qn('w:tbl'): ...    # rows → cells
```
Unzip `word/media/*` for the figures at original resolution (TIFF → PNG with Pillow).

**Equations.** OMML gives structure (`m:f` fraction, `m:sSub`, `m:nary` with `chr=∑`, `m:d begChr=⌊`) — read
it to rewrite each equation in TeX for `cv.equation`. MathType objects only carry a WMF preview: Pillow's GDI
rendering scrambles their fonts, but **PowerPoint renders them correctly** — insert the `.wmf` with
`slide.shapes.add_picture` (vector, black) or, better, re-typeset in TeX so all formulas share one style/size.

**pdf** — PyMuPDF (`fitz`) `page.get_text('blocks')` and `page.get_images()` if installed; otherwise ask for
the source file. Never OCR numbers you cannot verify.

**Figures with sub-panels** — crop each panel so one page shows one point: detect separator lines and
white gaps, then trim margins.

```python
import numpy as np; from PIL import Image
g = np.array(Image.open(fig).convert('L'))
seps = [y for y in range(g.shape[0]) if ((g[y] > 190) & (g[y] < 240)).mean() > 0.8]   # light-gray rules
gaps = (g[:, 40:-40] > 238).mean(axis=1) > 0.995                                    # white bands
def trim(im, pad=14):
    a = np.array(im.convert('L')); ys, xs = np.where(a < 245)
    return im.crop((xs.min() - pad, ys.min() - pad, xs.max() + pad, ys.max() + pad))
```

## 2. Storyline (≈ 1 page per minute; a 20–25 min talk ≈ 25–30 pages)

| Paper part | Page(s) | Layout / pattern |
|---|---|---|
| Title, keywords | cover (`project='学术论文汇报'`, `info=[关键词, 日期]`, a native motif drawn on the band) | `cover()` + drawing |
| Abstract | **研究概览：一页看懂全文** — bottleneck → method → 4 result stat cards + conclusion bar (结论先行) | custom 3-panel |
| Intro: needs | demand columns + bottom “bottleneck” rows | `columns(cols, bottom)` |
| Intro: related work | one panel per route: icon + 3 short points incl. **局限** + conclusion “待回答：①…②…” | `panels(cols=4)` or `bands(国外 / 国内)` |
| Intro: contributions | goal → questions → topics; or 总体目标 band + 研究内容 cards | `route()` / `band_cards()` |
| Technical route | steps × levels with phases and arrows | `process_matrix()` |
| Each section start | big-number divider saying what the part shows | `section(i, variant='number', desc=[...])` |
| Each method | formula panel (numbered as in paper) + figure crop + 3–5 bullets; 2–3 governing equations → formula cards on a band | custom / `band_cards(card_style='topline')` |
| System / software framework | tiers of modules | `architecture()` |
| Iterative / closed-loop method | loop of 3–6 steps | `cycle()` |
| Implementation | figure + explanation blocks; per-method columns in method colors | custom |
| Model equations | one row per method: colored chip · formula · symbol notes | custom |
| Cases / setup | figure + mini table; icon rows + metric formula + typeset-symbol definition rows | custom |
| Accuracy | three-line table (key columns highlighted, extremes in red) + stat cards + yellow conclusion | `tables.table` |
| Performance | native column chart (per-point method colors) + stat cards + speed-up range chips | custom |
| Scaling / sensitivity | figure + `zoom_inset` of the key panel + mini table | custom |
| Comparison with literature | figure + cards: others gray, **ours highlighted** | custom / `versus()` |
| Validation | figure + stat cards per method + calibration / validation info boxes | custom |
| Conclusions | `innovations()` (tag + 2-line text, ranges in red, method names colored) | layout |
| Outlook | icon rows (applications ↔ future work) + conclusion | custom |
| References | only those cited on slides, paper numbering kept | `references(numbered=False)` |

## 3. Page rules (fused NSFC style + tutorial techniques)

- **结论先行**: the statement bar is the page's finding with 1–3 `[[red]]` keywords; the title only names the
  topic.
- **数据拆成卡片**: every headline number becomes a stat card — big value + unit + two-line label; colored by
  method.
- **方法色彩指向**: reuse the paper figures' method colors for chips, ribbons, chart bars, table cells and
  method names in text — `d.add_colors(moc='0072BD', wcm='77AC30')`, `'{{wcm|WCM}}'`.
  Sample them from the figure: most frequent saturated pixels.
- **对比**: ours highlighted, others gray; parallel items use equal-brightness colors.
- **Tables**: three-line, shaded header, highlight the key columns (`highlight_col=(5, 6)`), extremes in
  `[[red]]`; all-number tables usually read better as a chart.
- **Charts**: one hue + accent, no gridlines, labels on; category labels may contain `'\n'`; set
  `max_value` for label headroom.
- **Figures**: never redraw or recolor; crop to the panel that proves the point; caption
  “Fig. n(x) 节选：…” in Chinese under English figures; `A.zoom_inset` instead of a bare red box;
  `A.callout` for one key point.
- **Equations**: `A.formula` at body + 3–4 pt, numbered as in the paper, one Chinese symbol line below;
  ≤ 6 equations per page; symbols mentioned in prose go into typeset definition rows (no `R_t` in text).
- **Text**: ≤ 3–5 bullets per box, each ≤ 2 lines; shorten before shrinking. Numeric ranges and codes
  (`4.6–10.5`, `A-50`) are glued automatically (U+2011) so PowerPoint never splits them.
- **Navigation**: `Deck(nav='mini')` chapter chips in the title bar; short labels via
  `set_sections(..., short=[...])`.
- **Faithfulness**: every number and claim must trace to the paper; do not add inferences (“X 直接制约 Y”)
  or fill gaps with invented data. Schematic additions are labeled “（示意）”.
- **Speaker notes** on every page with the numbers to say.

## 4. Code patterns

```python
d = Deck('nsfc_blue', nav='mini')
d.add_colors(moc='0072BD', mix='D95319', wcm='77AC30')
d.set_sections([...], en=[...], short=['背景', '方法', '求解', '验证', '结论'])
CB = 6.36                                                      # y of the bottom conclusion bar

def stmt(cv, text):                                            # statement bar → returns next y
    c = cv.content
    return c.y + A.statement(cv, c.x, c.y, c.w, text) + 0.17

def figure_box(cv, image, x, y, w, caption, max_h=None):       # frame sized from the picture's aspect
    ar = Image.open(image).width / Image.open(image).height
    h = (w - 0.12) / ar + 0.12 + (0.34 if caption else 0)
    if max_h and h > max_h:
        h = max_h; w = (h - 0.12 - (0.34 if caption else 0)) * ar + 0.12
    return Box(x, y, w, h), A.figure(cv, Box(x, y, w, h), image, caption)

# formula panel
ip = A.panel(cv, box, '控制方程')
A.formula(cv, Box(ip.x, ip.y, ip.w, 0.8), r'\dfrac{\partial H}{\partial t}+\dfrac{a^{2}}{gA}\dfrac{\partial Q}{\partial x}=0',
          num=1, note='H 测压管水头 · Q 流量 · a 波速')
# one method per row: chip + formula + notes
cv.equation(tex, x, y, size=18, w=6.7, h=row.h - 0.1, align='center', anchor='middle')
# chart with per-point method colors
ch = chart(cv, x, y, w, h, kind='column', categories=[...], series={'耗时/s': [...]}, colors=['A6A6A6'])
for i, col in enumerate(['A6A6A6', '0072BD', 'D95319', '77AC30']):
    pt = ch.plots[0].series[0].points[i]; pt.format.fill.solid(); pt.format.fill.fore_color.rgb = RGBColor.from_string(col)
# zoom the decisive panel of a multi-panel figure
fb, pic = figure_box(cv, fig, c.x, y, 6.7, 'Fig. 3 …')
A.zoom_inset(cv, fig, pic, (0.5, 0.5, 1.0, 1.0), Box(fb.r + 0.45, y + 0.36, c.r - fb.r - 0.45, 2.45), label='B工程')
```

## 5. QA for paper decks

1. Facts pass: compare every number on the slides with the facts table (tables, abstract, conclusion).
2. Equation pass: same point size on a page, numbering matches the paper, no clipped fractions.
3. Figure pass: crops complete (axis labels, legends), English figures have a Chinese caption.
4. Wrap pass: no range or code broken across lines, no single-character last lines; then
   `python -m pptstudio check deck.pptx --com` must report 0 issues.
