针对不同内容类型，分别给你写好提示词模板：

危险启动：claude --dangerously-skip-permissions

---

### 摄入新论文（Web Clipper 裁剪后）

```
I added a new paper to raw/papers/. 
Read it and follow CLAUDE.md to:
1. Create a paper page in wiki/papers/
2. Create any new concept pages in wiki/concepts/ 
   if new concepts appear
3. Update existing concept pages if this paper 
   extends them
4. Add wikilinks between this paper and related 
   papers/concepts
5. Update index.md
```

---

### 精读论文（PDF 放入后）

```
Read raw/papers/论文名.pdf in full detail.
Update wiki/papers/对应页面.md with:
- Core method explained in plain language
- Key mathematical formulations
- How it differs from previous work
- Experimental results and limitations
- Any new concepts → create wiki/concepts/ pages
```

---

### 摄入博客 / 教程

```
I added a tutorial/blog to raw/blogs/.
Read it and:
1. Extract any concept explanations → update 
   wiki/concepts/ pages
2. If it explains a paper intuitively, link it 
   in that paper's wiki page under ## 参考资料
3. Do not create a separate wiki page for the blog,
   just integrate its insights into existing pages
```

---

### 看完视频后手动记录笔记摄入

```
I added my notes from watching a video to 
raw/videos/视频名.md.
Treat it like a blog: extract concepts and 
integrate into existing wiki pages.
```

---

### 定期整理（每摄入5-10篇后运行）

```
Run a wiki maintenance pass:
1. Find all orphan pages with no wikilinks → 
   connect them or flag in log.md
2. Find concepts mentioned in multiple papers 
   but without a concept page → create them
3. Update wiki/synthesis/ with a timeline of 
   3DGS development based on paper years
4. Report what was changed in log.md
```

---

### 专题查询

```
Based on the wiki, compare all papers that 
improve rendering speed of 3DGS.
Write a comparison table to 
output/speed-optimization-comparison.md
including: method, key idea, FPS improvement, 
trade-offs.
```

---

### PDF高亮标注

`</`

`>`

Read raw/papers/论文名.pdf in full detail.

When processing figures with system overview or architecture diagrams,
apply enhanced annotation to the figure captions ONLY.
Do not annotate the figures themselves.

For each architecture figure caption:

1. DECOMPOSE the caption into individual claims:

   - One claim per module or mechanism described
   - One claim per design decision explained
   - One claim per connection between modules
2. For each claim generate a highlight annotation:
   {
   "page": N,
   "phrase": "exact phrase under 10 words from the caption",
   "category": "module | dataflow | design_decision | loss | frozen_component",
   "note": "模块职责/数据流向/设计原因 的详细中文解释，2-3句，
   包含：是什么 + 为什么这样设计 + 对应图中哪个部分"
   }
3. Annotation coverage requirements for architecture captions:

   - Every named module must have at least one highlight
   - Every input/output relationship must have a highlight
   - Every "due to / because / to mitigate" clause must have a highlight
     (these explain design decisions, highest priority)
   - Loss function mentions must be highlighted
   - Frozen vs trained component distinctions must be highlighted
4. Note field must follow this structure:
   "【模块/机制名】+ 具体功能描述 + 与其他模块的关联 +
   对应图中颜色/位置（如：对应图中紫色Trained Online模块）"
5. Save as annotations JSON and run annotate_pdf.py

### 建议保存方式

把这些提示词存成一个文件放在 vault 里：

```
your-kb/
└── prompts.md   # 常用 Claude Code 指令集
```

用的时候直接复制粘贴，不需要每次重新想。需要我帮你把这些整理成一个完整的 `prompts.md` 文件内容吗？



## 粗读



I added multiple papers to raw/papers/.
Find all .md files in raw/papers/ not yet logged in log.md.
If log.md is empty or does not exist, treat ALL .md files
in raw/papers/ as unprocessed.

BATCH SHALLOW INGEST — process all at once:

For each unprocessed paper clip:
1. Create wiki/papers/论文名.md with:
   - Front matter (title/authors/year/venue/status: skimmed)
   - 一句话总结
   - 解决的问题
   - 核心贡献 (bullet list, from abstract only)
   - 关联 (wikilinks to obviously related existing pages)
   - ## 待精读标记: ⬜ 未精读

2. Create STUB concept pages only for brand-new concepts
   not yet in wiki/concepts/ — one line definition only,
   mark as stub: true in front matter

3. After all papers processed, generate output/待精读列表.md:
   | 论文 | venue | 年份 | 与现有知识的关联度(高/中/低) | 建议精读优先级 |
   Based on: how many existing concept pages it connects to,
   venue prestige, recency.

4. Update index.md
Auto git sync.
Report: N papers ingested, M concept stubs created.



## 精读
Find all papers that need deep reading:
- Look in wiki/papers/ for pages with status: skimmed
- These are papers that have been shallow ingested
  but not yet deep-read (no PDF processing done)

Process them in order of 建议精读优先级 from output/待精读列表.md
If 待精读列表.md does not exist, process in order of year (newest first)

For each paper with status: skimmed, in priority order:

STEP 1 — VERIFY PDF EXISTS AND CHECK SIZE
Check if raw/papers/对应论文名.pdf exists.
If PDF not found: skip, log "⚠️ PDF缺失", continue to next.

Check file size:
- If under 25MB: read directly
- If over 25MB: run compression first:
  python scripts/compress_pdf.py raw/papers/论文名.pdf
  Then read the _compressed version.
  Delete compressed file after processing is complete.

STEP 2 — READ PDF
Read raw/papers/论文名.pdf in full detail.

STEP 3 — UPDATE PAPER PAGE
Update (never recreate) wiki/papers/论文名.md:
- Expand 核心方法 with plain language explanation
- Add ## 数学形式 with key formulations
- Add ## 与前作的区别 (compare to papers already in wiki)
- Add ## 实验结论 with key numbers
- Add ## 局限性
- Change status: skimmed → done
- Remove ## 待精读标记

STEP 4 — UPGRADE CONCEPT PAGES
For each concept page marked stub: true that this paper covers:
- Expand from one-line stub to full concept page
- Remove stub: true from front matter

STEP 5 — GENERATE ANNOTATION JSON
Generate raw/papers/论文名_annotations.json
following the enhanced annotation format in CLAUDE.md.
Auto-run annotate_pdf.py to produce 论文名_annotated.pdf.

STEP 6 — CROSS-PAPER SYNTHESIS
After all papers processed:
Check if any 2+ papers address the same concept or problem.
If yes: update wiki/synthesis/ with a comparison page.

STEP 7 — DATE ARCHIVE
Get today's date (YYYY-MM format).
Save the paper page to wiki/papers/YYYY-MM-DD/论文名.md
instead of directly under wiki/papers/.
Create the YYYY-MM/ directory if it doesn't exist.

Update wiki/papers/_reading-log.md:
- Add a new row with: today's date / paper title / venue /
  status / wikilink / concept tags
- Keep sorted by date descending (newest first)

Auto git sync after each paper completes.
Report after each paper: title / sections added / concepts upgraded.
Report at end: total processed / skipped (PDF missing) / synthesis pages created.



## 论文迁移
Reorganize existing wiki/papers/ by read date:

1. For each .md file directly under wiki/papers/
   (not in a date subfolder):
   - Read the file's date_updated field from front matter
   - If no date field: use file creation date or today
   - Move to wiki/papers/YYYY-MM-DD/论文名.md

2. Create wiki/papers/_reading-log.md
   with one row per paper, sorted by date descending.

3. Update all wikilinks across wiki/ that point to
   old paths [[papers/论文名]] → [[papers/YYYY-MM/论文名]]

4. Auto git sync.
Report: N files moved, M wikilinks updated.



两个功能分别给你提示词：

---

## 功能一：整理某天论文的方法论创新点

```
Read wiki/papers/_reading-log.md.
Find all papers read on [日期, e.g. 2026-06-01].
Read each corresponding wiki page in wiki/papers/YYYY-MM/.

Generate output/论文整理_[日期].md with the following structure:

# 论文阅读整理 — [日期]

## 概览
| 论文 | venue | 核心问题 | 方法创新 | 相比baseline提升 |
|------|-------|---------|---------|----------------|

## 逐篇分析

### 论文名A
**解决的问题：**
(一句话，what gap does it address)

**Baseline / 前作：**
(what method does it compare against or build upon)

**方法创新点：**
1. (具体创新，不是泛泛而谈)
2. 
3. 

**关键结果：**
(最重要的1-2个数字，说明改进幅度)

**局限性：**
(作者自己承认的或明显的)

---

(repeat for each paper)

## 横向对比
(if 2+ papers address similar problems)

| 维度 | 论文A | 论文B | 论文C |
|------|-------|-------|-------|
| 核心思路 | | | |
| 解决的主要问题 | | | |
| 计算开销 | | | |
| 适用场景 | | | |

## 可借鉴的方法论
(cross-paper insights: what ideas could transfer to other problems)

Save to output/论文整理_[日期].md
Auto git sync.
```

---

## 功能二：基于某个 Baseline 的方法谱系整理

```
I want to understand all methods in the wiki that
build upon or compare against [baseline名称, e.g. 3DGS / MonoGS / SLAM].

Read all pages in wiki/papers/ and wiki/concepts/.
Find every paper that:
a. Directly builds on [baseline]
b. Proposes an alternative to [baseline]
c. Combines [baseline] with other methods

Generate output/方法谱系_[baseline名称].md:

# [Baseline] 方法谱系

## Baseline 概述
(what is [baseline], what problem it solves, key limitations)

## 基于该Baseline的改进方向

### 方向一：[改进维度, e.g. 动态场景处理]
- **论文名**：核心改进 + 如何解决baseline的局限
- **论文名**：...

### 方向二：[改进维度, e.g. 训练效率]
- ...

### 方向三：[改进维度]
- ...

## 方法演进时间线
[baseline年份] baseline名 → [年份] 论文A（改进点）→ [年份] 论文B（改进点）

## 各方法对比
| 方法 | 解决baseline哪个问题 | 引入的代价/局限 | 适用场景 |
|------|-------------------|--------------|---------|

## 仍未解决的问题
(gaps across all surveyed methods — potential research directions)

Save to output/方法谱系_[baseline名称].md
Auto git sync.
```

---

## 功能三：生成可直接发给工程负责人的整理

在功能一或二生成后，再发这条提示词转换格式：

```
Read output/论文整理_[日期].md (or 方法谱系_xxx.md).

Reformat into a concise technical briefing for an engineering lead.
Save to output/工程简报_[日期].md

Requirements:
- Total length: under 500 words
- No academic jargon without explanation
- Each paper/method in 3 lines max:
  问题 → 方法 → 结果
- End with a section: ## 工程可借鉴点
  List 2-3 concrete ideas that could apply to real implementation
  (not "this is interesting" but "specifically, you could do X by Y")
- Tone: peer-to-peer technical discussion, not a report

Do not include: author lists, citation numbers, venue names
Do include: actual method names, key numbers, concrete mechanisms

Auto git sync.
```

---

## 使用流程

```
当天读完论文
    ↓
发功能一 → output/论文整理_日期.md（自己看）
    ↓
发功能三 → output/工程简报_日期.md（发给工程负责人）

需要梳理某个方向时
    ↓
发功能二 → output/方法谱系_baseline.md（技术选型参考）
```

三个输出文件定位不同：论文整理是给自己的详细笔记，工程简报是对外沟通用的精简版，方法谱系是做技术选型或找研究方向时用的全景图。


## 批量标注

```
Read wiki/papers/_reading-log.md.
Find all papers read on [日期, e.g. 2026-06-11].

For each paper found, run the full annotation pipeline:

STEP 1 — CHECK PREREQUISITES
For each paper:
- Confirm wiki/papers/YYYY-MM-DD/论文名.md exists (deep-read done)
- Confirm raw/papers/论文名.pdf exists
- If PDF missing or encrypted: log to output/待获取PDF列表.md, skip
- If PDF over 25MB: run python scripts/compress_pdf.py first

STEP 2 — GENERATE ANNOTATIONS JSON
Read the paper's wiki page wiki/papers/YYYY-MM-DD/论文名.md.
Read the corresponding PDF.

Generate raw/papers/论文名_annotations.json with TWO types:

Type A — Body text highlights:
{
  "page": N,
  "phrase": "exact phrase under 10 words",
  "category": "core_contribution | method | result | limitation",
  "note": "【模块/机制名】功能描述 + 与其他模块关联 + 设计原因，2-3句"
}

Coverage requirements for body text:
- Every named module or component → at least one highlight
- Every "because / due to / in order to" clause → highlight
  (these explain design decisions, highest priority)
- Every quantitative result → highlight
- Loss function mentions → highlight
- Frozen vs trained component distinctions → highlight

Type B — Architecture figure caption decomposition:
For every figure with system overview or architecture diagram,
decompose the caption into individual claims.
For each claim:
{
  "page": N,
  "phrase": "exact phrase under 10 words from caption",
  "category": "module | dataflow | design_decision | loss | frozen_component",
  "note": "【模块名】功能 + 输入输出 + 与其他模块关联 + 对应图中位置/颜色，2-3句"
}

Coverage requirements for captions:
- Every named module in the diagram
- Every input/output relationship
- Every design decision clause
- Frozen vs trained distinctions from legend

STEP 3 — RUN ANNOTATION SCRIPT
python scripts/annotate_pdf.py \
  raw/papers/论文名.pdf \
  raw/papers/论文名_annotations.json

Confirm output saved to raw/papers/论文名_annotated.pdf

STEP 4 — UPDATE WIKI PAGE
Update wiki/papers/YYYY-MM-DD/论文名.md:
Add or update ## 标注状态 section:
---
annotated: true
annotation_date: [today]
annotated_pdf: raw/papers/论文名_annotated.pdf
---

STEP 5 — CLEANUP
If a compressed PDF was created in STEP 1,
delete raw/papers/论文名_compressed.pdf after annotation.

Auto git sync after each paper completes.

FINAL REPORT:
| 论文 | 状态 | highlights数 | margin notes数 | 输出文件 |
|------|------|------------|--------------|---------|
Report total: N papers annotated / M skipped (reason).
```

---

### 使用方式

日期填好直接发，Claude Code 会自动从 `_reading-log.md` 找到当天读的所有论文，逐篇走完整个标注流水线，不需要手动指定论文名。

如果只想标注某几篇而不是某天全部，把第一行改成：

```
Process annotation pipeline for the following papers:
1. 论文名A
2. 论文名B
```

其余步骤完全不变。