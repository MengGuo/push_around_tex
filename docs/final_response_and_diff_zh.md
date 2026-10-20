# 本轮 response 与 diff 整理记录

> 2026-10-21 更新：最终审查与打包已完成，源码及多媒体 ZIP 状态以 [final_audit_zh.md](final_audit_zh.md) 为准；本文保留前一轮记录。R5-2 的实验实现溯源限制尚未关闭。

日期：2026-10-20。作者已核验正文修改方向并授权编写本轮回复。

## 文件

- `response/response.tex`：本轮回复源码。沿用二投稿件的 11pt、页边距、灰底斜体 Q / 黑字 A 和蓝字修改摘录，恢复正式作者署名。
- `ral_final_submit/response.pdf`：5 页，142,061 字节。
- `ral_final_submit/root_diff.pdf`：最新版正文的选择性蓝字标注版，8 页，2,774,981 字节。只标针对本轮审稿意见的澄清；无下划线、删除线或旧文本，文字和分页与干净版一致。
- `ral_final_submit/response_and_diff.pdf`：回复在前、标注版正文在后，13 页，2,833,536 字节。
- `ral_final_submit/root.pdf`：正式干净论文，仍为 8 页、2,774,730 字节。Our Method 恢复及后续压缩复核见 [compression_review_zh.md](compression_review_zh.md)。
- `ral_final_submit/PushAround.mp4`：作者更新封面后的原文件，23,406,704 字节；未转码或覆盖。MP4 容器记录为 1920×1080、约 271.07 s。已加入 `.gitignore` 的原始视频例外，避免后续版本管理漏掉此文件。

原 `response/response.tex` 完整备份为 `response/archive/response_before_final_round.tex`，SHA-256 保持 `de57cda7e1793b8af27bc41ae75eadecf5b363d3da09c77694d9eb59aa60c3b0`。`ral_2nd_submit/` 和其冻结 ZIP 未改动。

## 逐条覆盖

| 意见 | 本轮回复 |
|---|---|
| AE：落实 minor concerns | 简述五项澄清及出版信息、视频封面更新 |
| R5-1：模式生成方式、场景、PT | 指向 p.7 IV-A6，说明三组 nominal PT 和预计算 preparation 不计 PT |
| R5-2：quick-pass 复用条件、状态和代价 | 指向 pp.4–5 III-C3 与 III-D，按名义模型的相对轨迹/代价复用规则回答，不引入代码简化讨论 |
| R5-3：种子复用、样本数与 nominal success | 指向 p.7 IV-A6 的 paired、single-parameter、10/5 seeds、3/5 vs 10/10 及比较边界 |
| R5-4：15.9 s 与旧回复的 159.6/115.0 s | p.8 IV-B2 明确标准差；159.6 s 为 force-limit ×0.6 成功 trial 均值，115.0 s 为八个 ±40% 条件的成功均值之等权平均，nominal 为 104.7 s |
| R5-5：重规划触发不一致 | 指向 p.7 IV-B1，删除 only，纳入 p.5 III-E1 的失败事件 |
| R6-1：物理模型误差实验 | 指向 p.7 IV-A6、Table III 的四类参数、四个扰动倍率和 156/160；说明这些实验二投已有，本轮只补清晰的协议与限制 |
| R6-2：高密度仅五种子 | 明确二投已扩为每密度十个种子，M=45 为 10/10；仅说明 Table III 的时间离散度及 Fig.10 时间面板误差棒，不将成功率曲线误写成带 Wilson 区间 |

全部编辑及审稿文字按原顺序纳入 12 个 Q/A 框；自动逐词核对原文共 931 词，未删掉正面评价、技术意见或结束语。Reviewer 5 的原始文本用 CP1252 解码，恢复了引号、± 和 ×，未改写意见内容。

## 标注范围及构建

按作者随后提出的样式要求，取消逐词新增/删除对照，改为与二投一致的“最新版正文 + 蓝字”格式。`root_diff.pdf` 沿用文件名，但不再是显示旧文本的 latexdiff 输出。

`ral_tex/root.tex` 中原 `change` 宏现在直接输出黑字；新增 `minorchange` 宏仅标蓝本轮 comments 对应的八处文字范围：R5-1 的实验协议段、R5-2 的 quick-pass 条件及其在 III-D 的三处一致性说明、R5-3 的失配比较限制、R5-4 的 mean ± standard deviation、R5-5 的重规划触发段。摘要、引言和其他为节省空间而调整的表述，以及署名和出版信息，均不标蓝。

Reviewer 6 对应的敏感性和十种子结果二投已经存在，保持黑字。response 中这两处摘录也改为黑字并标注 Existing manuscript result；本轮新增澄清的摘录仍用蓝字。response 开头同步说明选择性标蓝规则。

本次只改颜色包装，不改正文文字、公式、实验数据或图表尺寸。干净论文提取文字与改样式前完全一致；标注版与干净版的 `pdftotext -layout` 输出完全一致。上一步曾核验二投基准：Git 提交 `8c94a3d` 重建的正文文字与冻结 `ral_2nd_submit/root_clean.pdf` 完全一致，此次不再生成或编译逐词 diff。

在仓库根目录运行 `bash build_final.sh` 可构建全套 PDF；仅构建回复和 diff 可运行 `python3 packaging/build_final_review.py`，后者使用已存在的最终论文源码。两个脚本均不写入 `ral_2nd_submit/`，也不处理或转换视频。

已检查：正式论文两种工作输出、response、标注版编译均无 LaTeX 错误、Overfull 或未定义引用；合并 PDF 的提取文字与两个组成 PDF 的文字拼接完全一致。各 PDF 均低于 5 MB。检查关键页的旧文字转黑、本轮澄清标蓝，以及灰底问题框和页尾。

当前目录为核验用 PDF 与视频材料，尚未生成上传用源码 ZIP、多媒体 ZIP 或提交到系统。
