# Design rules (distilled)

Sources: public PPT tutorial / redesign articles, ≈3,000 designer and redesign slides
(designer collections and public redesign cases), 21 NSFC/科技奖 defense samples and 86 finished
decks of 国家科技奖 / 重点研发 / 人才计划 / 重点实验室 templates (§14).

Contents: 1 Principles · 2 Content processing · 3 Emphasis · 4 Color · 5 Typography · 6 Layout types ·
7 Page types · 8 Images · 9 Charts & tables · 10 Quantitative defaults · 11 Amateur signals ·
12 Research / defense rules from the 2024–2026 article review · 13 Visual patterns & parameters from the image review ·
14 Template families from the finished-deck review (新参考)

---

## 1. Principles (what every page must satisfy)

| Principle | Rule | How the library enforces it |
|---|---|---|
| 对齐 Alignment | Nothing is placed by eye: left edges, tops and bottoms line up; equal gaps (distribute) | `Box.cols/rows/grid`, all layouts compute positions |
| 分组 Proximity | Related text sits in one container (color block, frame, or whitespace); unrelated items are far apart | panels, cards, ribbons |
| 对比 Contrast | Size, weight, color, font contrast create hierarchy; “没有层次感” = not enough contrast | type scale, red/primary emphasis, big numbers |
| 重复 Repetition | Same title bar, colors, fonts, icon style on every page | theme + chrome on `d.page()` |
| 留白 Whitespace | Never touch the slide edge; line spacing 1.2–1.3 (body) and paragraph gap > line gap | margins, `ls`, `sa` |
| 平衡 Balance | Visual weight balanced left/right (image right → text left; title top-left → info bottom-left) | layouts split by weights |
| 修饰 Decoration | Meaningless-but-harmonious elements (faint English watermark, corner shapes, dots) only to balance, never to fill | `watermark`, `glow_orb`, `dot_map`, corner triangles |


## 2. Content processing (do this before choosing a layout)

1. **划分内容结构** — read everything, find 2–5 groups and their relation (parallel, progressive, contrast,
   one-to-many, cause–effect). The relation picks the layout (§6).
2. **梳理内容细节** — “长文变短句，短句变词汇”: extract a 4–10 char subheading per group, cut sentences to ≤ 28
   chars, pull numbers out, make the key word bold/red. Delete repetition (a column of “研究…” becomes the
   table header).
3. **丰富视觉效果** — add the visual that carries meaning: figure, native chart (numbers), table (repeated
   fields), flow (sequence), icons (short points), photo (context).

Conversions that almost always improve a page:
- paragraph with 3+ numbers → stats row or bar chart; a percentage → donut/ring; shares summing to 100 % → one pie;
- items sharing the same fields (time/length/cost) → table;
- steps → flow/chevron; years → timeline; “A vs B” → comparison columns (not a bare “VS”);
- uneven text amounts → container sizes proportional to content, or a surround (hub) layout.

## 3. Emphasis

- Don't paint random words red. Emphasis = extract the phrase into a heading/label/number, then contrast it
  (size, weight, color, container).
- Defense style *does* use red keywords — the NSFC convention — but only 2–4 short phrases per page, never
  whole sentences, and always the words a reviewer must remember.
- Tables: emphasize a column with a tinted/raised block behind it, not red text everywhere.
- Data up/down: small ▲▼ triangles (red up / green down in CN convention) beside the number.

## 4. Color

- One main hue + black/white/gray; a second hue only if you control it (safe pairs: navy+red emphasis,
  blue+orange accent, teal+yellow). Never red+green, never 5 colors on a page.
- The main color is for titles, headers, accents — not large areas; body text stays dark gray (`1F1F1F`–`404040`).
- Derive colors from the client/school logo (清华紫 `660874`, 北大红, 企业标准色).
- Light backgrounds should not be flat white everywhere: faint gradient (same hue at 90–95 % brightness),
  pale panels, or a very light texture; shadows tinted with the main color, soft (≈ 85–90 % transparency,
  20–26 pt blur, small distance). Black default shadows look dirty.
- Dark backgrounds: containers only slightly lighter than the background; bright accent only on key info;
  glow = gradient strokes and radial orbs.
- Gradients: adjacent hues only (blue→cyan), never wide-span rainbow gradients.
- Masks over photos: vivid/dark photo → dark or colored mask; white mask only on light photos (or desaturate
  first).

## 5. Typography

- ≤ 2 CJK families + 1 number/Latin font per deck. Body in a sans (思源黑体/Noto Sans SC, HarmonyOS Sans,
  阿里巴巴普惠体, OPPO Sans, MiSans); serif (思源宋体) for formal titles; calligraphy only for 1–2 display words.
- Weight contrast: headings Bold/Black, body Regular, statements Medium.
- Measured on 2,987 designer slides: body 14–18 pt (mode 16), content titles 28–32 pt, hero numbers 54–96 pt,
  covers up to 166 pt; 微软雅黑 appears in only 0.4 % of characters — prefer the free commercial families above
  (微软雅黑 has commercial-use restrictions; `portable=True` still uses it for maximum compatibility).
- Line spacing 1.2–1.5 for paragraphs; paragraph spacing ≈ 0.5 em (> line gap); justify multi-line CJK text.
- Numbers: a font whose digits align with CJK height (Bahnschrift, OPPO Sans, DIN); unit at ~45 % size.

## 6. Layout types (pick by content structure)

| Type | Use when | Library |
|---|---|---|
| 左右 (text/figure) | one idea + one visual | `figure_text`, `text_image`, `panels(2)` |
| 上下 | wide figure/chart + short explanation | `panels` with `image_h`, `chart_page` |
| 卡片/并列 | 2–6 equal items | `panels`, `cards` |
| 拦腰 | one summary + several details | `band`, `panels` with conclusion bar |
| 分割 | 2–4 blocks of different weight / progression | `split`, `columns`, `panels(weights=)` |
| 环绕 | a core concept + 3–8 keyword satellites (keywords, not paragraphs; odd or even counts) | `hub` |
| 错落/扇形 | many short items where rigid grids look stiff | custom page (`poly`, `cards` staggered agenda) |
| 表格化 | repeated fields | `table_page`, `mini_table` |
| 层级 | architecture / system levels | `layers`, `pyramid` |

## 7. Page types

- **Cover** = copy + image + layout. Break the title into meaningful lines; add a level (theme phrase /
  English / presenter / unit); 3 layouts: left-aligned, centered, split. Images with natural empty space, or a
  mask/fade; defense covers use a navy band and serif title.
- **Agenda** 3–6 items; numbered pills/cards; academic decks re-use the agenda as section dividers with the
  current chapter highlighted (NSFC convention).
- **Section** big number + title + English, or agenda-with-highlight.
- **Ending** just “谢谢” in strong typography (default convention for every deck); a closing quote, contact/QR
  or Q&A only when asked.
- **Navigation bars** (top tabs or left sidebar) for long academic decks: #tabs = #chapters, current one
  highlighted.
- **Comparison**: parallel blocks sized by content, shared parameters in a middle column, or central symmetry
  — not a bare “VS”.
- **Timeline**: thin line or curve, not fat arrows; key stage larger/colored; earlier stages lighter.
- **Architecture diagrams**: fewer outlines, light fills, consistent boxes, highlight 1 path.

## 8. Images

- Four rules: no watermark, no distortion, relevant to the topic, legally usable.
- Crop images in one row to identical size and ratio; align and equalize gaps.
- Treatments available in `pptstudio.images`: `cover_crop` (focus crop), `fade` (gradient transparency to blend
  into the page), `duotone`/`tint` (unify colors with the theme), `desaturate`, `blur`, `line_art`
  (building line drawing at low opacity, e.g. university gate on the cover), `diffuse` (soft color-blob
  backgrounds), `dot_map`, `tech_bg`, `gradient_png`.
- Screenshots → put them on a frame/card (or phone/laptop mockup) instead of floating raw.
- Scientific figures: never recolor, never stretch (`fit='contain'`), keep white background on a white card.

## 9. Charts & tables

- Charts: title states the conclusion; remove gridlines/axis clutter; data labels on; main color for the key
  series/bar, light gray/pale for the rest; merge pies that sum to 100 %; donut rings for single % values
.
- Multi-chart pages: pair each chart with its sentence as one module; unify module style.
- Tables: header in main color + white bold; zebra rows in a very light tint; or academic three-line table
  (thick top/bottom rules, thin header rule, no verticals); highlight a key column with a raised block;
  uniform row height; center numbers.

## 10. Quantitative defaults (from 2,987 designer slides)

| Metric | Value |
|---|---|
| Body size (per-slide dominant) | 14 pt 23 % · 16 pt 22 % · 18 pt 14 % · 12 pt 9 % |
| Title size (per-slide max) | 28 pt 20 % · 32 pt 17 % · 30 pt 12 % · 36 pt 8 % |
| Title position (content pages) | x ≈ 1.9 cm (median), y ≈ 1.3 cm; median title length 9 chars |
| Text colors | black/white + dark grays 404040 / 262626 / 595959 |
| Line widths | 1 pt (47 %), 0.75 pt (17 %), 0.5 pt (10 %) |
| Alignment | left 57 %, center 36 % |
| Shapes | freeform/icons 39 %, rect 27 %, ellipse 11 %, rounded rect 10.5 %, line 7 % |
| Pictures per slide | 1 (25 %), 2 (17 %), 0 (17 %), 3 (10 %) |

## 11. Amateur signals (“五大乱” and friends) — check before delivering

排版凌乱 (misalignment, unequal gaps) · 配色脏乱 (dark text on dark bg, too many colors, black shadows, default
blue-gray tables) · 字体杂乱 (3+ families, artsy fonts for body) · 素材错乱 (unrelated stock photos, mixed
illustration + photo styles, low-res images) · 风格混乱 (one page in a different style) · walls of text ·
text below 12 pt · SmartArt defaults · big arrows · red text everywhere.

## 12. Research / defense rules from the 2024–2026 article review

About 140 research-related tutorial articles were read in full. Rules that matter for 科研答辩风 decks:

| Rule | Detail |
|---|---|
| 论文是“读”的，PPT是“看”的 | each page: one finding + its evidence; numbers → cards, process → modules + arrows, comparisons → cards with ours highlighted, history → timeline |
| 结论先行 | the statement bar carries the conclusion; details follow; AI-style “everything copied from the paper” pages fail |
| 规范先行 | one main color from the school/logo + black/white/gray (+ ≤1 accent); white background for projectors; 2 font families (标题宋/黑 + 正文黑) |
| 色彩指向 | same color = same kind of module/method across the deck; architecture diagrams with 3 colors (title color, dark gray, light gray) |
| 主次对比 | parallel items: equal brightness; main vs. secondary: color vs. gray or dark vs. light |
| 大段文字 | sans-serif, no first-line indent, justified, line spacing 1.2–1.5, paragraph gap > line gap, line length ≤ ½ page |
| 结构化排版 | 1+N → 拦腰 (band across the middle); several blocks → 分栏 (columns, emptier column darker); cards with inner padding |
| 表格 | three-line or shaded header, no vertical rules, key column/row tinted in the header's hue, text left / numbers right; numeric tables → charts; text tables with few rows → cards |
| 图表 | separate the chart from text, remove gridlines/borders/legend boxes, one hue + gray, highlight the key bar |
| 逻辑图 | 点线面 contrast for simple diagrams; hierarchy dark → light, lines weakened; multi-dimensional processes as an arrow + rectangle matrix |
| 截图 / 原图 | unify sizes, thin frame; emphasize a region by an enlarged crop, not only a red box |
| 导航与过渡 | chapter navigation shows progress in long academic decks; dividers with a big chapter number |
| 封面 | logo + title + presenter as three levels; theme picture under a translucent mask, or a theme motif (water → wave curves) |

## 13. Visual patterns & parameters from the image review

About 1,700 before → after images from those articles were reviewed. Recurring patterns, ranked by
frequency, and the parameters the redesigns use (implemented as the `B2` layouts in `layout-catalog.md`):

| Pattern | Parameters / rules |
|---|---|
| 拦腰 band + overlapping cards | band ≈ 35–45 % of the content height, full bleed, deep→primary gradient, white text with 1–2 yellow keywords; cards overlap the band edge by 0.4–0.6 in; card shadow tinted, ~85–90 % transparent, large blur; inner padding ≥ 0.15 in |
| 3-level architecture | solid (level 1: labels, banner) → pale (level 2: rows) → white + thin border (level 3: chips); no nested outline frames; side columns for cross-cutting systems; one type scale per level |
| Formula card | header + one-line meaning + formula centred + symbol legend strip (symbol over meaning, thin rules) — never a paragraph of “式中 …” |
| Ours vs others | ours: deep header, badge, ✓ rows, values in the accent color, shadow; others: gray header and gray values; VS badge; same row labels aligned |
| Process matrix | chevron header deepening left→right, phase brackets above, white cells on a pale grid, dashed arrows, short notes row, conclusion bar |
| Closed loop | 3–6 arrow segments, labels along the ring, centre disc; details in blocks around, numbered in ring order |
| 国内外研究现状 | horizontal bands with a big faded word (国外 / 国内) + columns; end with the research gap |
| Number grid / bars | label small & gray above a big value; bars with pale track, value at the end, one highlighted bar |
| Color weight | saturated fills only on small areas (labels, header strips, highlights ≈ ≤ 25 % of the content area); big areas white or pale; ratio white/pale > main > accent |
| Water motif | layered wave shapes on the cover band edge for 水利 / 流域 / 海洋 topics |
| Chapter navigation | chips at the top (title bar), left, or bottom; current chapter solid |

## 14. Template families from the finished-deck review (新参考, 2026-10-02)

86 finished decks / page sets (国家科技进步奖, 国家科学技术奖, 国家重点研发计划 项目 + 申报书, 长江学者, 全国重点实验室,
万人计划青年拔尖, 国自然青年学生项目, 科研架构图 hub diagrams) were reviewed page by page. They turned into 7 skins
(`jinbu kexue zhongdian changjiang lab wanren shenbao`), 5 covers, 2 agendas, 2 endings and the `B3` layouts.

| Pattern | Families | Rules / parameters |
|---|---|---|
| Title bar = the family's signature | all | one style per deck: full-width band (科技进步奖 bright #1170C6, 重点研发 deep #0A4FA0 + faded topic photo at the right end) or a mark + navy title + full rule (numbox 长江, two-tone square 实验室, ╱╱ 科学技术奖, half-disc 申报书, plain bold + rule 万人); number in Bahnschrift, logo right |
| Cover hierarchy | all covers | logo / 年度 line (13–16 pt) → title (serif bold 54–66 pt, ≤ 2 lines) → subtitle (serif 22–30 pt, letter-spaced 2–3) → presenter pill (often straddling a band edge) → 单位 lines (12–15 pt bold, units in 2 rows split by “|” or an aligned grid) → date; nothing else |
| Band-carried titles | 科学技术奖, 万人, 重点研发 | the title sits in a full-width blue band (white serif) or a navy block with a bowed lower edge; faint city / sea skyline inside the band at ≤ 15 % opacity |
| Statement strips | 科学技术奖, 科技进步奖 | “◆ red key phrase ▸ navy explanation” on a pale band, or a white box with a thin navy border — one per page, ≤ 2 lines |
| Risk pages | 万人, 申报书 | each risk = name + one-line summary + 负面影响 + level + 涉及课题 (every risk maps to a 课题); traffic-light colors only on small chips (低 72AE48 · 中 EE7F32 · 高 BF0202), everything else navy/gray; 4 risks in 2×2 or 6 in 2×3; close with a 防控 strategy bar |
| 预期成果 | 万人, 申报书 | centre figure card + numbered outline pills (left 01–02, right 03–04), quantified outputs, figure row, one conclusion bar; or award photos + application table |
| 课题分解 | 重点研发 | 2×2 课题 panels (red 课题k + navy title + figure); the relations are written on the arrows (认知 / 感知, 协同认知, 条件支撑, 迭代优化闭环); outer brackets for “提供输入 / 依赖反馈”; integration banner on top; conclusion bar “覆盖…全链条” |
| People pages | 重点研发, 长江, 万人 | ID photos cropped identically with a navy name band; roles in red under the photo; team stats as red numbers (total, ≤ 40 岁); roster tables with key people in red; leader = photo + honour strip (first honour yellow) + achievements with red counts + laurel badges for the top awards. Use real photos supplied by the user only; silhouettes as placeholders |
| 背景四卡 → 科学机遇 | 长江 | four perspectives (科学挑战 / 国家需求 / 国际竞争 / 技术发展): tab + image with a caption ribbon + colored heading + bold sub + gray note; chevrons between; a V funnel to “科学机遇” and a red conclusion |
| 发展历程 | 重点实验室 | year pills on a light→navy arrow, key events red, ★ for importance, photos of equal size, pale conclusion band |
| 获奖 | 重点研发 | banner with counts (yellow numbers), minimal table with key rows red, certificate photos on a shelf (equal height, soft shadow) |
| 科研架构图 (hub) | 佑泽学长 / 科研绘图 | centre keyword in a hexagon; 4 ring nodes on a dashed circle, each with 2 sub bubbles; an acrostic of 4 characters on the diagonals; curved red phrases with arc arrows; near side columns of circles, far side columns of dashed boxes with headers; bottom chain of cans pointing at the highlighted middle; 2 colors only (teal 1E6B7F + maroon A0323C, or navy + red) + white |
| Color families | all | bright royal (1170C6 / 1369C1 / 1D5CA6) for 奖励 decks, deep navy (013E87 / 0A36A2 / 0A4FA0) for 人才 / 实验室 / 重点研发; red C00000-ish only for keywords and the current item |
