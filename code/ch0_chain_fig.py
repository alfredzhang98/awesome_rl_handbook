# -*- coding: utf-8 -*-
"""第 0 课的数值后端与插图：五状态链上的 V_k 逐遍迭代。

    python ch0_chain_fig.py           # 打印正文引用的数字
    python ch0_chain_fig.py --embed   # 连同两版插图一起写回 docs/ch0.html

正文里出现的每个数都从这里出：真值 6.5610、各遍的 V_k、首次非零的 γ^d、
差距 γ^k/(1−γ)、以及「刷几遍够」那张 44/66/88 的表。
插图画两版（亮/暗），配色取自讲义的 CSS token，base64 内嵌进 <picture>。
"""
import argparse
import base64
import io
import math
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
CH0 = os.path.join(HERE, os.pardir, "docs", "ch0.html")

# ── 链的定义 ────────────────────────────────────────────────────────────
STATES = ["s_0", "s_1", "s_2", "s_3", "s_4"]
GAMMA = 0.9
KMAX = 40


def step(i):
    """走一步。到了 s_4 就原地打转。"""
    return min(i + 1, len(STATES) - 1)


def reward(i):
    """站在 s_4 上出发才拿 1 分，其余为 0。"""
    return 1.0 if i == len(STATES) - 1 else 0.0


def sweep_table(kmax=KMAX, gamma=GAMMA):
    """逐遍刷表。返回 V[k][i]，V[0] 全 0（一步都不许走，一分也拿不到）。"""
    V = [[0.0] * len(STATES)]
    for _ in range(kmax):
        prev = V[-1]
        V.append([reward(i) + gamma * prev[step(i)] for i in range(len(STATES))])
    return V


def v_star(i=0, gamma=GAMMA):
    """预算无限时的答案：走 d 步到 s_4，之后每步 1 分。"""
    d = len(STATES) - 1 - i
    return gamma ** d / (1.0 - gamma)


def sweeps_for(eps, gamma=GAMMA, r_max=1.0):
    """差距 γ^k·R/(1−γ) < eps 所需的最小 k。"""
    return math.ceil(math.log(eps * (1.0 - gamma) / r_max) / math.log(gamma))


# ── 配色：讲义的 CSS token + 图里那对橙/蓝（正文按颜色指认，不能换） ────
THEMES = {
    "light": dict(bg="#fcfbfc", ink="#1c1b19", ink3="#7d7a73", line="#e5e2dc",
                  band="#efedec", warm="#e2683a", cool="#8bb2e7", legend="#ffffff"),
    "dark": dict(bg="#1a1a1a", ink="#eceaf2", ink3="#87848f", line="#2e2c35",
                 band="#262724", warm="#d65a28", cool="#2b5589", legend="#1e1d23"),
}


def draw(theme, gamma=GAMMA, kmax=KMAX):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    t = THEMES[theme]
    plt.rcParams.update({
        "font.sans-serif": ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "DejaVu Sans"],
        "axes.unicode_minus": False,
        "font.size": 10,
    })

    V = sweep_table(kmax, gamma)
    ks = list(range(1, kmax + 1))
    cum = [V[k][0] for k in ks]                      # 起点 s_0 那一列
    inc = [V[k][0] - V[k - 1][0] for k in ks]        # 这一遍新加进来的一项
    star = v_star(0, gamma)
    gap = [star - c for c in cum]
    tail = [gamma ** k / (1.0 - gamma) for k in ks]
    d0 = len(STATES) - 1                             # s_0 到 s_4 的距离

    fig, (ax, bx) = plt.subplots(1, 2, figsize=(12.82, 4.81), dpi=100)
    fig.patch.set_facecolor(t["bg"])

    for a in (ax, bx):
        a.set_facecolor(t["bg"])
        a.tick_params(colors=t["ink3"], labelsize=9)
        for s in a.spines.values():
            s.set_color(t["line"])
        a.grid(True, color=t["line"], linewidth=0.7, alpha=0.8)
        a.set_axisbelow(True)

    # ── 左：级数一项一项加进来 ──────────────────────────────────────
    ax.axvspan(0.5, d0 + 0.5, color=t["band"], zorder=0)
    # 小块要骑在上一遍的累计值上——「多加恰好一项」看的就是这一截的高度
    ax.bar(ks, inc, bottom=[V[k - 1][0] for k in ks], width=0.72,
           color=t["cool"], zorder=2,
           label="这一次刷新新加进来的一项 $\\gamma^{k-1}$")
    ax.plot(ks, cum, color=t["warm"], marker="o", markersize=3.2, linewidth=1.8,
            zorder=3, label="$V_k(s_0)$（累计）")
    ax.axhline(star, color=t["ink"], linestyle="--", linewidth=1.8, zorder=4)
    ax.text(kmax, star + 0.18, "$V^{*}(s_0) = %.4f$" % star,
            ha="right", va="bottom", color=t["ink"], fontsize=10)
    ax.text(1.0, star * 0.55,
            "预算 $\\leqslant$ %d\n够不着奖励\n$V_k(s_0) = 0$" % d0,
            ha="left", va="top", color=t["ink3"], fontsize=9)
    ax.annotate("$k$=%d 第一次够到，只吃到一口 $\\gamma^{%d}$=%.4f" % (d0 + 1, d0, gamma ** d0),
                xy=(d0 + 1, cum[d0]), xytext=(d0 + 3.2, star * 0.229),
                color=t["ink"], fontsize=9,
                arrowprops=dict(arrowstyle="->", color=t["ink3"], linewidth=1.1))
    ax.set_title("每刷一遍，级数就多加恰好一项", color=t["ink"], fontsize=12,
                 loc="left", pad=12)
    ax.set_xlabel("预算 $k$（刷了几遍）", color=t["ink3"])
    ax.set_ylabel("$V_k(s_0)$", color=t["ink3"])
    ax.set_xlim(0.5, kmax + 0.5)
    ax.set_ylim(0, star * 1.12)

    # ── 右：差距每刷一遍精确乘 γ ────────────────────────────────────
    bx.semilogy(ks, gap, color=t["cool"] if theme == "light" else "#5a8ac2",
                marker="o", markersize=3.2, linewidth=1.6,
                label="还差多少（尚未加进来的尾巴）")
    bx.semilogy(ks, tail, color=t["warm"], linestyle="--", linewidth=1.4,
                label="$\\gamma^{k}/(1-\\gamma)$")
    bx.set_title("差距每刷一遍精确乘 $\\gamma$", color=t["ink"], fontsize=12,
                 loc="left", pad=12)
    bx.set_xlabel("预算 $k$", color=t["ink3"])
    bx.set_ylabel("$V^{*}(s_0) - V_k(s_0)$", color=t["ink3"])
    bx.set_xlim(0.5, kmax + 0.5)
    bx.set_ylim(1e-2, 2e1)
    bx.text(2.0, 3.5e-2,
            "$k \\geqslant$ %d 之后两条线完全重合：\n差距就是级数没加完的那条尾巴。" % d0,
            color=t["ink3"], fontsize=9)

    for a, loc in ((ax, "lower right"), (bx, "upper right")):
        lg = a.legend(loc=loc, fontsize=9, framealpha=1.0)
        lg.get_frame().set_facecolor(t["legend"])
        lg.get_frame().set_edgecolor(t["line"])
        for txt in lg.get_texts():
            txt.set_color(t["ink"])

    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="webp", facecolor=t["bg"])
    plt.close(fig)
    return buf.getvalue()


def embed():
    """把两版图写回 docs/ch0.html 的 <picture>。"""
    imgs = {k: base64.b64encode(draw(k)).decode("ascii") for k in ("dark", "light")}
    html = open(CH0, encoding="utf-8").read()
    pic = re.search(r"<picture>.*?</picture>", html, re.S)
    if not pic:
        raise SystemExit("docs/ch0.html 里没找到 <picture>")
    new = ('<picture>\n'
           '      <source srcset="data:image/webp;base64,%s" media="(prefers-color-scheme: dark)">\n'
           '      <img src="data:image/webp;base64,%s" alt="V_k(s_0) 逐遍逼近 V⋆(s_0)">\n'
           '    </picture>' % (imgs["dark"], imgs["light"]))
    html = html[:pic.start()] + new + html[pic.end():]
    open(CH0, "w", encoding="utf-8", newline="\r\n").write(html.replace("\r\n", "\n"))
    for k, b in imgs.items():
        print("  %-5s %d KB" % (k, len(base64.b64decode(b)) // 1024))


def report():
    V = sweep_table()
    star = v_star(0)
    print("V⋆(s_0) = %.4f" % star)
    print("\n逐遍刷表（前 7 遍）")
    print("  刷第几遍 " + " ".join("%8s" % s for s in STATES))
    for k in range(1, 8):
        print("  V_%-6d " % k + " ".join("%8.4f" % v for v in V[k]))
    print("\n首次非零 = γ^d（d 为到 s_4 的距离）")
    for i, s in enumerate(STATES):
        d = len(STATES) - 1 - i
        print("  %-4s d=%d  第 %d 遍冒头  γ^%d = %.4f" % (s, d, d + 1, d, GAMMA ** d))
    print("\n差距 = γ^k/(1−γ)")
    for k in (5, 7, 10, 20, 40):
        g = GAMMA ** k / (1 - GAMMA)
        print("  k=%-3d V_k(s_0)=%8.4f  差距=%9.6f" % (k, star - g, g))
    print("\n刷几遍够")
    for eps in (0.1, 0.01, 0.001):
        k = sweeps_for(eps)
        print("  差距 < %-6s → %2d 遍，此时 V_k(s_0)=%.4f（差 %.6f）"
              % (eps, k, star - GAMMA ** k / (1 - GAMMA), GAMMA ** k / (1 - GAMMA)))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--embed", action="store_true", help="重画两版图并写回 docs/ch0.html")
    a = p.parse_args()
    report()
    if a.embed:
        print("\n写回 docs/ch0.html：")
        embed()
