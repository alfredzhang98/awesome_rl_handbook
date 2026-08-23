# -*- coding: utf-8 -*-
"""第 1 课的数值后端：4x4 仓库网格上的值迭代。
所有正文引用的数字与插图（内联 SVG）都由本文件产出。
    python grid_dp.py            # 打印数字
    python grid_dp.py --json     # 连同 SVG 一起写 grid_figs.json
"""
import io, json, sys, math, os
from collections import deque

N = 4
GOAL = (3, 3)                      # 充电桩
SHELF = {(1, 1), (2, 3)}           # 货架，进不去
GAMMA = 0.90
REW = -1.0                         # 每走一步的奖励（越快到越好）
ACTS = [("上", -1, 0), ("下", 1, 0), ("左", 0, -1), ("右", 0, 1)]

def cells():
    return [(r, c) for r in range(N) for c in range(N) if (r, c) not in SHELF]

def step(s, a):
    """确定性转移：撞墙或撞货架就留在原地。"""
    _, dr, dc = a
    r, c = s[0] + dr, s[1] + dc
    if r < 0 or r >= N or c < 0 or c >= N or (r, c) in SHELF:
        return s
    return (r, c)

def backup(V, s, gamma=GAMMA, slip=0.0):
    """返回 (最优值, 最优动作, 每个动作的明细)"""
    rows = []
    for a in ACTS:
        s2 = step(s, a)
        if slip > 0:
            # 以 slip 的概率被地面带偏，均分给另外两个垂直方向
            perp = [b for b in ACTS if (b[1] == 0) != (a[1] == 0)]
            nxt = [(1 - slip, s2)] + [(slip / 2.0, step(s, b)) for b in perp]
        else:
            nxt = [(1.0, s2)]
        ev = sum(p * V[t] for p, t in nxt)
        rows.append((a[0], REW, s2, ev, REW + gamma * ev))
    best = max(rows, key=lambda x: x[4])
    return best[4], best[0], rows

def value_iteration(gamma=GAMMA, slip=0.0, inplace=False, tol=1e-12, cap=2000):
    V = {s: 0.0 for s in cells()}
    hist = []
    for k in range(1, cap + 1):
        src = V if inplace else dict(V)
        new = V if inplace else {}
        delta = 0.0
        for s in cells():
            if s == GOAL:
                val = 0.0
            else:
                val = backup(src, s, gamma, slip)[0]
            delta = max(delta, abs(val - V[s]))
            new[s] = val
        V = new
        hist.append((k, delta, dict(V)))
        if delta < tol:
            break
    return V, hist

def bfs_dist():
    d = {GOAL: 0}
    q = deque([GOAL])
    while q:
        s = q.popleft()
        for a in ACTS:                       # 反向搜索，转移是对称的
            for t in cells():
                if step(t, a) == s and t not in d:
                    d[t] = d[s] + 1
                    q.append(t)
    return d

def fmt(x, n=4):
    return round(float(x), n)

# ---------------- 主计算 ----------------
V, hist = value_iteration()
dist = bfs_dist()
closed = {s: REW * (1 - GAMMA ** dist[s]) / (1 - GAMMA) for s in cells()}
max_gap = max(abs(V[s] - closed[s]) for s in cells())

sweeps = len(hist)
first_nonzero = {}
for k, _, Vk in hist:
    for s in cells():
        if s not in first_nonzero and abs(Vk[s]) > 1e-12:
            first_nonzero[s] = k

# 收缩率实测：每轮 sup 误差之比
err = [max(abs(Vk[s] - V[s]) for s in cells()) for _, _, Vk in hist]
ratio = [err[i + 1] / err[i] for i in range(len(err) - 1) if err[i] > 1e-9 and err[i + 1] > 1e-9]
geo = math.exp(sum(math.log(r) for r in ratio) / len(ratio)) if ratio else 0.0

# 停机界：第 k 轮的后验界 vs 真误差
bound_rows = []
for k, delta, Vk in hist[:12]:
    real = max(abs(Vk[s] - V[s]) for s in cells())
    bound_rows.append((k, fmt(delta), fmt(delta * GAMMA / (1 - GAMMA)), fmt(real)))

# 一次备份摊开：挑一个有代表性的格子
DEMO = (2, 2)
_, best_a, rows = backup(V, DEMO)
demo = [(a, fmt(g), s2, fmt(ev), fmt(tot)) for a, g, s2, ev, tot in rows]

# 原地更新 vs 两张表
Vi, hist_i = value_iteration(inplace=True)
inplace_sweeps = len(hist_i)
inplace_same = max(abs(Vi[s] - V[s]) for s in cells())

# γ 的影响
gam_rows = []
for g in (0.5, 0.9, 0.99):
    Vg, hg = value_iteration(gamma=g)
    gam_rows.append((g, len(hg), fmt(Vg[(0, 0)]), fmt(1 / (1 - g))))

# 打滑 10%
Vs, hist_s = value_iteration(slip=0.10)
pol = {s: backup(V, s)[1] for s in cells() if s != GOAL}
pol_s = {s: backup(Vs, s, slip=0.10)[1] for s in cells() if s != GOAL}
changed = sorted([s for s in pol if pol[s] != pol_s[s]])
slip_gap = {"%d%d" % s: fmt(Vs[s] - V[s]) for s in cells()}

OUT = {
    "grid": {"n": N, "goal": GOAL, "shelf": sorted(SHELF), "gamma": GAMMA, "reward": REW},
    "cells": len(cells()), "pairs": (len(cells()) - 1) * len(ACTS),
    "sweeps": sweeps,
    "V": {"%d%d" % s: fmt(V[s]) for s in cells()},
    "dist": {"%d%d" % s: dist[s] for s in cells()},
    "closed_form_max_gap": fmt(max_gap, 12),
    "first_nonzero": {"%d%d" % s: first_nonzero.get(s) for s in cells()},
    "contraction": {"geo": fmt(geo), "gamma": GAMMA, "first5": [fmt(r) for r in ratio[:5]]},
    "stop_bound": bound_rows,
    "demo_cell": DEMO, "demo_best": best_a, "demo_rows": demo,
    "inplace": {"sweeps": inplace_sweeps, "two_table_sweeps": sweeps, "max_diff": fmt(inplace_same, 10)},
    "gamma_rows": gam_rows,
    "slip": {"sweeps": len(hist_s), "V00": fmt(Vs[(0, 0)]), "V00_det": fmt(V[(0, 0)]),
             "changed": ["%d%d" % s for s in changed],
             "max_gap": fmt(max(slip_gap.values())), "gap_at_00": slip_gap["00"]},
    "policy": {"%d%d" % s: pol[s] for s in pol},
    "policy_slip": {"%d%d" % s: pol_s[s] for s in pol_s},
    "hist_first4": [{"k": k, "V": {"%d%d" % s: fmt(Vk[s], 3) for s in cells()}} for k, _, Vk in hist[:4]],
}


# 第几轮这一格算准了（= 离充电桩几步）
first_final = {}
for k, _, Vk in hist:
    for s in cells():
        if s not in first_final and abs(Vk[s] - V[s]) < 1e-12:
            first_final[s] = k

# 扫描顺序 / 初值 / 一张表还是两张表，各值多少钱
def sweep_count(inplace, init, rev):
    Vp = {s: (0.0 if s == GOAL else init) for s in cells()}
    order = sorted(cells(), reverse=rev)
    for k in range(1, 300):
        src = Vp if inplace else dict(Vp)
        delta = 0.0
        for s in order:
            val = 0.0 if s == GOAL else backup(src, s)[0]
            delta = max(delta, abs(val - Vp[s])); Vp[s] = val
        if delta < 1e-12:
            return k, fmt(max(abs(Vp[s] - V[s]) for s in cells()), 9)
    return None, None

order_rows = []
for inplace in (False, True):
    for init in (0.0, 100.0, -100.0):
        for rev in (False, True):
            k, gap = sweep_count(inplace, init, rev)
            order_rows.append({"表": "原地一张表" if inplace else "两张表",
                               "初值": init, "顺序": "倒序" if rev else "正序",
                               "轮数": k, "与 V⋆ 的差": gap})

# ---------------- 内联 SVG ----------------
CELL, PAD = 66, 26
START = (0, 0)                     # AGV 出发的格子

def grid_svg(vals=None, policy=None, title_cells=True, w_extra=0, agv=None):
    W = N * CELL + 2 * PAD + w_extra; H = N * CELL + 2 * PAD
    o = ['<svg class="gridsvg" viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg">' % (W, H),
         '<defs><marker id="gah" viewBox="0 0 8 8" refX="6" refY="4" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0 L8 4 L0 8 z" fill="var(--accent)"/></marker></defs>']
    vmax = max(abs(v) for v in vals.values()) if vals else 1.0
    for r in range(N):
        for c in range(N):
            x, y = PAD + c * CELL, PAD + r * CELL
            s = (r, c)
            if s in SHELF:
                o.append('<rect x="%d" y="%d" width="%d" height="%d" fill="var(--ink-3)" fill-opacity=".28" stroke="var(--line-2)"/>' % (x, y, CELL, CELL))
                o.append('<text class="g-lbl" x="%d" y="%d">货架</text>' % (x + CELL // 2, y + CELL // 2 + 4))
                continue
            op = (abs(vals[s]) / vmax * 0.5) if vals and vmax > 0 else 0
            o.append('<rect x="%d" y="%d" width="%d" height="%d" fill="var(--accent)" fill-opacity="%.3f" stroke="var(--line-2)"/>' % (x, y, CELL, CELL, op))
            if s == GOAL:
                o.append('<circle cx="%d" cy="%d" r="13" fill="none" stroke="var(--accent)" stroke-width="2"/>' % (x + CELL // 2, y + CELL // 2))
            if vals:
                o.append('<text class="g-num" x="%d" y="%d">%.3f</text>' % (x + CELL // 2, y + CELL // 2 + 5, vals[s]))
            if policy and s in policy and s != GOAL:
                ar = {"上": (0, -1), "下": (0, 1), "左": (-1, 0), "右": (1, 0)}[policy[s]]
                cx, cy = x + CELL // 2, y + CELL - 13
                o.append('<path class="g-arrow" d="M%d %d l%d %d" marker-end="url(#gah)"/>' % (cx - ar[0] * 9, cy - ar[1] * 7, ar[0] * 18, ar[1] * 14))
            if agv and s == agv:
                cx, cy = x + CELL // 2, y + CELL // 2
                o.append('<g class="g-agv"><rect x="%d" y="%d" width="26" height="18" rx="4"/>'
                         '<circle cx="%d" cy="%d" r="3.4"/><circle cx="%d" cy="%d" r="3.4"/>'
                         '<text class="g-agvlbl" x="%d" y="%d">AGV</text></g>'
                         % (cx - 13, cy - 13, cx - 7, cy + 7, cx + 7, cy + 7, cx, cy + 23))
            if title_cells:
                o.append('<text class="g-idx" x="%d" y="%d">%d%d</text>' % (x + 5, y + 13, r, c))
    o.append('</svg>')
    return "".join(o)

def mini(Vk, k):
    C = 30; W = N * C + 8; H = N * C + 22
    o = ['<svg class="minisvg" viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg">' % (W, H)]
    o.append('<text class="m-cap" x="%d" y="12">第 %d 轮</text>' % (W // 2, k))
    vmax = max(abs(v) for v in V.values())
    for r in range(N):
        for c in range(N):
            x, y = 4 + c * C, 18 + r * C
            s = (r, c)
            if s in SHELF:
                o.append('<rect x="%d" y="%d" width="%d" height="%d" fill="var(--ink-3)" fill-opacity=".28" stroke="var(--line-2)"/>' % (x, y, C, C)); continue
            done = abs(Vk[s] - V[s]) < 1e-12
            o.append('<rect x="%d" y="%d" width="%d" height="%d" fill="var(--accent)" fill-opacity="%.3f" stroke="var(--line-2)"/>' % (x, y, C, C, abs(Vk[s]) / vmax * 0.5 if vmax else 0))
            o.append('<text class="m-num%s" x="%d" y="%d">%.1f</text>' % (" fin" if done else "", x + C // 2, y + C // 2 + 4, Vk[s]))
    o.append('</svg>')
    return "".join(o)

OUT["first_final"] = {"%d%d" % s: first_final[s] for s in cells()}
OUT["order_rows"] = order_rows
OUT["svg"] = {
    "map": grid_svg(agv=START),
    "vstar": grid_svg(vals=V, policy=pol, title_cells=False),
    "slip": grid_svg(vals=Vs, policy=pol_s, title_cells=False),
    "sweeps": "".join(mini(Vk, k) for k, _, Vk in hist[:6]),
}


def mini2(vals, cap, hi=(), vmax=None, dec=3):
    C = 34; W = N * C + 8; H = N * C + 22
    vmax = vmax or max(abs(v) for v in vals.values()) or 1.0
    o = ['<svg class="minisvg wide" viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg">' % (W, H)]
    o.append('<text class="m-cap" x="%d" y="12">%s</text>' % (W // 2, cap))
    for r in range(N):
        for c in range(N):
            x, y = 4 + c * C, 18 + r * C
            s_ = (r, c)
            if s_ in SHELF:
                o.append('<rect x="%d" y="%d" width="%d" height="%d" fill="var(--ink-3)" fill-opacity=".28" stroke="var(--line-2)"/>' % (x, y, C, C)); continue
            o.append('<rect x="%d" y="%d" width="%d" height="%d" fill="var(--accent)" fill-opacity="%.3f" stroke="%s" stroke-width="%s"/>'
                     % (x, y, C, C, abs(vals[s_]) / vmax * 0.5,
                        "var(--accent)" if s_ in hi else "var(--line-2)", "2" if s_ in hi else "1"))
            o.append('<text class="m-num%s" x="%d" y="%d">%s</text>'
                     % (" fin" if s_ in hi else "", x + C // 2, y + C // 2 + 4, ("%%.%df" % dec) % vals[s_]))
    o.append('</svg>')
    return "".join(o)

V3 = hist[2][2]; V4 = hist[3][2]
DIFF = {s: abs(V4[s] - V3[s]) for s in cells()}
dmax = max(DIFF.values())
HI = set(s for s in cells() if abs(DIFF[s] - dmax) < 1e-12)
OUT["dist_demo"] = {"k": 4, "max": fmt(dmax), "cells": ["%d%d" % s for s in sorted(HI)]}
OUT["svg"]["dist"] = (mini2(V3, "第 3 轮 V₃", dec=3) + mini2(V4, "第 4 轮 V₄", dec=3)
                      + mini2(DIFF, "逐格作差 |V₄ − V₃|", hi=HI, vmax=dmax, dec=3))


# 打滑版：把一格的备份彻底摊开（挑一个最优动作翻了向的格子）
FLIP = changed[0] if changed else (2, 0)
def expand(V_, s0, slip):
    out = []
    for a in ACTS:
        s2 = step(s0, a)
        perp = [b for b in ACTS if (b[1] == 0) != (a[1] == 0)]
        nxt = [(1 - slip, s2)] + [(slip / 2.0, step(s0, b)) for b in perp]
        ev = sum(p_ * V_[t] for p_, t in nxt)
        out.append({"a": a[0],
                    "nxt": [[round(p_, 3), "%d%d" % t, fmt(V_[t])] for p_, t in nxt],
                    "ev": fmt(ev), "tot": fmt(REW + GAMMA * ev)})
    best = max(out, key=lambda r: r["tot"])
    return out, best["a"]

det_rows, det_best = expand(V, FLIP, 0.0)
slip_rows, slip_best = expand(Vs, FLIP, 0.10)
OUT["flip"] = {"cell": "%d%d" % FLIP, "det_best": det_best, "slip_best": slip_best,
               "det_rows": det_rows, "slip_rows": slip_rows,
               "V_det": fmt(V[FLIP]), "V_slip": fmt(Vs[FLIP])}


# ---------------- §8 习题 2 / 3 的答案 ----------------
def eval_policy(P, slip, tol=1e-13):
    """给定策略在指定打滑率下的值（策略评估，不重新取 max）。"""
    Vp = {s: 0.0 for s in cells()}
    for _ in range(20000):
        new = {}; d = 0.0
        for s in cells():
            if s == GOAL:
                new[s] = 0.0; continue
            a = [x for x in ACTS if x[0] == P[s]][0]
            s2 = step(s, a)
            perp = [b for b in ACTS if (b[1] == 0) != (a[1] == 0)]
            nxt = [(1 - slip, s2)] + [(slip / 2.0, step(s, b)) for b in perp] if slip > 0 else [(1.0, s2)]
            new[s] = REW + GAMMA * sum(p_ * Vp[t] for p_, t in nxt)
            d = max(d, abs(new[s] - Vp[s]))
        Vp = new
        if d < tol:
            break
    return Vp

# 习题 2：把 (1,1) 的货架挪到 (2,2)，和 (2,3) 连成一堵横墙
_SHELF_BAK = SHELF
SHELF = {(2, 2), (2, 3)}
V_q2, hist_q2 = value_iteration()
pol_q2 = {s: backup(V_q2, s)[1] for s in cells() if s != GOAL}
dist_q2 = bfs_dist()
SHELF = _SHELF_BAK
_common = [s for s in cells() if s != (2, 2) and s != GOAL]
OUT["ex2"] = {
    "shelf": [[2, 2], [2, 3]], "sweeps": len(hist_q2),
    "flipped": [["%d%d" % s, pol[s], pol_q2[s]] for s in sorted(_common) if pol_q2[s] != pol[s]],
    "moved": [["%d%d" % s, dist[s], dist_q2[s], fmt(V[s]), fmt(V_q2[s])]
              for s in sorted(_common) if dist[s] != dist_q2[s]],
    "V00": fmt(V_q2[(0, 0)]),
    "unchanged": sum(1 for s in _common if abs(V[s] - V_q2[s]) < 1e-12),
}

# 习题 3：打滑 40%
V_q3, hist_q3 = value_iteration(slip=0.40)
pol_q3 = {s: backup(V_q3, s, slip=0.40)[1] for s in cells() if s != GOAL}
_cost = eval_policy(pol, 0.40)          # 确定性最优策略扔到 40% 打滑的地上
_best = eval_policy(pol_q3, 0.40)
OUT["ex3"] = {
    "sweeps": {"0": sweeps, "10": len(hist_s), "40": len(hist_q3)},
    "V00": {"0": fmt(V[(0, 0)]), "10": fmt(Vs[(0, 0)]), "40": fmt(V_q3[(0, 0)])},
    "changed_40": [["%d%d" % s, pol[s], pol_q3[s]] for s in sorted(pol_q3) if pol_q3[s] != pol[s]],
    "same_as_10": all(pol_q3[s] == pol_s[s] for s in pol_q3),
    "hug_12": [[r[0], fmt(r[4])] for r in backup(V_q3, (1, 2), slip=0.40)[2]],
    "robust_loss": {"00": fmt(_best[(0, 0)] - _cost[(0, 0)]),
                    "worst": fmt(max(_best[s] - _cost[s] for s in cells())),
                    "worst_cell": "%d%d" % max(cells(), key=lambda s: _best[s] - _cost[s])},
}



# ================= 第 2 课：动态规划三件套 =================
IDX = {s: i for i, s in enumerate(cells())}
POL0 = {s: u"右" for s in cells() if s != GOAL}          # 一个笨策略：一律往右

def _act(name):
    return [a for a in ACTS if a[0] == name][0]

def eval_iter(P, tol=1e-12, cap=100000):
    """迭代式策略评估：反复代入，直到不动。返回 (V, 轮数, 每轮最大改动)"""
    Vp = {s: 0.0 for s in cells()}; deltas = []
    for k in range(1, cap + 1):
        new = {}; d = 0.0
        for s in cells():
            new[s] = 0.0 if s == GOAL else REW + GAMMA * Vp[step(s, _act(P[s]))]
            d = max(d, abs(new[s] - Vp[s]))
        Vp = new; deltas.append(d)
        if d < tol:
            return Vp, k, deltas
    return Vp, cap, deltas

def eval_exact(P):
    """直接解线性方程组 (I − γP^π)V = r^π（高斯消元）"""
    n = len(cells()); A = [[0.0] * (n + 1) for _ in range(n)]
    for s in cells():
        i = IDX[s]; A[i][i] = 1.0
        if s == GOAL:
            continue
        A[i][IDX[step(s, _act(P[s]))]] -= GAMMA
        A[i][n] = REW
    for c in range(n):                              # 前向消元
        piv = max(range(c, n), key=lambda r: abs(A[r][c]))
        A[c], A[piv] = A[piv], A[c]
        for r in range(c + 1, n):
            f = A[r][c] / A[c][c]
            for k in range(c, n + 1):
                A[r][k] -= f * A[c][k]
    x = [0.0] * n                                   # 回代
    for r in range(n - 1, -1, -1):
        x[r] = (A[r][n] - sum(A[r][k] * x[k] for k in range(r + 1, n))) / A[r][r]
    return {s: x[IDX[s]] for s in cells()}

def greedy(Vp):
    return {s: backup(Vp, s)[1] for s in cells() if s != GOAL}

def policy_iteration(P0):
    """返回每轮 (评估轮数, 改了几格, 改进后 V(0,0))；直到策略不再变"""
    P = dict(P0); rows = []
    for k in range(1, 50):
        Vp, ev, _ = eval_iter(P)
        Pn = greedy(Vp)
        changed = [s for s in P if Pn[s] != P[s]]
        rows.append({"k": k, "eval": ev, "changed": len(changed),
                     "V00": fmt(Vp[(0, 0)]), "cells": ["%d%d" % s for s in sorted(changed)]})
        if not changed:
            return P, Vp, rows
        P = Pn
    return P, Vp, rows

def mpi(m, P0=None):
    """改进策略迭代：每轮只做 m 次评估再改进一次。m=1 就是值迭代。"""
    P = dict(P0 or POL0); Vp = {s: 0.0 for s in cells()}
    for k in range(1, 3000):
        for _ in range(m):                          # m 次不完全评估
            new = {}
            for s in cells():
                new[s] = 0.0 if s == GOAL else REW + GAMMA * Vp[step(s, _act(P[s]))]
            Vp = new
        Pn = greedy(Vp)
        stable = all(Pn[s] == P[s] for s in P)
        P = Pn
        if stable and max(abs(Vp[s] - V[s]) for s in cells()) < 1e-9:
            return k, k * (13 * m + 52), fmt(max(abs(Vp[s] - V[s]) for s in cells()))
    return None, None, None

V0_iter, ev_k, ev_deltas = eval_iter(POL0)
V0_exact = eval_exact(POL0)
POL1 = greedy(V0_iter)
V1 = eval_iter(POL1)[0]
PI_P, PI_V, PI_ROWS = policy_iteration(POL0)

QSTAR = {}
for s in cells():
    if s == GOAL:
        continue
    for a in ACTS:
        QSTAR[(s, a[0])] = REW + GAMMA * V[step(s, a)]

OUT["l2"] = {
    "pol0": {"name": u"一律往右", "V": {"%d%d" % s: fmt(V0_iter[s]) for s in cells()},
             "eval_sweeps": ev_k,
             "exact_gap": fmt(max(abs(V0_iter[s] - V0_exact[s]) for s in cells()), 12),
             "stuck": ["%d%d" % s for s in cells() if abs(V0_iter[s] + 10.0) < 1e-9]},
    "improve": {"changed": [["%d%d" % s, POL0[s], POL1[s]] for s in sorted(POL0) if POL1[s] != POL0[s]],
                "gain": {"%d%d" % s: fmt(V1[s] - V0_iter[s]) for s in cells()},
                "no_drop": all(V1[s] >= V0_iter[s] - 1e-12 for s in cells()),
                "V00": [fmt(V0_iter[(0, 0)]), fmt(V1[(0, 0)])]},
    "pi_rows": PI_ROWS,
    "pi_total_backups": sum(r["eval"] * 13 + 52 for r in PI_ROWS),
    "vi_total_backups": sweeps * 52,
    "mpi": [[m] + list(mpi(m)) for m in (1, 2, 3, 5, 10)],
    "q": {"%d%d|%s" % (s[0], s[1], a): fmt(q) for (s, a), q in QSTAR.items()},
    "q_demo": {"cell": "22", "rows": [[a[0], fmt(QSTAR[((2, 2), a[0])]),
                                      fmt(QSTAR[((2, 2), a[0])] - V[(2, 2)])] for a in ACTS]},
}


OUT["svg"]["pol0"] = grid_svg(vals=V0_iter, policy=POL0, title_cells=False)
OUT["svg"]["pol1"] = grid_svg(vals=V1, policy=POL1, title_cells=False)
OUT["svg"]["polstar"] = grid_svg(vals=V, policy=pol, title_cells=False)

if __name__ == "__main__":
    if sys.platform == "win32":
        try: sys.stdout.reconfigure(encoding="utf-8")
        except Exception: pass
    print(json.dumps(OUT, ensure_ascii=False, indent=1))
