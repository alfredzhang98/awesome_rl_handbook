# -*- coding: utf-8 -*-
"""路线图：一份数据，出两个文件。
    docs/assets/roadmap.drawio   draw.io 源文件，可继续手改
另外 build_index() 返回内联 SVG（用 CSS 变量，亮/暗自适应），供 docs/index.html 使用。
    python roadmap_fig.py
"""
import io, os

W = 680
PAD = 16

# ---- 版式常量 ----
BOX_H = 46
GAP_Y = 26
LANE_PAD = 14

# 颜色：内联版用 CSS 变量，独立版写死
VAR = {"ink": "var(--ink)", "ink2": "var(--ink-2)", "ink3": "var(--ink-3)",
       "line": "var(--line)", "line2": "var(--line-2)", "acc": "var(--accent)",
       "accsoft": "var(--accent-soft)", "panel": "var(--panel)", "bg": "none"}
LIT = {"ink": "#1c1b19", "ink2": "#4d4a45", "ink3": "#8d8981",
       "line": "#e5e2dc", "line2": "#d9d5cd", "acc": "#8a5a2b",
       "accsoft": "#f3ece3", "panel": "#ffffff", "bg": "#faf9f7"}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Fig(object):
    def __init__(self, C):
        self.C = C
        self.o = []
        self.nodes = {}
        self.meta = {}
        self.edges = []

    def lane(self, x, y, w, h, title, tag=None):
        C = self.C
        self.o.append('<rect x="%d" y="%d" width="%d" height="%d" rx="12" fill="none" '
                      'stroke="%s" stroke-dasharray="4 4"/>' % (x, y, w, h, C["line2"]))
        self.o.append('<text class="rm-lane" x="%d" y="%d">%s</text>' % (x + 14, y + 20, esc(title)))
        if tag:
            self.o.append('<text class="rm-tag" x="%d" y="%d">%s</text>' % (x + w - 12, y + 20, esc(tag)))

    def box(self, key, x, y, w, title, sub=None, main=False, h=None):
        C = self.C
        h = h or (BOX_H if not sub else BOX_H + 14)
        fill = C["panel"]
        stroke = C["acc"] if main else C["line"]
        self.o.append('<rect x="%d" y="%d" width="%d" height="%d" rx="9" fill="%s" stroke="%s"/>'
                      % (x, y, w, h, fill, stroke))
        ty = y + (h // 2 + 5 if not sub else 22)
        self.o.append('<text class="rm-t%s" x="%d" y="%d">%s</text>'
                      % (" main" if main else "", x + w // 2, ty, esc(title)))
        if sub:
            self.o.append('<text class="rm-s" x="%d" y="%d">%s</text>'
                          % (x + w // 2, y + h - 12, esc(sub)))
        self.nodes[key] = (x, y, w, h)
        self.meta[key] = (title, sub or "", main)
        return key

    def arrow(self, a, b, label=None, dashed=False, side="v"):
        C = self.C
        self.edges.append((a, b, label or ""))
        ax, ay, aw, ah = self.nodes[a]
        bx, by, bw, bh = self.nodes[b]
        if side == "v":
            x1, y1 = ax + aw // 2, ay + ah
            x2, y2 = bx + bw // 2, by
            d = "M%d %d L%d %d" % (x1, y1, x2, y2) if x1 == x2 else \
                "M%d %d L%d %d L%d %d L%d %d" % (x1, y1, x1, (y1 + y2) // 2, x2, (y1 + y2) // 2, x2, y2)
        else:
            x1, y1 = ax + aw, ay + ah // 2
            x2, y2 = bx, by + bh // 2
            d = "M%d %d L%d %d" % (x1, y1, x2, y2) if y1 == y2 else \
                "M%d %d L%d %d L%d %d L%d %d" % (x1, y1, (x1 + x2) // 2, y1, (x1 + x2) // 2, y2, x2, y2)
        self.o.append('<path class="rm-e%s" d="%s" marker-end="url(#rmah)"%s/>'
                      % (" dash" if dashed else "", d,
                         ' stroke-dasharray="4 4"' if dashed else ""))
        if label:
            mx, my = (x1 + x2) // 2, (y1 + y2) // 2
            self.o.append('<rect x="%d" y="%d" width="%d" height="16" rx="4" fill="%s"/>'
                          % (mx - len(label) * 6 - 4, my - 8, len(label) * 12 + 8, C["bg"] if C["bg"] != "none" else "var(--bg)"))
            self.o.append('<text class="rm-l" x="%d" y="%d">%s</text>' % (mx, my + 4, esc(label)))


def build(C, height):
    f = Fig(C)
    y = PAD

    # ===== Stage 0 =====
    f.lane(PAD, y, W - 2 * PAD, 216, "STAGE 0 · 马尔可夫决策过程与动态规划")
    w3 = (W - 2 * PAD - 2 * LANE_PAD - 24) // 3
    xs = PAD + LANE_PAD
    f.box("s0a", xs, y + 34, w3, "第 0 课", "值函数与最优值函数")
    f.box("s0b", xs + w3 + 12, y + 34, w3, "第 1 课", "MDP 与 Bellman 算子", main=True)
    f.box("s0c", xs + 2 * (w3 + 12), y + 34, w3, "第 2 课", "动态规划", main=True)
    f.arrow("s0a", "s0b", side="h"); f.arrow("s0b", "s0c", side="h")
    w2 = (W - 2 * PAD - 2 * LANE_PAD - 12) // 2
    f.box("s0d", xs, y + 132, w2, "第 3 课", "蒙特卡罗与时序差分")
    f.box("s0e", xs + w2 + 12, y + 132, w2, "第 4 课", "SARSA：on-policy 控制")
    f.arrow("s0c", "s0d"); f.arrow("s0d", "s0e", side="h")
    y += 216 + GAP_Y

    # ===== Stage 1 =====
    H1 = 412
    f.lane(PAD, y, W - 2 * PAD, H1, "STAGE 1 · off-policy 与深度价值方法")
    cx = PAD + LANE_PAD
    cw = W - 2 * PAD - 2 * LANE_PAD
    f.box("v1", cx, y + 34, cw, "① Q-learning 与 off-policy", "把目标里的 a′ 换成 max", main=True)
    f.box("v2", cx, y + 34 + 76, cw, "② 多步方法与重要性采样", "n-step / TD(λ) / 资格迹 / Dyna")
    f.box("v3", cx, y + 34 + 152, cw, "③ 值函数逼近", "从表格到神经网络：稳定性为什么会丢", main=True)
    f.box("v4", cx, y + 34 + 228, cw, "④ DQN 家族", "replay · target network · Double", main=True)
    f.arrow("v1", "v2"); f.arrow("v2", "v3"); f.arrow("v3", "v4")
    gy = y + 34 + 312
    bw2 = (cw - 3 * 10) // 4
    for k, (t, sub) in enumerate([("Double", "修 max 的偏差"), ("Dueling", "拆成 V + A"),
                                  ("Prioritized Replay", "按 TD-error 采样"), ("Rainbow / 分布型", "合并 · 学整个分布")]):
        f.box("q%d" % k, cx + k * (bw2 + 10), gy, bw2, t, sub, h=52)
    ax, ay, aw, ah = f.nodes["v4"]
    mx = ax + aw // 2
    f.o.append('<path class="rm-e" d="M%d %d L%d %d" marker-end="url(#rmah)"/>'
               % (mx, ay + ah, mx, gy - 2))
    y += H1 + GAP_Y

    # ===== Stage 2 =====
    H2 = 296
    f.lane(PAD, y, W - 2 * PAD, H2, "STAGE 2 · 策略梯度方法")
    f.box("p1", PAD + LANE_PAD, y + 32, 290, "策略梯度 REINFORCE", "直接优化 π(a|s)", main=True)
    f.box("p2", PAD + LANE_PAD + 306, y + 32, 290, "Actor-Critic", "actor 出策略，critic 降方差", main=True)
    f.arrow("p1", "p2", side="h")
    by = y + 118
    f.box("b1", PAD + LANE_PAD, by, 190, "A2C / A3C", "并行采样", h=52)
    f.box("b2", PAD + LANE_PAD + 206, by, 190, "TRPO → PPO → GRPO", "信任域：别走太远", h=52, main=True)
    f.box("b3", PAD + LANE_PAD + 412, by, 190, "DDPG → TD3 → SAC", "连续控制 · off-policy", h=52, main=True)
    f.arrow("p2", "b1"); f.arrow("p2", "b2"); f.arrow("p2", "b3")
    f.box("why", PAD + LANE_PAD, by + 74, 596, "三支各解决什么",
          "并行提吞吐 · 信任域保稳定 · 确定性策略进连续动作", h=56)
    y += H2 + GAP_Y

    # ===== Stage 3–5 =====
    f.lane(PAD, y, W - 2 * PAD, 118, "STAGE 3–5 · 进阶主题")
    bw = (W - 2 * PAD - 2 * LANE_PAD - 24) // 3
    f.box("t3", PAD + LANE_PAD, y + 34, bw, "Stage 3 · 模仿学习", "从示范里学，奖励难写时", h=60)
    f.box("t4", PAD + LANE_PAD + bw + 12, y + 34, bw, "Stage 4 · 离线 RL", "只有一个固定数据集", h=60)
    f.box("t5", PAD + LANE_PAD + 2 * (bw + 12), y + 34, bw, "Stage 5 · 部署与探索", "Sim2Real · Meta-RL · 探索", h=60)
    y += 118 + PAD
    return f, y


def svg(inline=True):
    C = VAR if inline else LIT
    _, h = build(C, 0)
    f, _ = build(C, h)
    css = """
  .rm-lane{font-size:11.5px;letter-spacing:.08em;font-weight:700;fill:%(ink3)s}
  .rm-tag{font-size:10.5px;fill:%(ink3)s;text-anchor:end}
  .rm-t{font-size:13.5px;font-weight:700;fill:%(ink)s;text-anchor:middle}
  .rm-t.main{fill:%(ink)s}
  .rm-s{font-size:11px;fill:%(ink3)s;text-anchor:middle}
  .rm-e{stroke:%(acc)s;stroke-width:1.6;fill:none}
  .rm-e.dash{stroke:%(line2)s;stroke-width:1.4}
  .rm-l{font-size:11px;fill:%(ink3)s;text-anchor:middle}
  .rm-v{font-size:11.5px;fill:%(ink2)s;text-anchor:middle}
""" % C
    head = ('<svg class="roadmap-svg" viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg" '
            'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif">' % (W, h))
    defs = ('<defs><marker id="rmah" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="5" markerHeight="5" '
            'orient="auto"><path d="M0 0 L8 4 L0 8 z" fill="%s"/></marker></defs>' % C["acc"])
    bg = "" if inline else '<rect width="%d" height="%d" fill="%s"/>' % (W, h, C["bg"])
    return head + "<style>" + css + "</style>" + defs + bg + "".join(f.o) + "</svg>"


def drawio():
    """同一份版式导出成 draw.io 源文件：节点带真实标题，箭头一并导出。"""
    C = LIT
    _, hh = build(C, 0)
    f, _ = build(C, hh)
    cells = ['<mxCell id="0"/><mxCell id="1" parent="0"/>']
    ids = {}
    for n, (key, (x, y, w, h)) in enumerate(f.nodes.items(), start=2):
        title, sub, main = f.meta[key]
        ids[key] = "n%d" % n
        label = "&lt;b&gt;%s&lt;/b&gt;" % esc(title)
        if sub:
            label += "&lt;br&gt;&lt;font color=&quot;#8d8981&quot; style=&quot;font-size:11px&quot;&gt;%s&lt;/font&gt;" % esc(sub)
        cells.append('<mxCell id="%s" value="%s" style="rounded=1;arcSize=12;html=1;'
                     'fillColor=%s;strokeColor=%s;fontColor=%s;fontSize=13;" vertex="1" parent="1">'
                     '<mxGeometry x="%d" y="%d" width="%d" height="%d" as="geometry"/></mxCell>'
                     % (ids[key], label, C["accsoft"] if main else C["panel"],
                        C["acc"] if main else C["line"], C["ink"], x, y, w, h))
    for n, (a, b, lab) in enumerate(f.edges, start=1):
        if a not in ids or b not in ids:
            continue
        cells.append('<mxCell id="e%d" value="%s" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;'
                     'strokeColor=%s;strokeWidth=1.6;endArrow=blockThin;endFill=1;fontSize=11;fontColor=%s;" '
                     'edge="1" parent="1" source="%s" target="%s"><mxGeometry relative="1" as="geometry"/></mxCell>'
                     % (n, esc(lab), C["acc"], C["ink3"], ids[a], ids[b]))
    return ('<mxfile host="app.diagrams.net"><diagram name="roadmap" id="0">'
            '<mxGraphModel dx="1200" dy="900" grid="0" page="0" background="none"><root>'
            + "".join(cells) + '</root></mxGraphModel></diagram></mxfile>')


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    a = os.path.join(here, "docs", "assets")
    io.open(os.path.join(a, "roadmap.svg"), "w", encoding="utf-8", newline="\n").write(svg(inline=False))
    io.open(os.path.join(a, "roadmap.drawio"), "w", encoding="utf-8", newline="\n").write(drawio())
    io.open(os.path.join(a, "roadmap.inline.svg"), "w", encoding="utf-8", newline="\n").write(svg(inline=True))
    print("roadmap.svg / roadmap.drawio / roadmap.inline.svg 已生成")
