# API reference (`scripts/pptstudio`)

Units: inches on a 13.333 × 7.5 slide; font sizes in pt. Colors: theme roles, `role+NN` (tint), `role-NN`
(shade) or hex `'1F57C3'`. Text markup: `[[emphasis]]`, `**bold**`, `{{color|text}}` (bold text in a role / named color / hex, e.g.
`{{wcm|WCM}}`), `\n` = new paragraph. Numeric ranges and codes (`4.6–10.5`, `A-50`) are glued automatically
with U+2011 so PowerPoint never breaks them across lines (`canvas.nobreak`).

Contents: Deck · Theme · Canvas & Box · Layouts · academic · components · images · charts · tables · render ·
qa · fonts · icons · gallery · CLI

---

## Deck (`pptstudio.Deck`)

```python
Deck(theme='nsfc_blue', scenario='research', nav=None, page_numbers=True, portable=False, skin=None, **overrides)
```
- `theme`: preset name, hex color (`'#660874'`, add `style='defense'` for the defense spec), dict, or `Theme`.
- `scenario`: `'research'|'daily'|'competition'` — type-scale defaults for *modern* themes only.
- `nav`: `None | 'top' | 'left' | 'mini' | 'bottom'` navigation on content pages (uses `set_sections`); `'mini'` =
  compact chapter chips inside the defense title bar (past pale / current solid / future gray) — costs no height;
  `'bottom'` = the same chips centred above the bottom rule (开题 / 答辩 decks; content area 0.42 in shorter).
- `skin`: 答辩风格家族 for defense decks — `pixel` (default look) · `leaf` · `baibao` · `bright` · `badge` · `center` ·
  `tab` · `tech` (see `theme.SKINS`, gallery `style_<skin>.jpg`); stored in `theme.extras` (`title_bar`,
  `panel_header`, `cover`, `agenda`, `deco`, `bottom`, `ending`), each overridable via `extras={...}`.
- `portable=True`: only Microsoft YaHei / SimSun / Arial (safe on any Windows PC).
- `**overrides`: any `Theme` field (`primary=`, `size_body=`, `font_body=`, `extras={'title_bar': 'bars'}`…).

| Method | Purpose |
|---|---|
| `d.meta(**kw)` / `d.set_meta(**kw)` | deck info: `title, subtitle, en, author, advisor, org, unit, lab, project, date, logo, completers, units` |
| `d.set_sections(titles, en=None, short=None)` | chapter names (agenda, navigation, auto numbering); `short` = labels for `nav='mini'` (default: text before 与/及/和) |
| `d.add_colors(**named)` | named colors usable in every color spec and in `{{name|text}}` markup, e.g. a paper's method colors `d.add_colors(moc='0072BD', wcm='77AC30')`; tints like `'moc+55'` work |
| `d.<layout>(...)` | one slide per call (see layout-catalog.md) |
| `d.page(title, en=None, source=None, bg=True, section=None, nav=True, num=None) -> Canvas` | blank content page with chrome; `cv.content` = free Box |
| `d.new(kind='content'|'cover'|'section', bg=True) -> Canvas` | truly blank slide (+ optional background) |
| `d.save(path, render=False, check=True, pdf=False, width=1600)` | write .pptx; `check` prints static QA; `render` → `<name>_preview/` PNGs + contact sheet (PowerPoint COM) |
| `d.theme`, `d.prs` (python-pptx Presentation), `d.cur_section`, `d.style` | escape hatches |

## Theme (`pptstudio.theme`)

- `get(name_or_theme=None, **overrides) -> Theme`, `from_color(primary, mode='light', name=None, secondary=None,
  accent=None, style='modern', **kw) -> Theme`, `PRESETS` (dict), `SCENARIO_DEFAULTS`.
- Presets — defense: `nsfc_blue, nsfc_navy, bright_blue, nsfc_red, nsfc_green, nsfc_purple, burgundy, water_nsfc,
  royal_blue (1170C6), deep_blue (0A4FA0), navy_deep (013E87), cobalt (0A36A2), steel_blue (1D5CA6)`;
  modern: `academic_blue, academic_navy, tsinghua_purple, pku_red, academic_green, business_blue, business_navy,
  gov_red, eco_green, warm_orange, minimal_gray, tech_dark, vivid_purple, water`.
- Key fields: `style ('defense'|'modern'), mode ('light'|'dark'), primary, secondary, accent, deep, emph, yellow,
  panel, panel_line, dark, text, muted, line, bg, bg2, surface, font_title, font_body, font_latin, font_number,
  font_serif, font_display, title_weight, size_cover, size_section, size_title, size_heading, size_body,
  size_small, size_caption, size_min, line_spacing, margin_x, title_y, content_top, content_bottom, gap, radius,
  card_style ('shadow'|'tint'|'outline'|'flat'|'glass'), bg_style ('soft'|'plain'|'grid'|'dots'|'dark_glow'),
  title_style ('plain'|'en'|'mark'), decoration ('min'|'normal'|'rich'), icon_style, extras`.
- `t.c(spec) -> hex`, `t.font(role) -> (ea, latin, force_bold)`, `t.ramp(n)` series colors, `t.copy(**kw)`.

### Skins (`pptstudio.theme`)

`SKINS` (dict name → chrome settings + label), `SKIN_THEMES` (suggested color theme per skin),
`apply_skin(theme, skin) -> Theme`. 15 skins: `pixel, leaf, baibao, bright, badge, center, tab, tech` (2026-10-01) +
`jinbu, kexue, zhongdian, changjiang, lab, wanren, shenbao` (新参考 2026-10-02). Structure layouts read the skin:
`cover(variant=None)` → `band|sky|award|left|tech|plaque|midband|arc|tag|lab` (the last five live in
`pptstudio/covers.py`), `agenda(variant=None)` → `vertical|split|card|corner|band`, `section(variant=None)` →
agenda / `number` / `band`, `ending(variant=None)` → `band|sky|split|plaque|midband` (text “谢谢” only by default).
Skin keys (all overridable through `extras`): `title_bar, panel_header, cover, agenda, section, deco, bottom, ending,
statement, cover_pill, cover_texture, band_image`.

### Sample figures (`pptstudio.samples`)

Synthetic research figures with Chinese labels for galleries and layout tests (never for real decks):
`route_map, stress_field, microseismic, section, network, risk3d, curves, scatter` (each returns a cached PNG);
`all_figures() -> {name: path}`. `images.circuit(color, size, seed, alpha, fade)` → transparent circuit-trace PNG
(tech covers).

## Canvas & Box (`pptstudio.canvas`)

`Box(x, y, w, h)`: `.r .b .cx .cy`, `.inset(dx, dy=None)`, `.cols(n, gap=0.24, weights=None)`,
`.rows(n, gap=0.24, weights=None)`, `.grid(n, cols=None, gap=0.24, row_gap=None)`, `.split(frac, gap=0.3, vertical=False)`.

| Canvas method | Signature |
|---|---|
| text | `text(x, y, w, h, content, size=None, color='text', role='body', bold=None, italic=False, align='left', anchor='top', ls=None, sa=None, sb=None, fit=True, min_size=None, max_lines=None, spacing=None, emph=None, name=None, alpha=1.0, grad=None, grad_angle=0, bullet=None, bullet_color='primary', indent=None, shadow=None, wrap=True, outline=None, vert=None, rot=0, insets=(0,0,0,0), bullet_font=None)` |
| measure | `measure(content, w, size=None, role='body', bold=None, ls=None, sa=None) -> inches` |
| width_of | `width_of(s, size, role='body', bold=None, spacing=0) -> inches` |
| rect | `rect(x, y, w, h, fill='primary', radius=0.0, name=None, **style)` |
| shape | `shape(prst, x, y, w, h, fill='primary', adj=None, name=None, **style)` — prst in `canvas.PRST` |
| ellipse / circle | `ellipse(x, y, w, h, fill, **style)`, `circle(cx, cy, r, fill, **style)` |
| ring | `ring(cx, cy, r, thickness, color='primary', start=0, sweep=360, **style)` |
| line | `line(x1, y1, x2, y2, color='line', width=1.0, alpha=1.0, dash=None, head=None, tail=None, cap='round', name=None, grad=None)` |
| poly | `poly(pts, fill='primary', line=None, line_w=1.0, closed=True, smooth=False, name=None, **style)` |
| path | `path(subpaths, x, y, w, h, vb_w, vb_h, fill=None, line=None, ...)` (custom geometry) |
| icon | `icon(name_or_keyword, x, y, size, color='primary', stroke=2.0, alpha=1.0)` |
| image | `image(path, x, y, w, h, fit='cover'|'contain'|'stretch', focus=(0.5,0.5), radius=0.0, shape=None, alpha=1.0, line=None, line_w=1.0, shadow=None, name=None)` |
| equation | `equation(tex, x, y, size=20, color='text', w=None, h=None, align='left', anchor='top')` → Box (TeX formula at true pt size; shrinks to w/h) |
| misc | `c(spec)`, `notes(text)`, `transition(kind)`, `to_back(shape)`, `to_front(shape)` |

`**style` keys: `alpha, line, line_w, line_alpha, dash, grad=[(pos, color, alpha)…] or [(color, alpha)…],
grad_angle, grad_kind ('linear'|'radial'|'rect'|'shape'), shadow (True|'soft'|'strong'|'glow'|dict), glow,
soft_edge, rot`. PRST names: arc, blockArc, can, chevron, chord, cloud, corner, cube, diamond, donut,
doubleWave, downArrow, ellipse, flowChartProcess, flowChartTerminator, frame, halfFrame, hexagon, homePlate,
leftArrow, leftBrace, leftBracket, leftRightArrow, octagon, parallelogram, pentagon, pie, plaque, rect, rightArrow,
rightBrace, rightBracket, round1Rect, round2DiagRect, round2SameRect, roundRect, rtTriangle, snip1Rect,
snip2DiagRect, star5, teardrop, trapezoid, triangle, upArrow, wave, wedgeRoundRectCallout.

## Layouts

See `layout-catalog.md` for parameters. Defense: `panels, columns, problems, figure_text, route, innovations,
achievements, schedule, profile, layers, milestones`. Research (image review): `band_cards, architecture, versus,
process_matrix, cycle, bands, tree`. Template families (新参考, `layouts_pro.py`): `risks, outcomes, topics,
lab_team, leader, need_cards, framework, history, awards`. Generic: `cards, bullets, text_image, kpis, quote,
chart_page, table_page, timeline, process, hub, compare, matrix, pyramid, band, split, figure, image_grid, team,
references`. Structure (style-aware): `cover, agenda, section, ending`.

## academic (`pptstudio.academic`, defense building blocks)

```
background(cv, kind='content')
title_bar(cv, title, num=None, style=None, logo=True, en=None, nav=None) -> content top y   # style: slant|bars|underline|band|badge|center|tab|lightband|vband|photoband|numbox|square|thin|halfdisc|slash
background(cv, kind='content')            # skin deco: corner | arcs | dots | none
bottom_rule(cv, page=None, style=None)    # rule | band | none
header_shape(cv) -> ribbon shape matching the skin's panel headers
mini_nav(cv, labels, current, right, y, h=0.3, size=10.5) -> left x used
bottom_rule(cv, page=None)
statement(cv, x, y, w, text, style=None (skin) |'bar'|'label'|'centered'|'pink'|'plain'|'key'|'box', label=None, size=None, color='dark', h=None, align='left', label_w=1.6) -> height
panel(cv, box, header=None, header_style=None|'ribbon'|'strip'|'tab'|'pill'|'trap'|'fade'|'pale'|'dash'|'notch', fill='panel_light', line='panel_line', header_w=None, size=None, header_fill='primary') -> inner Box
ribbon(cv, x, y, w, text, h=None, fill='primary', color='FFFFFF', size=None, shape='rect'|'tab'|'chevron'|'pill'|'fade'|'pale'|'dash'|'notch', align='center') -> height
tag(cv, x, y, w, h, text, style='navy'|'chevron'|'pill'|'red'|'light'|'outline', size=None)
vlabel(cv, x, y, w, h, text, fill='primary', color='FFFFFF', size=None)
red_marker(cv, x, y, text, w=1.25, h=0.42, size=None) -> right edge x
arrow_list(cv, box, items, size=None, color='dark', role='medium', gap=None, fit=True, marker_color='primary', anchor='top')
figure(cv, box, image=None, caption=None, frame=True, cap_style='band', placeholder='示意图', fit='contain') -> picture | None
pic_box(pic) -> Box actually covered by a picture (after letterboxing)
formula(cv, box, tex, num=None, size=None, color='text', align='center', note=None, note_size=None) -> Box  # equation + '(n)' + symbol note
mini_nav_width(cv, labels, size=10.5) -> width of a mini_nav chip row
# diagram helpers (pptstudio/diagrams.py, re-exported here)
card_box(cv, box, style='shadow'|'topline'|'outline'|'pale', accent='primary', radius=0.08, fill='FFFFFF', pad=0.16) -> inner Box
card_title(cv, x, y, w, title, icon=None, size=None, color='primary_deep', sub=None) -> height used
symbol_strip(cv, box, symbols=[(tex, meaning)], size=None, sym_size=None, cols=None)   # legend under a formula
formula_block(cv, box, tex, symbols=(), num=None, size=None, note=None, cols=None) -> Box
formula_card(cv, box, tex, title=None, meaning=None, symbols=(), num=None, size=None, style='shadow', accent='primary', icon=None) -> inner Box
cycle(cv, cx, cy, r, labels, thickness=None, colors=None, center=None, center_sub=None, icon=None, gap_deg=4, size=None, start_deg=0) -> [(mid_deg, color)]
stat_grid(cv, box, items=[{label, value, unit, color}], cols=None, color='primary', size=None, rules=True, align='left')
progress_bars(cv, box, items=[{label, value, display}], color='primary', max_value=100, highlight=None, value_fmt='{:g}%')
vs_badge(cv, cx, cy, d=0.64, text='VS')
hbracket(cv, x0, x1, y, label=None, color='primary', size=None)        # phase bracket with a label pill
water_waves(cv, x0, x1, y, h, colors=(...), alphas=(...), amp=None, periods=1.15, phase=0.4)   # 水波 motif
zoom_inset(cv, image, pic, src=(x0, y0, x1, y1), dst=Box, color='emph', label=None, line_w=1.5, connect=True) -> Box  # 局部放大
callout(cv, tx, ty, x, y, w, h, text, color='emph', size=None, dot=True)   # dot at target + leader line + framed label
flow_chain(cv, box, nodes, style='box'|'light'|'grad', arrow='chevron'|'red'|'block', size=None, colors=None, sub_size=None)
mini_table(cv, box, columns, rows, size=None, emph_cols=(), align=None, zebra=True) -> (frame, geometry)
stat(cv, box, value, unit='', label='', color='emph', size=None, align='center', label_size=None, prefix=None)   # prefix: small '小于' / '减少' before the value
conclusion(cv, text, y=None, x=None, w=None, h=0.58, style='navy'|'yellow'|'red'|'light', serif=False, size=None, icon=None) -> y
block_arrow(cv, x, y, w, h, direction='right'|'left'|'up'|'down'|'lr', color='primary', label=None, label_color='emph', size=11, light=False)
axis(cv, x, y, w, nodes=0 | [x positions], h=0.16, color='primary')
brace(cv, x, y, h, side='left'|'right', color='primary', w=0.18)
num_square(cv, x, y, n, size=0.46, fill='primary')
icon_badge_ac(cv, cx, cy, d, icon, color='primary')
dots_divider(cv, x, y, w, color='primary')
# template-family parts (pptstudio/parts.py, re-exported here)
LEVELS = {'低': '72AE48', '中': 'EE7F32', '高': 'BF0202'};  level_key(level) -> '低'|'中'|'高';  level_color(level) -> hex
chip(cv, x, y, w, h, text, style='soft'|'outline'|'fill', color='primary', size=None)
level_chip(cv, x, y, w, h, level, style='soft'|'fill', prefix='级别', size=None)
chevrons(cv, x, cy, color='primary', n=2, size=0.24, point='right'|'left', alpha=1.0) -> width
silhouette(cv, x, y, w, h)                                    # ID-photo placeholder (no stock photos of people)
person(cv, box, name=None, role=None, photo=None, band=True, role_color='emph', size=None)
stars(cv, cx, cy, n=3, size=0.14, color='primary', gap=0.05, center_big=True)
laurel(cv, cx, cy, w, h, title, sub=None, color='primary', sub_color='emph', n_stars=3, size=None)
certificate(cv, box, image=None, title='荣誉证书', seal=True)
metric_box(cv, box, label, value, unit='', arrow=None|'up'|'down', dashed=True, color='emph', size=None)
converge(cv, box, left=None, right=None, center='科学机遇', conclusion=None, color='primary', size=None)
vchain(cv, box, items, header=None, highlight=(), size=None, header_h=0.5)
arc_text(cv, cx, cy, r, text, start, end=None, size=14, color='emph')   # degrees clockwise from 12 o'clock; start > end = upright on the lower half
hub_node(cv, cx, cy, r, title, subs=None|[a, b]|'label', color='primary_deep', size=None)
cylinder(cv, x, y, w, h, text, color='primary_deep', size=None, highlight=False)
```

`pptstudio/covers.py` (used by `cover()` / `agenda()`; helpers reusable on custom title pages):
`rules_caption(cv, text, y, …)` caption between long fading rules · `fading_rule(cv, x0, x1, y, color, width,
toward='left'|'right'|'both')` · `pill(cv, text, cx, y, h, size, style='solid'|'navy'|'outline'|'ghost')` ·
`split_pill(cv, text, cx, y)` (汇报人 | name) · `units_grid(cv, units, y, …)` aligned unit cells with thin rules ·
`rows_of(units, per=None)` balanced rows · `logo_center(cv, path, y, h)`.

## components (`pptstudio.components`, modern building blocks)

```
background(cv, kind='content', style=None, strength=1.0)      glow_orb(cv, cx, cy, r, color='primary', alpha=0.2)
watermark(cv, text, x, y, w, h, size=96, color='primary', alpha=0.06, align='left', role='heavy', spacing=0)
waves(cv, y=5.9, h=1.7, colors=('primary','secondary'), alphas=(0.16,0.1), phase=0.0, amp=0.18, n=2)
wave_curve(cv, x0, x1, y, amp, color='primary', width=1.5, alpha=0.5, periods=1.0, phase=0.0)
page_title(cv, title, en=None, x=None, y=None, w=None, size=None, color='dark', align='left', logo=True) -> bottom y
logo(cv, path=None, x=None, y=None, h=0.42, align='right')     footer(cv, page=None, source=None, show_page=True)
nav_top(cv, sections, current, y=0.0, h=0.52, show_logo=True) nav_left(cv, sections, current, w=2.05)
card(cv, box, style=None, radius=None, fill=None, line=None, alpha=None)
icon_badge(cv, cx, cy, d, icon, style=None, color=None)       num_badge(cv, cx, cy, d, n, style='fill'|'outline'|'pale', color='primary', size=None)
pill(cv, x, y, text, size=12, fill='primary', color='FFFFFF', h=None, pad=0.16, align='left', bold=True, line=None, alpha=1.0) -> (shape, width)
kpi(cv, box, value, unit='', label='', sub=None, color='primary', align='left', size=None, trend=None|'up'|'down', label_color='text')
heading_block(cv, x, y, w, head, body=None, head_size=None, body_size=None, head_color='dark', body_color='text', gap=0.08, align='left', max_h=None) -> height
bullets(cv, box, items, size=None, marker='dot'|'num'|'check'|'icon', color='text', marker_color='primary', gap=None, ls=None) -> height
divider(cv, x, y, w, color='line', width=1.0, dash=None)      quote_mark(cv, x, y, size=1.0, color='primary', alpha=0.25)
arrow(cv, x1, y1, x2, y2, color='primary', width=1.5)         chevron_arrow(cv, cx, cy, size=0.28, color='primary')
screen_frame(cv, box, image=None, kind='browser'|'phone'|'laptop', url='', shadow=True, placeholder='截图') -> screen Box
```

## images (`pptstudio.images`, all return a file path; cached in the temp dir)

```
diffuse(colors, base='FFFFFF', size=(1600,900), seed=7, blobs=None, blur=160, strength=0.55)
dot_map(color, alpha=0.35, size=(1600,900), step=14, seed=3)      dot_texture(color, alpha=0.1, step_in=0.3)
tech_bg(bg='07122B', glow='2F7CFF', glow2='22D3EE', size=(1600,900), seed=5, grid=True)
gradient_png(stops=[(pos, hex[, alpha])], size=(1600,900), angle=90)
cover_crop(path, aspect, focus=(0.5,0.5), max_w=2400)    fade(path, side='bottom', start=0.45, end=1.0)
duotone(path, dark, light, contrast=1.1)    tint(path, color, amount=0.35)    desaturate(path, amount=1.0, brightness=1.0)
line_art(path, color='FFFFFF', alpha=0.5, threshold=40, blur=0.6)    blur(path, radius=18)
circuit(color, size=(1600,900), seed=3, alpha=0.55, fade='left')                          # tech cover traces
skyline(color='FFFFFF', size=(1400,240), seed=11, alpha=0.32, fade='left'|'right'|'both'|'none', motif='mixed'|'water'|'city')
hexgrid(color, size=(1600,900), r=46, alpha=0.18, fade='center'|'top'|'bottom'|'none')    # 科学技术奖 texture
dot_wave(color, size=(1600,420), step=12, alpha=0.4, waves=2.2)                           # halftone wave (重点实验室)
```

## charts / tables

```
charts.chart(cv, x, y, w, h, kind='column', categories=(), series=None, highlight=None, colors=None, labels=True,
             number_format='General', legend=None, gridlines=False, axis=True, font_size=11, gap=70, overlap=None,
             smooth=True, hole=62, label_pos=None, value_axis=False, max_value=None, min_value=None, gradient=True,
             show_percent=None, label_color=None) -> python-pptx chart
tables.table(cv, x, y, w, h, columns, rows, style='header'|'three_line'|'minimal'|'card', col_widths=None, align=None,
             font_size=None, header_size=None, highlight_col=None|int|(i, j, …), highlight_mode='fill'|'raised', highlight_rows=None,
             first_col_bold=False, zebra=True, fit=True, max_row_h=None, header=True) -> (frame, {col_x, row_y, font_size, height})
```

## mathtex (equations)

```
mathtex.render(tex, size=20.0, color='1A1A1A', fontset='stix', dpi=600) -> (png, w_in, h_in)   # true-size PNG, cached
cv.equation(tex, x, y, size=20.0, color='text', w=None, h=None, align='left', anchor='top', name=None) -> Box
```
Supported TeX (matplotlib mathtext): `\frac \dfrac \sum_{}^{} \left( \right) \lfloor \hat \mathrm \mathcal \partial`,
Greek, sub/superscripts. Not supported: `\begin{align}`, Chinese inside formulas (put Chinese in a text box).

## render (PowerPoint COM) / qa

```
render.export_png(pptx, outdir=None, width=1600, slides=None) -> [png]
render.contact_sheet(pngs, out, cols=4, thumb_w=480, labels=None) -> path
render.to_pdf(pptx, out=None)          render.embed_fonts(pptx, out=None)
render.check_overflow(pptx, tol_pt=2.0) -> [{slide, name, text, box_h, text_h, box_w, text_w, size}]
render.fix_overflow(pptx, out=None, min_size=9.0, step=0.5, tol_pt=1.5, skip_prefixes=('deco:',)) -> count
qa.check(path, theme=None, min_font=10.0) -> {slides, issues: [(slide, kind, msg)], fonts}; qa.format_report(rep)
```
Static QA kinds: `off-slide`, `tiny-font`, `overflow?` (estimate), `text-overlap`. Shapes named `bg:*`/`deco:*` are
ignored by overlap/off-slide checks.

## fonts / icons / gallery

```
fonts.pick(stack|list, portable=False) -> family     fonts.is_installed(family)     fonts.weight_family(family, 'bold'|'black'|'medium'|'light')
fonts.text_width(text, size, ea, latin=None, bold=False, spacing=0) -> pt     fonts.wrap(text, width_pt, size, ea, ...) -> [lines]
fonts.STACKS: sans, serif, kai, latin, number, portable_sans, portable_serif, portable_latin
icons.find(keyword, limit=8) -> [names]     icons.resolve(name_or_keyword) -> name     icons.exists(name)
gallery.build_gallery(style='defense'|'modern', out=None, theme=None, sheets_prefix=None)
gallery.export_sheets(pptx, prefix, per=9, cols=3, thumb_w=620)
```

## CLI (`python -m pptstudio …`, run from `<skill>/scripts`)

`render deck.pptx [--width 1600] [--slides 1,4]` · `check deck.pptx [--com]` · `fix deck.pptx [--out x.pptx]` ·
`pdf deck.pptx` · `embed deck.pptx` · `icons 关键词 [--n 12]` · `fonts` · `themes` · `analyze ref.pptx [--json out.json]` ·
`gallery [--style defense|modern] [--theme name] [--out g.pptx] [--sheets prefix]`.
