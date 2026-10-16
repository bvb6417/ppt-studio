---
name: ppt-studio
description: >
  Build designer-grade, fully editable PowerPoint (.pptx) decks with Python (python-pptx) plus optional
  PowerPoint COM automation (render, real-layout QA, PDF, font embedding). Ships a design system distilled
  from ~3,000 professional Chinese slides, public PPT tutorials and NSFC / 国省科技奖 / 重点研发 / 人才计划 / 重点实验室 defense decks, with 50 ready layouts,
  27 themes, 15 答辩 template-family skins, 1,850 vector icons, native charts/tables, true-size equations and
  figure zoom/callouts for turning papers into talks.
  Two styles: 科研答辩风 (default — 国自然申请/结题、国省科技奖、毕业/开题答辩、挑战杯/互联网+ 答辩: dense,
  navy + red emphasis, numbered title bars, figure panels) and 现代设计风 (日常汇报、课件、路演: airy cards,
  gradients, big numbers). Use this skill whenever the user wants to create, generate, rebuild, restyle or
  beautify a PPT / PPTX / 幻灯片 / 演示文稿 / 答辩PPT / 汇报PPT / 课件 / 路演稿, or turn a paper, report,
  outline, Word document or data into slides — even if they never mention Python, COM or these style names.
---

# ppt-studio

A Python library (`scripts/pptstudio`) + design rules for producing decks that look hand-made by a
professional PPT designer, fully editable in PowerPoint/WPS (native shapes, text, tables, charts, icons —
no screenshots of slides). You write one short build script; the library handles grid, typography,
auto-fitting, colors, icons, backgrounds and QA.

- Library: `<skill>/scripts/pptstudio` (pure python-pptx; COM only for rendering/QA)
- Gallery (look before choosing): `<skill>/assets/gallery/style_<skin>.jpg` — the same 9-page sample talk in each of
  the 15 答辩风格家族 (pick the skin); `defense_layouts_1..7.jpg` (59 pages: every cover / agenda / ending variant and
  every defense layout) / `modern_layouts_*.jpg` — each thumbnail labeled with its call
- Worked examples (one build script each, open them before writing your own):
  `<skill>/examples/nsfc_sodium/build.py` (16-page 国自然申请答辩, almost only stock layouts) ·
  `<skill>/examples/journal_club/build.py` (11-page 期刊风文献汇报: custom chrome + stock layouts + image slots) ·
  `<skill>/examples/ink_showcase/build.py` (8-page 水墨风: calligraphy shapes, picture-filled text, Morph)

## 1. Setup

```bash
pip install python-pptx pillow numpy lxml fonttools    # required
pip install pywin32 matplotlib                          # optional: PowerPoint COM render/QA (Windows), figures
```

```python
import sys; sys.path.insert(0, r'<skill>/scripts')     # <skill> = folder containing this SKILL.md
from pptstudio import Deck, Box
from pptstudio import academic as A, components as K, images as IMG
```

Useful CLI (run from `<skill>/scripts`): `python -m pptstudio themes | fonts | icons 水 | render deck.pptx |
check deck.pptx --com | fix deck.pptx | pdf deck.pptx | embed deck.pptx | analyze ref.pptx | gallery`.

## 2. Workflow — do these in order

1. **Brief.** Pin down scenario (科研 / 日常 / 竞赛 → see §3), audience, talk length, the materials that must
   appear (figures, data, logo, photos), and the output path. Page budget ≈ 1 page per minute (defenses:
   10 min ≈ 10–14 pages, 20 min ≈ 18–22 pages). If the user gives only a topic, research the facts first
   (web search) and cite sources on the pages (`source=`).
2. **Storyline before code.** Write an outline table: `page | layout | title | key sentence | visuals`.
   One message per page. The title names the topic; the *statement bar* (or conclusion bar) states the
   conclusion in one sentence. Read `references/scenarios.md` for proven outlines (国自然、科技奖、毕业答辩、
   开题、竞赛、工作汇报、课件).
3. **Pick style + theme + layouts.** §3 and §4 below; look at the gallery sheets to choose layouts.
   **Layout variety is mandatory**: choose each page's layout from its content structure (§4), never run one
   layout (e.g. `panels` or `bullets`) through the whole deck. A 10–15 page deck normally uses ≥ 7 different
   layouts; no layout on more than 3 content pages unless the content really repeats.
   **Turning a paper / thesis / report into slides?** Follow `references/paper-to-slides.md` (extraction of
   text, tables, figures and OMML/MathType equations; page-by-page mapping; 结论先行, data cards, method colors).
4. **Prepare assets — a figure on (almost) every page.** Put user figures in as-is (never recolor or redraw
   scientific figures); use native charts for numbers you have (`chart=` specs); icons by keyword
   (`python -m pptstudio icons 渗漏`); schematic figures may be generated with matplotlib and must be captioned
   “（示意）”. Illustrations / mood images (covers, background bands, concept pictures — never data plots):
   generate them if you have an image model; otherwise write one prompt per image (file name, aspect ratio,
   composition notes, “no text”) to `img/图片提示词.md`, build with labeled placeholders, and tell the user to
   drop the generated files into `img/` and rerun (see `examples/journal_club/build.py`, `img()` helper).
   Never invent data, citations, awards, logos or photos of real people; use placeholders
   (`'placeholder': '图：XXX'`) instead.
5. **Write one build script and run it** with `d.save(path, render=True)` (writes `<name>_preview/` PNGs +
   `contact_sheet.jpg`). Template in §5; full example in `examples/nsfc_sodium/build.py`.
6. **QA loop (mandatory).** Look at `contact_sheet.jpg`, then open 3–5 dense slides at full size. Run
   `python -m pptstudio check deck.pptx --com` (PowerPoint's own text layout; reports real overflow).
   Fix content/params, rebuild, re-check. Checklist in §7. Stop when a fresh look finds nothing to fix.
7. **Deliver**: the .pptx path, the preview sheet, and a one-paragraph summary of structure and sources.
   Offer PDF (`python -m pptstudio pdf`) and, for sharing to other PCs, `Deck(..., portable=True)`
   (Microsoft YaHei/Arial only) or `python -m pptstudio embed` (embeds fonts; CJK fonts add ~15–35 MB).

## 3. Style and theme

| Scenario | Style | Theme (`Deck(theme)`) | Notes |
|---|---|---|---|
| 国自然申请/结题/中期、国省科技奖、重点研发、学术报告 | defense | `nsfc_blue` (default) · `nsfc_navy` · `bright_blue` | numbered title bars, red keywords, dense panels |
| 国家 / 省科技进步奖、科学技术奖、技术发明奖 | defense | skin `jinbu` or `kexue` (theme `royal_blue`) | plaque / midband covers, 获奖 + 效益 pages |
| 重点研发计划 项目答辩 / 中期 / 申报书 | defense | skin `zhongdian` (`deep_blue`) or `shenbao` | arc cover, corner agenda, 课题分解 + 风险 + 团队 pages |
| 长江学者 / 杰青 / 优青 / 万人计划 等人才答辩 | defense | skin `changjiang` (`navy_deep`) or `wanren` (`steel_blue`) | tag / midband covers, 负责人 + 背景四卡 + 预期成果 pages |
| 重点实验室 组建 / 评估 / 平台汇报 | defense | skin `lab` (`cobalt`) | lab cover, 发展历程, 人员构成, 科研架构图 |
| 论文汇报 / 组会 / 学术会议报告（20+ 页） | defense | `nsfc_blue` + `nav='mini'` + `section(i, variant='number')` | formulas, original figures, method colors (`paper-to-slides.md`) |
| 毕业答辩、开题答辩（按学校色） | defense | `nsfc_blue` / `nsfc_red` / `nsfc_green` / `nsfc_purple` / `burgundy`, or `from_color('#660874', style='defense')` | put school logo via `d.meta(logo=...)`; `nav='top'` or `'left'` for long decks |
| 挑战杯 / 互联网+ / 创新大赛 答辩 | defense | `nsfc_blue`, `nsfc_red` | add `achievements`, `innovations`, `profile` pages |
| 日常工作汇报、述职、课件、讲座 | modern | `business_blue` · `academic_blue` · `eco_green` · `gov_red` · `minimal_gray` | airy cards, big numbers |
| 路演 / 发布 / 科技感封面 | modern | `tech_dark` · `vivid_purple` | dark glow backgrounds |

**答辩风格家族 (skins)** — defense decks also choose a page-chrome family that mirrors real template families;
colors still come from the theme. Default `pixel`. Show the user `assets/gallery/style_*.jpg` when they have no
preference, or pick by occasion:

| skin | Looks like | Use for |
|---|---|---|
| `pixel` | 像素答辩: slanted title marks, navy ribbons | 国自然 / 省科技奖 答辩 (default) |
| `leaf` | 树叶答辩: bar marks, pill headers | 国自然青年学生 / 博士项目, 博士答辩 |
| `baibao` | 百宝箱: underlined titles, tab headers, light covers | 基金答辩, 学术报告 |
| `bright` | 亮蓝白: gradient title band, corner arcs | 申请 / 结题汇报 |
| `badge` | 深蓝白: navy band + number badge, 科技奖 cover | 科技奖, 项目论证 |
| `center` | 居中标题 | red / burgundy themes |
| `tab` | arrow-tab titles | green / 农林生态 themes |
| `tech` | 重点研发: circuit tech cover, light title band | 重点研发, 工程技术 |
| `jinbu` | 国家科技进步奖: bright full-width title band, plaque cover (units band + date) | 科技进步奖 |
| `kexue` | 国家科学技术奖: ╱╱ slash titles, “— 标题 —” cards, key-phrase strips, band agenda | 科学技术奖, 技术发明奖 |
| `zhongdian` | 国家重点研发计划: deep band with faded topic image, arc cover, corner agenda | 重点研发 项目答辩 |
| `changjiang` | 长江学者: navy number boxes, trapezoid tabs, tag cover with split pill | 人才计划答辩 |
| `lab` | 全国重点实验室: two-tone square marks, pale headers, lab cover | 重点实验室, 平台汇报 |
| `wanren` | 万人计划青年拔尖: plain title + rule, band cover with outline pill | 青年人才项目 |
| `shenbao` | 重点研发申报书: half-disc marks, notched headers | 申报书 / 指南方向答辩 |

```python
d = Deck('nsfc_navy', skin='leaf')          # or Deck('#660874', style='defense', skin='badge')
from pptstudio.theme import SKIN_THEMES     # suggested color per skin: Deck(SKIN_THEMES['zhongdian'], skin='zhongdian')
```

Themes are dataclasses; override anything: `Deck('nsfc_blue', primary='0E57A8', size_body=16)`.
Brand/school color: `Deck('#660874', style='defense')` (defense spec in that color; deep/pale tints derived)
or `Deck('#1E66F5')` for the modern style. All presets: `python -m pptstudio themes`.

## 4. Layout chooser

Every layout is a `Deck` method, returns the slide's `Canvas`, and accepts `notes=` (speaker notes),
`source=` (footnote) and `num=` (override the auto “2.3” section number). Content text supports
`[[重点]]` (emphasis color: red in defense themes) and `**加粗**`.

| Content structure | Defense-style layout | Modern-style layout |
|---|---|---|
| Title page | `cover(variant='band'|'sky'|'award'|'left'|'tech'|'plaque'|'midband'|'arc'|'tag'|'lab')` (default from the skin; `d.meta(units=[…], date=…, lab=…)`) | `cover(variant='left'|'center'|'split'|'dark'|'image')` |
| Agenda / chapter divider | `agenda(variant='vertical'|'split'|'card'|'corner'|'band')`, `section(i)` (agenda with current item red), `section(i, variant='number', desc=[...])` (big “PART 01” divider) | `agenda()`, `section(i, variant='bignum'|'nav'|'center')` |
| Equations / paper figures | custom page: `A.formula`, `cv.equation`, `A.figure` → `A.zoom_inset`, `A.callout`; formula cards: `band_cards(..., card_style='topline', cards=[{'formula', 'symbols'}])` | same |
| 1+N 总分 (goal → contents, background → problems, KPIs + charts) | `band_cards(headline, text, kpis, cards)` (拦腰) | `band` |
| System / technical / platform architecture | `architecture(tiers, top, sides)` | `pyramid(variant='layers')` |
| 本文方法 vs 对比方法 | `versus(ours, others)` | `compare` |
| Technical route as a matrix (steps × levels) | `process_matrix(steps, rows, cells, phases, arrows)` | `process` |
| Closed loop / PDCA / 监测—决策—反馈 | `cycle(steps, center)` | `hub` |
| 国内外研究现状 | `bands(bands=[国外, 国内], conclusion='不足：…')` | `compare` |
| 课题分解 / 组织架构 | `tree(root, children)`; 4 课题 with their relations → `topics(topics, links, banner)` | `team` |
| 研究背景四视角 → 科学机遇 | `need_cards(cards, converge)` | `cards` |
| 研究框架 / 科研架构图 (hub) | `framework(center, ring, accents, arcs, left, right, bottom, palette='teal')` | `hub` |
| 风险分析 / 风险清单 | `risks(risks, variant='cards'|'tabs'|'rows')` (levels 低/中/高, 涉及课题, 应对措施) | `cards` |
| 预期成果 | `outcomes(items, center, figures)` | `kpis` / `cards` |
| 实验室 / 团队人员构成 | `lab_team(stats, headline, leader, members, columns, rows)` | `team` |
| 项目负责人 / 申请人 | `leader(name, photo, honors, points, awards, groups)` (or `profile` for students) | `team` |
| 发展历程 | `history(events, banner, subtitle)` or `milestones` | `timeline` |
| 科研团队获奖 | `awards(columns, rows, banner, certificates)` | `table_page` |
| 2–6 parallel blocks with figures/points | `panels(statement=, panels=[...], conclusion=)` | `cards(items)` |
| 4 problems/features + bottom bottleneck rows | `columns(statement, cols, bottom)` | `split(panels, arrows=True)` |
| 问题一/问题二 (+figure +研究目标) | `problems(items, variant='rows'|'columns')` | `compare` / `cards` |
| Big figure + explanation blocks | `figure_text(image|visual, blocks|points, statement)` | `text_image`, `figure` |
| Technical route (goal → questions → topics) | `route(target, top, questions, topics)` | `process` |
| Innovation points | `innovations(items, subtitle, footer)` | `cards(variant='number')` |
| Achievements (papers/patents + red numbers) | `achievements(stats, images)` | `kpis` |
| Research schedule / Gantt | `schedule(periods, tasks)` | `timeline(variant='cards')` |
| Personal profile (education/results) | `profile(name, groups)` | `team` |
| Layered architecture | `layers(levels, side)` | `pyramid(variant='layers')` |
| Milestones + headline numbers | `milestones(events, stats)` | `timeline`, `kpis` |
| Table | `table_page(style='header'|'three_line')` | same |
| Chart + findings | `chart_page(chart={...}, points=)` or `panels([{'chart': {...}}])` | same |
| Center concept + aspects | `hub` | `hub` |
| 2×2 / priority | `matrix` | `matrix` |
| Closing | `ending()` → just **“谢谢”** (default; add other lines only if the user asks) | `ending()` → “谢谢” (`qa`/`critique`/`contact` only on request) |
| Anything else | `cv = d.page('标题')` + helpers (§6) | same |

Generic layouts (cards, bullets, timeline, process, hub, compare, kpis, matrix, …) also work inside a defense
deck and pick up its chrome/colors. Panels and cards also take `formula`+`symbols`, `stat_grid` (number grid) and
`bars` (progress bars). Water / 流域 topics: `cover(motif='wave')`; 开题 / 答辩 decks: `Deck(nav='bottom')`. Exact parameters, capacities and variants: `references/layout-catalog.md`.

## 5. Build-script template

```python
import sys, os
sys.path.insert(0, r'<skill>/scripts')
from pptstudio import Deck

d = Deck('nsfc_blue')                                   # defense style; Deck('business_blue') for modern
d.meta(title='复杂系统XXX机理与调控方法研究', author='张三', unit='XXX大学 XXX学院', lab='XXX重点实验室',
       project='国家自然科学基金面上项目 结题汇报', logo=None)
d.set_sections(['立项依据', '研究内容与方案', '研究成果与创新', '总结与展望'])

d.cover()
d.agenda()
d.section(1)
d.panels('国家重大需求',
         statement='我国XXX面临[[“卡脖子”]]问题，亟需突破[[关键科学问题]]',
         panels=[{'header': '需求一', 'image': 'fig1.png', 'caption': '图1 XXX', 'points': ['要点，[[关键词]]', '要点']},
                 {'header': '需求二', 'chart': {'kind': 'column', 'categories': ['A', 'B'], 'series': {'指标': [3, 5]}},
                  'points': ['要点', '要点']}],
         conclusion='一句话结论：本项目瞄准XXX', conclusion_style='yellow',
         source='数据来源：XXX（2025）', notes='讲稿：……')
d.problems('关键科学问题', lead='拟解决两大[[关键科学问题]]', items=[
    {'label': '问题一', 'question': '如何XXX？', 'image': 'fig2.png', 'caption': '图2', 'tag': '研究目标',
     'points': ['目标一', '目标二']},
    {'label': '问题二', 'question': '如何XXX？', 'placeholder': '图：待补充', 'tag': '研究目标', 'points': ['目标一']}])
# ... one call per page ...
d.ending()
d.save(r'out/项目答辩.pptx', render=True)                 # then inspect out/项目答辩_preview/contact_sheet.jpg
```

## 6. Custom pages (when no layout fits)

`cv = d.page('标题')` draws the chrome and returns a `Canvas`; `cv.content` is the free `Box(x, y, w, h)`
in inches on a 13.333×7.5 slide. `Box` helpers: `.cols(n, gap, weights)`, `.rows(n, gap)`, `.grid(n, cols)`,
`.split(frac)`, `.inset(dx, dy)`, `.cx/.cy/.r/.b`.

```python
from pptstudio import academic as A, Box
cv = d.page('方向三：智能调度')
b = cv.content
y = b.y + A.statement(cv, b.x, b.y, b.w, '以[[能耗最低]]为目标，实现联合优化调度', style='label', label='核心阐述') + 0.18
left, right = Box(b.x, y, b.w, b.b - y).split(0.5, gap=0.25)
inner = A.panel(cv, left, header='模型构建')              # light panel + navy ribbon; returns inner Box
A.arrow_list(cv, inner, ['多目标[[优化模型]]', '约束条件……'])  # ➢ bullets (native, editable)
A.figure(cv, right, 'energy.png', '图3 优化调度效果（示意）')
A.conclusion(cv, '一句话结论', y=b.b - 0.55)               # full-width navy bar
```

Primitives: `cv.text(x,y,w,h, text, size, color, role, align, anchor, fit=True)` (auto-shrinks to fit),
`cv.rect/ellipse/circle/shape/line/poly/ring`, `cv.icon(name_or_keyword, x, y, size, color)`,
`cv.image(path, x, y, w, h, fit='cover'|'contain')`, `cv.measure(text, w, size)` → height in inches.
Colors are theme roles (`primary`, `primary_deep`, `emph`, `panel`, `text`, `muted`, `primary+30` tint,
`primary-20` shade) or hex. Defense helpers (`academic.py`): `title_bar, statement, panel, ribbon, tag, vlabel,
arrow_list, figure, flow_chain, mini_table, stat, conclusion, block_arrow, axis, brace, num_square,
red_marker, icon_badge_ac, formula, zoom_inset, callout`; template-family parts `level_chip, chip, person,
silhouette, laurel, stars, certificate, metric_box, converge, vchain, arc_text, hub_node, cylinder`; textures
`IMG.skyline / hexgrid / dot_wave / circuit`. Full API: `references/api.md`.

Research extras: `cv.equation(r'\dfrac{a}{b}', x, y, size=19)` typesets TeX at true point size;
`A.formula(cv, box, tex, num=3, note='符号说明')` numbered display equations; `A.zoom_inset(cv, img, pic,
(x0, y0, x1, y1), dst)` enlarges a figure region (better than a red box); `d.add_colors(wcm='77AC30')` +
`'{{wcm|WCM}}'` markup keep a paper's method colors in text, chips, charts and tables. Numeric ranges such as
`4.6–10.5` never break across lines (auto-glued).

## 7. QA checklist (what to look for in the renders)

1. Text overflow / clipped text / orphan characters on a new line → shorten text first, then widen the box.
   `python -m pptstudio check deck.pptx --com` lists real overflow; `fix` shrinks font as a last resort.
2. Collisions: labels crossing lines/figures, text on top of shapes, footnote touching content.
3. Empty or unbalanced areas (a half-empty panel, content hugging the top) → add a figure/stat/flow, change
   layout (`cols`, `weights`, `variant`), or move content to a neighbour page.
4. Emphasis discipline: 2–4 `[[red]]` phrases per page; one conclusion bar max; titles ≤ 16 CJK chars.
5. Consistency: same theme across pages, numbering order (`1.1, 1.2 …` resets at each `section()`),
   figure captions present, sources on data pages.
6. Density vs legibility: body ≥ 14 pt (defense 15 pt default, min 10.5 pt in tables); if auto-fit had to
   shrink below 12 pt, split the page.
7. Variety & visuals: list the layout used on each page — the same layout page after page, or more than two
   text-only pages, means the deck is not done: switch layouts and add figures / charts / images.

## 8. Design rules that matter most

- **Content first, then layout.** Split long paragraphs into a 4–10 char subheading + short points; pull
  numbers out into stats/charts; convert repeated fields into a table (details: `references/design-rules.md`).
- **Restraint in color.** One main hue (+ its deep/pale tints) + neutrals; defense style adds red only for
  keywords. Never use default Office blue tables/SmartArt looks; shadows are soft and tinted, not black.
- **Alignment & grouping.** Everything snaps to the page grid (margins 0.42–0.75 in); related items share a
  container; equal gaps; images cropped to identical size in a row.
- **Hierarchy.** Title 26–30 pt > statement/heads 16–18 pt > body 14–16 pt > captions 11–12 pt; numbers
  large (28–60 pt) with small units.
- **Scientific integrity.** Keep original figures unaltered, label schematic ones “（示意）”, cite sources.
- **Fonts.** Default stack: 思源黑体/Noto Sans SC (body), 思源宋体/Noto Serif SC Bold (cover titles and
  conclusion bars), Bahnschrift for numbers. For decks that will be opened elsewhere use `portable=True`.

## 9. Gotchas

- Coordinates are inches; the slide is 13.333 × 7.5 (16:9). Don't hand-edit generated XML.
- `cv.text(fit=True)` shrinks to `min_size` — if text still doesn't fit, it is too long: cut it.
- Pass image *paths*; huge photos are fine (cropped via `fit='cover'`), but compress > 5 MB files first.
- Charts are native and editable; `chart['highlight']` colors key bars, others are pale.
- Rendering/QA need Windows + PowerPoint (pywin32). Without it the build still works; convert with
  LibreOffice (`soffice --headless --convert-to pdf`) to review.
- Icons: exact Lucide names or Chinese/English keywords (`cv.icon('渗漏', ...)`); `python -m pptstudio icons 关键词`.
- Studying a template/reference deck? `python -m pptstudio analyze ref.pptx` prints its fonts, sizes, colors.

## 10. Reference files (read when relevant)

| File | Read when |
|---|---|
| `references/defense-style.md` | any 科研/答辩/基金/奖励/人才/实验室 deck — visual spec, 15 skins, page recipes |
| `references/layout-catalog.md` | choosing/parameterizing layouts; capacities per layout; variants |
| `references/scenarios.md` | planning the storyline: outlines for 国自然申请/结题、科技奖、毕业/开题答辩、竞赛、汇报、课件 |
| `references/design-rules.md` | writing/splitting content, color/typography/spacing rules, quantitative defaults |
| `references/techniques.md` | emphasis, image handling, charts, tables, backgrounds, icons, COM tricks as code |
| `references/api.md` | full function signatures (Deck, Canvas, academic, components, images, charts, tables, mathtex, render, qa) |
| `references/paper-to-slides.md` | the input is a paper/thesis/report: extraction, page mapping, equations, figure crops, faithfulness QA |
| `references/sources.md` | where the rules came from (kinds of material analysed) |
