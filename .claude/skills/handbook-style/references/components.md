# 组件词典

样式定义见 `assets/handbook.css`。下面每个组件给出：用途、边界、可直接复制的标记。
所有颜色只准用 `var(--…)` token，深色模式自动跟随。

---

## 1. 课头 header

```html
<div class="parttag">第 4 课 · Stage 2 · 无模型表格法</div>
<header>
  <div class="kicker">第四课 · STAGE 2 · 无模型表格法</div>
  <h1>没有模型的时候<br>MC / TD / SARSA / Q-learning</h1>
  <p class="lede">前面三课的每一个数字，都是算出来的——因为 <em>r</em> 和 <em>s'</em> 你都知道。这一课把模型拿走，只留下一条条跑出来的轨迹。</p>
</header>
```

- `.parttag`：全大写小字 + 字距，右侧自动接一条横线（`:after`）。给的是**这一课在全书里的坐标**。
- `.kicker`：主色，重复课号 + Stage，视觉上把 header 顶起来。
- `h1`：**两行**。第一行白话现象（「没有模型的时候」「把表换成函数」），第二行术语或副题。
- `.lede`：3 句以内。第一句接住上一课，第二句说这一课拿掉/加上了什么，第三句给一个「你会看到」。

## 2. `.big` 领读句

把定义翻译成大白话，通常带 `＝`。一节最多一个，放在正式定义**之前**。

```html
<div class="big">
<span class="mj">V_k(s)</span> ＝ <strong>从 s 出发，如果只允许你再走 k 步，你最多能拿到多少</strong>（折现之后）。
</div>
```

## 3. `.key` 结论块

绿色左边框。**这一节的那一句话**。开头必须是 `<b>完整断言。</b>`，后面才展开。

```html
<div class="key">
<b>盯住三件事。</b>
<ul style="margin:8px 0 0">
<li><b>消息从终点倒着往外传。</b>刷一遍，消息走一格。……<strong>这就是稀疏奖励难学的全部原因</strong>，跟算法聪不聪明无关。</li>
<li><b>每一格都是拿上一稿算的。</b>这正是 V_k = T V_{k−1} 里那个下标。</li>
<li><b>什么时候停：刷一遍数字不再变。</b>朴素到不像个定理的一句话。</li>
</ul>
</div>
```

边界：一节 ≤ 1 个。列表最多 3 条。不要把推导塞进来，`.key` 只放结论。

## 4. `.warn` 提醒块

虚线框、无底色。四种用途，都以 `<b>…</b>` 开头：

```html
<div class="warn"><b>读书时的一个坑。</b>本文 r_t 表示"在 (s_t,a_t) 上拿到的奖励"……但 Sutton &amp; Barto 写作 R_{t+1}：内容一样，记账起点差一格——读那本书觉得下标不对时，不是你看错了。</div>
```

- 符号约定差异（「看论文先确认符号约定」）
- 常见误算（「如果去掉自环，答案就完全不同——而且很多人第一反应算的是这个」）
- 实践坑，成对出现时编号（「坑一：连续动作空间里 max_a 本身就是个优化问题」「坑二：控制频率越高，……」）
- 回收伏笔（「回收一个前面留下的谜」）

## 5. 公式

```html
<p>规则简单到没有任何歧义：</p>
<div class="math"><span class="mj mjd">…MathJax 渲染出的 SVG…</span></div>
<p class="small">先记住这个数 <b>6.5610</b>。下面我们<strong>假装不知道它</strong>，用"刷"的方式一步一步把它逼出来。</p>
```

- `.math` 是灰底圆角容器，可横向滚动；里面可以放多行 `<p>`（把「先…再…」两步式子放一起）。
- 行内公式 `<span class="mj">`，不要额外容器。
- 公式后紧跟 `.small` 或普通段落做白话复述。

## 6. 表格

三种典型用法，都用 `class="num"` 对齐数字列：

```html
<!-- ① 逐行长出来的迭代表：最后一列固定是"这一行在回答什么" -->
<tr><th>刷第几遍</th><th>s_A</th>…<th>这一行在回答</th></tr>
<tr><td class="num">k=3</td>…<td>只剩 3 步能拿多少</td></tr>

<!-- ② 对照表：左列是命题，右列是"还成立吗" -->
<tr><th></th><th>还成立吗</th></tr>
<tr><td>Bellman 方程 V*(s)=max…</td><td><b>成立</b>，一个字没改</td></tr>

<!-- ③ 方法对照：目标是什么 / 怎么更新 -->
<tr><th></th><th>目标是什么</th><th>怎么更新</th></tr>
<tr><td><b>DP（有模型）</b></td><td>r + γΣP V 精确期望</td><td>V ← 直接赋值</td></tr>
```

关键数字用 `<b>`；收敛率这类要**连列 8–10 行**让读者自己看出规律，不要只给两行再断言。

## 7. `.card` 算法卡

一个方法的说明书。四栏 `<dl>` 固定为：输入 / 一次迭代 / 输出 / **失效点**。

```html
<div class="card">
  <div class="role">已知模型 · 全局解</div>
  <h4>值迭代 / 策略迭代（DP）</h4>
  <dl>
    <dt>输入</dt><dd>转移 P、代价、离散化后的状态与动作集合</dd>
    <dt>一次迭代</dt><dd>对<b>每一个状态</b>：枚举所有动作，取最优，写回 V</dd>
    <dt>输出</dt><dd><b>全局</b>的 V* 和 π*：状态空间里每一点都有答案</dd>
    <dt>失效点</dt><dd>状态维数一高就爆炸……<b>这就是 RL 存在的原因。</b></dd>
  </dl>
</div>
```

「失效点」是这张卡的重点——每个方法都要写清楚它在哪断掉，下一个方法才有存在理由。

## 8. `<figure>` 数据图

```html
<figure>
  <picture>
    <source srcset="data:image/webp;base64,…暗色版…" media="(prefers-color-scheme: dark)">
    <img src="data:image/webp;base64,…亮色版…" alt="V_k(s0) 逐遍逼近 V*(s0)">
  </picture>
  <figcaption>左：每刷一遍，级数就<b>多加恰好一项</b> γ^{k−5}（蓝色小块），累计值（橙线）爬向虚线 V*。前 4 遍够不着奖励，全是 0。右：还差多少，与 γ^k 完全重合——差距就是<b>级数还没加完的那条尾巴</b>。</figcaption>
</figure>
```

图题写法：**左：… 右：…**，逐块说该看什么，带真实数字，结论词加粗。不要写「图 3 展示了收敛过程」这种废话。

## 9. 手绘 SVG 示意图

结构图（状态转移、开关面、数据流）直接写 SVG，靠 `currentColor` 适配深浅色：

```html
<svg class="cliffsvg" viewBox="0 0 660 250" xmlns="http://www.w3.org/2000/svg" fill="none">
  <defs><marker id="ah" markerWidth="9" markerHeight="7" refX="8.5" refY="3.5" orient="auto">
    <path d="M0,0 L9,3.5 L0,7 z" fill="currentColor"/></marker></defs>
  <g stroke="currentColor" stroke-width="1.4" marker-end="url(#ah)">…</g>
  <g font-size="13" font-family="inherit" fill="currentColor">…</g>
</svg>
```
```css
.cliffsvg{width:100%;max-width:660px;display:block;margin:18px auto;color:var(--ink-2)}
```
危险/错误的那条边可以单独给 `stroke="#c0392b"`。

## 10. `.wgt` 交互组件

```html
<div class="wgt" id="cw">
  <div class="wgt-head">交互 · 刷一遍 = 作用一次 T</div>
  <div class="wgt-body">
    <div class="chain" id="cw-nodes"></div>      <!-- 状态格子，JS 填 -->
    <div class="calcline" id="cw-calc">按「算一格」开始。注意每一格都是拿<b>上一稿</b>的数字来算的。</div>
    <canvas id="cw-geo" width="440" height="150"></canvas>
  </div>
  <div class="wgt-ctl">
    <button id="cw-one" class="pri">算一格</button>
    <button id="cw-sweep">刷完这一遍</button>
    <button id="cw-auto">自动</button>
    <button id="cw-reset">重置</button>
    <label>γ <input type="range" id="cw-g" min="0.5" max="0.95" step="0.05" value="0.9"><span class="val" id="cw-gv">0.90</span></label>
  </div>
  <div class="wgt-stat">
    <span>当前是第 <b id="cw-k">0</b> 稿</span>
    <span>本轮最大改动 <b id="cw-d">—</b></span>
    <span>离真值还差 <b id="cw-e">—</b></span>
  </div>
</div>
```

- 状态格子 `.cnode` 有四种态：`.zero`（还没被消息碰到，数字淡出）、`.act`（本步正在算，主色 + 上移）、`.tgt`（这一步的目标来源，绿色）、`.gold`（真值参照，虚线框）。
- `.calcline` 每步写出**这一格的算式**（`0 + 0.9 × 1.000 = 0.900`），把公式和动画对上。
- JS 写在同一 `<section>` 内的 `<script>`，IIFE 包住，id 加组件前缀（`cw-`）。
- 组件之后必须跟一个 `.key` 告诉读者盯什么。

## 11. 路线图 Stage 卡片

```html
<section class="stage" id="s2" data-status="done">
  <div class="stage-head"><span class="num">STAGE 2</span><h2>无模型表格法：MC / TD / Q-learning</h2>
    <a class="chip d" href="#l4">第四课</a><a class="chip d" href="#l5">第五课</a></div>
  <p class="why">丢掉 P，只剩采样。这一阶段的数学主线是随机逼近与偏差-方差权衡——它决定了后面每一个算法的设计动机。</p>
  <div class="block"><h4>核心算法</h4>
    <ul class="algos"><li><b>TD(0)</b>：自举带来偏差，换取方差和在线性</li>…</ul></div>
  <div class="demo"><h4>CartPole 落点</h4><p>在同一个离散化 CartPole 上跑表格 Q-learning 和 SARSA。<strong>关键实验：</strong>把 ‖Q_k − Q*‖∞ 对着 Stage 1 的精确解画出来。</p></div>
  <p class="pitfall"><b>最容易踩的坑：</b>……</p>
</section>
```

`data-status` 取 `done|now|pending`，控制左边框颜色（绿 / 橙 / 无）。
`.why` 是**为什么必须学这一段**，一句狠话，不是内容摘要。
