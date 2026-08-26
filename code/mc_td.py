# -*- coding: utf-8 -*-
"""第 3 课的数值后端：打滑仓库上的蒙特卡罗与时序差分。

    python mc_td.py            # 打印正文引用的每一个数
    python mc_td.py --embed    # 连同两版插图一起写回 docs/ch3.html

环境与第 1 课 §7 完全相同：4×4 仓库，(1,1) 与 (2,3) 是货架，(3,3) 是充电桩，
每走一步 −1，γ = 0.9，每一步有 10% 概率往左右偏（各 5%）。

这一课只做「给定策略估值」：策略固定为第 1 课算出的打滑版最优策略 π，
真值 V^π 由动态规划算出来当尺子，MC 与 TD 只准看采样出来的轨迹。
"""
import argparse
import base64
import io
import os
import random
import re
import sys

sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

HERE = os.path.dirname(os.path.abspath(__file__))
CH3 = os.path.join(HERE, os.pardir, "docs", "ch3.html")

# ── 环境 ────────────────────────────────────────────────────────────────
N = 4
SHELF = {(1, 1), (2, 3)}
GOAL = (3, 3)
GAMMA = 0.9
STEP = -1.0
SLIP = 0.10

STATES = [(i, j) for i in range(N) for j in range(N) if (i, j) not in SHELF]
NONTERM = [s for s in STATES if s != GOAL]
ACTIONS = [("上", (-1, 0)), ("下", (1, 0)), ("左", (0, -1)), ("右", (0, 1))]
NAME = {d: n for n, d in ACTIONS}


def move(s, d):
    n = (s[0] + d[0], s[1] + d[1])
    return s if (not (0 <= n[0] < N and 0 <= n[1] < N) or n in SHELF) else n


def outcomes(s, d, slip=SLIP):
    """[(下一格, 概率)]：直走 1−slip，左右各 slip/2。"""
    if slip <= 0:
        return [(move(s, d), 1.0)]
    left, right = (-d[1], d[0]), (d[1], -d[0])
    out = {}
    for dd, p in ((d, 1 - slip), (left, slip / 2), (right, slip / 2)):
        k = move(s, dd)
        out[k] = out.get(k, 0.0) + p
    return sorted(out.items())


def q(s, d, V, slip=SLIP):
    return STEP + GAMMA * sum(p * V[n] for n, p in outcomes(s, d, slip))


# ── 尺子：动态规划算出的真值 ────────────────────────────────────────────
def value_iteration(slip=SLIP, theta=1e-13):
    V = {s: 0.0 for s in STATES}
    while True:
        old, delta = dict(V), 0.0
        for s in NONTERM:
            V[s] = max(q(s, d, old, slip) for _, d in ACTIONS)
            delta = max(delta, abs(V[s] - old[s]))
        if delta < theta:
            return V


def greedy(V, slip=SLIP):
    return {s: max(ACTIONS, key=lambda a: q(s, a[1], V, slip))[1] for s in NONTERM}


def policy_value(pi, slip=SLIP, theta=1e-13):
    """给定策略的真值 V^π，也是这一课所有误差的参照。"""
    V = {s: 0.0 for s in STATES}
    while True:
        old, delta = dict(V), 0.0
        for s in NONTERM:
            V[s] = q(s, pi[s], old, slip)
            delta = max(delta, abs(V[s] - old[s]))
        if delta < theta:
            return V


VSTAR = value_iteration()
PI = greedy(VSTAR)
VPI = policy_value(PI)                    # 这一课的真值表


# ── 采样 ────────────────────────────────────────────────────────────────
def rollout(rng, s0=None, cap=200, pi=None, slip=SLIP):
    """按 π 走一条轨迹，返回 [(s, r)]，最后一步之后就进了充电桩。"""
    pi = pi if pi is not None else PI
    s = s0 if s0 is not None else rng.choice(NONTERM)
    traj = []
    for _ in range(cap):
        if s == GOAL:
            break
        d = pi[s]
        u, acc = rng.random(), 0.0
        nxt = s
        for n, p in outcomes(s, d, slip):
            acc += p
            if u <= acc:
                nxt = n
                break
        traj.append((s, STEP))
        s = nxt
    return traj


def returns_of(traj, gamma=GAMMA):
    """每一步往后的折现回报 G_t，倒着一遍算完。"""
    G, out = 0.0, [0.0] * len(traj)
    for i in range(len(traj) - 1, -1, -1):
        G = traj[i][1] + gamma * G
        out[i] = G
    return out


# ── 两个算法 ────────────────────────────────────────────────────────────
def mc(rng, n_ep, alpha=None, first_visit=True, s0=None, track=None):
    """alpha=None 用样本均值（每个状态各自数自己的次数），否则用固定步长。"""
    V = {s: 0.0 for s in STATES}
    cnt = {s: 0 for s in STATES}
    curve = []
    for e in range(1, n_ep + 1):
        traj = rollout(rng, s0)
        Gs = returns_of(traj)
        seen = set()
        for t, (s, _) in enumerate(traj):
            if first_visit and s in seen:
                continue
            seen.add(s)
            cnt[s] += 1
            a = (1.0 / cnt[s]) if alpha is None else alpha
            V[s] += a * (Gs[t] - V[s])
        if track and e % track == 0:
            curve.append((e, rms(V)))
    return V, curve


def td0(rng, n_ep, alpha=0.1, s0=None, track=None):
    V = {s: 0.0 for s in STATES}
    curve = []
    for e in range(1, n_ep + 1):
        traj = rollout(rng, s0)
        for t, (s, r) in enumerate(traj):
            nxt = traj[t + 1][0] if t + 1 < len(traj) else GOAL
            V[s] += alpha * (r + GAMMA * V[nxt] - V[s])
        if track and e % track == 0:
            curve.append((e, rms(V)))
    return V, curve


def rms(V):
    """13 个非终点格上的均方根误差——这一课所有曲线的纵轴。"""
    return (sum((V[s] - VPI[s]) ** 2 for s in NONTERM) / len(NONTERM)) ** 0.5


def batch(rng, n_ep, mode, s0=None, iters=4000):
    """把同一批轨迹反复喂给同一个更新式，直到值表不再动。
    batch-MC 收敛到「每个状态各自的回报平均」，batch-TD 收敛到
    「先用数据估一个模型、再解那个模型的 Bellman 方程」——两者不一样。"""
    eps = [rollout(rng, s0) for _ in range(n_ep)]
    V = {s: 0.0 for s in STATES}
    a = 0.01
    for _ in range(iters):
        inc = {s: 0.0 for s in STATES}
        for traj in eps:
            if mode == "mc":
                Gs = returns_of(traj)
                for t, (s, _) in enumerate(traj):
                    inc[s] += Gs[t] - V[s]
            else:
                for t, (s, r) in enumerate(traj):
                    nxt = traj[t + 1][0] if t + 1 < len(traj) else GOAL
                    inc[s] += r + GAMMA * V[nxt] - V[s]
        d = 0.0
        for s in NONTERM:
            V[s] += a * inc[s]
            d = max(d, abs(a * inc[s]))
        if d < 1e-11:
            break
    return V




# ── 习题用：把 γ 显式放出来的一组 ────────────────────────────────────────
def policy_value_g(pi, gamma, slip=SLIP, theta=1e-13):
    V = {s: 0.0 for s in STATES}
    while True:
        old, delta = dict(V), 0.0
        for s in NONTERM:
            V[s] = STEP + gamma * sum(p * old[n] for n, p in outcomes(s, pi[s], slip))
            delta = max(delta, abs(V[s] - old[s]))
        if delta < theta:
            return V


def rms_g(V, ref):
    return (sum((V[s] - ref[s]) ** 2 for s in NONTERM) / len(NONTERM)) ** 0.5


def mc_g(rng, n_ep, gamma, alpha):
    V = {s: 0.0 for s in STATES}
    for _ in range(n_ep):
        traj = rollout(rng)
        Gs = returns_of(traj, gamma)
        seen = set()
        for t, (s, _) in enumerate(traj):
            if s in seen:
                continue
            seen.add(s)
            V[s] += alpha * (Gs[t] - V[s])
    return V


def td_g(rng, n_ep, gamma, alpha):
    V = {s: 0.0 for s in STATES}
    for _ in range(n_ep):
        traj = rollout(rng)
        for t, (s, r) in enumerate(traj):
            nxt = traj[t + 1][0] if t + 1 < len(traj) else GOAL
            V[s] += alpha * (r + gamma * V[nxt] - V[s])
    return V


# ── 打印 ────────────────────────────────────────────────────────────────
def grid(V, w=8, prec=4):
    rows = []
    for i in range(N):
        rows.append("  ".join((" 货架  " if (i, j) in SHELF else
                               ("%*.*f" % (w - 1, prec, V[(i, j)])))
                              for j in range(N)))
    return "\n".join("    " + r for r in rows)


def report():
    import statistics as st
    rng = random.Random(20240301)

    print("第 3 课 §1　打滑仓库：策略与真值")
    print("    最优策略（第 1 课算出来的，这一课固定不动）：")
    for i in range(N):
        print("    " + "  ".join("货架" if (i, j) in SHELF else
                                 ("充电桩" if (i, j) == GOAL else NAME[PI[(i, j)]])
                                 for j in range(N)))
    print("    真值 V^π（也就是 V⋆，因为策略就是最优的那个）：")
    print(grid(VPI))
    print()

    print("第 3 课 §1　一条真实轨迹（从 (0,0) 出发，种子 20240301）")
    tr = rollout(rng, (0, 0))
    Gs = returns_of(tr)
    print("     t  状态      奖励    G_t      V^π(s)   G_t − V^π")
    for t, (s, r) in enumerate(tr):
        print("    %2d  %-8s %5.0f  %8.4f  %8.4f  %+8.4f"
              % (t, str(s), r, Gs[t], VPI[s], Gs[t] - VPI[s]))
    print("    这条轨迹走了 %d 步；它给 (0,0) 的那个样本是 %.4f，真值 %.4f"
          % (len(tr), Gs[0], VPI[(0, 0)]))
    print()

    print("第 3 课 §3　回报是样本，值是它的期望（从 (0,0) 出发，20000 条）")
    rng = random.Random(7)
    G0 = [returns_of(rollout(rng, (0, 0)))[0] for _ in range(20000)]
    L0 = [len(rollout(rng, (0, 0))) for _ in range(20000)]
    print("    步数     均值 %.2f   最短 %d   最长 %d" % (st.mean(L0), min(L0), max(L0)))
    print("    回报 G   均值 %.4f   标准差 %.4f   最小 %.4f   最大 %.4f"
          % (st.mean(G0), st.pstdev(G0), min(G0), max(G0)))
    print("    真值     V^π(0,0) = %.4f" % VPI[(0, 0)])
    print("    单条轨迹的误差标准差就是 %.4f——这是 MC 抖的全部来源" % st.pstdev(G0))
    print()

    print("第 3 课 §4 / §5　同一批轨迹，两种算法（起点随机，α = 0.1）")
    print("      轨迹数        MC 的 RMS 误差      TD(0) 的 RMS 误差")
    for n in (10, 30, 100, 300, 1000, 3000):
        ms, ts = [], []
        for seed in range(30):
            r1 = random.Random(1000 + seed)
            ms.append(rms(mc(r1, n, alpha=0.1)[0]))
            r2 = random.Random(1000 + seed)
            ts.append(rms(td0(r2, n, alpha=0.1)[0]))
        print("    %8d %16.4f %20.4f" % (n, st.mean(ms), st.mean(ts)))
    print("    （每格都是 30 次独立重跑的平均）")
    print()

    print("第 3 课 §4　首次访问 vs 每次访问（样本均值，1000 条，30 次重跑）")
    fv, ev = [], []
    for seed in range(30):
        fv.append(rms(mc(random.Random(2000 + seed), 1000, first_visit=True)[0]))
        ev.append(rms(mc(random.Random(2000 + seed), 1000, first_visit=False)[0]))
    print("    首次访问 RMS %.4f    每次访问 RMS %.4f" % (st.mean(fv), st.mean(ev)))
    print()

    print("第 3 课 §5　一条轨迹上，MC 与 TD 各更新了什么（V 全填 0，α = 0.1）")
    tr = rollout(random.Random(20240301), (0, 0))
    Gs = returns_of(tr)
    print("     t  状态      MC 的目标 G_t   TD 的目标 r+γV(s′)   两者之差")
    Vz = {s: 0.0 for s in STATES}
    for t, (s, r) in enumerate(tr[:6]):
        nxt = tr[t + 1][0] if t + 1 < len(tr) else GOAL
        tdt = r + GAMMA * Vz[nxt]
        print("    %2d  %-8s %12.4f %18.4f %14.4f" % (t, str(s), Gs[t], tdt, Gs[t] - tdt))
    print("    第 0 稿全是 0，所以 TD 的目标一律是 −1；MC 的目标已经带上了整条轨迹的信息。")
    print()

    print("第 3 课 §7　步长 α 怎么选（1000 条轨迹，30 次重跑）")
    print("      α        MC 的 RMS        TD 的 RMS")
    for a in (0.01, 0.05, 0.1, 0.3, 0.5, 1.0):
        ms, ts = [], []
        for seed in range(30):
            ms.append(rms(mc(random.Random(3000 + seed), 1000, alpha=a)[0]))
            ts.append(rms(td0(random.Random(3000 + seed), 1000, alpha=a)[0]))
        print("    %6.2f %14.4f %16.4f" % (a, st.mean(ms), st.mean(ts)))
    print("    对照：MC 用样本均值（α_n = 1/n，满足 Robbins–Monro）RMS %.4f"
          % st.mean([rms(mc(random.Random(3000 + s), 1000)[0]) for s in range(30)]))
    print()

    print("第 3 课 §8　确定性等价：同一批轨迹反复刷到底")
    print("      轨迹数     batch-MC 的 RMS    batch-TD 的 RMS")
    for n in (5, 10, 30, 100):
        ms, ts = [], []
        for seed in range(12):
            ms.append(rms(batch(random.Random(4000 + seed), n, "mc")))
            ts.append(rms(batch(random.Random(4000 + seed), n, "td")))
        print("    %8d %18.4f %18.4f" % (n, st.mean(ms), st.mean(ts)))
    print("    （12 次独立重跑的平均。同一批数据、刷到不再动，两者收敛到的不是同一张表。）")
    print()

    print("第 3 课 §9 习题 1　γ 换成 0.5 / 0.9 / 0.99（1000 条轨迹，30 次重跑）")
    print("      γ      V^π(0,0)    单条 G 的标准差    MC 的 RMS    TD 的 RMS")
    for g in (0.5, 0.9, 0.99):
        vs = policy_value_g(PI, g)
        rr = random.Random(51)
        sd = st.pstdev([returns_of(rollout(rr, (0, 0)), g)[0] for _ in range(4000)])
        ms, ts = [], []
        for seed in range(30):
            ms.append(rms_g(mc_g(random.Random(5000 + seed), 1000, g, 0.1), vs))
            ts.append(rms_g(td_g(random.Random(5000 + seed), 1000, g, 0.1), vs))
        print("    %6.2f %10.4f %16.4f %13.4f %12.4f"
              % (g, vs[(0, 0)], sd, st.mean(ms), st.mean(ts)))
    print()

    print("第 3 课 §9 习题 2　把打滑关掉（确定性）之后，MC 还抖不抖")
    Vd = value_iteration(0.0)
    pid = greedy(Vd, 0.0)
    rr = random.Random(11)
    Gd = [returns_of(rollout(rr, (0, 0), pi=pid, slip=0.0))[0] for _ in range(2000)]
    Ld = [len(rollout(rr, (0, 0), pi=pid, slip=0.0)) for _ in range(2000)]
    print("    确定性：2000 条轨迹步数全是 %d，G 的标准差 %.1e（每条轨迹一模一样）"
          % (Ld[0], st.pstdev(Gd)))
    print("    打滑 10%%：步数 6–16，G 的标准差 %.4f" % st.pstdev(G0))
    print("    所以 MC 的方差不是算法的毛病，是环境随机性直接透到目标里。")


# ── 插图 ────────────────────────────────────────────────────────────────
THEMES = {
    "light": dict(bg="#fcfbfc", ink="#1c1b19", ink3="#7d7a73", line="#e5e2dc",
                  band="#efedec", warm="#e2683a", cool="#8bb2e7", legend="#ffffff"),
    "dark": dict(bg="#1a1a1a", ink="#eceaf2", ink3="#87848f", line="#2e2c35",
                 band="#262724", warm="#d65a28", cool="#2b5589", legend="#1e1d23"),
}


def draw(theme):
    import statistics as st
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    t = THEMES[theme]
    plt.rcParams.update({
        "font.sans-serif": ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "DejaVu Sans"],
        "axes.unicode_minus": False,
        "font.size": 10,
    })

    # 左：单条轨迹的回报分布；右：RMS 误差随轨迹数下降
    rng = random.Random(7)
    G0 = [returns_of(rollout(rng, (0, 0)))[0] for _ in range(20000)]

    RUNS, NEP, TRACK = 30, 1000, 10
    mcs, tds = [], []
    for seed in range(RUNS):
        mcs.append(mc(random.Random(1000 + seed), NEP, alpha=0.1, track=TRACK)[1])
        tds.append(td0(random.Random(1000 + seed), NEP, alpha=0.1, track=TRACK)[1])
    xs = [e for e, _ in mcs[0]]
    mc_m = [st.mean([r[i][1] for r in mcs]) for i in range(len(xs))]
    td_m = [st.mean([r[i][1] for r in tds]) for i in range(len(xs))]

    fig, (ax, bx) = plt.subplots(1, 2, figsize=(12.82, 4.81), dpi=100)
    fig.patch.set_facecolor(t["bg"])
    for a in (ax, bx):
        a.set_facecolor(t["bg"])
        a.tick_params(colors=t["ink3"], labelsize=9)
        for s in a.spines.values():
            s.set_color(t["line"])
        a.grid(True, color=t["line"], linewidth=0.7, alpha=0.8)
        a.set_axisbelow(True)

    ax.hist(G0, bins=60, color=t["cool"], zorder=2)
    ax.axvline(VPI[(0, 0)], color=t["warm"], linestyle="--", linewidth=2, zorder=3)
    ax.text(VPI[(0, 0)], ax.get_ylim()[1] * 0.94,
            "  真值 $V^{\\pi}$ = %.4f" % VPI[(0, 0)],
            color=t["warm"], fontsize=10, ha="left", va="top")
    ax.text(0.02, 0.86, "标准差 %.4f\n最差一条 %.3f" % (st.pstdev(G0), min(G0)),
            transform=ax.transAxes, color=t["ink3"], fontsize=9, va="top")
    ax.set_title("一条轨迹给出的 $G_0$：无偏，但散得很开", color=t["ink"],
                 fontsize=12, loc="left", pad=12)
    ax.set_xlabel("单条轨迹的回报 $G_0$", color=t["ink3"])
    ax.set_ylabel("出现次数（共 20000 条）", color=t["ink3"])

    bx.plot(xs, mc_m, color=t["warm"], linewidth=1.9, label="蒙特卡罗")
    bx.plot(xs, td_m, color=t["cool"], linewidth=1.9, label="时序差分 TD(0)")
    bx.set_yscale("log")
    bx.set_title("13 格上的 RMS 误差（$\\alpha$ = 0.1，30 次重跑平均）",
                 color=t["ink"], fontsize=12, loc="left", pad=12)
    bx.set_xlabel("已经跑过的轨迹条数", color=t["ink3"])
    bx.set_ylabel("与真值表的 RMS 误差", color=t["ink3"])
    leg = bx.legend(facecolor=t["legend"], edgecolor=t["line"], fontsize=9)
    for txt in leg.get_texts():
        txt.set_color(t["ink"])
    for a in (ax, bx):
        a.title.set_color(t["ink"])

    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=t["bg"])
    plt.close(fig)
    from PIL import Image
    buf.seek(0)
    im = Image.open(buf).convert("RGB")
    out = io.BytesIO()
    im.save(out, format="WEBP", quality=88, method=6)
    return out.getvalue()


def embed():
    imgs = {k: base64.b64encode(draw(k)).decode("ascii") for k in ("dark", "light")}
    html = open(CH3, encoding="utf-8").read()
    pic = re.search(r"<picture>.*?</picture>", html, re.S)
    if not pic:
        raise SystemExit("docs/ch3.html 里没找到 <picture>")
    new = ('<picture>\n'
           '      <source srcset="data:image/webp;base64,%s" media="(prefers-color-scheme: dark)">\n'
           '      <img src="data:image/webp;base64,%s" alt="单条轨迹的回报分布，以及 MC 与 TD 的 RMS 误差">\n'
           '    </picture>' % (imgs["dark"], imgs["light"]))
    html = html[:pic.start()] + new + html[pic.end():]
    open(CH3, "w", encoding="utf-8", newline="\r\n").write(html.replace("\r\n", "\n"))
    for k, b in imgs.items():
        print("  %-5s %d KB" % (k, len(base64.b64decode(b)) // 1024))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--embed", action="store_true")
    a = ap.parse_args()
    report()
    if a.embed:
        print("\n写回 docs/ch3.html：")
        embed()
