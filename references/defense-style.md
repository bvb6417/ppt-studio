# 科研答辩风 (defense style) — visual spec & page recipes

The default style of this skill. Distilled from NSFC (国自然) / 省科学技术奖 / 国自然青年学生项目 / 毕业答辩
reference decks (像素答辩、树叶答辩、百宝箱 samples) and the EasySlides academic template library
(国自然-深蓝/亮蓝白/深蓝白/白蓝/绿/红/紫、毕业答辩上导航/左导航、开题答辩), extended on 2026-10-02 with 86 finished
decks of 国家科技进步奖 / 国家科学技术奖 / 国家重点研发计划 (项目 + 申报) / 长江学者 / 全国重点实验室 / 万人计划 and
科研架构图 hub diagrams (design-rules §14). Reviewers read these pages
at a glance: **dense but orderly, every page = one numbered claim + evidence (figure/data) + red keywords.**

Contents: 1 Visual system · 2 Building blocks · 3 Page recipes · 4 Copywriting · 5 Variants · 6 Don'ts

---

## 1. Visual system

| Item | Spec (theme `nsfc_blue`) | Library |
|---|---|---|
| Canvas | 16:9, 13.333×7.5 in, white; faint panel-blue fade on the lower half + pale corner triangle | `academic.background` |
| Margins | 0.42 in sides (title rules run 0.42 → 12.91 in); content from y≈1.2 in to 6.94 in | `deck.page()` |
| Title bar | y 0.28 in, height 0.62 in: slanted double mark · section number (Bahnschrift bold) · thin divider · title 26 pt bold deep navy; 2.5 pt primary rule under it; logo at right | `academic.title_bar` (`style=` from the skin: `slant|bars|underline|band|badge|center|tab|lightband|vband|photoband|numbox|square|thin|halfdisc|slash`) |
| Bottom | 2.5 pt primary rule at y 7.24 in; page number right above it; optional source line left | `academic.bottom_rule` |
| Colors | primary `124CAD` (headers, ribbons) · deep `033E9C` (titles, conclusion bars) · panel `F0F3F8` + border `C5D3EA` 0.75 pt · emphasis red `C00000` · yellow `F8D008` (only on navy bars) · body `1F1F1F` | theme roles `primary`, `primary_deep`, `panel`, `panel_line`, `emph`, `yellow`, `text` |
| Type scale | title 26 · statement 16 · panel header 16 · body 15 · caption 11.5 bold navy · big numbers 28–40 red · min 10.5 (tables) | theme `size_*` |
| Fonts | 思源黑体/Noto Sans SC (Bold for heads, Medium for statements, Regular body) · 思源宋体/Noto Serif SC Bold for cover titles & yellow conclusion bars · Bahnschrift SemiBold for numbers | `role='title'|'medium'|'body'|'serif'|'number'` |
| Bullets | ➢ (Wingdings `Ø`) in primary color, hanging indent, 0.45 em paragraph gap, line spacing 1.12 | `academic.arrow_list` |
| Gaps | 0.12–0.2 in between panels; panels fill the content area edge to edge | layouts |

Density target: 60–75 % of the content area covered by panels/figures; 60–180 CJK characters of body text per
page; at least one visual (figure, chart, table, diagram, flow) on every content page.

## 2. Building blocks (all in `pptstudio.academic`)

| Block | Looks like | Call |
|---|---|---|
| Statement bar | light gradient strip, 0.07 in navy left bar, one sentence with red keywords | `statement(cv, x, y, w, text, style='bar')` |
| Labeled statement | navy chevron label “核心阐述” + sentence | `statement(..., style='label', label='核心阐述')` |
| Centered statement | ▪▪▪ 科学目标：… ▪▪▪ | `statement(..., style='centered')` |
| Pink statement | pale-red box, red text (warnings, 痛点) | `statement(..., style='pink')` |
| Key-phrase strip | pale band: red ◆ + red key phrase ▸ navy rest (科学技术奖) | `statement(..., style='key')` (key = text before the first ：/，, or `label=`) |
| Boxed statement | white box, thin navy border, soft shadow (科技进步奖 / 重点研发) | `statement(..., style='box')` |
| Panel with ribbon | light panel, navy ribbon header centered on the top edge | `panel(cv, box, header='…')` → inner Box |
| Panel with strip | full-width navy header strip | `panel(cv, box, header='…', header_style='strip')` |
| Ribbon / tag | navy rectangle label; chevron tag “算法\n算力”; red tag “问题一”; light tag | `ribbon(...)`, `tag(..., style='navy'|'chevron'|'red'|'light'|'pill'|'outline')` |
| Vertical label | navy bar with stacked characters “教育经历” | `vlabel(...)` |
| Question marker | red “问题一” + ›› chevrons | `red_marker(...)` |
| Figure frame | thin frame + caption band in navy bold; placeholder when no image | `figure(cv, box, image, caption)` |
| Flow chain | nodes joined by ›› (light→navy progression) | `flow_chain(cv, box, nodes, style='grad'|'box'|'light')` |
| Mini table | navy header, zebra rows, first column bold, `emph_cols` red | `mini_table(cv, box, columns, rows)` |
| Stat | big red number + small unit + label | `stat(cv, box, value, unit, label)` |
| Conclusion bar | full-width navy bar; white bold or yellow serif text | `conclusion(cv, text, y, style='navy'|'yellow'|'red'|'light')` |
| Axis | light→navy gradient arrow with white nodes | `axis(cv, x, y, w, nodes)` |
| Block arrow | gradient thick arrow (up/down/left/right/lr) | `block_arrow(...)` |
| Brace, number square, icon badge | `{` connectors, navy “01” squares, navy circle icons | `brace`, `num_square`, `icon_badge_ac` |
| Risk level chip | “级别高” grey chip with the level word colored (低 green · 中 orange · 高 red) or a filled chip | `level_chip(cv, x, y, w, h, '高', style='soft'|'fill')`, `chip(...)` |
| Person card | photo (or drawn ID-photo silhouette) + navy name band + red role caption | `person(cv, box, name, role, photo)`, `silhouette(...)` |
| Laurel award badge | two laurel branches, award name navy, grade red, ★★★ | `laurel(cv, cx, cy, w, h, '国家科技进步奖', '一等奖')` |
| Certificate | framed certificate photo, or a drawn placeholder (gold frame, title, lines, red seal) | `certificate(cv, box, image=None, title='荣誉证书')` |
| Metric box | dashed box: label + big red value (+ ↑/↓) “复杂场景决策准确率降低 25.6%” | `metric_box(cv, box, label, value, unit, arrow)` |
| Convergence | two side statements funnel (V) into a red keyword and a red conclusion (科学机遇) | `converge(cv, box, left, right, center, conclusion)` |
| Vertical chain | bordered column, navy header, light boxes joined by ▼ | `vchain(cv, box, items, header, highlight)` |
| Hub parts | ring node with sub bubbles, curved red phrases, 3-D cans | `hub_node`, `arc_text`, `cylinder` |

Emphasis markup inside any text: `[[关键词]]` → bold red (theme `emph`); `**粗体**` → bold.

## 3. Page recipes (what each typical page contains)

Numbering: `d.section(i)` starts chapter *i*; every following `d.<layout>(...)` title is auto-numbered
`i.1, i.2 …` (override with `num='2.5'` or suppress with `num=False`).

| Page (typical title) | Layout call | Ingredients |
|---|---|---|
| 封面 | `cover(variant='band')` | project line (指南方向/项目类别/会议) · 2-line serif title · “汇报人：XXX” pill · 申报单位/所在实验室 on white |
| 科技奖封面 | `cover(variant='award', title='XX省科学技术奖', subtitle='项目名称')` | completers line (`meta(completers=…)`), units on bottom navy band (`meta(units=[…])`) |
| 汇报提纲 | `agenda()` | vertical serif “汇报提纲” block + numbered pill rows |
| 章节过渡 | `section(i)` | the agenda again, current chapter red (NSFC convention) |
| 国家重大需求 / 立项背景 | `panels(statement=…, panels=[2 panels with chart/figure + points], conclusion=…, conclusion_style='yellow')` | numbers from authoritative sources, `source=` footnote |
| 卡脖子问题 / 研究现状不足 | `columns(statement, cols=[4], bottom=[2 rows])` | 4 navy headers → light cards (subtitle + ➢ points) → gradient axis → 2 chevron-tag rows |
| 关键科学问题 / 研究问题 | `problems(items=[问题一, 问题二 …])` | red markers, question sentence, figure + “研究目标/研究重点” points |
| 研究目标与内容 | `panels(... 'flow': [...])` or `layers(levels, side)` | goal statement + 3 research contents |
| 技术路线 / 研究思路 | `route(target, top, questions, topics, left_image, right_image)` | 科学目标 line · top goal box · ↑ arrow · questions ↔ braces ↔ topics |
| 研究方案 / 核心方法 | `figure_text(image, blocks=[…], statement='…')` | big figure left, 3 chevron-tag blocks right, “核心阐述” statement |
| 特色与创新 | `innovations(items=[理论/方法/应用], subtitle, footer)` | numbered rows, navy tab labels, red keywords |
| 研究基础 / 前期成果 | `achievements(stats, images, headline)` | paper/certificate thumbnails + red stats row |
| 研究计划 / 进度安排 | `schedule(periods, sub_periods, tasks)` (+ `table_page` for expected results) | Gantt bars per research content |
| 个人基本情况 (青年/博士生项目) | `profile(name, groups, direction, conclusion)` | photo card, vertical labels 教育经历/成果列表, red roles |
| 支撑条件 / 平台 | `panels([{'header': '依托平台', 'image': …, 'tags': [...]}, …])` | lab photos, equipment table (`'table': {...}`) |
| 应用推广 / 经济社会效益 | `panels([{'stats': [...]}, {'table': {...}}], conclusion=…)` | red numbers, benefit table |
| 发展历程 / 里程碑 | `milestones(events, stats)` | stats row + alternating event boxes |
| 研究目标与研究内容 (1+N) | `band_cards(headline, text, kpis, cards)` | 拦腰 band with the goal + KPIs, content cards overlapping it |
| 国内外研究现状 | `bands(bands=[国外, 国内], conclusion='不足：…')` | faded big words, deep/pale bands, research gap bar |
| 技术路线（矩阵式） | `process_matrix(steps, rows, cells, phases, arrows)` | phases → chevrons → cells → notes |
| 总体架构 / 平台架构 | `architecture(tiers, top, sides)` | label tabs, pale rows, white chips, side systems |
| 课题分解 | `tree(root, children)` | root → 课题 → 任务 |
| 与已有方法对比 | `versus(ours, others)` | highlighted ours, gray others, VS |
| 闭环 / 运行机制 | `cycle(steps, center)` | ring + numbered blocks |
| 科技进步奖封面 | `cover(variant='plaque')` | logo + 年度 line, huge blue serif title, spaced subtitle, presenter pill on a bottom band with `meta(units=[…], date=…)` |
| 科学技术奖 / 万人计划封面 | `cover(variant='midband')` | logo or caption between rules, full-width blue band with the white serif title, pill (`extras['cover_pill']='outline'` for 万人), 牵头/依托单位, units grid |
| 重点研发封面 | `cover(variant='arc')` | navy block with a bowed lower edge, caption between rules, pill on the arc, units below |
| 人才计划封面 (长江学者 / 青年拔尖) | `cover(variant='tag')` | white card, navy tag (方向 / 依托项目), chevron subtitle band, split pill 汇报人｜姓名, bottom swoosh |
| 重点实验室封面 | `cover(variant='lab', presenter='实验室主任：X')` | navy pill (年度评审), lab name between rules (`meta(lab=…)`), » 主任 « band, 依托 / 联合单位 |
| 汇报目录（重点研发） | `agenda(variant='corner')` / `agenda(variant='band')` | white card with diagonal corner sashes + vertical serif 汇报目录 / navy band + numbered cards |
| 风险分析 | `risks(risks, variant='cards'|'tabs'|'rows')` | per risk: name, summary, 负面影响, level chip (低/中/高 colors), 涉及课题, (应对措施) |
| 预期成果 | `outcomes(items, center, figures, conclusion)` | navy centre card with a figure, numbered outline pills left/right, figure row, conclusion bar |
| 课题分解（关联图） | `topics(topics, banner, links, side_left, side_right)` | 2×2 课题 panels (red 课题k + title + figure), labeled arrows between them, bracket labels |
| 实验室 / 团队人员构成 | `lab_team(stats, headline, leader, members, columns, rows, highlight_rows)` | red stat numbers with pill labels, leader card, photo row, roster table (key rows red) |
| 项目负责人 | `leader(name, photo, honors, points, awards, groups)` | photo + navy name band, honour strip, ➢ achievements, laurel badges, sub-team photo groups |
| 研究背景（四卡 + 机遇） | `need_cards(cards, converge, statement)` | 科学挑战 / 国家需求 / 国际竞争 / 技术发展 tab cards with image captions, chevrons, V-convergence |
| 研究框架（科研架构图） | `framework(center, ring, accents, arcs, left, right, bottom, banner, palette='teal')` | centre hexagon, 4 ring nodes, accent dots, curved red phrases, side circles + dashed boxes, bottom cans |
| 发展历程 | `history(events, banner, subtitle)` | year pills on a gradient arrow, titles (key ones red), ★ ratings, photos |
| 科研团队获奖 | `awards(columns, rows, banner, highlight_rows, certificates)` | navy banner with yellow counts, award table, certificate shelf |
| 结束页 | `ending()` | just “谢谢” (large serif, small ornament) — nothing else unless asked; `variant='band'|'sky'|'split'|'plaque'|'midband'` |

## 4. Copywriting conventions (they are part of the style)

- Titles are nouns/short phrases (≤ 16 CJK chars): 国家重大需求 · 卡脖子问题 · 研究热点 · 目标解决 · 技术路线 ·
  创新点 · 研究进度及预期成果 · 应用推广 · 经济社会效益.
- Statement bar = the page's claim (≤ 45 chars): “首当其冲的是[[“感知之困”]]：……”, “总体目标：构建三大核心能力，
  实现从[[“0”到“1”]]的系统性突破”.
- Panel headers are 4–10 char noun phrases; points are ≤ 28 chars, start with the key term, 2–4 per panel.
- Conclusion bar (≤ 30 chars) closes the argument: “构成了从底层材料创新到顶层应用服务的完整技术闭环”.
- Red keywords: 2–4 per page, only the words a reviewer must remember (numbers, “首次”, “卡脖子”, method names).
- Numbers: value big + unit small (“80篇”, “1000次”, “±10 m”); always say what and when (“截至2026年8月”).
- Every data page gets `source='资料来源：…'`; schematic figures get “（示意）”.

## 5. Variants

- **Style family (skin)** — `Deck(theme, skin=...)` switches the whole page chrome (title bar, panel headers,
  cover, agenda, background, footer, ending) to one of the template families found in real decks; colors stay
  the theme's, so every skin works with every color. Look at `assets/gallery/style_<skin>.jpg` (same 9-page
  sample talk in each skin) and pick one per deck:

  | skin | Source family | Title bar | Panel header | Cover | Agenda | Footer | Fits |
  |---|---|---|---|---|---|---|---|
  | `pixel` | 像素答辩 (国自然 / 省科技奖) | slanted marks + number + rule | navy ribbon | navy band | vertical | rule | default, any 基金/奖励答辩 |
  | `leaf` | 树叶答辩 (国自然青年学生 / 博士项目) | bars mark + double rule | rounded pill | navy band | vertical | rule | 青年/学生项目, 博士答辩 |
  | `baibao` | 百宝箱 (国自然基金答辩) | number + title, gradient underline | trapezoid tab | light sky | split | rule | 面上/青年基金, 学术报告 |
  | `bright` | EasySlides 亮蓝白 | full-width bright gradient band | full-width strip | slanted block, left title | white card | none | 申请/结题汇报, 推介 |
  | `badge` | EasySlides 深蓝白 | navy band + round number badge | full-width strip | 科技奖 award | white card | navy strip | 科技奖, 项目论证 |
  | `center` | EasySlides 红色 / 酒红 | centered title with side rules | navy ribbon | navy band | vertical | rule | 红色主题, 党政/医学 |
  | `tab` | EasySlides 绿色 | colored arrow tab | left tab | light sky | white card | rule | 农林生态, 绿色主题 |
  | `tech` | EasySlides 重点研发 | light band + bar mark | navy ribbon | circuit tech background | split | navy strip | 重点研发, 工程技术 |
  | `jinbu` | 国家科技进步奖 | bright full-width band, white “▏1.1 title” | full-width strip | plaque (huge blue serif title, units band + date) | vertical | none | 科技进步奖 / 省科技奖 |
  | `kexue` | 国家科学技术奖 (波浪能…) | “╱╱ 1.1 title” + thin rule | “— title —” on white cards | midband (blue band holding the title, units grid) | band (navy band + numbered cards) | rule | 科学技术奖, 技术发明奖 |
  | `zhongdian` | 国家重点研发计划 (深海…) | deep band + faded topic image at the right | strip fading right | arc (bowed navy block, pill on the arc) | corner (diagonal sashes) | none | 重点研发 项目答辩 / 中期 |
  | `changjiang` | 长江学者 / 人才计划 | navy number box ▸ title + full rule | trapezoid tab | tag (white card, navy tag, split pill, swoosh) | card | rule | 长江学者, 杰青 / 优青, 人才答辩 |
  | `lab` | 全国重点实验室 (树叶) | two-tone square mark + navy title + rule | pale strip, navy text | lab (navy pill, lab name between rules, » 主任 «) | split | rule | 重点实验室 组建 / 评估, 平台汇报 |
  | `wanren` | 万人计划青年拔尖 | plain bold title + full blue rule | full-width strip | midband with outline pill, plain texture | vertical | none | 青年拔尖, 人才项目 |
  | `shenbao` | 国家重点研发 申报 (NO.483) | half-disc mark + title, darker rule under the title | navy strip with a notch | navy band | corner | none | 申报书答辩, 指南方向论证 |

  Suggested colors per skin (`theme.SKIN_THEMES`): pixel `nsfc_blue`, leaf/badge `nsfc_navy`, baibao `water_nsfc`,
  bright `bright_blue`, center `nsfc_red`, tab `nsfc_green`, tech `nsfc_blue`, jinbu/kexue `royal_blue` (#1170C6),
  zhongdian `deep_blue` (#0A4FA0), changjiang `navy_deep` (#013E87), lab `cobalt` (#0A36A2), wanren `steel_blue`
  (#1D5CA6), shenbao `nsfc_blue`.
- **Theme color**: `nsfc_blue` (像素答辩 blue) · `nsfc_navy` (deep, bars mark) · `bright_blue` (full-width title band)
  · `nsfc_red` · `nsfc_green` · `nsfc_purple` · `burgundy` (毕业答辩 酒红) · any school color:
  `Deck('#660874', style='defense', skin='leaf')`.
- **Single elements**: override one part of a skin with `extras`, e.g. `Deck('nsfc_blue', skin='pixel',
  extras={'title_bar': 'bars'})`; title bars `slant|bars|underline|band|badge|center|tab|lightband|vband|photoband|
  numbox|square|thin|halfdisc|slash`, panel headers `ribbon|strip|tab|pill|trap|fade|pale|dash|notch`, covers
  `band|sky|award|left|tech|plaque|midband|arc|tag|lab`, agendas `vertical|split|card|corner|band`, statements
  `bar|label|centered|pink|key|box`, background deco `corner|arcs|dots|none`, footers `rule|band|none`, endings
  `band|sky|split|plaque|midband`; extra keys `band_image` (photo for photoband / arc / midband bands),
  `cover_pill` (`navy|solid|outline|ghost`), `cover_texture` (`hex|plain`).
- **Navigation** (long 毕业/开题答辩 decks): `Deck('nsfc_blue', nav='top')` → navy tab bar with current chapter
  highlighted; `nav='left'` → light sidebar with navy current item. Titles then use a compact underline style.
- **Agenda**: `agenda(variant='split')` → navy left panel “目录 CONTENTS” + numbered list (EasySlides 开题 style).
- **Ending**: `ending()` = “谢谢” only (default convention). Add subtitle / presenter / info lines only when the
  user asks (`ending(subtitle=..., presenter=True, info=[...])`).

## 6. Don'ts (what makes this style look amateur)

- Pastel gradients, big empty areas, decorative stock photos unrelated to the science.
- Recoloring or redrawing authors' scientific figures; stretching figures (use `fit='contain'`).
- More than one conclusion bar per page, red on more than ~4 phrases, whole sentences in red.
- Mixing title-bar styles or theme colors between pages.
- Text below 12 pt in panels (tables may go to 10.5 pt) — split the page instead.
