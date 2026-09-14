# RA-L 投稿 / 返修可复用手册

来源：PushAround（RA-L，R&R 一轮）投稿‑返修全过程，含导师 50 条意见、写作 agent 多轮评审、以及本仓库中实际踩过的坑。
所有"教训"都对应本项目中的一个具体事件，不是泛泛而谈。

---

## 0. 三条最贵的教训（如果只记三条）

1. **RA-L 的 8 页是硬预算，不是软目标。** 任何新增内容都必须同时删掉等量内容。
   本项目为了容纳导师要求的 6 处新增，先后压缩了摘要、Setup、Results、Ablation、Conclusion、Table III 行距、图注，并把一个 display 公式改行内。
2. **每个数字都要能追到数据文件。** 被外部评审抓出的 5 处问题全是口径不一致，而不是写作问题：
   166/170 = 97.6% vs 156/160 = 97.5%；baseline 只跑 ±40% 却写 "same perturbations"；29–30 s 漏掉 N=2 的 23.9 s；WCCG 的 FP/FN 定义范围（300 vs 296）；FR 分辨率 0.02 写成 0.01（实际数据是 0.01）。
3. **附件内容必须与回复信声明逐字一致。** 我们写了 "raw logs"，但包里只有 per-trial CSV、没有 `.log`。
   写作 agent 明确说：这是"最容易造成负面印象的地方"。

---

## 1. 投稿前：为返修预留结构

### 1.1 蓝色标注机制（必须一开始就有）

```latex
% root.tex
\newcommand{\change}[1]{{\color{blue}#1}}
% 干净版：pdflatex -jobname=root_clean "\def\CLEANCOPY{}\input{root.tex}"
\ifdefined\CLEANCOPY
  \renewcommand{\change}[1]{#1}
\fi
```

两个必须做的校验（否则返修时一定漏标）：

- **论文侧**：新增段落是否都包了 `\change{}`。本项目最后仍发现 3 处新增文本（模式生成细化、Eq.(5) 可行性措辞、共享对比协议）漏标，被写作 agent 抓到。
- **干净版确实无蓝**：定点采样颜色，而不是"看蓝色像素总数"——图里本来就有蓝色元素（WCCG 起始面、曲线），会用噪声淹没结论。

```python
# 定点采样：对同一段文字在 root.pdf / root_clean.pdf 中取 RGB 中位数
def sample(pdf, page, word):      # 见本仓库历史命令；返回 (r,g,b)
    ...
print("root.pdf 蓝?", b - r > 25, "| clean 版应为 False")
```

### 1.2 版面预算表（先记账，再动笔）

| 操作 | 典型收益/代价 |
|---|---|
| `\arraystretch` 1.15 → 1.0（19 行表） | **省 ~23 pt ≈ 2.4 行** |
| display 公式改行内 | 省 15–20 pt |
| 图注删一句 | 省 ~9.6 pt |
| 通栏图 0.85 → 0.80 `\linewidth` | 省 ~10–25 pt |
| 新增一段正文（5–6 行） | 花 ~60 pt |
| 新增一条参考文献（3 行） | 花 ~29 pt |

**关键现象：小改动不传导。** 浮动体会吸收零散空间，删 2–3 行往往毫无变化；
必须一次性腾出 ≥1/8 页才有可见效果。因此**批量凑够再编译**，不要逐行试。

### 1.3 图尺寸规则（显式约定，避免反复）

- 单栏图 ≥ 0.80 `\columnwidth`；通栏图 ≥ 0.80 `\linewidth`。
- 图‑图注间距要有**数值标准**（IEEEtran 图注间距 = `0.5\baselineskip` ≈ 6 pt）；
  本项目实测发现某图间距只有 **0.24 pt（横线穿过字母降部）**，靠肉眼是发现不了的。
- 用像素级实测，不要目测：

```python
# 跳过字形抗锯齿，测真实空白带
ink = (img < 245).any(axis=1)
i = y_caption - 1
while ink[i]: i -= 1          # 跳过 caption 自身 + AA 像素
cap_top = i + 1
while not ink[i]: i -= 1      # 穿过白缝
gap_pt = (cap_top - i - 1) / dpi * 72
```

---

## 2. 返修信（Response Letter）结构与规范

### 2.1 结构（本项目最终采用，经三方确认）

```
To Associate Editor      ← Q: AE 原文 / A: 致谢 + 修订路线图 + at-a-glance 表 + principal revisions
To Reviewer 3            ← Q: 摘要段原文 / A: 致谢 + 路线图
  ├ Strengths（4 条，逐字引用）      ← A: 简短回应（不做过度承诺）
  ├ Weakness 1 / Weakness 2          ← A: 新实验 + 证据
  ├ Follow-up 1–4（逐字引用）        ← A: 逐条回答
  └ 收尾评价段（逐字引用）            ← A: 1 段致谢
To Reviewer 4            ← 同上：摘要+总体评价 / First–Fourth / 收尾段
Updated and added figures ← 新旧图并排对照
（完整数据表分别就近放在相关回复旁，不放附录节）
```

### 2.2 六条硬性要求

| 要求 | 反例（本项目实际发生） |
|---|---|
| **覆盖审稿人全部文字**，包括 strengths 和收尾评价 | 初版漏了 R3 的 4 条 strengths 与两段收尾评价，被指出"没有完整覆盖 comments" |
| **顺序不重组**，按审稿人原始条目顺序 | 曾按"弱点→追问"自行分组，用户明确要求按原文顺序 |
| **Q 框逐字引用，不用省略号** | 初版用 `\dots{}` 省略，被要求"通篇去掉省略号" |
| 每条"先直接回答，再给证据，最后列修改点" | — |
| 修改点标注 (Page X, Sec. Y)，且**排版一变就重新核验** | 导师重排版面后 6 处页码失效（I-B p2→p1、II-D p3→p2、III-E2 p6→p5、IV-B2 p8→p7…） |
| 修改点附**蓝字原文引用**，且只引最相关的 1–2 句 | 曾整段粘贴（最长 602 字符）被要求收敛；收敛后最长 ~300 字符 |

### 2.3 页码定位的权威来源：`.aux`，不是文本搜索

```python
# 权威：hyperref 写入的编号 + 页码（注意 \mbox 包裹的编号格式）
re.findall(r'\\newlabel\{([^}]+)\}\{\{(?:\\mbox\s*)?\{?([^}]*?)\}?\}\{(\d+)\}', aux)
```

在 PDF 里搜字符串会产生大量误报（例如搜 "Algorithm 1:" 得到算法浮动体所在页 p5，
而 III-D **小节标题**实际在 p4；搜段落短语还会命中正文引用）。

### 2.4 语气：克制 > 辩护

| 避免 | 改成 |
|---|---|
| the two formal weaknesses … are closed | the two main concerns are addressed through dedicated experiments |
| This question turned out to be more productive than expected | This comment revealed a bottleneck in the shared mode-generation module |
| Thank you for insisting on this | We appreciate the opportunity to clarify … |
| collapses to 0% | falls to 0/10 at M=45 |
| the reviewer's reading is exactly the intended one | Yes. The objective covers … |
| the most economical | has the lowest observed planning/execution cost |
| fully consistent with nominal physics | 同义反复，删 |

绝对词（exactly / only / all / clearly / identical）除非数据严格支持，否则不用。

### 2.5 主张与证据必须同级

- 没有全局最优性/完备性证明 → 明说"finite sampling + non-admissible priority ⇒ 不保证"，
  不要把"节点扩展数少、消融有效"包装成 solution-quality guarantee。
- 300/300 一致是**经验验证**，不能写成形式化保证；同时说明 decomposition assumptions。
- 主动承认局限（baseline 5 seeds；Wilson 区间重叠 → 只作 descriptive comparison）
  **反而提升可信度**——写作 agent 对这一点的评价最高。

---

## 3. 返修中改动方法时必须交代的三件事

本项目在返修中改进了 mode generation（bounded backtracking + 临时释放机器人），
如果处理不当会被质疑"返修中改算法"。必须写明：

1. 改动**位于共享模块**，所有方法（含 baseline）同样受益；
2. **所有方法在改动后重跑**，比较在同一起点上；
3. 改动对结论的**具体影响**（本例：N=4 成功率 PushAround 70%→100%、SL-Push 0%→80%、DFS-WCCG 80%→90%）。

另外：新机制要给出**复杂度界**，且界的形式要和实现一致。
本例：贪心 ≤ N|A| 次替换；回溯 ≤ B=2000 个部分分配（代码里的 `mode_gen_backtrack_budget`）；
subset fallback 再重复一次 ⇒ 每任务 ≤ (N|A|+2B) 次 LP 检验，每次 2N 个力变量。
**不要断言"LP 总代价对 N 线性"**——LP 维度本身随 N 增长。

---

## 4. 图表排版：三宗罪与正确做法

| 罪状 | 现象 | 正确做法 |
|---|---|---|
| `\resizebox{\linewidth}{!}{…}` 整表缩小 | 字号被压、观感廉价 | 用小字号 + 缩短单元格文案让它**自然**适配 |
| 列距小 + 无分隔线 | 列粘连难读 | `\tabcolsep` 5–6 pt + `\addlinespace[2pt]`（booktabs 风格不用竖线） |
| 内部换行切断单词（"tri-als"） | 生硬 | 列用 `>{\raggedright\arraybackslash}p{}` + 局部 `\hyphenpenalty=10000` |
| 对照图用浮动体 | 文字与图错位（F1/F2/F3 与图不匹配） | 用 `[H]` 或 `center` + `\captionof{figure}{}`，保证"文本→图→文本→图"严格顺序 |
| 图例贴边/离图太远 | 图例压标题、或悬空 22 pt | 先 `tight_layout` 再按标题实测 extent 锚定图例；打印实测间距 |

---

## 5. 自动化校验工具箱（本会话真正救过命的 5 个检查）

1. **页数 + 溢出**：`pdfinfo | grep Pages`，`grep -c '^!' *.log`，`grep -c Overfull`，
   再看"第 N+1 页内容"判断是溢出还是尾页。
2. **孤行（单行单词）检测**：按 y 聚类每页单词，找 `len(line)==1` 且以句号结尾的词；
   公式/表格单元需过滤。
3. **真实页尾空白**：渲染 72 dpi 找最低墨迹行，**排除页脚页码**（页码 y≈740–751，
   按"内容 == 页码 且 y>700"过滤），否则每页都会报"满页"。
4. **页码/图号一致性**：以 `.aux` 的 `\newlabel` 为权威，逐条比对回复信里的
   `(Page N, Sec. X)` 标签（注意同一括号内可含多组，要按 `;` 切分，否则全是假报警）。
5. **干净版无蓝**：定点采样文字颜色（见 §1.1）。

附带提醒：`cite.sty` 会把 `[3],[4],[5]` 压缩为 `[3]–[5]` 并自动排序——这是导师要的效果，
但引入全局包会改变全篇分页，需立刻重编译核对页数。

---

## 6. 协作流程

### 6.1 与导师

- 口语化意见**必须 todolist 化**，每条标"我直接做 / 需你确认 / 图由你改"，**执行前先给方案**。
- 歧义必须回问。本项目两例：
  - "Remark 1, marker 单独一行" → 指 ■ 符号还是标题？（后来又要改回行内，说明当初就该确认）
  - "Fig.8 不用说了" → 指响应文档第 8 个图（F3）还是论文 Fig. 8？
- 导师意见常**重复/矛盾**（"去掉黑体总结" 实际只针对审稿人回复小节，不针对 AE 的 principal revisions）——
  逐条问清适用范围，比自己猜更省时间。

### 6.2 与写作 agent（外部评审）

把反馈分三级执行：

| 级别 | 处理 |
|---|---|
| 必须修正（口径不一致、事实错误） | 立即改，且**回到原始数据核对**（本例 agent 报的 4 条全部成立，还额外发现 FR 分辨率写反） |
| 强烈建议（版本过时、格式） | 有空就改 |
| 可选润色 | 版面/时间允许再改，避免为润色引发版面连锁 |

### 6.3 提交清单（RA-L 实测）

- [ ] `root.pdf` ≤ 8 页（6 页 + 2 页超页费），0 error / 0 overfull
- [ ] `root_clean.pdf`（无标注版）
- [ ] `response.pdf`（**单一 PDF**：回复 + 标注版论文合并，否则可能直接拒）
- [ ] `multimedia.zip` ≤ 50 MB，**恰好一个视频**，含 `ReadMe.txt` + `Summary.txt`，且**不含正文/图**
- [ ] 所有作者 ORCID；human-subjects 选 No
- [ ] 30 天期限（逾期自动转 Reject）
- [ ] 附件内容与回复信声明逐字一致 ← 见 §0.3

---

## 7. 本项目具体踩坑清单（作为警示）

| 坑 | 代价 | 预防 |
|---|---|---|
| 用"蓝色像素总数"判断干净版 | 被图内蓝色元素误导，得到错误结论 | 定点采样 |
| 用文本搜索定位小节页码 | 大量误报，两次误判"页码漂移" | 用 `.aux` |
| 图片 `\vspace{-...}` 过负 | 算法顶横线穿过 caption 字母降部 | 像素级间距实测 |
| 响应图浮动 | 文字与图错位 | 非浮动 + `\captionof` |
| 删节时正则贪婪匹配到文件尾 | 删掉 `\end{document}`，编译崩溃 | 删节后立即检查文件尾 |
| 用 `sed` 插入 LaTeX 命令 | 反斜杠被吞（`usepackage{cite}`），编译失败 | 用 edit 工具或检查插入结果 |
| 脚本逐行 `replace` 无校验 | 表格引用匹配跨表，产生重复表格 | 每次替换后统计标签唯一性 |
| 附件写 "raw logs" 但包里没有 | 提交前被评审点出（唯一"必修"之一） | 附件的每个名词都回文件系统核对 |

---

## 8. 一句话总结

**写作阶段**：把"页面预算 + 蓝色标注机制 + 图表规范"当工程约束，一开始就建好，别等返修时救火。
**返修阶段**：逐条覆盖、顺序不动、原文引用、页码可核查、数字可追溯、语气克制、附件一致。
**协作阶段**：把导师意见 todolist 化并回问歧义；把外部评审意见分三级；用脚本做第二双眼睛。
