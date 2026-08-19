# -*- coding: utf-8 -*-
"""第 1 课的四张图。每张渲染亮/暗两版 → webp → base64，写进 arm_figs.json。

    python arm_figs.py          # 约 2 分钟
"""
import base64
import io as _io
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import arm_dp as A

# 与讲义 CSS token 对齐的两套色板
LIGHT = dict(bg="#faf9f7", panel="#ffffff", ink="#1c1b19", ink2="#4a4843", ink3="#7d7a73",
             line="#e5e2dc", accent="#8a5a2b", green="#3f7d58", orange="#a8551f",
             blue="#3d6b9e", cmap="YlGnBu")
DARK = dict(bg="#1e1d23", panel="#1e1d23", ink="#eceaf2", ink2="#b8b5c0", ink3="#87848f",
            line="#2e2c35", accent="#d8a26a", green="#7cc79b", orange="#e8a273",
            blue="#7ea8d8", cmap="YlGnBu_r")

plt.rcParams["font.family"] = ["Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 9


def theme(fig, axes, c):
    fig.patch.set_facecolor(c["bg"])
    for ax in np.atleast_1d(axes).ravel():
        ax.set_facecolor(c["panel"])
        for s in ax.spines.values():
            s.set_color(c["line"])
        ax.tick_params(colors=c["ink3"], labelsize=8)
        ax.xaxis.label.set_color(c["ink2"]); ax.yaxis.label.set_color(c["ink2"])
        ax.title.set_color(c["ink"])
        lg = ax.get_legend()
        if lg:
            lg.get_frame().set_facecolor(c["panel"]); lg.get_frame().set_edgecolor(c["line"])
            for t in lg.get_texts():
                t.set_color(c["ink2"])


def save(fig, c):
    buf = _io.BytesIO()
    fig.savefig(buf, format="webp", dpi=170, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()


# ---------------------------------------------------------------- 数据
print("求解…")
Am, Bd = A.linearize()
P, K = A.lqr_discounted(Am, Bd)
lam_cl = np.abs(np.linalg.eigvals(Am - Bd @ K)).max()
g = A.Grid(161, 161, 41)
SNAPS = {1, 2, 3, 5, 10, 30, 100}
V, PI, hist, kfin, snaps = g.solve(tol=1e-10, snapshots=SNAPS)
Vq = np.einsum("...i,ij,...j->...", g.X, P, g.X)
print("  值迭代 %d 轮" % kfin)

e1 = []
for n in [(61, 61, 15), (121, 121, 31), (241, 241, 61)]:
    gs = A.Grid(*n, th_max=0.9, dth_max=5.0)
    Vs_, _, _, _, _ = gs.solve(tol=1e-9)
    Vqs = np.einsum("...i,ij,...j->...", gs.X, P, gs.X)
    m = (np.abs(gs.X[..., 0]) <= 0.15) & (np.abs(gs.X[..., 1]) <= 1.0) & (Vqs >= 0.05)
    e = np.abs(Vs_[m] - Vqs[m]) / Vqs[m]
    e1.append((gs.th[1] - gs.th[0], np.median(e) * 100, e.max() * 100))
    print("  E1 %s 完成" % (n,))

figs = {}


def fig1(c):
    fig, ax = plt.subplots(1, 2, figsize=(9.4, 3.5))
    Vc = np.clip(V, 0, 60)
    im = ax[0].pcolormesh(g.th, g.dth, Vc.T, cmap=c["cmap"], shading="gouraud")
    cs = ax[0].contour(g.th, g.dth, np.clip(Vq, 0, 60).T, levels=[1, 5, 15, 30, 50],
                       colors=c["accent"], linewidths=1.1, linestyles="--")
    ax[0].clabel(cs, fmt="%g", fontsize=7, colors=c["accent"])
    cb = fig.colorbar(im, ax=ax[0]); cb.outline.set_edgecolor(c["line"])
    cb.ax.tick_params(colors=c["ink3"], labelsize=7)
    ax[0].set_xlabel("θ (rad)"); ax[0].set_ylabel("θ̇ (rad/s)")
    ax[0].set_title("填色：值迭代 V⋆   虚线：LQR 的 xᵀPx")

    j = len(g.dth) // 2
    sl = np.abs(g.th) <= 0.5
    ax[1].plot(g.th[sl], V[sl, j], color=c["green"], lw=2, label="值迭代 V⋆")
    ax[1].plot(g.th[sl], Vq[sl, j], "--", color=c["accent"], lw=1.6, label="LQR  P₁₁θ² = %.2f θ²" % P[0, 0])
    ax[1].set_xlabel("θ (rad)，θ̇ = 0 切片"); ax[1].set_ylabel("代价-到-去")
    ax[1].legend(); ax[1].set_title("小角度区两条线压在一起")
    theme(fig, ax, c)
    return fig


def fig2(c):
    fig, ax = plt.subplots(figsize=(5.6, 3.3))
    d = [x[0] for x in e1]
    ax.loglog(d, [x[1] for x in e1], "o-", color=c["green"], lw=2, label="中位相对误差")
    ax.loglog(d, [x[2] for x in e1], "s--", color=c["orange"], lw=1.5, label="最大相对误差")
    ref = np.array(d) / d[0] * e1[0][1]
    ax.loglog(d, ref, ":", color=c["ink3"], lw=1.2, label="斜率 1 参考线 O(Δθ)")
    for dd, med, _ in e1:
        ax.annotate("%.1f%%" % med, (dd, med), textcoords="offset points",
                    xytext=(4, 6), fontsize=7.5, color=c["ink2"])
    ax.set_xlabel("网格步长 Δθ (rad)"); ax.set_ylabel("与 LQR 解析解的相对偏差 (%)")
    ax.legend(); ax.set_title("网格越细，值迭代越贴近那条解析解")
    theme(fig, ax, c)
    return fig


def fig3(c):
    fig, ax = plt.subplots(figsize=(5.8, 3.4))
    k = np.arange(1, len(hist) + 1)
    ax.semilogy(k, hist, color=c["green"], lw=2, label="实测 ‖V_k − V_{k−1}‖∞")
    ax.semilogy(k, hist[0] * A.GAMMA ** (k - 1), "--", color=c["ink3"], lw=1.3,
                label="γ^k  (γ = %.2f，上界)" % A.GAMMA)
    ax.semilogy(k, hist[0] * (A.GAMMA * lam_cl) ** (k - 1), ":", color=c["accent"], lw=1.6,
                label="(γ·|λ_cl|)^k = %.4f^k" % (A.GAMMA * lam_cl))
    ax.set_xlabel("刷第几遍 k"); ax.set_ylabel("这一遍最大改动")
    ax.set_ylim(1e-11, max(hist) * 3); ax.legend(fontsize=7.5)
    ax.set_title("γ 是上界，真正的速度由闭环极点定")
    theme(fig, ax, c)
    return fig


def fig4(c):
    fig, ax = plt.subplots(1, 2, figsize=(9.4, 3.5))
    im = ax[0].pcolormesh(g.th, g.dth, PI.T, cmap="coolwarm", shading="auto",
                          vmin=-A.TAU_MAX, vmax=A.TAU_MAX)
    cb = fig.colorbar(im, ax=ax[0], label="τ⋆ (N·m)")
    cb.outline.set_edgecolor(c["line"]); cb.ax.tick_params(colors=c["ink3"], labelsize=7)
    cb.set_label("τ⋆ (N·m)", color=c["ink2"], fontsize=8)
    th_line = np.linspace(-0.6, 0.6, 50)
    ax[0].plot(th_line, -(K[0, 0] / K[0, 1]) * th_line, color=c["ink"], lw=1.4,
               label="LQR 零力矩线 τ = −Kx = 0")
    for s in (+1, -1):
        ax[0].plot(th_line, s * (A.TAU_MAX - K[0, 0] * s * th_line) / K[0, 1] * 0 +
                   (-K[0, 0] * th_line - s * A.TAU_MAX) / K[0, 1], "--",
                   color=c["ink2"], lw=1.0)
    ax[0].axvline(A.np.arcsin(A.TAU_MAX / A.MGL), color=c["orange"], lw=1.2, ls=":")
    ax[0].axvline(-A.np.arcsin(A.TAU_MAX / A.MGL), color=c["orange"], lw=1.2, ls=":")
    ax[0].set_xlim(-1.3, 1.3); ax[0].set_ylim(-6, 6)
    ax[0].set_xlabel("θ (rad)"); ax[0].set_ylabel("θ̇ (rad/s)")
    ax[0].legend(fontsize=7, loc="upper right")
    ax[0].set_title("最优力矩：中间一条窄带没饱和，其余全是 bang-bang")

    x0 = [0.35, 0.0]
    xs_l, us_l, Jl = A.rollout(x0, K=K, grid=g)
    xs_g, us_g, Jg = A.rollout(x0, pi=PI, grid=g)
    t = np.arange(len(xs_l)) * A.DT
    ax[1].plot(t, xs_l[:, 0], color=c["accent"], lw=1.8, label="截断 LQR   J = %.3f" % Jl)
    t2 = np.arange(len(xs_g)) * A.DT
    ax[1].plot(t2, xs_g[:, 0], "--", color=c["green"], lw=1.8, label="网格 DP    J = %.3f" % Jg)
    ax[1].axhline(0, color=c["line"], lw=1)
    ax[1].set_xlim(0, 3); ax[1].set_xlabel("时间 (s)"); ax[1].set_ylabel("θ (rad)")
    ax[1].legend(fontsize=8); ax[1].set_title("θ₀ = 0.35 rad（正好卡在饱和角）")
    theme(fig, ax, c)
    return fig



def fig5(c):
    """前几稿在 θ̇ = 0 切片上的样子：算子一遍一遍把 V 抬起来。"""
    fig, ax = plt.subplots(figsize=(6.0, 3.6))
    j = len(g.dth) // 2
    sl = np.abs(g.th) <= 0.8
    cols = [c["ink3"], c["blue"], c["blue"], c["orange"], c["orange"], c["green"], c["green"]]
    for n, (k, col) in enumerate(zip(sorted(snaps), cols)):
        ax.plot(g.th[sl], snaps[k][sl, j], color=col, lw=1.3,
                alpha=0.35 + 0.09 * n, label="k = %d" % k)
    ax.plot(g.th[sl], V[sl, j], "--", color=c["ink"], lw=2, label="不动点 V⋆")
    ax.set_xlabel("θ (rad)，θ̇ = 0 切片"); ax.set_ylabel("代价-到-去")
    ax.set_ylim(0, 26); ax.legend(fontsize=7.5, ncol=2)
    ax.set_title("每作用一次 T⋆，曲线往上长一层")
    theme(fig, ax, c)
    return fig

for name, fn in [("f1", fig1), ("f2", fig2), ("f3", fig3), ("f4", fig4), ("f5", fig5)]:
    figs[name] = {}
    for tag, c in [("light", LIGHT), ("dark", DARK)]:
        figs[name][tag] = save(fn(c), c)
    print("  %s 完成（%.0f KB / %.0f KB）"
          % (name, len(figs[name]["light"]) / 1024, len(figs[name]["dark"]) / 1024))

json.dump(figs, open("arm_figs.json", "w"), indent=0)
print("→ arm_figs.json")
