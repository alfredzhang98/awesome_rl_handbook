# Awesome RL Handbook

数学优先、面向 robotics 的一份强化学习讲义：从 MDP 与 Bellman 算子（Stage 0–1），到无模型表格法（Stage 2）、函数逼近与致命三角（Stage 3）、DQN 家族（Stage 4）、策略梯度（Stage 5），全程用同一个例子从头跑到尾，公式都能在页面里直接看到数字。

**在线阅读**：https://alfredzhang98.github.io/awesome_rl_handbook/

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
awesome_rl_handbook.html   讲义原稿（单文件版，可直接双击打开）
split_book.py               切分脚本：把原稿拆成多页 + 生成侧边栏目录
docs/                       多页版（GitHub Pages 站点根目录）
  index.html                路线图
  ch0.html … ch8.html       第 0–8 课
  assets/book.css | book.js 侧边栏版式与目录脚本
```

正文内容与原稿逐字一致，切分只重写了跨章锚点（`#l4` → `ch4.html`）并加了导航。
数学公式是内联 SVG，按每页实际用到的字形分发，离线双击任意 HTML 都能正常显示。

改了原稿之后，在仓库根目录运行 `python split_book.py` 即可重新切分；`python publish.py` 一步完成「重切 + 提交 + 推送」。

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
按 handbook-style 给这份讲义加第 9 课：〈主题〉
按 handbook-style 检查这一课，重点看图题和数字来源
```
