---
name: roadmap-diagram
description: 用 draw.io（diagrams.net）的 XML 直接画讲义里的流程图/路线图——算法演进图、Stage 依赖图、数据流图。触发词：路线图、流程图、draw.io、drawio、架构图、演进图、把这几个算法的关系画出来。产出 .drawio 文件（可在 draw.io 里继续手改）与导出 SVG 的步骤，配色与讲义的亮/暗双主题一致。
---

# 画讲义里的流程图

思路和 [next-ai-draw-io](https://github.com/DayuanJiang/next-ai-draw-io) 一样：**直接写 draw.io 的 mxGraph XML**。
draw.io 的文件就是纯文本 XML，写出来存成 `*.drawio`，双击就能在 draw.io 里打开并继续手改——
不需要跑那个 Next.js 应用。

## 工作流

1. 先在脑子里定好**层次**：几条泳道（分类）、每条泳道里几个节点、箭头是「演进」还是「依赖」。
2. 写 `docs/assets/<名字>.drawio`（XML，见下面的骨架）。
3. 让用户在 <https://app.diagrams.net> 或 draw.io 桌面版打开，`File → Export as → SVG`
   （勾选 **Transparent Background**、**Include a copy of my diagram** 以便以后继续改），
   存成 `docs/assets/<名字>.svg`。
4. 页面里用 `<div class="figwrap"><img src="assets/<名字>.svg" alt="…"></div>` 引用。
   README 里用相对路径 `docs/assets/<名字>.svg`。

> 导出 SVG 时不要嵌字体。中文用系统字体渲染即可，讲义正文字体本来就跟随系统。

## 配色（和讲义同一套）

| 用途 | 亮色 | 说明 |
|---|---|---|
| 画布 | `none`（透明） | 让页面自己的底色透出来 |
| 节点边框 | `#e5e2dc` | 与正文分隔线同色 |
| 主文字 | `#1c1b19` | |
| 次要文字 | `#7d7a73` | 节点里的说明小字 |
| 强调 / 主线箭头 | `#8a5a2b` | 赭石，讲义主色 |
| 强调底 | `#f3ece3` | 主线节点的填充 |
| 已完成 / 正面 | `#3f7d58` | |
| 当前 / 警示 | `#a8551f` | |
| 中性底 | `#faf9f7` | 普通节点填充 |

**暗色模式**：SVG 里写死颜色在暗底上会发闷。两种做法——
① 导出两份（亮/暗各一），页面用 `<picture>` + `prefers-color-scheme` 切换；
② 只画线框（`fillColor=none`）、文字用 `#7d7a73` 这类中性色，两个主题都能看。
简单的关系图优先用 ②。

## XML 骨架

```xml
<mxfile host="app.diagrams.net">
  <diagram name="roadmap" id="0">
    <mxGraphModel dx="1200" dy="800" grid="0" page="0" background="none">
      <root>
        <mxCell id="0"/><mxCell id="1" parent="0"/>

        <!-- 分组底板（泳道） -->
        <mxCell id="g1" value="Value-Based" style="rounded=1;arcSize=6;fillColor=none;strokeColor=#e5e2dc;dashed=1;verticalAlign=top;align=left;spacingLeft=12;spacingTop=8;fontSize=13;fontStyle=1;fontColor=#7d7a73;"
                vertex="1" parent="1"><mxGeometry x="40" y="40" width="720" height="180" as="geometry"/></mxCell>

        <!-- 主线节点 -->
        <mxCell id="n1" value="&lt;b&gt;Q-learning&lt;/b&gt;&lt;br&gt;&lt;font color=&quot;#7d7a73&quot; style=&quot;font-size:11px&quot;&gt;表格法 · off-policy&lt;/font&gt;"
                style="rounded=1;arcSize=12;html=1;fillColor=#f3ece3;strokeColor=#8a5a2b;fontColor=#1c1b19;fontSize=13;"
                vertex="1" parent="1"><mxGeometry x="70" y="90" width="170" height="56" as="geometry"/></mxCell>

        <!-- 普通节点 -->
        <mxCell id="n2" value="&lt;b&gt;DQN&lt;/b&gt;&lt;br&gt;&lt;font color=&quot;#7d7a73&quot; style=&quot;font-size:11px&quot;&gt;神经网络 + replay + target&lt;/font&gt;"
                style="rounded=1;arcSize=12;html=1;fillColor=#faf9f7;strokeColor=#e5e2dc;fontColor=#1c1b19;fontSize=13;"
                vertex="1" parent="1"><mxGeometry x="300" y="90" width="200" height="56" as="geometry"/></mxCell>

        <!-- 箭头 -->
        <mxCell id="e1" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor=#8a5a2b;strokeWidth=1.6;endArrow=blockThin;endFill=1;"
                edge="1" parent="1" source="n1" target="n2"><mxGeometry relative="1" as="geometry"/></mxCell>

        <!-- 带标注的箭头 -->
        <mxCell id="e2" value="拿掉表格" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor=#e5e2dc;strokeWidth=1.4;endArrow=blockThin;dashed=1;fontSize=11;fontColor=#7d7a73;"
                edge="1" parent="1" source="n2" target="n1"><mxGeometry relative="1" as="geometry"/></mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## 约定

- **节点尺寸**：主线节点 `170×56`，带两行小字的 `200×64`；同一层的节点等宽等高，纵向对齐到同一条基线。
- **间距**：同层水平间距 ≥ 60，层与层垂直间距 ≥ 70。宁可留白，别挤。
- **节点内容**：粗体名字 + 一行 11px 灰字说明。**不要超过两行**——细节留给正文，图只负责关系。
- **箭头**：主线演进用实线赭石；「同一族的变体」用虚线灰；跨泳道的跳转标一个两三个字的动词（「换成函数」「不再学值」）。
- **泳道**：用 `fillColor=none;dashed=1` 的圆角矩形当底板，标题写在左上，不要用 draw.io 自带的 swimlane（导出 SVG 后不好看）。
- **别画的东西**：图例里重复正文已经说过的话；渐变、阴影、3D；超过 3 层的嵌套。

## 自检

- [ ] 导出的 SVG 在亮/暗两个主题下都能读（或者备了两份）
- [ ] 图里每个名词，正文里都出现过或马上会出现
- [ ] 箭头方向 = 阅读顺序（左→右、上→下），没有交叉线
- [ ] 窄屏下缩放到 340px 宽时，最小的字还认得出（≥ 11px 原始字号）
- [ ] `.drawio` 源文件和导出的 `.svg` 都进了仓库，以后能改
