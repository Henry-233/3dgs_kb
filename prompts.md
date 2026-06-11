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

