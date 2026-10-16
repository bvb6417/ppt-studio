# Sources and method

The design rules and layouts were distilled (by analysis only) from:

| Material | How it was used |
|---|---|
| ≈3,000 designer and redesign slides, grouped by page type (封面、目录、过渡、多段内容、图文、图表、表格、时间轴、架构、人物、荣誉、结尾 …) | rendered to thumbnails for the visual survey; XML parsed for fonts, sizes, colors and geometry statistics (`design-rules.md §10`) |
| Public PPT tutorial and redesign articles (≈140 research-related ones read in full, ≈1,700 before → after images reviewed) | rules in `design-rules.md §1–13`, the research layouts (`band_cards`, `architecture`, `versus`, `process_matrix`, `cycle`, `bands`, `tree`), the paper-to-slides workflow |
| Public defense-deck pages and online template previews (国自然, 国家科技进步奖 / 科学技术奖, 国家重点研发计划, 长江学者, 全国重点实验室, 万人计划) | the default 科研答辩风, the 15 skins, covers, agendas and the template-family layouts (`design-rules.md §14`) |

No slides, templates, fonts, photos or article images from these materials are included in this repository.
Colors of the defense style were sampled from the reference images (`124CAD` headers, `033E9C` deep navy,
`C00000` red, `F8D008` yellow, `F0F3F8` panels).

## Third-party assets bundled

- Lucide icons (ISC License) — `assets/icons/lucide.json` (paths + tags), license in `assets/icons/LUCIDE_LICENSE.txt`.
  Icons are converted to native PowerPoint custom geometry at build time.
