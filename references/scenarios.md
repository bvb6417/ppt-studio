# Scenarios and storylines

Plan the storyline as a table before writing code:

| # | layout call | title (≤ 16 chars) | key sentence (statement / conclusion) | visuals & data |
|---|---|---|---|---|

Rules of thumb: 1 page ≈ 1 minute (defense pages are dense: 45–60 s each); one message per page; the
statement bar carries the claim, the panels carry the evidence; end each chapter with its strongest page.
Reviewers skim — put the conclusion in the first line of the page, not in the speaker notes.

Contents: 1 科研 (国自然申请 · 结题/中期 · 青年学生项目 · 科技奖 · 学术报告) · 2 学位/开题答辩 · 3 竞赛 ·
4 日常 (工作汇报 · 课件/讲座) · 5 Choosing sources and facts

---

## 1. 科研 (defense style, `Deck('nsfc_blue')`)

### 1.1 国自然申请 / 答辩 (面上、青年、重点；10–15 min, 14–18 pages)
| Chapter | Pages (layout) |
|---|---|
| 封面 · 提纲 | `cover(project='国家自然科学基金XX项目答辩')`, `agenda()` |
| 一、立项依据 | `section(1)` · 国家重大需求 `panels(2, conclusion yellow)` · 研究现状与不足 / 卡脖子问题 `columns(4, bottom)` · 关键科学问题 `problems(2)` |
| 二、研究内容与方案 | `section(2)` · 研究目标与内容 `panels(3)` or `layers` · 技术路线 `route` · 研究方案/关键技术 `figure_text` ×1–3 · 可行性分析 `panels` |
| 三、特色与创新 | `innovations(3)` (理论/方法/应用 or 三个层面递进) |
| 四、研究基础与条件 | 前期成果 `achievements` · 工作基础 `figure_text` · 平台条件 `panels(images+tags)` |
| 五、研究计划与预期成果 | `schedule` · 预期成果 `table_page` or `panels(stats)` |
| 结束 | `ending()` |

### 1.2 结题 / 中期汇报 (15–20 min)
项目概况 (`panels`: 任务书目标 + 研究内容) → 研究进展 (one `figure_text`/`panels` per research content, each with a
conclusion bar) → 主要成果 (`achievements` papers/patents/awards + `table_page` of representative outputs) →
计划执行情况 (`schedule` with done/ongoing colors via `color`) → 人才培养与合作交流 (`panels(stats)`) →
存在问题与下一步 (`columns`) → `ending()`.

### 1.3 国自然青年学生基础研究项目 (博士生) (EasySlides/树叶答辩 pattern)
个人基本情况 `profile` → 科研项目及学术参与 `panels([flow, table])` → 荣誉奖项 `panels(images+points)` →
研究背景及研究领域 `panels(3 figures)` → 前期工作基础 (学术成果一/二) `figure_text` ×2 → 课题计划：立项依据
`panels(core equations/figures)`、研究目标与内容 `panels`、研究条件与平台 `panels(images, table)`、工作计划及预期
成果 `schedule`/`table_page` → 创新点异同 (项目创新点 vs 博士论文) `compare(variant='rows')` or `panels` → `ending()`.

### 1.4 国省科学技术奖答辩 (科技进步/技术发明；8–12 min)
`cover(variant='award', title='XX省科学技术奖', subtitle=项目名)` (meta: completers, units) → 提纲 →
一、项目背景: 国家重大需求 `panels` · 卡脖子问题 `columns` · 研究热点 `panels` →
二、主要创新: 研究问题 `problems` · 目标解决 `panels(flow)` · 创新点1–3 `figure_text` (核心阐述 + 标签块) →
三、应用推广: 应用情况 `panels(images+stats)` · 用户评价/第三方评价 `panels` · 经济社会效益 `panels(stats + table)` →
四、成果与比较: 知识产权/论文 `achievements` · 与国内外同类技术对比 `table_page(highlight_col=本项目)` → `ending()`.

### 1.5 学术报告 / 研究方向综述
背景与意义 (需求 `panels`, 典型工程 `table`, 成效 `milestones`) → 特点与科学问题 (`columns`, `panels(flow+figure)`,
`problems(3, columns)`) → 研究方向 (总览 `panels(cols=3, icons)`, one page per direction: `figure_text`/`panels`/
`layers`) → 前景 (`innovations` as trends, `panels` 展望) → `ending()`.

## 2. 学位 / 开题答辩 (defense style with school color; long decks: `nav='top'` or `nav='left'`)

### 2.1 毕业答辩 (硕士 15–20 min / 博士 30–45 min)
封面 (`cover`, school logo in `meta(logo=...)`) → 目录 → 研究背景与意义 (`panels`) → 国内外研究现状
(`columns` or `table_page` of literature) → 研究内容与技术路线 (`layers` or `route`) → 第X章 研究 (per chapter:
方法 `figure_text`, 结果 `panels` with original figures + conclusion bar, 验证 `chart_page`/`table_page`) →
结论与展望 (`innovations` for conclusions, `panels` for 不足与展望) → 攻读学位期间成果 (`achievements` or
`table_page`) → 致谢 (optional `quote`) → `ending()` (just “谢谢”).
Keep figures exactly as in the thesis; add figure numbers to captions (`图3-2 …`).

### 2.2 开题答辩 (10 min)
选题背景与意义 → 国内外研究现状 (`columns`, 现有不足 in `bottom`) → 研究目标与内容 (`panels(3)`) → 研究方法与
技术路线 (`route` or `panels(flow)`) → 关键问题与创新点 (`problems` + `innovations`) → 研究基础与可行性
(`panels`) → 进度安排与预期成果 (`schedule`) → 主要参考文献 (`references`) → `ending()`.

## 3. 竞赛 (挑战杯、互联网+、创新创业、科创赛)

Judges score: 痛点真实 · 技术创新 · 成果证据 · 应用/市场 · 团队. Two looks:
- 学术类 (挑战杯课外学术作品): defense style — like 1.4 but with a `profile`/`team` page for members.
- 创业/路演类: modern style (`tech_dark`, `vivid_purple`, `business_blue`) — `cover(variant='dark'|'center')`.

Storyline: 痛点 (`cards` or `columns` with numbers) → 解决方案 (`hub` / `text_image`) → 核心技术与创新
(`innovations` / `figure_text`) → 成果与验证 (`kpis`, `chart_page` with highlighted bar, `achievements`) →
应用场景与市场 (`panels`, `kpis`) → 商业模式 (`process` or `hub`) → 竞品对比 (`compare(variant='rows')` or
`table_page(highlight_mode='raised')`) → 团队 (`team` / `profile`) → 发展规划 (`timeline`) → `ending()` with a
one-line slogan.

## 4. 日常 (modern style)

### 4.1 工作汇报 / 述职 / 季度总结 (`business_blue`, `business_navy`, `gov_red` for 党政)
封面 (`cover(variant='split')`) → 目录 (`agenda(variant='cards')`) → 核心指标 (`kpis(variant='row', lead=…)`) →
重点工作与成果 (`cards`, `chart_page` with highlight) → 问题与原因 (`bullets` rows, `compare`) → 下阶段计划
(`process(variant='cards')`, `timeline`) → 需要支持的事项 (`band`) → `ending()`.
Titles state the conclusion: “三季度营收同比增长28%” instead of “营收情况”.

### 4.2 课件 / 讲座 / 培训
学习目标 (`cards(variant='icon_left')`) → 概念 (`text_image`, `hub`) → 原理/步骤 (`process`) → 案例
(`figure`, `image_grid`) → 对比辨析 (`compare`) → 小结 (`bullets` / `quote`) → 思考题 (`ending(variant='qa')`).
Use larger text (`Deck('academic_blue', size_body=18)`), fewer items per page.

## 5. Choosing sources and facts

- Prefer primary/authoritative sources: government sites (gov.cn, 部委), 新华网/人民网, official project sites,
  journals; record the date (“截至2026年8月”). Put them in `source=` on the page.
- Check units and time stamps; don't mix cumulative numbers from different dates on one page.
- If a number cannot be verified, leave it out or mark it as an estimate — never invent it.
