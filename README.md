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

## 怎么读

从[路线图](https://alfredzhang98.github.io/awesome_rl_handbook/)开始，它给了 Stage 0–12 的全景。每一课是独立的 HTML，自带侧边栏目录与上/下一章导航。

## 版本与发布

在线站点始终跟随 `main`；内容定稿会打 tag，改动记在 [Releases](https://github.com/alfredzhang98/awesome_rl_handbook/releases)。

## 许可

**版权所有，保留一切权利。本作品仅授权在线阅读**——详见 [LICENSE](LICENSE)。

## 写作方法

这套写法（先数后式、所有数字由脚本产出）已打包成 Claude Code Skill：`.claude/skills/handbook-style/`。
