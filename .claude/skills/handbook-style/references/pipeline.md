# 生产流水线

目标：**一个单文件 HTML，双击能开、断网能看、公式和图都在里面**。所以整条流水线的硬约束是「零外部请求」。

---

## 1. 先跑实验，后写字

每一课配一到两个脚本，命名说清职责：

```
arm_dp.py     动力学、离散化、值迭代、折扣 LQR       ← 出数字
arm_figs.py   作图与对比实验                         ← 出图
```

脚本要求：

- 固定随机种子，参数写在文件顶部，改完能一键重跑。
- 把正文要引用的数打印成一张表（收敛率、误差界、格点数、耗时），写讲义时照抄。
- 记录**整跑耗时**，写进 `<footer>`（「改参数重跑大约 90 秒」）。

## 2. 双主题配图

CSS token 与 matplotlib 配色对应关系：

| 用途 | 亮色 | 暗色 |
|---|---|---|
| 画布/背景 | `#faf9f7` | `#16151a` |
| 主文字 | `#1c1b19` | `#eceaf2` |
| 次要文字/网格 | `#7d7a73` | `#87848f` |
| 强调（主色） | `#8a5a2b` | `#d8a26a` |
| 正面/收敛（绿） | `#3f7d58` | `#7cc79b` |
| 当前/警示（橙） | `#a8551f` | `#e8a273` |

同一张图渲染两遍，只换配色，**尺寸与布局完全一致**，然后：

```bash
# 每张图两版 → webp（质量 80 左右，几十 KB 一张）
python arm_figs.py                 # 产出 fig_xx.light.png / fig_xx.dark.png
cwebp -q 80 fig_xx.light.png -o fig_xx.light.webp
```

嵌入时亮色放 `<img src>`，暗色放 `<source media="(prefers-color-scheme: dark)">`：

```python
import base64, pathlib
def embed(p): return "data:image/webp;base64," + base64.b64encode(pathlib.Path(p).read_bytes()).decode()
```

- `alt` 写公式含义（`alt="V_k(s0) 逐遍逼近 V*(s0)"`），不是「图片」。
- 一张图别超过 ~120 KB base64；31 张图的手册最终 6.5 MB，还能双击秒开。

## 3. 公式预渲染成内联 SVG

正文里写 LaTeX，最后整篇跑一次 MathJax，把 `$…$` / `$$…$$` 换成 SVG：

```bash
npm i -g mathjax-node-page
mjpage --output CommonHTML --format "TeX" --svg < draft.html > handbook.html
```

结果形态（照着检查就行）：

- 行内：`<span class="mj"><svg …><use xlink:href="#MJX-TEX-I-1D449"></use></svg></span>`
- 展示：`<span class="mj mjd">…</span>`，外面套 `<div class="math">`
- 所有字形 `<path id="MJX-TEX-…">` 收在 body 顶部一个隐藏的 `<svg style="display:none"><defs>…</defs></svg>`

**校验**：页面里出现的每个 `xlink:href="#MJX-…"` 都必须能在 `<defs>` 里找到同名 `<path>`；拆页时尤其要重查（每页只带该页用到的字形）。

符号约定：

- 最优量 `V^\star / Q^\star / \pi^\star` → 渲染成 ⋆。正文行文里也用 ⋆，**不要用黑星 ★**（它不是数学符号，字重和基线都不对）。
- 迭代次数 `k`，时刻 `t`，两者不混用；换符号必须在正文公告。
- 关键式子用 `\underbrace{r_t + \gamma V(s_{t+1})}_{\text{目标（一个样本）}}` 给每一块起名字。

## 4. 交互组件

- 数据要和公式对得上：`.wgt-stat` 里的「本轮最大改动」就是 `‖V_k − V_{k−1}‖∞`，「残余权重」就是 `γ^k`。
- 只用原生 DOM + canvas，不引任何库（外部请求会破坏离线可用）。
- 脚本放在所属 `<section>` 内的 `<script>`，IIFE 包住，所有 id 加组件前缀。
- 默认停在第 0 步，等读者点「算一格」；「自动」用 `setInterval` 并在再次点击时清掉。

## 5. 切分成网页书

单文件适合发给人 / 存档，网页书适合阅读。本仓库已经切完，只留网页书形态（`docs/`：index.html + ch0..ch8.html + assets/），之后直接改各页 HTML。从单文件切一遍要做的事（改造新讲义时照搬）：

- 按 `<section class="doc lesson" id="lN">` 切页，正文**逐字不动**，只重写跨章锚点（`#l4` → `ch4.html`）。
- 抽出 `<head>` 里的样式到 `assets/book.css`，追加侧栏版式。
- 每页只带该页用到的 MathJax 字形，页面仍可离线双击打开。
- 侧栏目录按 Stage 分组；本章 § 小目录由 JS 从 `h2` 生成（不改正文），标题里的公式用 `<use data-c>` 的码位 + NFKC 还原成可读字符。
- 写 `docs/.nojekyll`、`SUMMARY.md`（GitBook 形态）。

## 6. 发布

```bash
python publish.py                  # 有改动才 commit + push
python publish.py -m "自定义信息"
```

GitHub Pages：Settings → Pages → Deploy from a branch → `main` / `/docs`。
想让「我改完就自动发布」，在 `.claude/settings.local.json` 里挂一个 Stop hook 调 `publish.py --quiet`。
