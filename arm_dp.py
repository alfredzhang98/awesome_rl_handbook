# -*- coding: utf-8 -*-
"""第 1 课（Stage 0 + Stage 1）的数值后端。

主线例子：一台协作臂的**单个关节**——带重力、力矩受限、50 Hz 控制。
    I θ̈ = τ − b θ̇ + m g l sin θ        θ = 0 是"举直"的不稳定平衡

跑五组实验，讲义里引用的每个数字都来自这里：
    E1 桥      精确离散化 MDP 上的值迭代 V*  vs  折扣 LQR 的二次型 xᵀPx
    E2 收缩    实测 ‖V_{k+1}−V_k‖∞ 的衰减率，与 γ、γ·|λ_cl| 对比
    E3 饱和    线性律在哪失效：力矩饱和角、物理保持极限、代价比 J_lqr/J*
    E4 奖励    二次代价 vs 存活奖励：后者在核内是平的，没有梯度
    E5 维数    同样网格密度下，关节数一涨格点怎么爆

    python arm_dp.py            # 打印全部数字（约 3 分钟）
    python arm_dp.py --json     # 额外写出 arm_numbers.json 供作图脚本使用
"""
import json
import sys

import numpy as np
from scipy.linalg import solve_discrete_are

# ---------------------------------------------------------------- 物理与代价
M, L, G, B = 1.2, 0.25, 9.81, 0.10      # 连杆质量 kg / 质心距 m / 重力 / 粘滞阻尼
I = M * L * L                            # 转动惯量 kg·m²
MGL = M * G * L                          # 最大重力矩 N·m
DT = 0.02                                # 50 Hz
TAU_MAX = 2.0                            # 力矩上限 N·m
GAMMA = 0.98

Q = np.diag([1.0, 0.05])                 # 代价权重：θ, θ̇
R = 0.20                                 # 力矩权重

THETA_MAX, DTHETA_MAX = np.pi / 2, 6.0   # 状态框
OUT_COST = 500.0                         # 出框吸收代价


def step(x, u):
    """半隐式欧拉一步。x = (θ, θ̇)。"""
    th, dth = x[..., 0], x[..., 1]
    ddth = (u - B * dth + MGL * np.sin(th)) / I
    dth2 = dth + DT * ddth
    th2 = th + DT * dth2
    return np.stack([th2, dth2], axis=-1)


def stage_cost(x, u):
    return Q[0, 0] * x[..., 0] ** 2 + Q[1, 1] * x[..., 1] ** 2 + R * u ** 2


def linearize():
    """半隐式欧拉在原点的精确离散线性化，与 step() 逐位一致。"""
    a = MGL / I
    A = np.array([[1 + DT * DT * a, DT * (1 - DT * B / I)],
                  [DT * a,          1 - DT * B / I]])
    Bd = np.array([[DT * DT / I], [DT / I]])
    return A, Bd


def lqr_discounted(A, Bd, gamma=GAMMA):
    """折扣 LQR = 对 (√γ A, √γ B) 解 DARE。"""
    s = np.sqrt(gamma)
    P = solve_discrete_are(s * A, s * Bd, Q, np.array([[R]]))
    K = np.linalg.solve(R + gamma * Bd.T @ P @ Bd, gamma * Bd.T @ P @ A)
    return P, K


# ---------------------------------------------------------------- 网格 DP
class Grid:
    def __init__(self, nth, ndth, nu, th_max=THETA_MAX, dth_max=DTHETA_MAX,
                 tau_max=TAU_MAX):
        self.nth, self.ndth, self.nu = nth, ndth, nu
        self.th_max, self.dth_max = th_max, dth_max
        self.th = np.linspace(-th_max, th_max, nth)
        self.dth = np.linspace(-dth_max, dth_max, ndth)
        self.u = np.linspace(-tau_max, tau_max, nu)
        TH, DTH = np.meshgrid(self.th, self.dth, indexing="ij")
        self.X = np.stack([TH, DTH], axis=-1)
        xs = np.broadcast_to(self.X[:, :, None, :], (nth, ndth, nu, 2))
        us = self.u[None, None, :]
        self.g = stage_cost(xs, us)
        self.nxt = step(xs, us)

    def interp(self, V, x):
        """多线性插值——非扩张，所以 T 复合它之后仍是 γ-收缩。"""
        th, dth = x[..., 0], x[..., 1]
        out = (np.abs(th) > self.th_max) | (np.abs(dth) > self.dth_max)
        ti = np.clip((th + self.th_max) / (2 * self.th_max) * (self.nth - 1),
                     0, self.nth - 1 - 1e-9)
        di = np.clip((dth + self.dth_max) / (2 * self.dth_max) * (self.ndth - 1),
                     0, self.ndth - 1 - 1e-9)
        t0, d0 = ti.astype(int), di.astype(int)
        a, b = ti - t0, di - d0
        v = ((1 - a) * (1 - b) * V[t0, d0] + a * (1 - b) * V[t0 + 1, d0]
             + (1 - a) * b * V[t0, d0 + 1] + a * b * V[t0 + 1, d0 + 1])
        return np.where(out, OUT_COST, v)

    def solve(self, gamma=GAMMA, tol=1e-11, max_iter=6000, snapshots=()):
        V = np.zeros((self.nth, self.ndth))
        hist, snaps = [], {}
        for k in range(1, max_iter + 1):
            TV = np.min(self.g + gamma * self.interp(V, self.nxt), axis=-1)
            hist.append(np.max(np.abs(TV - V)))
            V = TV
            if k in snapshots:
                snaps[k] = V.copy()
            if hist[-1] < tol:
                break
        Qsa = self.g + gamma * self.interp(V, self.nxt)
        pi = self.u[np.argmin(Qsa, axis=-1)]
        return V, pi, np.array(hist), k, snaps

    def solve_survival(self, gamma=GAMMA, tol=1e-11, max_iter=4000):
        """存活奖励：框内每步 +1，出框 0。最大化。"""
        Vs = np.zeros((self.nth, self.ndth))
        for k in range(max_iter):
            th, dth = self.nxt[..., 0], self.nxt[..., 1]
            out = (np.abs(th) > self.th_max) | (np.abs(dth) > self.dth_max)
            nv = np.where(out, 0.0, self.interp_raw(Vs, self.nxt))
            TV = np.max(1.0 + gamma * nv, axis=-1)
            d = np.max(np.abs(TV - Vs))
            Vs = TV
            if d < tol:
                break
        Qsa = 1.0 + gamma * np.where(
            (np.abs(self.nxt[..., 0]) > self.th_max) | (np.abs(self.nxt[..., 1]) > self.dth_max),
            0.0, self.interp_raw(Vs, self.nxt))
        return Vs, Qsa, k

    def interp_raw(self, V, x):
        ti = np.clip((x[..., 0] + self.th_max) / (2 * self.th_max) * (self.nth - 1),
                     0, self.nth - 1 - 1e-9)
        di = np.clip((x[..., 1] + self.dth_max) / (2 * self.dth_max) * (self.ndth - 1),
                     0, self.ndth - 1 - 1e-9)
        t0, d0 = ti.astype(int), di.astype(int)
        a, b = ti - t0, di - d0
        return ((1 - a) * (1 - b) * V[t0, d0] + a * (1 - b) * V[t0 + 1, d0]
                + (1 - a) * b * V[t0, d0 + 1] + a * b * V[t0 + 1, d0 + 1])


def rollout(x0, n=800, K=None, pi=None, grid=None):
    x = np.asarray(x0, float)
    xs, us, J, disc = [x.copy()], [], 0.0, 1.0
    for _ in range(n):
        if K is not None:
            u = float(np.clip(-(K @ x)[0], -TAU_MAX, TAU_MAX))
        else:
            i = int(np.clip(round((x[0] + grid.th_max) / (2 * grid.th_max) * (grid.nth - 1)), 0, grid.nth - 1))
            j = int(np.clip(round((x[1] + grid.dth_max) / (2 * grid.dth_max) * (grid.ndth - 1)), 0, grid.ndth - 1))
            u = float(pi[i, j])
        J += disc * float(stage_cost(x, u))
        disc *= GAMMA
        x = step(x, u)
        xs.append(x.copy()); us.append(u)
        if abs(x[0]) > grid.th_max or abs(x[1]) > grid.dth_max:
            J += disc * OUT_COST
            break
    return np.array(xs), np.array(us), J


def batch_rollout(X0, tau_max, K=None, pi=None, grid=None, n=600):
    """一次跑一批初值（向量化）。返回折扣代价与"是否收住"。"""
    x = X0.copy()
    J = np.zeros(len(X0))
    alive = np.ones(len(X0), bool)
    disc = 1.0
    for _ in range(n):
        if K is not None:
            u = np.clip(-(x @ K.ravel()), -tau_max, tau_max)
        else:
            i = np.clip(np.round((x[:, 0] + grid.th_max) / (2 * grid.th_max) * (grid.nth - 1)),
                        0, grid.nth - 1).astype(int)
            j = np.clip(np.round((x[:, 1] + grid.dth_max) / (2 * grid.dth_max) * (grid.ndth - 1)),
                        0, grid.ndth - 1).astype(int)
            u = pi[i, j]
        J += np.where(alive, disc * stage_cost(x, u), 0.0)
        disc *= GAMMA
        x = np.where(alive[:, None], step(x, u), x)
        out_now = alive & ((np.abs(x[:, 0]) > THETA_MAX) | (np.abs(x[:, 1]) > DTHETA_MAX))
        J += np.where(out_now, disc * OUT_COST, 0.0)
        alive &= ~out_now
    settled = alive & (np.abs(x[:, 0]) < 0.05) & (np.abs(x[:, 1]) < 0.3)
    return J, settled


def compare_under_limit(tau_max, K):
    """同一台关节、同一个代价，只把力矩上限压低：截断 LQR vs 网格 DP。"""
    gl = Grid(161, 161, 41, tau_max=tau_max)
    Vl, pil, hl, kl, _ = gl.solve(tol=1e-9)
    th0 = np.linspace(-1.2, 1.2, 49)
    dth0 = np.linspace(-4.0, 4.0, 49)
    T0, D0 = np.meshgrid(th0, dth0, indexing="ij")
    X0 = np.stack([T0.ravel(), D0.ravel()], axis=-1)
    Jl, Sl = batch_rollout(X0, tau_max, K=K)
    Jg, Sg = batch_rollout(X0, tau_max, pi=pil, grid=gl)
    both = Sl & Sg
    only_dp = Sg & ~Sl
    ratio = Jl[both] / Jg[both]
    res = dict(tau_max=tau_max, iters=int(kl),
               n0=int(len(X0)), lqr_settled=int(Sl.sum()), dp_settled=int(Sg.sum()),
               only_dp=int(only_dp.sum()),
               ratio_med=float(np.median(ratio)), ratio_max=float(ratio.max()),
               ratio_p90=float(np.percentile(ratio, 90)))
    print("    网格 DP（161×161×41）%d 轮；在 %d 个初值上比较" % (kl, len(X0)))
    print("    收得住的初值：截断 LQR %d 个，网格 DP %d 个（DP 多救回 %d 个，+%.1f%%）"
          % (Sl.sum(), Sg.sum(), only_dp.sum(), 100 * only_dp.sum() / max(Sl.sum(), 1)))
    print("    两者都收得住的 %d 个初值上，J_lqr / J_dp 中位 %.3f，90 分位 %.3f，最差 %.3f"
          % (both.sum(), np.median(ratio), np.percentile(ratio, 90), ratio.max()))
    return res


# ---------------------------------------------------------------- 实验
def main(dump_json=False):
    out = {}
    A, Bd = linearize()
    P, K = lqr_discounted(A, Bd)
    lam_ol = np.abs(np.linalg.eigvals(A))
    lam_cl = np.abs(np.linalg.eigvals(A - Bd @ K))

    print("=" * 74)
    print("物理  I = %.4f kg·m²   mgl = %.4f N·m   dt = %.3f s   τmax = %.1f N·m   γ = %.2f"
          % (I, MGL, DT, TAU_MAX, GAMMA))
    print("线性化 A = [[%.4f, %.4f], [%.4f, %.4f]]   B = [%.5f, %.4f]ᵀ"
          % (A[0, 0], A[0, 1], A[1, 0], A[1, 1], Bd[0, 0], Bd[1, 0]))
    print("开环 |λ| = %.4f, %.4f  → 不稳定" % tuple(lam_ol))
    print("LQR  K = [%.4f, %.4f]   闭环 |λ| = %.4f, %.4f" % (K[0, 0], K[0, 1], *lam_cl))
    print("     P = [[%.4f, %.4f], [%.4f, %.4f]]" % (P[0, 0], P[0, 1], P[1, 0], P[1, 1]))
    out.update(I=I, mgl=MGL, dt=DT, tau_max=TAU_MAX, gamma=GAMMA,
               A=A.tolist(), B=Bd.ravel().tolist(), K=K.ravel().tolist(), P=P.tolist(),
               lam_ol=lam_ol.tolist(), lam_cl=lam_cl.tolist())

    # ---------- E1 桥：网格加密 → 值迭代解逼近 LQR 二次型 ----------
    print("\nE1  桥：值迭代 V* 与 LQR 的 xᵀPx，在小角度区（|θ|≤0.15、|θ̇|≤1）的相对偏差")
    print("    网格(θ×θ̇×τ)       Δθ(rad)   轮数   最大相对误差   中位")
    e1 = []
    for nth, ndth, nu in [(61, 61, 15), (121, 121, 31), (241, 241, 61)]:
        gsm = Grid(nth, ndth, nu, th_max=0.9, dth_max=5.0)
        Vs_, pis_, hs_, kf, _ = gsm.solve(tol=1e-9)
        Vq = np.einsum("...i,ij,...j->...", gsm.X, P, gsm.X)
        m = ((np.abs(gsm.X[..., 0]) <= 0.15) & (np.abs(gsm.X[..., 1]) <= 1.0)
             & (Vq >= 0.05))
        e = np.abs(Vs_[m] - Vq[m]) / Vq[m]
        dth_step = float(gsm.th[1] - gsm.th[0])
        e1.append(dict(n=[nth, ndth, nu], dtheta=dth_step, iters=int(kf), npts=int(m.sum()),
                       emax=float(e.max()), emed=float(np.median(e))))
        print("    %3d×%3d×%-3d       %.4f    %4d      %7.3f%%      %6.3f%%"
              % (nth, ndth, nu, dth_step, kf, 100 * e.max(), 100 * np.median(e)))
    out["e1_refine"] = e1

    # ---------- 主网格（后面几组实验共用） ----------
    g = Grid(121, 121, 21)
    snaps = {1, 2, 3, 5, 10, 30, 100}
    V, pi, hist, kfin, snapV = g.solve(snapshots=snaps)
    print("\n主网格 121×121×21：%d 轮收敛（tol 1e-11），每轮 %d 次备份"
          % (kfin, 121 * 121 * 21))
    out.update(main_iters=int(kfin), backups=121 * 121 * 21)

    # ---------- E2 收缩率 ----------
    ratio = hist[1:] / hist[:-1]
    lo, hi = int(0.6 * len(ratio)), int(0.95 * len(ratio))
    tail = float(np.exp(np.mean(np.log(ratio[lo:hi]))))     # 几何平均更稳
    pred = float(GAMMA * lam_cl.max())
    print("\nE2  收缩：实测末段衰减率 %.4f" % tail)
    print("    理论上界 γ = %.4f（松）   γ·|λ_cl| = %.4f（几乎正中）" % (GAMMA, pred))
    print("    第 2 轮 %.4f，前 10 轮均值 %.4f —— 早期贴着 γ，后期由闭环极点接管"
          % (ratio[1], ratio[:10].mean()))
    out.update(rate_tail=tail, rate_pred=pred, rate_k2=float(ratio[1]),
               rate_first10=float(ratio[:10].mean()), hist=hist.tolist())

    # ---------- E3 饱和与非线性 ----------
    th_sat = TAU_MAX / K[0, 0]
    th_hold = float(np.arcsin(min(1.0, TAU_MAX / MGL)))
    print("\nE3  线性律在哪失效")
    print("    LQR 在 θ̇=0 时命令 τ = −%.3f θ  → θ > %.4f rad (%.2f°) 就饱和"
          % (K[0, 0], th_sat, np.degrees(th_sat)))
    print("    物理保持极限 arcsin(τmax/mgl) = %.4f rad (%.2f°)：再远，静止时谁也拉不住"
          % (th_hold, np.degrees(th_hold)))
    gf = Grid(241, 241, 61)
    Vf, pif, histf, kff, _ = gf.solve(tol=1e-9)
    print("    对照用的细网格策略：241×241×61（Δθ = %.4f rad，Δτ = %.3f N·m），%d 轮"
          % (gf.th[1] - gf.th[0], gf.u[1] - gf.u[0], kff))
    ratios = []
    for x0 in [[0.05, 0.0], [0.20, 0.0], [0.35, 0.0], [0.50, 0.0],
               [0.60, 1.5], [0.68, 2.5], [0.72, 3.0]]:
        _, _, Jl = rollout(x0, K=K, grid=gf)
        _, _, Jg = rollout(x0, pi=pif, grid=gf)
        who = "LQR 更省" if Jl < Jg * 0.999 else ("网格 DP 更省" if Jg < Jl * 0.999 else "打平")
        ratios.append(dict(x0=x0, J_lqr=Jl, J_grid=Jg, ratio=Jl / Jg, who=who))
        print("    x0 = (%5.2f, %4.1f)   J_lqr = %9.3f   J_grid = %9.3f   比值 %6.3f   %s"
              % (x0[0], x0[1], Jl, Jg, Jl / Jg, who))
    out["e3_cost_ratio"] = ratios
    out.update(th_sat=float(th_sat), th_hold=th_hold, fine_iters=int(kff))

    # 力矩饱和区的大扰动：线性律真正开始亏钱的地方
    print("    大扰动（远超饱和角）：")
    spin = []
    for x0 in [[0.74, 4.0], [0.80, 5.0], [-0.70, 5.5], [1.10, 2.0]]:
        _, _, Jl = rollout(x0, K=K, grid=gf)
        _, _, Jg = rollout(x0, pi=pif, grid=gf)
        spin.append(dict(x0=x0, J_lqr=Jl, J_grid=Jg, ratio=Jl / Jg))
        print("      x0 = (%5.2f, %4.1f)   J_lqr = %10.3f   J_grid = %10.3f   比值 %6.3f"
              % (x0[0], x0[1], Jl, Jg, Jl / Jg))
    out["e3_spin"] = spin

    # ---------- E3b 把力矩上限压到重力矩之下：约束真正咬人 ----------
    print("\nE3b 把 τmax 压到 %.1f N·m（< mgl = %.2f）——约束开始咬人" % (0.8, MGL))
    out["e3b"] = compare_under_limit(0.8, K)

    # ---------- E4 奖励设计 ----------
    Vs, Qs, ks = g.solve_survival()
    core = (np.abs(g.X[..., 0]) < 0.6) & (np.abs(g.X[..., 1]) < 2.0)
    vs_core = Vs[core]
    best = np.max(Qs, axis=-1, keepdims=True)
    ties = np.mean(np.sum(np.abs(Qs - best) < 1e-6, axis=-1)[core] > 1)
    Vquad_core = V[core]
    print("\nE4  奖励设计：同一台关节，两种目标")
    print("    存活奖励(+1/步)：核内 V 的标准差 %.4f，极差 %.4f（上限 1/(1−γ) = %.1f）"
          % (vs_core.std(), np.ptp(vs_core), 1 / (1 - GAMMA)))
    print("                     核内 %.1f%% 的状态存在并列最优动作 —— 梯度是平的"
          % (100 * ties))
    print("    二次代价      ：核内 V 的标准差 %.4f，极差 %.4f —— 处处有坡度"
          % (Vquad_core.std(), np.ptp(Vquad_core)))
    out.update(surv_std=float(vs_core.std()), surv_ptp=float(np.ptp(vs_core)),
               surv_cap=1 / (1 - GAMMA), surv_ties=float(ties),
               quad_std=float(Vquad_core.std()), quad_ptp=float(np.ptp(Vquad_core)))

    # ---------- E5 维数 ----------
    print("\nE5  同样 121 格/维：")
    for d, name in [(2, "1 个关节"), (4, "2 个关节（本课那台臂的肩+肘）"), (12, "6 关节机械臂")]:
        print("    %-28s 状态维 %2d → %.3g 个格点" % (name, d, 121.0 ** d))
    out["dims"] = {str(d): 121.0 ** d for d in (2, 4, 12)}
    print("=" * 74)

    if dump_json:
        np.save("arm_V.npy", V); np.save("arm_pi.npy", pi); np.save("arm_Vs.npy", Vs)
        np.save("arm_Vfine.npy", Vf); np.save("arm_pifine.npy", pif)
        with open("arm_numbers.json", "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
        print("→ arm_numbers.json / arm_V.npy / arm_pi.npy / arm_Vs.npy")
    return out


if __name__ == "__main__":
    main(dump_json="--json" in sys.argv)
