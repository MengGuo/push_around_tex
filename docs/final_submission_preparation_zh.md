# RA-L 26-3602 终稿格式整理

> 2026-10-21 更新：最终审查与打包已完成，源码及多媒体 ZIP 状态以 [final_audit_zh.md](final_audit_zh.md) 为准；本文保留前一轮记录。R5-2 的实验实现溯源限制尚未关闭。

更新日期：2026-10-20。此记录对应加入署名和出版信息后的终稿；此前的 `second_round_pdf_audit_zh.md` 保留为匿名正文版本的逐条审查记录。

## 已确认的信息

- 作者顺序：Zili Tang、Zongyuan Li、Zishao Qiao、Meng Guo；通讯作者为 Meng Guo，邮箱 `meng.guo@pku.edu.cn`。
- Zili Tang、Zishao Qiao、Meng Guo 署名 School of Advanced Manufacturing and Robotics；Zongyuan Li 署名 College of Engineering。共同学校及地址为 Peking University, Beijing 100871, China。
- 首次投稿：June 24, 2026；修回：September 16, 2026；接收：October 20, 2026。后两项由作者明确确认。
- 资助仅填写本篇确认的 NSFC U2241214 和 T2121002；未沿用上一篇的国家重点研发项目。
- 关键词与 PaperCept 一致：Multi-Robot Systems；Task and Motion Planning；Manipulation Planning。

## 格式处理及依据

依据 [RA-L Information for Authors](https://www.ieee-ras.org/publications/ra-l/ra-l-information-for-authors/) 的 Final Submission 要求，采用 IEEEtran journal、twoside、letterpaper、10pt；恢复署名、单位和通讯作者，添加稿件日期、Editor M. Ani Hsieh 推荐发表说明、资助和 DOI 占位脚注，并加入期刊及作者页眉、页码、关键词和引言首字下沉。

DOI 使用官方要求的占位说明 `Digital Object Identifier (DOI): see top of this page.`；未填写上一篇文章的 DOI、出版日期或 current version 日期。本稿无作者简介和照片。

为给新增首页信息腾出空间，初版曾收紧摘要、引言首段及 Our Method。随后按作者意见恢复方法概览的完整性，转而从重复背景与图注文字中腾出空间，详见 [compression_review_zh.md](compression_review_zh.md)。方法公式、实验数据、图表尺寸和字号保持不变，最终仍为 8 页。

## 文件与复现

- 上传候选 PDF：`ral_final_submit/root.pdf`，干净版，8 页、2,774,730 字节（约 2.77 MB），US Letter，PDF 1.5。
- 工作版：`ral_tex/root.pdf`，仅将针对本轮 comments 的澄清标蓝；上轮蓝字及本轮压缩措辞均为黑色。
- 未压缩干净版：`ral_tex/root_clean.pdf`。
- 日期集中在 `ral_tex/contents/final_metadata.tex`；署名、脚注和页眉在 `ral_tex/root.tex`。
- 在仓库根目录执行 `bash build_final.sh`，重新生成论文、当前 response、正文 diff 及二者合并版。脚本不运行旧 `build.sh`，不更新冻结的二投稿件包。response 与 diff 的本轮整理记录见 [final_response_and_diff_zh.md](final_response_and_diff_zh.md)。

根据 [Final Submission Checklist](https://www.ieee-ras.org/publications/ra-l/final-submission-checklist/) 的 PDF 大小要求，对上传候选文件进行质量 95 的彩色图像编码优化；不降低图像像素尺寸，灰度数据及透明度掩码保持无损。图像编码优化不等于所有彩色图像均无损。

## 已做检查及后续范围

- 工作版和干净版编译均无 LaTeX 错误、Overfull 或未定义引用。
- 上传候选 PDF 为 8 页、低于 5 MB，字体全部嵌入；与原始干净版对比，非空白字符计数一致、图像像素尺寸不变。
- 检查最终干净 PDF 的首页和末页渲染，署名、脚注、页眉及参考文献无遮挡；此前正文核验时已检查新增段落及段末短行。
- 首页终稿格式整理时未修改 response；作者随后授权编写，本轮 response 与 diff 已完成，见上方记录。
- 当前已完成论文、response 和 diff PDF 及构建脚本；尚未整理上传用源码 ZIP、多媒体 ZIP 和版权表单，未向 PaperCept 提交。

首页格式整理时检查 PDF 的 SHA-256：`886f8670eb1e5d948c150ad9dadb8d23025b169ede5225cce98618e554ed7da0`。重新构建可能因时间戳而改变哈希。
