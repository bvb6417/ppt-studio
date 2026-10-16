# Layout catalog

Every layout is a method of `Deck` (`d.<name>(...)`), draws one slide and returns its `Canvas`.
Look at `assets/gallery/defense_layouts_*.jpg`, `style_*.jpg` (答辩风格家族) and `modern_layouts_*.jpg` — each thumbnail is labeled with the
call that produced it.

Common keyword arguments on every content layout: `en=` (English subtitle, modern style), `source=` (footnote
line: 资料来源/数据来源), `notes=` (speaker notes), `section=` (set current chapter explicitly), `num=`
(defense style: override the auto “i.k” number; `False` hides it).
Text anywhere accepts `[[emphasis]]` (theme `emph`: red in defense themes, primary in modern ones) and `**bold**`.
Capacities below are comfortable maxima at default sizes; beyond them the auto-fit shrinks text — split the page.

Contents: A. Structure pages · B. Defense-style content layouts · B2. Research layouts (tutorial review) ·
B3. Template-family layouts (新参考) · C. Generic content layouts · D. Chart/table specs

---

## A. Structure pages (style-aware: same call, different look per theme style)

### `cover(title=None, subtitle=None, en=None, tag=None, info=None, variant=None, image=None, ...)`
- Defense variants: `band` (default; navy band, serif title, “汇报人” pill, units below) · `sky` (light, navy serif
  title) · `award` (科技奖: big serif title + subtitle, completers, units on bottom band) · `left` (亮蓝白: slanted
  bright block, left title, corner arcs) · `tech` (重点研发: circuit background, bottom band with units) ·
  `plaque` (科技进步奖: logo + year line, huge blue serif title, spaced subtitle with a fading rule, faint skyline,
  presenter pill sitting on a bottom band with `meta(units=[…])` in 1–2 rows + `meta(date=…)`) · `midband`
  (科学技术奖 / 万人计划: logo or caption between rules, full-width blue band holding the white serif title +
  subtitle, pill, 单位 lines, `units` as an aligned grid; `extras['cover_pill']='outline'`, `extras['cover_texture']=
  'plain'` give the 万人 look) · `arc` (重点研发: navy block with a bowed lower edge + light echo, caption between
  rules, pill on the lowest point, units below) · `tag` (长江学者 / 人才计划: white card, navy trapezoid tag with
  `project`, chevron subtitle band, split pill 汇报人｜name, navy swoosh) · `lab` (重点实验室: navy pill with
  `project`, `meta(lab=…)` between long rules, serif title + subtitle, pale » presenter « band — pass
  `presenter='实验室主任：X'`, left-aligned 依托 / 联合单位 block, halftone dot wave).
  `motif='wave'` adds layered water waves (水利 / 流域 / 海洋 topics) to `band`, `sky` and `award` covers.
  Extra kwargs: `project=` (small line above title, default `meta['project']`), `presenter=`.
  Units/lab lines come from `d.meta(unit=..., lab=..., org=...)`, or pass `info=['申报单位：…', …]`.
- Modern variants: `left` (default) · `center` · `split` · `dark` (tech) · `image` (full-bleed photo + mask).
  `info` default = author/advisor/org/date from `meta`; `tag` = chip above title; `watermark` = big faint word.
- Title: ≤ 2 lines, break with `\n`; ≤ 28 CJK chars total.

### `agenda(items=None, variant=None, title=..., en='CONTENTS', descs=None, ...)`
- Defense: `vertical` (default; navy block with vertical “汇报提纲”, numbered pill rows, 3–6 items) · `split`
  (navy left panel “目录 CONTENTS”, numbered list; `descs` shown as small English lines) · `card` (white card over a
  split background, vertical serif title) · `corner` (重点研发: white card with diagonal corner sashes, vertical
  serif “汇报目录” + faint vertical CONTENTS, rows on fading bars) · `band` (科技奖: navy title band + a row of
  numbered cards, `descs` under the titles; 3–5 items). `current=` index highlights one item in red (used by
  `section`).
- Modern: `list` (≤ 6) · `grid` (7–10) · `cards` (3–5, staggered cards with gradient numbers).
- Items default to `d.set_sections([...])`.

### `section(index, title=None, en=None, desc=None, variant=None, ...)`
- Defense: re-shows the agenda with chapter *index* (1-based) in red and resets sub-numbering (`index.1`, …).
  `variant='band'` → full navy page “第X部分 + title”.
  `variant='number'` → 大序号过渡页: navy block with huge “PART 01”, serif title + English line, `desc=[...]`
  bullets saying what the part will show, chapter progress bar at the bottom (best for 20+ page talks).
- Modern: `bignum` (default; giant gradient number) · `nav` (list with current chapter as a gradient bar) · `center`.

### `ending(title=None, subtitle=None, variant=..., info=None, ...)`
- Defense: default text is just **“谢谢”** (no 感谢专家/批评指正, no presenter or unit lines);
  `variant='band'|'sky'|'split'|'plaque'|'midband'` (default from the skin; plaque = white page, faint skyline,
  bottom band; midband = word on a full-width blue band across a hexagon-textured page). Extra lines only on request: `subtitle=`, `en=`, `presenter=True`, `info=[...]`.
- Modern: `thanks` (default, just “谢谢”) · `qa` · `critique` (恳请各位老师批评指正 — only if asked) · `contact`.

---

## B. Defense-style content layouts (designed for `nsfc_*` themes; usable in any theme)

### `panels(title, panels, statement=None, stmt_style='bar', stmt_label=None, conclusion=None, conclusion_style='navy', cols=None, header_style='ribbon', weights=None)`
The workhorse. Statement bar → grid of light panels with navy ribbon headers → optional conclusion bar.
- `panels`: list of dicts. Keys (all optional, rendered top → bottom in this order):
  `header` · `subtitle` (centered navy line) · one visual: `image` + `caption` | `chart` (spec, §D) | `visual`
  (callable `f(cv, box)` drawing native shapes) | `placeholder` (text shown in an empty frame) ·
  `image_h` (fraction of panel height for the visual; default: sized from the image aspect ratio) ·
  `table` `{columns, rows, emph_cols, align, size, h}` · `stats` `[{value, unit, label}]` · `flow`
  `[{title, sub, icon}]` + `flow_style` (`grad|box|light`) · `tags` `[str]` (light tag row) ·
  `points` `[str]` (➢ list; grows to fill, centered when with an image) or `text` · `icon` (icon badge + points,
  for text-only overview grids) · `size` (force point size).
- `cols`: default n≤4 → n columns; 5–6 → 3 per row. `weights=[1, 1.3]` sets relative column widths (per row).
- `stmt_style`: `bar` | `label` (+ `stmt_label='核心阐述'`) | `centered` | `pink`.
- `conclusion_style`: `navy` (white bold) | `yellow` (yellow serif, strongest) | `red` | `light`.
- `header_style`: `ribbon` (label centered on top edge) | `strip` (full-width header) | `tab`.
- Capacity: 2 panels → 2–4 points × ≤ 28 chars each (+ visual); 3 → 2–3 × ≤ 22; 6 (cols=3) → 2 × ≤ 16.

### `columns(title, cols, statement=None, axis=True, bottom=None, conclusion=None, arrow_between=True)`
“卡脖子问题”: 3–4 navy header boxes → small red arrows → light cards (centered navy `subtitle` + ➢ `points`) →
gradient axis with nodes → bottom zone.
- `cols`: `[{header, subtitle, points}]` (header ≤ 8 chars, subtitle ≤ 10, 2–3 points ≤ 16 chars).
- `bottom`: list of `{tag: '算法\n算力', title, text}` chevron-tag rows (1–3), or a string → navy conclusion bar.
- `conclusion`: extra yellow serif bar at the very bottom.

### `problems(title, items, lead=None, conclusion=None, variant=None)`
“问题一/问题二”. `items`: `[{label, question, image|placeholder, caption, tag, points}]`.
- `variant='rows'` (default ≤ 2 items): red marker + question bar, then figure (width from aspect ratio) +
  light panel with ribbon `tag` (“研究目标”) and points. Question ≤ 34 chars; 2–3 points ≤ 26 chars.
- `variant='columns'` (default 3–4 items): red label on top of each column, question box, figure, points.
- `lead`: statement line above (navy text with red keywords).

### `figure_text(title, image=None, caption=None, blocks=None, points=None, statement=None, side='left', frac=0.52, header=None, conclusion=None, visual=None, stmt_style='label', stmt_label='核心阐述', placeholder=None)`
Big figure (or `visual` callable) on one side; on the other side either `blocks` =
`[{tag: '机理\n研究', title, text}]` (2–4 chevron-tag blocks; title ≤ 14 chars, text ≤ 40 chars) or `points`
(+ optional strip `header`). Statement defaults to the “核心阐述” label style.

### `route(title, target, top, questions, topics, left_image=None, right_image=None, labels=('', ''), left_caption=None, right_caption=None)`
技术路线. `target` → centered “▪▪▪ 科学目标：… ▪▪▪” line; `top` → navy goal box; up arrow with two red `labels`;
`questions` `[{title, focus}]` listed top → bottom; `topics[i]` = list of topic strings for `questions[i]`
(joined by a brace). Side images optional (framed with captions). Typical: 2 questions × 2 topics.

### `innovations(title, items, subtitle=None, footer=None, image=None, visual=None, caption=None)`
Numbered rows: navy “01” square + navy tab label (`tag`) + text (`text`, ≤ 60 chars, 1–2 red keywords).
3–4 items. `subtitle` → centered statement; `footer` → light closing line; optional figure right third.

### `achievements(title, stats, images=None, headline=None, footer=None, captions=None)`
Row of framed thumbnails (papers, certificates, photos; `None` → placeholder) + row of red stats
`[{value, unit, label}]` (3–5). `headline` → centered statement; `footer` → navy bar.

### `schedule(title, periods, tasks, statement=None, sub_periods=None)`
Gantt table. `periods=['2026', '2027', …]`, `sub_periods=['1-6月', '7-12月']` (optional),
`tasks=[{name, desc, span: (start, end), label, color}]` with `span` in sub-period units (0-based, end exclusive).
≤ 6 tasks, ≤ 10 sub-periods.

### `profile(title, name, groups, role=None, photo=None, direction=None, conclusion=None)`
个人基本情况. Photo card (placeholder if none) + `direction` bar + `groups=[{label: '教育经历', rows: [(时间,
单位, 专业, 学位)]}, {label: '成果列表', rows: [(类别, 内容, '', 角色)]}]` (first cell navy, last cell red).
≤ 3 rows per group, 2 groups. `conclusion` → yellow serif bar.

### `layers(title, levels, statement=None, side=None, conclusion=None)`
Layered architecture: navy label column + light rows of white chips (`levels=[{label, items}]`, top → bottom,
3–5 levels × 2–5 chips ≤ 8 chars). `side={'header', 'points'}` adds a tall panel at right.

### `milestones(title, events, statement=None, highlight=None, conclusion=None, stats=None)`
Gradient axis with navy year pills; event boxes alternate above/below (4–7 events; title ≤ 10, text ≤ 24 chars);
`highlight` index turns red. `stats=[{value, unit, label}]` adds a red-number row on top (3–4).

---

## B2. Research layouts from the tutorial-image review (defense look; usable in any theme)

Distilled from 1,679 images of 57 tutorial articles (2024–2026, see `design-rules.md §13`). Each answers a page type
that the classic NSFC layouts handled poorly. All accept `statement=` (except `band_cards`, whose band *is* the
statement), `conclusion=` + `conclusion_style=`, and the common keywords.

### `band_cards(title, cards, headline=None, text=None, kpis=None, pills=None, image=None, caption=None, band_h=None, overlap=0.5, card_style='shadow')`
拦腰式 — the most frequent pattern in the review (10+ articles). A full-width deep band carries the 总: `headline`
(1–2 lines, `[[x]]` turns yellow), `text` (1–3 lines), `kpis` `[{value, unit, label}]` (yellow numbers at the
right), `pills` (keyword chips), `image` (figure/cut-out at the right). 2–5 white `cards` overlap the band's lower
edge; card keys = every `panels` key plus `title`, `icon`, `tag` (pill above the title).
- Use for: 1+N 总分 pages (研究目标→研究内容, 背景→问题, 总体方案→子方案), formula pages (`card_style='topline'`,
  cards with `formula` + `symbols`), KPI + charts pages (kpis in the band, chart cards below), text + table pages.
- Short cards automatically become shorter and the band taller (no empty card bottoms); band text is centred.
- Capacity: 3 cards × (title + 3 points ≤ 18 chars); 2 cards with a chart/table/formula each.

### `architecture(title, tiers, top=None, sides=None, label_w=0.62)`
分层架构图 (system / technical / platform framework). `tiers` top→bottom: `{'label': '应用层', 'items': [str |
{'text', 'icon'}]}` or `{'label', 'groups': [{'title', 'items'}]}` (sub-containers in one tier). `top`: goal banner
over the tiers. `sides`: `[{'label': '标准规范体系', 'side': 'left'|'right'}]` tall columns spanning all tiers.
- Three color levels only: solid tier labels + banner · pale tier rows · white chips. Icons optional.
- Capacity: 3–5 tiers × ≤ 6 chips (≤ 6 chars each); groups 2–4 per tier.

### `versus(title, ours, others, statement=None)`
本文方法 vs 对比方法. `ours` = highlighted card (deep header, optional `badge` such as '综合最优', ✓ rows with values
in red, shadow); `others` (1–3) = gray cards; VS badge between. Card keys: `name`, `sub`, `rows` `[(label, value)]`
(same labels in the same order on every card) or `points`. Use real numbers only — the page invites scrutiny.

### `process_matrix(title, steps, cells, rows=None, phases=None, arrows=None, notes_row=None)`
技术路线 / 研究流程 as a matrix. `steps` = chevron header whose color deepens left→right; `phases` =
`[(label, first_col, last_col)]` brackets above; `rows` = row labels (理论/方法/应用 or 课题); `cells[r][c]` = str |
`{'title', 'text'}` | None; `arrows` = `[(r1, c1, r2, c2)]` dashed connectors; `notes_row` = one short line per step
(or `[(text, c0, c1)]`) under the grid. Capacity: 4–6 steps × 2–4 rows; cell text ≤ 2 short lines.

### `cycle(title, steps, center=None, center_sub=None, icon=None, colors=None)`
闭环 / 循环 (PDCA, 监测—模拟—决策—反馈, GROW …). Ring of 3–6 arrow segments with the step labels along the ring
(`label` ≤ 4 chars, default = title[:4]), centre disc with `center` / `center_sub` / `icon`, numbered detail blocks
left and right in ring order (`steps`: `{'label', 'title', 'points' | 'text'}`). Uses `A.cycle` (also callable alone).

### `bands(title, bands, word_w=2.0)`
国内外研究现状 / 对比综述. 2–3 full-width horizontal bands; each has a big faded serif `word` ('国外',
'国内', '理论', '应用'), a `label`, and 1–3 `cols` `{title, points}` (or plain `points`). First band deep, then
pale, alternating. Finish with `conclusion='不足：…'` (the research gap).

### `tree(title, root, children, root_sub=None)`
层级树: 课题分解 / 项目组织架构 / 研究内容分解. root (deep) → 2–6 level-2 nodes (`{'name', 'sub', 'children'}`) →
≤ 5 stacked leaves each (str or `{'name', 'sub'}`), thin elbow connectors.

### Panels / cards: extra keys
`formula` (TeX) + `symbols` `[(tex, meaning)]` (+ `formula_size`, `num`) · `stat_grid` `[{label, value, unit,
color}]` (+ `grid_cols`) · `bars` `[{label, value, display}]` (+ `bars_highlight`, `bars_max`) · `anchor`
(`top|middle` for the points block). Work in `panels`, `band_cards` cards and anywhere `_fill_panel` is used.

---

## B3. Template-family layouts (新参考, 2026-10-02)

Distilled from 86 finished decks of 国家科技进步奖 / 国家科学技术奖 / 国家重点研发计划 (项目 + 申报) / 长江学者 /
全国重点实验室 / 万人计划 and 科研架构图 hub diagrams (`design-rules.md §14`, `layouts_pro.py`, `parts.py`).
All accept `statement=` (+ `stmt_style`, `stmt_label`), `conclusion=` + `conclusion_style=` and the common keywords,
and pick up the skin's chrome (they look right in every skin). Missing photos are drawn as ID-photo silhouettes and
missing images as labeled placeholders — never fill them with photos of real people the user did not supply.

### `risks(title, risks, variant='cards', cols=None, impact_label='负面影响：', topic_prefix='涉及')`
风险分析 / 风险清单. `risks`: `{'name', 'summary', 'impact', 'level': '低'|'中'|'高', 'topic', 'label', 'points',
'measure'}`. Variants: `cards` (万人, 2 columns: navy arrow tag + › summary, red “负面影响：” line, separator,
chips 级别高 / 涉及课题三) · `tabs` (申报 NO.483, 3 columns: trapezoid tab header, red outlined label + dashed
summary box, ➢ bullets, 涉及课题 chip filled with the level color + the level word) · `rows` (one row per risk:
level badge, name + topic, impact, pale “应对：” box with `measure`). Level colors: 低 `72AE48` · 中 `EE7F32` ·
高 `BF0202`. Capacity: cards 4 (≤ 6) · tabs 6 · rows 4–5.

### `outcomes(title, items, center=None, figures=None)`
预期成果 (万人计划). A navy centre card (`center={'header': '预期成果', 'image', 'caption'}`) flanked by outline
pills with gradient number circles — first half of `items` left (01, 02 …), the rest right, text right-aligned.
`items`: `{'title', 'text' | 'points'}` (2–6). `figures`: up to 4 images (`path` or `{'image', 'caption'}`) in a row
underneath; finish with `conclusion=`.

### `topics(title, topics, banner=None, links=None, side_left=None, side_right=None)`
课题分解与关联 (重点研发). Four 课题 panels in 2×2: red `name` (课题1) | navy `title` (2 lines, `[[x]]` ok) + any
panel content (`image`, `points`, `chart`, `table`, …). `links` keys are 1-based pairs: horizontal `(1, 2)`/`(3, 4)`
(two labels → a pair of opposite arrows; one label → a navy double block arrow), vertical `(1, 3)`/`(2, 4)` (block
arrow down, label beside it; two labels → down + up), diagonal `(2, 3)`/`(1, 4)` (double arrow, label along it).
`banner` = pale strip on top (“系统集成与应用验证 ➜ [A] → [B]”); `side_left` / `side_right` = stacked labels on
outer brackets with arrows into the panels.

### `lab_team(title, stats=None, headline=None, leader=None, members=None, columns=None, rows=None, highlight_rows=(), left_header='成员组成', right_header='团队骨干成员')`
实验室 / 团队人员构成. Left: header strip, `headline` (“固定人员共计[[168]]人…”), `stats` `[(value, unit, label)]` →
red numbers over pill labels, `leader` card `{'name', 'label': '实验室主任', 'titles': [...], 'points': [...],
'photo'}`, `members` photo row `{'name', 'role', 'photo'}` (≤ 5). Right (when `rows` given): header strip + roster
table; `highlight_rows` (0-based) turn red. (The modern people-card layout is `team`.)

### `leader(title, name, photo=None, honors=None, points=None, awards=None, groups=None)`
科研项目负责人. Photo (or silhouette) with a navy name band | honour strip (`honors`, first one yellow) + ➢
`points` + laurel badges (`awards`: `{'title', 'level'}`, ≤ 3, titles ≤ 8 chars) on a pale strip; below, `groups`
`{'name': '课题一负责人', 'members': [{'name', 'role', 'photo'}]}` as tab-headed photo groups (widths ∝ member count).

### `need_cards(title, cards, converge=None)`
研究背景 / 需求四卡 (长江学者). 3–5 cards: trapezoid `tab` (科学挑战 / 国家需求 / 国际竞争 / 技术发展), `image` with a
`caption` ribbon over its lower edge, `head` (primary, bold), `sub` (bold), grey `foot` note; chevron circles between
cards. `converge={'left', 'right', 'center': '科学机遇', 'conclusion'}` adds the V-shaped funnel to a red conclusion.

### `framework(title, center, ring, accents=None, arcs=None, left=None, right=None, bottom=None, banner=None, palette=None, highlight=None)`
科研架构图 (hub). Centre hexagon (`center`, serif, `\n` for 2 lines), 4 `ring` nodes on a dashed circle (top, right,
bottom, left; `{'title', 'subs': ['诉求', '张力'] | '一个短标签'}`), `accents` (4 single characters on the diagonals),
`arcs` (≤ 4 phrases set along the ring between nodes with arc arrows, clockwise from the top-right quadrant), side
columns `left` / `right` = `{'circles': ['创新\n路径', …], 'boxes': [{'title', 'text'}]}`, `bottom` chain of 3-D cans
pointing at the highlighted middle item, `banner` on top. `palette='teal'` → teal `1E6B7F` + maroon `A0323C`
(the hub-diagram palette); default = theme navy + red.

### `history(title, events, banner=None, subtitle=None)`
发展历程. Navy pill `banner`, one-line `subtitle`, gradient arrow with navy year pills, per event `{'year', 'title',
'stars': 1–3, 'image', 'key': True → red title}` (4–6 events); images share one height.

### `awards(title, columns=None, rows=None, banner=None, highlight_rows=(), certificates=None, cert_aspect=0.74)`
科研团队获奖. Navy `banner` (`[[n]]` → yellow), award table (minimal style, key rows red), certificate shelf:
`certificates` = image paths / `{'image', 'title'}` / plain titles (drawn certificate placeholders) — use the
team's real certificate scans when available.

### Parts used by B3 (callable on custom pages, `A.<name>`)
`level_chip`, `chip`, `person`, `silhouette`, `laurel`, `stars`, `certificate`, `metric_box`, `converge`, `vchain`,
`arc_text`, `hub_node`, `cylinder`, `chevrons` — signatures in `api.md`.

## C. Generic content layouts (both styles; designed for the modern style)

| Layout | Signature (main args) | Notes / capacity |
|---|---|---|
| `cards` | `(title, items, variant='icon_top'|'number'|'icon_left'|'header', cols=None, summary=None, body_size=None)` | `items=[{icon, title, text, tag}]`, 2–6; `summary` → gradient takeaway pill |
| `bullets` | `(title, points, style='rows'|'plain', marker='num'|'dot'|'check'|'icon', lead=None, image=None, side='right')` | 3–6 points ≤ 40 chars; write `**小标题**：说明` |
| `text_image` | `(title, heading=None, text=None, image=None, points=None, side='right', caption=None, visual=None)` | one idea + photo/illustration |
| `kpis` | `(title, items, variant='cards'|'row'|'rings', lead=None, summary=None)` | `items=[{value, unit, label, desc, icon, trend}]`, 2–5; rings need `%` values |
| `chart_page` | `(title, chart, points=None, kpis=None, side='right', chart_title=None, unit=None, summary=None)` | chart spec §D; panel shows 2–4 findings or 2–3 KPIs |
| `table_page` | `(title, columns, rows, style='header'|'three_line'|'minimal', highlight_col=None, highlight_mode='fill'|'raised', highlight_rows=None, note=None, col_widths=None, align=None, font_size=None)` | ≤ 8 rows × 6 cols; `three_line` = academic 三线表 |
| `timeline` | `(title, events, variant='axis'|'cards'|'rise', highlight=None)` | `events=[{date, title, text}]`, 3–7 |
| `process` | `(title, steps, variant='chevron'|'circles'|'cards', summary=None)` | `steps=[{title, text, icon}]`, 3–6 |
| `hub` | `(title, center, items, center_sub=None)` | center concept + 3–6 aspects (surround layout) |
| `compare` | `(title, left, right, variant='cards'|'rows', rows=None, highlight='right')` | `left/right={title, subtitle, points, icon}`; `rows=[(label, lv, rv)]` |
| `matrix` | `(title, items, x_label=None, y_label=None, highlight=None)` | exactly 4 items TL, TR, BL, BR |
| `pyramid` | `(title, levels, variant='pyramid'|'layers')` | `levels=[{title, text}]` or `[{title, items}]` (layers) |
| `band` | `(title, statement, items, icon='lightbulb')` | 拦腰型: colored band with core idea + 2–4 blocks |
| `split` | `(title, panels, arrows=False)` | 分割型 full-height panels `[{title, points|text, icon, tag}]`, 2–4 |
| `figure` | `(title, image, caption=None, points=None, side='left', fig_no=None, frac=0.6)` | scientific figure on a card + numbered points |
| `image_grid` | `(title, images, cols=None, radius=0.1)` | 2–8 images cropped to identical cells, captions |
| `team` | `(title, members)` | `[{name, role, desc, photo}]`, 2–6 |
| `quote` | `(text, source=None, title=None)` | 金句页 |
| `references` | `(title='参考文献', refs=(), size=None, numbered=True)` | GB/T 7714 strings; 2 columns when > 8; `numbered=False` keeps a paper's own “[13] …” numbering |

---

## D. Chart and table specs

**Chart spec** (dict passed as `chart=` to `chart_page`, or as `'chart'` inside a `panels` item; same keys as
`pptstudio.charts.chart`):

```python
{'kind': 'column',            # column | bar | stacked | stacked_bar | stacked100 | line | line_plain | area |
                              # pie | donut | scatter | radar
 'categories': ['2021', '2022', '2023'],
 'series': {'调水量(亿m³)': [494, 586, 670]},   # dict (ordered) or [(name, values), ...]; scatter: [(name, [(x, y)])]
 'highlight': -1,             # index/list of key categories -> main color; others pale (single-series bar/pie)
 'number_format': '0.0',      # data label format ('0', '0.0', '0%', '#,##0')
 'colors': ['primary_deep', 'emph'],  # optional series colors (roles or hex)
 'legend': True, 'gridlines': False, 'value_axis': False, 'gradient': True,
 'gap': 70, 'hole': 62, 'show_percent': True, 'max_value': None, 'min_value': None, 'font_size': 11}
```

Charts are native PowerPoint charts (editable data). Pie/donut default to percentage labels. Bar charts list
the first category on top.

**Table** (`table_page` or `panels` item `'table'`): `columns` = header labels; `rows` = list of lists of strings
(markup allowed). Column widths follow content length unless `col_widths=[2, 1, 1]`. Header row uses the main
color with white bold text; zebra rows use a very light tint; `highlight_col` tints a key column
(`highlight_mode='raised'` puts a gradient card with shadow behind it); `highlight_rows=[i]` tints data rows.
