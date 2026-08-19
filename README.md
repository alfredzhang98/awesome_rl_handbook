# Awesome RL Handbook

数学优先、面向 robotics 的一份中文强化学习讲义。从 MDP 与 Bellman 算子（Stage 0–1），到无模型表格法（Stage 2）、函数逼近与致命三角（Stage 3）、DQN 家族（Stage 4）、策略梯度（Stage 5）——**每一阶段都落到同一台机器上算出具体的数**，公式后面跟着的都是跑出来的结果，不是抄的。

**在线阅读 → https://alfredzhang98.github.io/awesome_rl_handbook/**

## 每一课都有一个能把数算到底的例子

第 1 课是**一台 AGV 在 4×4 仓库里找充电桩**：14 个状态、4 个动作、每走一步 −1、γ = 0.9。整张值表就印在页面上，而且有闭式解可以逐格核对——

```
从离充电桩 d 步的格子出发：V⋆ = −(1 − 0.9^d) / (1 − 0.9) = −10 (1 − 0.9^d)
```

值迭代跑出来的 14 个数与它**逐格相同（最大差 0.0）**。所以这一课的每一句话你都能自己验：备份摊开成 4 行、收敛用相邻两稿的界卡住、传播规律是「离桩 d 步的格子正好第 d 稿变准」。往后再换更难的系统，尺子始终是这一把。

## 目录

| 章节 | 内容 | 主线 |
|---|---|---|
| [路线图](https://alfredzhang98.github.io/awesome_rl_handbook/) | Stage 0–12 全景：每阶段的核心算法、必须自己推一遍的数学、能看见差别的实验 | 机械臂 |
| [第 0 课](https://alfredzhang98.github.io/awesome_rl_handbook/ch0.html) | V 与 V⋆ 到底是什么：把一个具体的数一遍一遍刷出来 | 五格链 |
| [第 1 课](https://alfredzhang98.github.io/awesome_rl_handbook/ch1.html) | **Stage 0–1**：把仓库写成 MDP、Bellman 算子的 γ-收缩与停机界、值迭代刷出整张表、打滑引出期望，以及表格法的天花板（直通 DQN 三个补丁） | **4×4 仓库网格** |
| [第 2 课](https://alfredzhang98.github.io/awesome_rl_handbook/ch2.html) | Stage 0–1 补课：有模型 ≠ 有解析解，以及 V / Q / A 分别在算什么 | CartPole |
| [第 3 课](https://alfredzhang98.github.io/awesome_rl_handbook/ch3.html) | Stage 0 深入：值函数与 Bellman 方程在数学上到底在做什么 | CartPole |
| [第 4 课](https://alfredzhang98.github.io/awesome_rl_handbook/ch4.html) | Stage 2：无模型表格法 MC / TD / SARSA / Q-learning | CartPole |
| [第 5 课](https://alfredzhang98.github.io/awesome_rl_handbook/ch5.html) | Stage 2 补完：n-step、TD(λ)、Dyna、重要性采样 | CartPole |
| [第 6 课](https://alfredzhang98.github.io/awesome_rl_handbook/ch6.html) | Stage 3：把表换成函数，以及所有收敛保证是怎么坏掉的 | CartPole |
| [第 7 课](https://alfredzhang98.github.io/awesome_rl_handbook/ch7.html) | Stage 4：DQN 家族，三个补丁各修一处 | CartPole |
| [第 8 课](https://alfredzhang98.github.io/awesome_rl_handbook/ch8.html) | Stage 5：策略梯度，不再学值再取 argmax | CartPole |

> 表格最后一列标了每课当前用的例子。标着 CartPole 的几课是早期版本，会按同样的流程（先写实验脚本跑数字，再写正文）逐课换成机械臂。

### 第 1 课跑出来的几个结论

- **值迭代收敛到的就是「最优地走下去能拿多少」这句话本身**：14 个格子与闭式解 −10(1−0.9^d) 逐格相同，最大差 0.0。
- **刷一遍，消息只走一格**：离充电桩 d 步的格子，正好在第 d 稿变准，14 格无一例外。这就是稀疏奖励难学的全部原因。
- **停机界能用但保守**：第 1 稿界说「最多还差 9.0」，实际 3.69。放大倍数 γ/(1−γ) 在 γ = 0.9 时是 9，0.99 时是 99——它是所有近似误差的公共放大器。
- **随机性一进来，性质就变了**：确定性时 7 遍精确收敛；地面加 10% 打滑后要 32 遍，两格的最优动作翻向（开始躲着墙走），而且永远差一点点。
- **加速的代价**：原地更新 + 悲观初值 + 从目标倒着扫，3 遍就到底（两张表要 7 遍）。但 DQN 的选择是反过来的——**宁可不要这份加速，也要把「上一稿」冻回来**（target network），因为在表格里合成一张只是慢，在神经网络里合成一张会发散。

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
