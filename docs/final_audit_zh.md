# 最终文本与提交材料审查（2026-10-21）

## 结论

正文和 response 已逐项覆盖 AE、Reviewer 5 和 Reviewer 6 的意见，回复引用的页码、章节及关键数值与最终八页正文一致。不过，**不能将全部问题称为已经事实核验关闭**：R5-2 的完整缓存复用规则已经解释，但其与早期 Table II 实验实现的一致性仍无法追溯。最终是否接受回复还由编辑决定。

本轮未修改实验数字或宣称重跑实验。未上传 PaperCept，未签署版权文件，也未确认系统当前是否开放终稿入口。

## 意见对应与状态

| 意见 | 正文和回复对应 | 审查结论 |
|---|---|---|
| AE 落实 minor concerns | response 首页总述及后续逐项回复 | 已覆盖；保留下述 R5-2 证据限制 |
| R5-1 模式生成、场景及 PT 口径 | p.7 IV-A6：预计算/greedy、11.7/16.8/23.9 s、不同 realization、preparation excluded | 文字一致，已回应 |
| R5-2 quick-pass 条件、后继状态及代价 | pp.4–5 III-C3，p.5 III-D；response 说明 can store、匹配条件、变换端点和缓存增量 | 模型层面已回答；实验实现溯源未关闭 |
| R5-3 失配试验比较限制 | p.7 IV-A6：复用十个 base seeds，基线五个，3/5 vs 10/10，单参数与 end-to-end 限定 | 正文、回复一致，已回应 |
| R5-4 硬件标准差及旧回复的均值 | p.8 IV-B2：77.1 ± 15.9 s 为 mean ± SD；response 区分 159.6 与 115.0 s | 已回应；标准差定义由作者明确确认 |
| R5-5 重规划触发 | p.5 III-E1 与 p.7 IV-B1：姿态误差及接触失败、停滞、连通性失效 | 已回应，无 only 限定冲突 |
| R6-1 模型误差实验 | p.7 IV-A6、Table III：四参数族、四倍率、156/160 | 明确是二投已有结果，没有伪称新实验 |
| R6-2 高密度统计样本 | p.7 IV-A6、Table III、Fig.10：每密度十个种子，M=45 为 10/10 | 已回应；回复未把有限样本解释为普遍保证 |

R5-2 的限制不是排版或措辞问题：作者已说明早期 Table II 为冻结结果，原策略无法恢复。现存代码历史不能证实已经实现正文描述的完整状态序列及代价缓存。本文的 `can store` 是模型说明，不能据此认定原始实验实际使用该完整机制。按作者此前要求，本次未自行把实现简化说明写入正文或 response，也未修改 Table II。这个问题需要实现/实验依据才能真正关闭。

## 本轮直接修正

1. Eq. (6) 后将 “rollout in (13)” 改为 “evaluation in (13)”，与 quick-pass 分支一致。
2. Algorithm 1 原先在所有候选循环之后仅检查最后一个 `s'`，且失败返回变量未定义。现从队列取出当前 `(s, pi)` 后检查目标，成功返回当前 schedule；队列为空或预算用尽返回 failure。与 III-D4 的节点终止描述一致，算法仍为 17 行。属于伪代码修正，未声称重跑实验。
3. 实验引言加入 accompanying video 引用，满足附带多媒体在正文中被引用的要求。
4. 多媒体说明移除匿名占位联系信息，改为 Meng Guo 的正式单位和邮箱；使用 `PushAround.mp4`，修正时长、大小、最终 Fig.10 编号，并明确脚本对应的是二投回复。
5. 删除旧多媒体说明中“涵盖每个实验/每个数字”的过度表述；明确 Table II 与硬件逐试验记录不在包中，评估数据不等于完整规划器代码。

本轮校对修改保持黑字，蓝字仍只用于本轮审稿意见对应的澄清。

## 提交文件与尚需系统操作

`ral_final_submit/` 中的提交材料：

- `root.pdf`：正式干净版，8 页，小于 5 MB。
- `source.zip`：干净版 LaTeX 源码、IEEEtran 类及参考文献样式、BibTeX 数据和生成的 bbl、实际使用的 11 幅 PDF 图，小于 10 MB。PNG 原图在打包副本中无损嵌入 PDF，不缩放像素，工作区图文件不变。
- `multimedia.zip`：作者更新的原视频、ASCII `ReadMe.txt` 和 `Summary.txt`、二投已审阅的 evaluation_data，小于 50 MB。视频逐字节核对，未重新编码。
- `response.pdf`、`root_diff.pdf`、`response_and_diff.pdf`：供编辑核验，不能替代正式上传的干净稿。具体回复上传槽以 PaperCept 实际界面为准。

仍需通讯作者在 PaperCept 完成：

1. 核对作者列表、各作者资料、摘要和关键词。系统旧摘要与最终压缩版不同，需同步为最终 PDF 摘要。
2. 通过 IEEE Electronic Copyright Form 完成版权流程并返回 PaperCept；不是自行制作一个本地版权 PDF 就算完成。
3. 填写图数（11）、源文件格式（LaTeX），确认相关元数据和费用选项。按当前公开清单，8 页对应两页超页费，共 350 USD；系统账单为准。
4. 按系统指定终稿截止时间上传并最终确认，取得 `Final MS received` 状态及邮件回执。接收邮件要求接收后 14 天内完成，勿将本地打包完成当成已经提交。

## 检查范围

已阅读全文和 response，复核原始三份意见文件、回复关键数值及定位；正文重建无错误、Overfull 或未定义引用。干净版与蓝字版提取文字和分页一致，response 仍 5 页，合并版 13 页；最终论文各页版面及修改后的算法页已查看，无明显遮挡或溢出。字体嵌入通过检查。

打包脚本独立编译 production 源码副本，核对其正文与未优化的最终干净 PDF 的文字/分页；ZIP CRC 和大小检查通过后才输出成功。与未优化 PDF 比较是为了排除 Ghostscript 字体坐标舍入对数学重音字符提取顺序的影响。未重新运行仿真实验，未逐一重新验证全部参考文献的外部出版元数据。

## 官方依据

- [RA-L Final Submission Checklist](https://www.ieee-ras.org/publications/ra-l/final-submission-checklist/)：PDF、源码、多媒体大小与格式，版权流程、元数据、超页费及最终状态。
- [RA-L Information for Authors](https://www.ieee-ras.org/publications/ra-l/ra-l-information-for-authors/)：终稿和多媒体说明要求。

上述页面于 2026-10-21 重新核对。本文件是内部核验记录，不放入出版源码或多媒体包。
