# 强化学习学习手册 · 以 CartPole 为主线

数学优先、面向 robotics 的一份强化学习讲义：从 MDP 与 Bellman 算子（Stage 0–1），到无模型表格法（Stage 2）、函数逼近与致命三角（Stage 3）、DQN 家族（Stage 4）、策略梯度（Stage 5），全程用同一个 CartPole 例子跑到底，公式都能在页面里直接看到数字。

**在线阅读**：https://ALFRED-GH-USER.github.io/REPO-NAME/

## 目录

| 章节 | 内容 |
|---|---|
| [路线图](docs/index.html) | Stage 0–12 全景、每一阶段的核心算法与必须自己推的数学 |
| 第 0 课 | V 与 V★ 的含义 |
| 第 1 课 | Stage 0 + Stage 1：MDP、Bellman 算子，与通向 LQR 的那座桥 |
| 第 2 课 | Stage 0–1 补课：有模型 ≠ 有解析解，以及 V / Q / A 在算什么 |
| 第 3 课 | Stage 0 深入：值函数与 Bellman 方程在数学上到底在做什么 |
| 第 4 课 | Stage 2：无模型表格法 MC / TD / SARSA / Q-learning |
| 第 5 课 | Stage 2 补完：n-step、TD(λ)、Dyna、重要性采样 |
| 第 6 课 | Stage 3：把表换成函数，以及所有保证是怎么坏掉的 |
| 第 7 课 | Stage 4：DQN 家族，三个补丁各修一处 |
| 第 8 课 | Stage 5：策略梯度，不再学值再取 argmax |

完整目录见 [`docs/SUMMARY.md`](docs/SUMMARY.md)。

## 仓库结构

```
RL_Handbook_CartPole.html   讲义原稿（单文件版，可直接双击打开）
split_book.py               切分脚本：把原稿拆成多页 + 生成侧边栏目录
docs/                       多页版（GitHub Pages 站点根目录）
  index.html                路线图
  ch0.html … ch8.html       第 0–8 课
  assets/book.css | book.js 侧边栏版式与目录脚本
```

正文内容与原稿逐字一致，切分只重写了跨章锚点（`#l4` → `ch4.html`）并加了导航。
数学公式是内联 SVG，按每页实际用到的字形分发，离线双击任意 HTML 都能正常显示。

改了原稿之后，在仓库根目录运行 `python split_book.py` 即可重新切分。
