针对不同内容类型，分别给你写好提示词模板：

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

### 建议保存方式

把这些提示词存成一个文件放在 vault 里：

```
your-kb/
└── prompts.md   # 常用 Claude Code 指令集
```

用的时候直接复制粘贴，不需要每次重新想。需要我帮你把这些整理成一个完整的 `prompts.md` 文件内容吗？