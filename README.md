<div align="center">

<img src="docs/assets/cover.png" alt="Awesome RL Handbook 封面" width="360">

# Awesome RL Handbook

**数学优先的中文强化学习讲义**

[![在线阅读](https://img.shields.io/badge/在线阅读-GitHub_Pages-8a5a2b?style=flat-square)](https://alfredzhang98.github.io/awesome_rl_handbook/)
[![版本](https://img.shields.io/github/v/tag/alfredzhang98/awesome_rl_handbook?style=flat-square&label=版本&color=3f7d58)](https://github.com/alfredzhang98/awesome_rl_handbook/tags)
[![课程](https://img.shields.io/badge/讲义-第_0–8_课-555?style=flat-square)](https://alfredzhang98.github.io/awesome_rl_handbook/)
[![python](https://img.shields.io/badge/python-3.8+-3776ab?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/许可-仅供阅读_·_保留所有权利-8a5a2b?style=flat-square)](LICENSE)

</div>

一份**数学优先、面向 robotics** 的中文强化学习讲义：从 MDP 与 Bellman 算子出发，一路走到无模型表格法、函数逼近、DQN 与策略梯度。每一课都挑一个**小到能手算、又真能算到底**的例子，把公式落到具体的数上。

## 特点

- **数学优先**：先给能手算的数，再给公式，每一步都算得到底。
- **数字可复现**：正文每个数都由随附脚本产出，一行命令就能重跑。
- **离线可读**：公式是预渲染的内联 SVG，断网双击任意一章都能看。
- **自带交互**：值迭代可以一格一格点着看，参数能现场拖。

## 目录

| 章节 | 内容 | 例子 |
|---|---|---|
| [路线图](https://alfredzhang98.github.io/awesome_rl_handbook/) | Stage 0–12 全景：每阶段的核心概念、核心公式、核心知识点理解与对应讲义 | —— |
| [第 0 课](https://alfredzhang98.github.io/awesome_rl_handbook/ch0.html) | V 与 V⋆ 到底是什么：把一个具体的数一遍一遍刷出来 | 五格链 |
| [第 1 课](https://alfredzhang98.github.io/awesome_rl_handbook/ch1.html) | **Stage 0–1**：MDP 五要素、Bellman 算子的 γ-收缩与停机界、值迭代刷出整张表、打滑引出期望，以及表格法的天花板 | **4×4 仓库网格** |
| [第 2 课](https://alfredzhang98.github.io/awesome_rl_handbook/ch2.html) | Stage 0–1 补课：有模型 ≠ 有解析解，以及 V / Q / A 分别在算什么 | CartPole |
| [第 3 课](https://alfredzhang98.github.io/awesome_rl_handbook/ch3.html) | Stage 0 深入：值函数与 Bellman 方程在数学上到底在做什么 | CartPole |
| [第 4 课](https://alfredzhang98.github.io/awesome_rl_handbook/ch4.html) | Stage 2：无模型表格法 MC / TD / SARSA / Q-learning | CartPole |
| [第 5 课](https://alfredzhang98.github.io/awesome_rl_handbook/ch5.html) | Stage 2 补完：n-step、TD(λ)、Dyna、重要性采样 | CartPole |
| [第 6 课](https://alfredzhang98.github.io/awesome_rl_handbook/ch6.html) | Stage 3：把表换成函数，以及所有收敛保证是怎么坏掉的 | CartPole |
| [第 7 课](https://alfredzhang98.github.io/awesome_rl_handbook/ch7.html) | Stage 4：DQN 家族，三个补丁各修一处 | CartPole |
| [第 8 课](https://alfredzhang98.github.io/awesome_rl_handbook/ch8.html) | Stage 5：策略梯度，不再学值再取 argmax | CartPole |

> 最后一列标了每课当前用的例子。标着 CartPole 的几课是早期版本，会按同样的流程逐课翻新。

## 怎么读

从[路线图](https://alfredzhang98.github.io/awesome_rl_handbook/)开始，它给了 Stage 0–12 的全景。每一课是独立的 HTML，自带侧边栏目录与上/下一章导航。

## 版本与发布

在线站点始终跟随 `main`；内容定稿会打 tag，改动记在 [Releases](https://github.com/alfredzhang98/awesome_rl_handbook/releases)。

## 许可

**版权所有，保留一切权利。本作品仅授权在线阅读**——详见 [LICENSE](LICENSE)。

## 写作方法

这套写法（先数后式、所有数字由脚本产出）已打包成 Claude Code Skill：`.claude/skills/handbook-style/`。
