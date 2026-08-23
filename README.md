<div align="center">

<img src="docs/assets/cover.png" alt="Awesome RL Handbook 封面" width="360">

# Awesome RL Handbook

**数学优先的中文强化学习讲义**

[![在线阅读](https://img.shields.io/badge/在线阅读-GitHub_Pages-8a5a2b?style=flat-square)](https://alfredzhang98.github.io/awesome_rl_handbook/)
[![版本](https://img.shields.io/github/v/tag/alfredzhang98/awesome_rl_handbook?style=flat-square&label=版本&color=3f7d58)](https://github.com/alfredzhang98/awesome_rl_handbook/tags)
[![课程](https://img.shields.io/badge/讲义-第_0–2_课_·_持续更新-555?style=flat-square)](https://alfredzhang98.github.io/awesome_rl_handbook/)
[![python](https://img.shields.io/badge/python-3.8+-3776ab?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/许可-仅供阅读_·_保留所有权利-8a5a2b?style=flat-square)](LICENSE)

</div>

一份**数学优先、零控制背景也能读**的中文强化学习讲义。路线图规划到 PPO / SAC，讲义按 Stage 顺序逐课写出来——每一课挑一个**小到能手算、又真能算到底**的例子，把公式落到具体的数上，并且说清楚**上一步在哪儿撑不住、这一步补了什么、又带来了什么新问题**。

## 特点

- **数学优先**：先给能手算的数，再给公式，每一步都算得到底。
- **数字可复现**：正文每个数都由随附脚本产出，一行命令就能重跑。
- **离线可读**：公式是预渲染的内联 SVG，断网双击任意一章都能看。
- **自带交互**：值迭代可以一格一格点着看，参数能现场拖。

## 目录

路线图把整条路线切成 6 个 Stage，已经写完的课如下（其余在路线图里列了完整知识点清单，逐课补）：

| 章节 | 内容 | 例子 |
|---|---|---|
| [路线图](https://alfredzhang98.github.io/awesome_rl_handbook/) | Stage 0–5 全景：学习链条、数学前置、全书符号、每阶段的核心概念 / 公式 / 理解 | —— |
| [第 0 课](https://alfredzhang98.github.io/awesome_rl_handbook/ch0.html) | 值函数 V 与最优值函数 V⋆ | 五格链 |
| [第 1 课](https://alfredzhang98.github.io/awesome_rl_handbook/ch1.html) | 马尔可夫决策过程与 Bellman 算子：γ-收缩、停机界、随机转移、表格法的边界 | 4×4 仓库网格 |
| [第 2 课](https://alfredzhang98.github.io/awesome_rl_handbook/ch2.html) | 动态规划：策略评估、策略改进与值迭代 | 4×4 仓库网格 |

接下来：第 3 课 蒙特卡罗与时序差分 → 第 4 课 SARSA → 第 5 课 Q-learning 与 off-policy → …

## 每日一问

正课之外的一个小板块：**每天挑一个强化学习问题想清楚**，写法和讲义一样——先给能手算的数，再给公式，图和数字全部跑出来。不定期更新。

全部问题见[总目录](https://alfredzhang98.github.io/awesome_rl_handbook/daily/)。

| 日期 | 问题 | 例子 |
|---|---|---|
| [Day 1](https://alfredzhang98.github.io/awesome_rl_handbook/daily/001.html) | 蒙特卡罗、TD、动态规划之间到底是什么关系 | **三站地铁** |

## 怎么读

从[路线图](https://alfredzhang98.github.io/awesome_rl_handbook/)开始：先看那张流程图和「这条链为什么是这个顺序」，再按 Stage 顺序读。每一课是独立的 HTML，自带侧边栏目录与上/下一章导航。

## 版本与发布

在线站点始终跟随 `main`；内容定稿会打 tag，改动记在 [Releases](https://github.com/alfredzhang98/awesome_rl_handbook/releases)。

## 许可

**版权所有，保留一切权利。本作品仅授权在线阅读**——详见 [LICENSE](LICENSE)。

## 写作方法

这套写法（先数后式、所有数字由脚本产出）已打包成 Claude Code Skill：`.claude/skills/handbook-style/`。
