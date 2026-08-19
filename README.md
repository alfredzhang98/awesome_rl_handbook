<div align="center">

<img src="docs/assets/cover.png" alt="Awesome RL Handbook 封面" width="360">

# Awesome RL Handbook

**数学优先的中文强化学习讲义**<br>
每一个数字都是脚本跑出来的，不是抄的

[![在线阅读](https://img.shields.io/badge/在线阅读-GitHub_Pages-8a5a2b?style=flat-square)](https://alfredzhang98.github.io/awesome_rl_handbook/)
[![版本](https://img.shields.io/github/v/tag/alfredzhang98/awesome_rl_handbook?style=flat-square&label=版本&color=3f7d58)](https://github.com/alfredzhang98/awesome_rl_handbook/tags)
[![课程](https://img.shields.io/badge/讲义-第_0–8_课-555?style=flat-square)](https://alfredzhang98.github.io/awesome_rl_handbook/)
[![python](https://img.shields.io/badge/python-3.8+-3776ab?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/许可-仅供阅读_·_保留所有权利-8a5a2b?style=flat-square)](LICENSE)

</div>

从 MDP 与 Bellman 算子（Stage 0–1），到无模型表格法（Stage 2）、函数逼近与致命三角（Stage 3）、DQN 家族（Stage 4）、策略梯度（Stage 5）——每一课都挑一个**小到能手算、又真能算到底**的例子，把公式落到具体的数上。

---

## 这份讲义想解决什么

大多数 RL 教程有两种极端：一种只给公式和收敛定理，你看完不知道它在算什么；另一种直接甩代码，跑通了但不知道为什么这么写。这份讲义走中间：

- **先给能手算的数，再给公式。** 第 1 课把 14 个格子的值表整个印在页面上，还附了闭式解让你逐格核对。
- **所有数字都由随附脚本产出。** 正文里出现的每个 0.7290、每张热力图，都能用一行命令重跑出来。
- **每一课都留下钩子。** 「表格法在这里撑不住」→ 下一课补哪个窟窿，链条不断。
- **页面自带交互。** 值迭代可以一格一格点着看，γ 和打滑概率都能现场拖。
- **离线可读。** 公式是预渲染的内联 SVG，任意一个 HTML 断网双击都能正常显示公式、图和交互组件。

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

> 最后一列标了每课当前用的例子。标着 CartPole 的几课是早期版本，会按同样的流程（先写实验脚本跑数字，再写正文）逐课翻新。

**建议顺序**：第 0 课 → 第 1 课 → 第 4 课往后。第 2、3 课是补课性质，卡住了再回头看。

## 第 1 课在讲什么

一台 AGV 在 4×4 仓库里找充电桩：14 个状态、4 个动作、每走一步 −1、γ = 0.9。整张值表印在页面上，而且有闭式解可以逐格核对：

```
从离充电桩 d 步的格子出发：V⋆ = −(1 − 0.9^d) / (1 − 0.9) = −10 (1 − 0.9^d)
```

值迭代跑出来的 14 个数与它**逐格相同，最大差 0.0**。跑出来的几个结论：

- **刷一遍，消息只走一格**：离充电桩 d 步的格子，正好在第 d 稿变准，14 格无一例外。这就是稀疏奖励难学的全部原因。
- **停机界能用但保守**：第 1 稿界说「最多还差 9.0」，实际 3.69。放大倍数 γ/(1−γ) 在 γ = 0.9 时是 9、0.99 时是 99——它是所有近似误差的公共放大器。
- **随机性一进来性质就变**：确定性时 7 遍精确收敛；加 10% 打滑后要 32 遍，两格的最优动作被改写（开始躲着墙走），而且永远差一点点。
- **加速的代价**：原地更新 + 悲观初值 + 从目标倒着扫，3 遍就到底（两张表要 7 遍）。但 DQN 的选择是反过来的——**宁可不要这份加速，也要把「上一稿」冻回来**（target network），因为在表格里合成一张只是慢，在神经网络里合成一张会发散。

## 仓库结构

```
docs/                       讲义正文，GitHub Pages 站点根目录（直接改这里）
  index.html                路线图
  ch0.html … ch8.html       第 0–8 课
  assets/book.css | book.js 侧边栏版式与本章小目录
grid_dp.py                  第 1 课数值后端：4×4 仓库的值迭代、闭式解核对、停机界、
                            打滑对照、扫描顺序实验；正文插图也由它产出
publish.py                  一步完成「提交 + 推送」
arm_dp.py / arm_figs.py     旧主线（协作臂关节）的数值后端与配图，暂时没有课在用
.claude/skills/handbook-style/   写这类讲义的方法，打包成可复用 skill
```

每一课是一个自带侧边栏与上/下一章导航的独立 HTML，跨章链接直接指向 `ch4.html` 这样的文件名。

## 自己重跑

```bash
python grid_dp.py           # 第 1 课的全部数字与插图（不到 1 秒）
```

```bash
python publish.py           # commit + push
```

GitHub Pages 从 `main` 分支的 `/docs` 发布。`.npy` 与 `arm_numbers.json` 是中间产物，不入库，重跑即得。

## 版本

内容定稿会打 tag，改动记在 [Releases](https://github.com/alfredzhang98/awesome_rl_handbook/releases)。在线站点始终跟随 `main`，想读某个定稿版本按 tag 检出即可。

| Tag | 内容 |
|---|---|
| `v0.1.0` | 路线图 Stage 0–12，第 0–8 课在线；第 1 课以 4×4 仓库网格为主线重写 |

## 许可

**版权所有，保留一切权利。本作品仅授权在线阅读**——详见 [LICENSE](LICENSE)。

| | |
|---|---|
| ✅ 可以 | 在[官方站点](https://alfredzhang98.github.io/awesome_rl_handbook/)或本仓库在线阅读；为个人学习在本地保存副本；链接到官方站点；为评论、教学、研究作合理的少量引用（注明作者与原链接） |
| ❌ 不可以 | **镜像或转载**（搬到其他网站、网盘、公众号、课程平台）；出版（印刷、电子书、投稿）；翻译、改写、节选重排等演绎；任何商业使用；用于训练模型或并入数据集 |

版权人保留全部权利，包括商业出版与另行授权。要做上面「不可以」里的事，[开个 issue](https://github.com/alfredzhang98/awesome_rl_handbook/issues) 单独谈。

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
