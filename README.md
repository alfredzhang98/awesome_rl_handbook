# Awesome RL Handbook

数学优先、面向 robotics 的一份中文强化学习讲义。从 MDP 与 Bellman 算子（Stage 0–1），到无模型表格法（Stage 2）、函数逼近与致命三角（Stage 3）、DQN 家族（Stage 4）、策略梯度（Stage 5）——**每一阶段都落到同一台机器上算出具体的数**，公式后面跟着的都是跑出来的结果，不是抄的。

**在线阅读 → https://alfredzhang98.github.io/awesome_rl_handbook/**

## 主线例子：一台协作臂的关节

讲义不拿玩具环境当摆设。主线是**协作臂的单个关节**——带重力、力矩有上限、50 Hz：

```
I θ̈ = τ − b θ̇ + mgl sin θ        I = 0.075 kg·m²   mgl = 2.943 N·m   τ ≤ 2 N·m
```

θ = 0 是「举直」的不稳定平衡（开环特征值模长 1.1199，什么都不做一秒放大 240 倍）。同一个问题会被求两遍：**值迭代硬刷**一遍，**折扣 Riccati 解析算**一遍，然后看两者在哪一段重合、在哪一段分家。再往后，这台关节升级成肩+肘两关节、6 轴整臂，一路把每个 Stage 的动机逼出来。

## 目录

| 章节 | 内容 | 主线 |
|---|---|---|
| [路线图](https://alfredzhang98.github.io/awesome_rl_handbook/) | Stage 0–12 全景：每阶段的核心算法、必须自己推一遍的数学、能看见差别的实验 | 机械臂 |
| [第 0 课](https://alfredzhang98.github.io/awesome_rl_handbook/ch0.html) | V 与 V⋆ 到底是什么：把一个具体的数一遍一遍刷出来 | 五格链 |
| [第 1 课](https://alfredzhang98.github.io/awesome_rl_handbook/ch1.html) | **Stage 0 + Stage 1**：把关节写成 MDP、Bellman 算子的 γ-收缩、离散化与插值、值迭代 ↔ 折扣 LQR 的那座桥 | **机械臂关节** |
| [第 2 课](https://alfredzhang98.github.io/awesome_rl_handbook/ch2.html) | Stage 0–1 补课：有模型 ≠ 有解析解，以及 V / Q / A 分别在算什么 | CartPole |
| [第 3 课](https://alfredzhang98.github.io/awesome_rl_handbook/ch3.html) | Stage 0 深入：值函数与 Bellman 方程在数学上到底在做什么 | CartPole |
| [第 4 课](https://alfredzhang98.github.io/awesome_rl_handbook/ch4.html) | Stage 2：无模型表格法 MC / TD / SARSA / Q-learning | CartPole |
| [第 5 课](https://alfredzhang98.github.io/awesome_rl_handbook/ch5.html) | Stage 2 补完：n-step、TD(λ)、Dyna、重要性采样 | CartPole |
| [第 6 课](https://alfredzhang98.github.io/awesome_rl_handbook/ch6.html) | Stage 3：把表换成函数，以及所有收敛保证是怎么坏掉的 | CartPole |
| [第 7 课](https://alfredzhang98.github.io/awesome_rl_handbook/ch7.html) | Stage 4：DQN 家族，三个补丁各修一处 | CartPole |
| [第 8 课](https://alfredzhang98.github.io/awesome_rl_handbook/ch8.html) | Stage 5：策略梯度，不再学值再取 argmax | CartPole |

> 表格最后一列标了每课当前用的例子。标着 CartPole 的几课是早期版本，会按同样的流程（先写实验脚本跑数字，再写正文）逐课换成机械臂。

### 第 1 课跑出来的几个结论

- **桥**：网格加密一倍，小角度区与 LQR 解析解的中位偏差 44.6% → 15.0% → 4.7%。但结论是反的——**在这一端网格 DP 更差还更贵**，LQR 在这里就是精确解。
- **收缩率不是 γ**：实测每轮衰减 0.925，理论上界 γ = 0.98 明显松；真正的速度是 γ·|λ_cl| = 0.98 × 0.9176 = **0.899**，由最优闭环极点决定。
- **两个角度**：20.18° = τ_max/K₁ 起力矩饱和；42.81° = arcsin(τ_max/mgl) 之后，静止时物理上就拉不住。
- **最反直觉的一条**：把力矩上限压到 0.8 N·m（重力矩的 27%），2401 个初值里截断 LQR 收住 549 个，网格 DP 也是 **549 个，一个都没多救**。所以 RL 的入场券是另外三张：维数（6 关节 9.85×10²⁴ 个格点）、未知模型、非二次代价。

## 仓库结构

```
awesome_rl_handbook.html    讲义原稿（单文件，6 MB，双击即可离线阅读）
split_book.py               切分脚本：原稿 → docs/ 多页版 + 侧边栏目录
publish.py                  一步完成「重切 + 提交 + 推送」
arm_dp.py                   第 1 课数值后端：动力学、离散化值迭代、折扣 LQR、五组实验
arm_figs.py                 第 1 课四张图（亮/暗两版 → webp → base64 内嵌）
docs/                       多页版，GitHub Pages 站点根目录
  index.html                路线图
  ch0.html … ch8.html       第 0–8 课
  assets/book.css | book.js 侧边栏版式与本章小目录
.claude/skills/handbook-style/   写这类讲义的方法，打包成可复用 skill
```

多页版的正文与原稿逐字一致，切分只做三件事：重写跨章锚点（`#l4` → `ch4.html`）、把行文里的黑星 ★ 统一成公式里的 ⋆、加导航。
数学公式是 MathJax 预渲染的内联 SVG，按每页实际用到的字形分发——**任意一个 HTML 断网双击都能正常显示公式、图和交互组件**。

## 自己重跑

```bash
python arm_dp.py --json     # 第 1 课的全部数字（约 3 分钟）
python arm_figs.py          # 第 1 课的四张图（约 2 分钟）
python split_book.py        # 原稿 → docs/
python publish.py           # 重切 + commit + push
```

GitHub Pages 从 `main` 分支的 `/docs` 发布。`.npy` 与 `arm_numbers.json` 是中间产物，不入库，重跑即得。

## 写作方法已经打包成 Claude Code Skill

`.claude/skills/handbook-style/` 把这份讲义的写法整理成了一个可复用的 skill：一个例子贯穿到底、先给能手算的数字再给公式、所有数字必须由脚本跑出来、组件词典、公式与双主题配图规范、语气句式、交稿自检 25 条，外加可直接套用的设计系统 CSS 和空白骨架。

```
.claude/skills/handbook-style/
  SKILL.md                    方法总纲
  references/components.md    组件词典（.key/.warn/.big/.card/.wgt/figure/SVG…）
  references/writing.md       语气、句式、修辞与禁忌
  references/pipeline.md      公式预渲染、双主题配图、切书与发布
  references/checklist.md     交稿前 25 条自检
  assets/handbook.css         完整设计系统（亮/暗双色板）
  assets/skeleton.html        空白讲义骨架
```

### 安装到你自己的机器

在任意项目里打开 Claude Code，把下面这段整个粘进去：

```text
把 https://github.com/alfredzhang98/awesome_rl_handbook 里的 .claude/skills/handbook-style
安装成我的个人 skill：

1. 用 git clone --depth 1 把仓库拉到临时目录（或用 curl 拿 tar 包解压）；
2. 把整个 handbook-style 目录（含 SKILL.md、references/、assets/）
   复制到 ~/.claude/skills/handbook-style/，保持目录结构不变；
3. 删掉临时目录；
4. 读一遍 ~/.claude/skills/handbook-style/SKILL.md 的 frontmatter，
   确认 name 是 handbook-style、description 完整；
5. 告诉我装好了，以及之后我说"按 handbook-style 写一份 XX 讲义"时你会怎么开工。

装好后我需要重启 Claude Code 或打开一次 /skills 才能在列表里看到它——如果需要，提醒我。
```

只想在某个项目里用，就把第 2 步的目标改成那个项目的 `.claude/skills/handbook-style/`。

### 用法

```text
按 handbook-style 写一份〈主题〉讲义，主线例子用〈某个具体系统〉
按 handbook-style 把第 4 课的主线从 CartPole 换成机械臂
按 handbook-style 检查这一课，重点看图题和数字来源
```
