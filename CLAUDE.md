# Knowledge Base Schema — LeetCode Hot100

## Domain
LeetCode Hot100 algorithm problems organized by knowledge network.
Knowledge network takes priority over individual problems.
Problems are leaf nodes that belong to pattern nodes.

---

## Core principle
wiki/patterns/ is the backbone of this knowledge base.
Every problem must be linked to at least one pattern.
Every pattern must reflect its position in the dependency graph.

---

## Directory conventions
- wiki/patterns/         → Knowledge network nodes (organized by phase)
  - 数组/
  - 双指针技巧/
  - 基础数据结构/
  - 链表/
  - 二叉树/
  - 高级数据结构/
  - 综合算法/
- wiki/papers/YYYY-MM-DD/  → Paper pages organized by read date
  e.g. wiki/papers/2026-06-11/论文名.md
- wiki/papers/_reading-log.md → Master index of all papers read
- raw/problems/          → Raw problem statements
- raw/html-lectures/     → Structured lecture HTML files
- raw/references/        → Blog posts, editorial references
- output/                → Generated reports, review plans

---

## Learning phases (follow dependency order strictly)
Phase 1 — 数组基础
  前缀和 → 差分数组 → 二维数组

Phase 2 — 双指针技巧
  数组双指针 → 滑动窗口 → 二分搜索 → 随机算法

Phase 3 — 基础数据结构
  循环数组 → 栈与队列 → 哈希 → 设计类

Phase 4 — 链表
  链表双指针 → 递归

Phase 5 — 二叉树
  递归遍历 → 层序遍历

Phase 6 — 高级数据结构
  二叉搜索树 → 堆 → 字典树 → 图

Phase 7 — 综合算法
  回溯法 → DFS → BFS → 广度优先搜索
  分治算法 → 动态规划 → 最短路径
  数学 → 贪心算法

---

## Pattern page format
Each pattern page must include:

---
title: "模式名"
phase: 1-7
status: not-started | learning | mastered
depends_on: [前置模式wikilink]
problems_total: N
problems_solved: 0
---

## 适用场景
(什么特征的题目用这个模式，2-3句)

## 核心思路
(直觉解释，不用伪代码)

## 代码模板
```python
# 可直接套用的模板
```

## 复杂度
- 时间：O(?)
- 空间：O(?)

## 与相似模式的区别
(对比最容易混淆的模式)

## 前置依赖
- [[patterns/前置模式]]

## 题目列表
| 题号 | 题目 | 难度 | 状态 |
|------|------|------|------|
| 1 | [[problems/1-两数之和]] | Easy | solved |

---

## Problem page format
Each problem page must include:

---
title: "题号. 题目名"
difficulty: easy | medium | hard
status: todo | attempted | solved | reviewed
pattern: [主模式, 副模式]
date_solved: YYYY-MM-DD
---

## 题目描述
(one-line summary)

## 所属模式
- 主模式: [[patterns/xxx]]
- 依赖前置: [[patterns/xxx]]

## 解题思路
(核心思路，不是步骤流水账)

## 关键代码
```python
# 核心片段，不需要完整
```

## 复杂度
- 时间：O(?)
- 空间：O(?)

## 易错点
(一句话)

## 相似题
- [[problems/xxx]]

---

## HTML lecture ingest rule
When raw/html-lectures/ contains a lecture file:
1. Read the HTML and extract: concept, intuition, templates, complexity
2. Update the corresponding wiki/patterns/ page
3. Do NOT create a separate page for the HTML file
4. Preserve all existing problem links in the pattern page

---

## Ingest workflow — new problem
1. Create wiki/problems/题号-题目名.md
2. Update the corresponding pattern page's 题目列表
3. Update progress.md statistics
4. Add wikilinks: problem ↔ pattern (bidirectional)
5. Update index.md

## Ingest workflow — new HTML lecture
1. Read raw/html-lectures/xxx.html
2. Identify the target pattern page in wiki/patterns/
3. Update (never recreate) the pattern page with extracted content
4. Log in log.md

## Ingest workflow — new reference/blog
1. Extract concepts only, integrate into existing pattern pages
2. Do not create standalone pages for references

---

## Progress tracking
Maintain progress.md with:
- Total: solved / 100
- By difficulty: Easy X/17, Medium X/63, Hard X/20
- By phase: Phase1 X/N ... Phase7 X/N
- By status: todo / attempted / solved / reviewed
- Recently solved: last 5 problems

---

## Tags convention
difficulty: easy / medium / hard
status: todo / attempted / solved / reviewed
phase: 1 / 2 / 3 / 4 / 5 / 6 / 7
pattern:
  数组类: 前缀和 / 差分数组 / 二维数组
  双指针: 数组双指针 / 滑动窗口 / 二分搜索 / 随机算法
  数据结构: 循环数组 / 栈与队列 / 哈希 / 设计
  链表: 链表双指针 / 递归
  二叉树: 递归遍历 / 层序遍历
  高级结构: BST / 堆 / 字典树 / 图
  综合算法: 回溯 / DFS / BFS / 分治 / 动态规划 / 贪心 / 数学 / 最短路径


## Auto git sync rule
After EVERY operation that modifies any file in this vault:
1. Stage all changes: git add .
2. Commit with descriptive message: 
   git commit -m "auto: {{operation_type}} - {{affected_files_summary}}"
3. Push to remote: git push

Operation type examples:
- ingest: when processing a new clip
- update: when updating existing pages  
- create: when creating new pages
- progress: when updating progress.md
- restructure: when reorganizing directories

Example commit messages:
- "auto: ingest - 差分数组 pattern + 3 problem stubs"
- "auto: update - 滑动窗口 pattern page"
- "auto: progress - solved 1-两数之和"

Never skip git sync even if only log.md was changed.
Always run git push after commit, not just git commit.