# -*- coding: utf-8 -*-
"""第 1、2 课的数值后端：4×4 仓库网格上的动态规划。

    python grid_dp.py

仓库：4×4 共 16 格，(1,1) 与 (2,3) 是货架（进不去），(3,3) 是充电桩（吸收态）。
每走一步 −1，进桩之后不再有奖励；撞墙或撞货架留在原地，这一步照样白走。
γ = 0.9。合计 14 个状态、13 个非终点格、13 × 4 = 52 个状态-动作对。

正文里出现的每个数都从这里出：值表与闭式解、格 (2,0) 与 (2,2) 的 Q 行、
停机界、打滑对照、习题的三张表、策略评估的两条路、策略改进定理的逐格验证、
以及广义策略迭代这条轴上的轮数与备份计数。
"""
import sys
from collections import deque

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ── 环境 ────────────────────────────────────────────────────────────────
N = 4
SHELF = {(1, 1), (2, 3)}
GOAL = (3, 3)
GAMMA = 0.9
STEP = -1.0

STATES = [(i, j) for i in range(N) for j in range(N) if (i, j) not in SHELF]
NONTERM = [s for s in STATES if s != GOAL]
ACTIONS = [("上", (-1, 0)), ("下", (1, 0)), ("左", (0, -1)), ("右", (0, 1))]


def move(s, d):
    n = (s[0] + d[0], s[1] + d[1])
    return s if (not (0 <= n[0] < N and 0 <= n[1] < N) or n in SHELF) else n


def step(s, d, slip=0.0):
    """[(下一格, 概率)]。slip > 0 时左右各偏 slip/2。"""
    if slip <= 0:
        return [(move(s, d), 1.0)]
    left, right = (-d[1], d[0]), (d[1], -d[0])
    out = {}
    for dd, p in ((d, 1 - slip), (left, slip / 2), (right, slip / 2)):
        k = move(s, dd)
        out[k] = out.get(k, 0.0) + p
    return list(out.items())


def q(s, d, V, gamma=GAMMA, slip=0.0):
    """一个动作的账：当场的 −1，加上打折后的落点值按概率加权。"""
    return STEP + gamma * sum(p * V[n] for n, p in step(s, d, slip))


def dist_to_goal():
    """每一格到充电桩的最短步数。"""
    dist = {GOAL: 0}
    dq = deque([GOAL])
    while dq:
        s = dq.popleft()
        for _, d in ACTIONS:
            n = (s[0] - d[0], s[1] - d[1])
            if n in STATES and n not in dist and move(n, d) == s:
                dist[n] = dist[s] + 1
                dq.append(n)
    return dist


# ── 四个算法 ────────────────────────────────────────────────────────────
def value_iteration(gamma=GAMMA, slip=0.0, theta=1e-12, V0=0.0, order=None, inplace=False):
    """返回 (轮数, 备份次数, V, 每轮最大改动)。备份按单个动作计。
    默认 inplace=False，即「两张表」写法——每一格都拿旧表的数字算，
    与第 1 课那个交互组件一致；inplace=True 是就地覆盖（Gauss–Seidel）。"""
    V = {s: (0.0 if s == GOAL else V0) for s in STATES}
    cells = order or NONTERM
    rounds = backups = 0
    deltas = []
    while True:
        rounds += 1
        src = V if inplace else dict(V)
        delta = 0.0
        for s in cells:
            best = max(q(s, d, src, gamma, slip) for _, d in ACTIONS)
            backups += len(ACTIONS)
            delta = max(delta, abs(best - V[s]))
            V[s] = best
        deltas.append(delta)
        if delta < theta or rounds > 5000:
            return rounds, backups, V, deltas


def policy_eval(pi, gamma=GAMMA, theta=1e-12, V=None):
    """迭代法。返回 (扫描遍数, V)。"""
    V = dict(V) if V else {s: 0.0 for s in STATES}
    sweeps = 0
    while True:
        sweeps += 1
        delta = 0.0
        for s in NONTERM:
            v = V[s]
            V[s] = q(s, pi[s], V, gamma)
            delta = max(delta, abs(v - V[s]))
        if delta < theta:
            return sweeps, V


def policy_eval_solve(pi, gamma=GAMMA):
    """直接解 (I − γPπ)V = rπ：14 个未知数、14 条式子，高斯消元一次出结果。"""
    idx = {s: i for i, s in enumerate(STATES)}
    n = len(STATES)
    A = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    b = [0.0] * n
    for s in NONTERM:
        i = idx[s]
        b[i] = STEP
        for nxt, p in step(s, pi[s]):
            A[i][idx[nxt]] -= gamma * p
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(A[r][c]))
        A[c], A[p] = A[p], A[c]
        b[c], b[p] = b[p], b[c]
        for r in range(n):
            if r == c or A[r][c] == 0.0:
                continue
            f = A[r][c] / A[c][c]
            for k in range(c, n):
                A[r][k] -= f * A[c][k]
            b[r] -= f * b[c]
    return {s: b[idx[s]] / A[idx[s]][idx[s]] for s in STATES}


def policy_eval_slip(pi, slip, gamma=GAMMA, theta=1e-12):
    """带打滑的策略评估：把一个固定策略扔到有随机性的地面上打分。"""
    V = {s: 0.0 for s in STATES}
    sweeps = 0
    while True:
        sweeps += 1
        delta = 0.0
        for s in NONTERM:
            v = V[s]
            V[s] = q(s, pi[s], V, gamma, slip)
            delta = max(delta, abs(v - V[s]))
        if delta < theta:
            return sweeps, V


def greedy(V, gamma=GAMMA):
    return {s: max(ACTIONS, key=lambda a: q(s, a[1], V, gamma))[1] for s in NONTERM}


def policy_iteration(m=None, gamma=GAMMA, theta=1e-12):
    """m=None 是评估到底的策略迭代；m 为整数时是改进策略迭代（每轮只评估 m 遍）。
    值表在轮与轮之间接着用（不重新归零），所以第一轮最贵、后面几轮都很便宜。"""
    pi = {s: (0, 1) for s in NONTERM}          # 初始策略：一律往右
    rounds = backups = 0
    sweeps_each, changed_each = [], []
    V = {s: 0.0 for s in STATES}
    while True:
        rounds += 1
        if m is None:
            sw, V = policy_eval(pi, gamma, theta, V)
        else:
            sw = m
            for _ in range(m):
                new = {s: q(s, pi[s], V, gamma) for s in NONTERM}
                V.update(new)
        sweeps_each.append(sw)
        backups += sw * len(NONTERM)
        n = 0
        for s in NONTERM:
            best = max(ACTIONS, key=lambda a: q(s, a[1], V, gamma))[1]
            backups += len(ACTIONS)
            if best != pi[s]:
                n += 1
                pi[s] = best
        changed_each.append(n)
        if n == 0:
            return rounds, sweeps_each, backups, changed_each, V, pi


# ── 打印正文引用的每一段数字 ────────────────────────────────────────────
def grid(V):
    rows = []
    for i in range(N):
        rows.append("  ".join(" 货架  " if (i, j) in SHELF else "%7.4f" % V[(i, j)]
                              for j in range(N)))
    return "\n".join("    " + r for r in rows)


def main():
    global SHELF, STATES, NONTERM
    dist = dist_to_goal()
    rounds, backups, V, _ = value_iteration()

    print("第 1 课 §3　值表与闭式核对")
    print(grid(V))
    print("    离桩 d 步   −10(1−0.9^d)     值迭代")
    for k in range(7):
        s = next(x for x in STATES if dist[x] == k)
        print("      d=%d      %9.4f     %9.4f" % (k, -10 * (1 - 0.9 ** k), V[s]))
    print("    逐格最大差 %.2e" % max(abs(-10 * (1 - 0.9 ** dist[s]) - V[s]) for s in STATES))
    print("    值迭代 %d 轮、%d 次备份（13 格 × 4 动作 × %d 轮）\n" % (rounds, backups, rounds))

    for cell in ((2, 0), (2, 2)):
        print("第 1 课 §4.4 / §5.1　格 %s 的四个动作" % (cell,))
        for nm, a in ACTIONS:
            n = move(cell, a)
            print("      %s  落点 %s 离桩 %d 步  V⋆=%8.4f  Q⋆=%8.4f"
                  % (nm, n, dist[n], V[n], q(cell, a, V)))
        print()

    print("第 1 课 §6.1　停机界　‖Vk − V⋆‖∞ ≤ γ/(1−γ) · Δk")
    print("      轮  本轮最大改动  界说「最多还差」   实际还差")
    Vk = {s: 0.0 for s in STATES}
    for k in range(1, 7):
        prev = dict(Vk)
        for s in NONTERM:
            Vk[s] = max(q(s, a, prev) for _, a in ACTIONS)
        delta = max(abs(Vk[s] - prev[s]) for s in STATES)
        err = max(abs(Vk[s] - V[s]) for s in STATES)
        print("      %2d  %11.4f  %14.4f  %10.4f"
              % (k, delta, GAMMA / (1 - GAMMA) * delta, err))
    print()

    print("第 1 课 §6.2　确定性 vs 打滑 10%")
    for th in (1e-3, 1e-6, 1e-12):
        print("      阈值 %-8g 确定性 %2d 遍   打滑 10%% %2d 遍"
              % (th, value_iteration(theta=th)[0], value_iteration(theta=th, slip=0.10)[0]))
    print()

    print("第 1 课 §7.1　格 (2,0)：确定性 vs 打滑 10%")
    _, _, Vsl, _ = value_iteration(slip=0.10)
    for nm, a in ACTIONS:
        print("      %s  确定性 %8.4f   打滑 %8.4f"
              % (nm, q((2, 0), a, V), q((2, 0), a, Vsl, slip=0.10)))
    print()

    print("第 1 课 §9 习题 1　γ = 0.5 / 0.9 / 0.99")
    for g in (0.5, 0.9, 0.99):
        r2, _, V2, _ = value_iteration(gamma=g)
        print("      γ=%-5g 有效视野 %6.1f   左上角 %8.4f   %d 遍"
              % (g, 1 / (1 - g), V2[(0, 0)], r2))
    print()

    print("第 1 课 §9 习题 4　写回方式 × 初值 × 扫描顺序（十二组）")
    for inplace in (True, False):
        for v0 in (0.0, -100.0, 100.0):
            for onm, order in (("正序", NONTERM), ("倒序", list(reversed(NONTERM)))):
                print("      %s  初值 %-6g %s  %3d 遍"
                      % ("原地覆盖" if inplace else "两张表 ", v0, onm,
                         value_iteration(V0=v0, order=order, inplace=inplace)[0]))
    print()

    print("第 1 课 §9 习题 2　把货架从 (1,1) 挪到 (2,2)")
    old_shelf, old_states, old_nonterm = SHELF, STATES, NONTERM
    old_best = {s: max(ACTIONS, key=lambda a: q(s, a[1], V))[0] for s in NONTERM}
    SHELF = {(2, 2), (2, 3)}
    STATES = [(i, j) for i in range(N) for j in range(N) if (i, j) not in SHELF]
    NONTERM = [s for s in STATES if s != GOAL]
    r5, _, V5, _ = value_iteration()
    d5 = dist_to_goal()
    print(grid(V5))
    flipped = []
    for s in NONTERM:
        if s in old_nonterm:
            a2 = max(ACTIONS, key=lambda a: q(s, a[1], V5))[0]
            if old_best[s] != a2:
                flipped.append((s, old_best[s], a2))
    print("    翻向的格子：%s" % ", ".join("%s %s→%s" % f for f in flipped))
    print("    格子      挪前 d  挪前的值   挪后 d  挪后的值")
    for s in sorted(set(old_states) & set(STATES)):
        if abs(V5[s] - V[s]) > 1e-9:
            print("    %s      %d   %8.4f     %d   %8.4f" % (s, dist[s], V[s], d5[s], V5[s]))
    same = sum(1 for s in set(old_states) & set(STATES)
               if s != GOAL and abs(V5[s] - V[s]) <= 1e-9)
    print("    值一个数都没动的格子 %d 个（不含充电桩）；原货架 (1,1) 现在离桩 %d 步，值 %.4f"
          % (same, d5[(1, 1)], V5[(1, 1)]))
    print("    闭式解逐格最大差 %.2e；最远距离 %d 步，值迭代 %d 遍"
          % (max(abs(-10 * (1 - 0.9 ** d5[s]) - V5[s]) for s in STATES), max(d5.values()), r5))
    SHELF, STATES, NONTERM = old_shelf, old_states, old_nonterm
    print()

    print("第 1 课 §9 习题 3　打滑 0% / 10% / 40%")
    pi_det = greedy(V)
    for sl in (0.0, 0.10, 0.40):
        rr, _, Vv, _ = value_iteration(slip=sl)
        flip = [s for s in NONTERM
                if max(ACTIONS, key=lambda a: q(s, a[1], Vv, slip=sl))[1] != pi_det[s]]
        print("    打滑 %3d%%   (0,0)=%8.4f   %2d 遍   翻向 %s"
              % (sl * 100, Vv[(0, 0)], rr, flip or "——"))
    _, _, V40, _ = value_iteration(slip=0.40)
    for cell in ((1, 2), (2, 2)):
        best = sorted(((q(cell, a, V40, slip=0.40), nm) for nm, a in ACTIONS), reverse=True)
        print("    40%% 打滑下 %s：%s" % (cell, "，".join("%s %.4f" % (n, v) for v, n in best)))
    sw40, Vdet40 = policy_eval_slip(pi_det, 0.40)
    print("    把确定性策略原样扔到 40% 打滑地上（只评估、不重算）：")
    worst = max(NONTERM, key=lambda s: V40[s] - Vdet40[s])
    print("      (0,0) 亏 %.4f；亏得最惨的 %s 亏 %.4f"
          % (V40[(0, 0)] - Vdet40[(0, 0)], worst, V40[worst] - Vdet40[worst]))
    print()

    print("第 2 课 §5　策略评估：不管在哪一格，一律往右")
    right = {s: (0, 1) for s in NONTERM}
    sweeps, Vr = policy_eval(right)
    Vsolve = policy_eval_solve(right)
    print(grid(Vr))
    print("    迭代 %d 遍；与直接解的逐格最大差 %.2e"
          % (sweeps, max(abs(Vr[s] - Vsolve[s]) for s in STATES)))
    print("    值恰好是 −10 的格子 %d 个（−1/(1−γ) = %.1f）\n"
          % (sum(1 for s in STATES if abs(Vr[s] + 10) < 1e-9), -1 / (1 - GAMMA)))

    print("第 2 课 §6　策略改进定理：逐格不降")
    pi2 = greedy(Vr)
    _, V2 = policy_eval(pi2)
    print("    改完之后仍比原来差的格子 %d 个"
          % sum(1 for s in STATES if V2[s] < Vr[s] - 1e-12))
    print("    改了方向的格子 %d 个；左上角 %.4f → %.4f\n"
          % (sum(1 for s in NONTERM if pi2[s] != right[s]), Vr[(0, 0)], V2[(0, 0)]))

    print("第 2 课 §7 / §9　广义策略迭代这条轴")
    print("      每轮评估 m        是什么          轮数   总备份")
    print("      1（与取最大合并） 值迭代          %4d   %6d" % (rounds, backups))
    for m in (2, 3, 5, 10):
        r3, _, b3, _, _, _ = policy_iteration(m=m)
        print("      %-17d 改进策略迭代    %4d   %6d" % (m, r3, b3))
    r4, sweeps_each, b4, changed, Vp, _ = policy_iteration()
    print("      ∞（评估到底）     策略迭代        %4d   %6d" % (r4, b4))
    print("    策略迭代每轮的评估扫描 %s（合计 %d）" % (sweeps_each, sum(sweeps_each)))
    print("    策略迭代每轮改了几格   %s" % changed)
    print("    与值迭代的逐格最大差 %.2e；总备份之比 %.1f 倍\n"
          % (max(abs(Vp[s] - V[s]) for s in STATES), b4 / backups))

    print("第 2 课 §10.1　动作值函数 Q：格 (2,2) 那一行")
    print("      动作     Q⋆(s,a)    优势 A = Q⋆ − V⋆")
    for nm, a in ACTIONS:
        print("      %s     %8.4f   %8.4f" % (nm, q((2, 2), a, V), q((2, 2), a, V) - V[(2, 2)]))
    print("    V 表 %d 个数；Q 表 %d × %d = %d 个数"
          % (len(STATES), len(NONTERM), len(ACTIONS), len(NONTERM) * len(ACTIONS)))


if __name__ == "__main__":
    main()
