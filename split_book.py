# -*- coding: utf-8 -*-
"""Split RL_Handbook_CartPole.html into a GitBook-style multi-page book.
Content of each section is copied verbatim; only navigation/index is added."""
import os, re, io, shutil

SRC = r"C:\Users\alfred\Desktop\RL\RL_Handbook_CartPole.html"
OUT = r"C:\Users\alfred\Desktop\RL\docs"

src = io.open(SRC, encoding="utf-8").read()

# ---------- 1. pull out the shared pieces ----------
head_css = re.search(r"<style>\n(.*?)\n</style>\n</head>", src, re.S).group(1)
defs_svg = re.search(r'(<svg style="display:none".*?</svg>)', src, re.S).group(1)
defs_paths = dict(re.findall(r'<path id="([^"]+)"([^>]*)></path>', defs_svg))

# ---------- 2. split sections ----------
body = src[src.index("<body>"):]
starts = [(m.start(), m.group(1)) for m in
          re.finditer(r'<section class="doc (?:roadmap|lesson)" id="([a-z0-9]+)">', body)]
starts.append((body.index('\n</div>\n<a class="totop"'), None))

sections = {}
order = []
for i in range(len(starts) - 1):
    a, sid = starts[i]
    b = starts[i + 1][0]
    sections[sid] = body[a:b].rstrip()
    order.append(sid)

assert order == ["roadmap"] + ["l%d" % i for i in range(9)], order


def strip_tags(s):
    return " ".join(re.sub(r"<[^>]+>", "", s).split())


# ---------- 3. chapter metadata ----------
def parttag(sid):
    return strip_tags(re.search(r'<div class="parttag">(.*?)</div>', sections[sid], re.S).group(1))


PAGES = [("index.html", "roadmap")] + [("ch%d.html" % i, "l%d" % i) for i in range(9)]
titles = {}
nums = {}
for fn, sid in PAGES:
    t = parttag(sid)                                  # e.g. "第 4 课 · Stage 2 · 无模型表格法"
    m = re.match(r"第\s*(\d+)\s*[课部].*?·\s*(.*)$", t)
    if sid == "roadmap":
        nums[sid], titles[sid] = "", "路线图"
    else:
        # 分组标题里已经写了 Stage N，章节名去掉重复的前缀
        nums[sid], titles[sid] = m.group(1), re.sub(r"^Stage\s*\d+\s*·\s*", "", m.group(2))

GROUPS = [
    ("开始", ["roadmap"]),
    ("Stage 0–1", ["l0", "l1", "l2", "l3"]),
    ("Stage 2", ["l4", "l5"]),
    ("Stage 3", ["l6"]),
    ("Stage 4", ["l7"]),
    ("Stage 5", ["l8"]),
]
file_of = dict((sid, fn) for fn, sid in PAGES)

# ---------- 4. link rewriting ----------
def rewrite(html, cur_sid):
    def sub_l(m):
        return 'href="%s"' % file_of["l" + m.group(1)]
    html = re.sub(r'href="#l(\d)"', sub_l, html)
    if cur_sid != "roadmap":
        html = re.sub(r'href="#(s\d+)"', r'href="index.html#\1"', html)
        html = html.replace('href="#roadmap"', 'href="index.html"')
    return html


# ---------- 5. page shell ----------
def sidebar(cur_sid):
    out = ['<aside class="sidebar" id="sidebar">',
           '  <div class="sb-brand"><a href="index.html">强化学习 · 学习手册</a>'
           '<span class="sb-sub">数学优先 · 面向 robotics · CartPole 主线</span></div>',
           '  <nav class="sb-nav">']
    for label, sids in GROUPS:
        out.append('    <div class="sb-group">%s</div>' % label)
        out.append('    <ul>')
        for sid in sids:
            on = " class=\"on\"" if sid == cur_sid else ""
            num = ('<span class="sb-num">%s</span>' % nums[sid]) if nums[sid] else '<span class="sb-num">·</span>'
            out.append('      <li%s><a href="%s">%s<span class="sb-t">%s</span></a>%s</li>'
                       % (on, file_of[sid], num, titles[sid],
                          '<ol class="sb-sub-toc" id="subtoc"></ol>' if sid == cur_sid else ''))
        out.append('    </ul>')
    out.append('  </nav>')
    out.append('</aside>')
    return "\n".join(out)


def pagenav(idx):
    prev_ = PAGES[idx - 1] if idx > 0 else None
    next_ = PAGES[idx + 1] if idx < len(PAGES) - 1 else None
    parts = ['<nav class="pagenav">']
    if prev_:
        parts.append('  <a class="pn prev" href="%s" data-key="prev"><span class="pn-l">← 上一章</span>'
                     '<span class="pn-t">%s</span></a>' % (prev_[0], titles[prev_[1]]))
    else:
        parts.append('  <span class="pn ghost"></span>')
    if next_:
        parts.append('  <a class="pn next" href="%s" data-key="next"><span class="pn-l">下一章 →</span>'
                     '<span class="pn-t">%s</span></a>' % (next_[0], titles[next_[1]]))
    else:
        parts.append('  <span class="pn ghost"></span>')
    parts.append('</nav>')
    return "\n".join(parts)


def used_defs(html):
    ids = set(re.findall(r'xlink:href="#(MJX-[^"]+)"', html))
    ids |= set(re.findall(r'href="#(MJX-[^"]+)"', html))
    keep = [i for i in ids if i in defs_paths]
    keep.sort()
    if not keep:
        return ""
    return ('<svg style="display:none" xmlns="http://www.w3.org/2000/svg"><defs>'
            + "".join('<path id="%s"%s></path>' % (i, defs_paths[i]) for i in keep)
            + "</defs></svg>")


TPL = u"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · 强化学习学习手册</title>
<link rel="stylesheet" href="assets/book.css">
</head>
<body data-page="{page}">
{defs}
<header class="topbar">
  <button class="menu-btn" id="menuBtn" aria-label="目录">☰</button>
  <span class="tb-title">{title}</span>
</header>
{sidebar}
<div class="sb-mask" id="sbMask"></div>
<main class="content" id="content">
<div class="wrap">
{content}
</div>
{pagenav}
</main>
<a class="totop" href="#" id="totop">↑ 回到顶部</a>
<script src="assets/book.js"></script>
</body>
</html>
"""

# ---------- 6. emit ----------
for d in (OUT, os.path.join(OUT, "assets")):
    if os.path.isdir(d):
        for f in os.listdir(d):
            p = os.path.join(d, f)
            if os.path.isfile(p):
                os.remove(p)
    else:
        os.makedirs(d)

for idx, (fn, sid) in enumerate(PAGES):
    content = rewrite(sections[sid], sid)
    page = TPL.format(title=titles[sid], page=sid, defs=used_defs(content),
                      sidebar=sidebar(sid), content=content, pagenav=pagenav(idx))
    io.open(os.path.join(OUT, fn), "w", encoding="utf-8", newline="\n").write(page)
    print(fn, sid, "%.0f KB" % (len(page.encode("utf-8")) / 1024.0))

# ----- css -----
BOOK_CSS = u"""

/* ==========================================================================
   以下为「切分成书」时新增的版式：侧边栏目录 / 章节导航。
   上方样式与原单页文件完全一致，正文渲染不变。
   ========================================================================== */
:root{ --sb-w:296px; }

.sidebar{position:fixed;top:0;left:0;bottom:0;width:var(--sb-w);z-index:60;overflow-y:auto;
 background:var(--panel);border-right:1px solid var(--line);padding:22px 0 48px;
 overscroll-behavior:contain;scrollbar-width:thin}
.sidebar::-webkit-scrollbar{width:8px}
.sidebar::-webkit-scrollbar-thumb{background:var(--line-2);border-radius:99px}
.sb-brand{padding:4px 22px 18px;border-bottom:1px solid var(--line);margin-bottom:14px}
.sb-brand a{display:block;font-size:14.5px;font-weight:700;color:var(--ink);text-decoration:none;letter-spacing:-.01em}
.sb-sub{display:block;margin-top:5px;font-size:11.5px;line-height:1.5;color:var(--ink-3)}
.sb-group{padding:16px 22px 7px;font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;
 color:var(--ink-3);font-weight:700}
.sb-nav ul{list-style:none;margin:0;padding:0}
.sb-nav li{margin:0}
.sb-nav>ul>li>a{display:flex;gap:10px;align-items:baseline;padding:7px 22px;font-size:13.5px;line-height:1.5;
 color:var(--ink-2);text-decoration:none;border-left:2px solid transparent}
.sb-nav>ul>li>a:hover{background:var(--accent-soft);color:var(--accent)}
.sb-num{flex:none;width:14px;text-align:center;font-size:11.5px;font-weight:700;color:var(--ink-3);
 font-variant-numeric:tabular-nums}
.sb-nav>ul>li.on>a{background:var(--accent-soft);color:var(--accent);font-weight:600;border-left-color:var(--accent)}
.sb-nav>ul>li.on>a .sb-num{color:var(--accent)}

/* 本章小目录：细一号字 + 单行省略，靠一条竖线归拢，尽量不抢章节列表的视觉 */
.sb-sub-toc{list-style:none;margin:3px 0 10px;padding:2px 0 2px 0;
 margin-left:38px;border-left:1px solid var(--line)}
.sb-sub-toc li{margin:0}
.sb-nav .sb-sub-toc a{display:flex;gap:8px;align-items:baseline;padding:3px 18px 3px 11px;
 font-size:12px;line-height:1.5;color:var(--ink-3);text-decoration:none;margin-left:-1px;
 border-left:1px solid transparent}
.sb-nav .sb-sub-toc .sn{flex:none;min-width:13px;text-align:right;font-size:11px;opacity:.6;
 font-variant-numeric:tabular-nums}
.sb-nav .sb-sub-toc .st{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.sb-nav .sb-sub-toc a:hover{color:var(--accent)}
.sb-nav .sb-sub-toc a.cur{color:var(--accent);border-left-color:var(--accent)}
.sb-nav .sb-sub-toc a.cur .sn{opacity:1}

.content{margin-left:var(--sb-w)}
.content .wrap{max-width:880px}

.topbar{display:none;position:sticky;top:0;z-index:55;background:var(--nav);
 -webkit-backdrop-filter:saturate(180%) blur(14px);backdrop-filter:saturate(180%) blur(14px);
 border-bottom:1px solid var(--line);padding:9px 14px;align-items:center;gap:12px}
.menu-btn{font-size:17px;line-height:1;background:transparent;border:1px solid var(--line-2);
 color:var(--ink-2);border-radius:8px;padding:5px 10px;cursor:pointer}
.tb-title{font-size:13.5px;font-weight:600;color:var(--ink);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.sb-mask{display:none;position:fixed;inset:0;z-index:58;background:rgba(0,0,0,.34)}
.sb-mask.show{display:block}

.pagenav{max-width:880px;margin:0 auto;padding:34px 24px 72px;display:flex;gap:14px}
.pagenav .pn{flex:1;min-width:0;display:flex;flex-direction:column;gap:5px;padding:14px 17px;
 border:1px solid var(--line);border-radius:11px;background:var(--panel);text-decoration:none}
.pagenav a.pn:hover{border-color:var(--accent);background:var(--accent-soft)}
.pagenav .pn.ghost{border:none;background:none}
.pn-l{font-size:11.5px;letter-spacing:.06em;color:var(--ink-3);font-weight:700}
.pn-t{font-size:14px;color:var(--ink);line-height:1.45}
.pagenav .next{text-align:right}

@media (max-width:1080px){
  .sidebar{transform:translateX(-100%);transition:transform .22s ease;box-shadow:0 0 30px rgba(0,0,0,.18)}
  .sidebar.open{transform:none}
  .content{margin-left:0}
  .topbar{display:flex}
  section.doc{padding-top:30px}
}
@media print{ .sidebar,.topbar,.pagenav,.totop,.sb-mask{display:none!important} .content{margin-left:0} }
"""
io.open(os.path.join(OUT, "assets", "book.css"), "w", encoding="utf-8", newline="\n").write(head_css + BOOK_CSS)

BOOK_JS = u"""/* 侧边栏交互 + 本章小目录（由 h2 自动生成，不修改正文内容） */
(function(){
  var sb=document.getElementById('sidebar'), btn=document.getElementById('menuBtn'),
      mask=document.getElementById('sbMask'), totop=document.getElementById('totop');

  /* CSS 里 html{scroll-behavior:smooth}，正文很长时平滑滚动会走很久，跳转一律用即时定位 */
  function jump(y){ try{ window.scrollTo({top:y,behavior:'instant'}); }
                    catch(e){ window.scrollTo(0,y); } }

  function toggle(open){ sb.classList.toggle('open',open); mask.classList.toggle('show',open); }
  if(btn) btn.addEventListener('click',function(){ toggle(!sb.classList.contains('open')); });
  if(mask) mask.addEventListener('click',function(){ toggle(false); });

  /* ---- 本章小目录 ---- */

  /* 标题里的公式是内联 SVG，textContent 取不到；
     用 <use data-c="…"> 上的码位还原成字符（𝑉 → V、𝛾 → γ），标题才读得通 */
  function readText(node){
    var out='';
    for(var i=0;i<node.childNodes.length;i++){
      var c=node.childNodes[i];
      if(c.nodeType===3){ out+=c.nodeValue; continue; }
      if(c.nodeType!==1) continue;
      if(c.tagName.toLowerCase()==='svg'){
        var us=c.querySelectorAll('use[data-c]'), s='';
        for(var j=0;j<us.length;j++){
          var cp=parseInt(us[j].getAttribute('data-c'),16);
          if(cp) s+=String.fromCodePoint(cp);
        }
        try{ s=s.normalize('NFKC'); }catch(e){}
        out+=s;
      }else out+=readText(c);
    }
    return out;
  }
  function tidy(s){
    return s.replace(/\\s+/g,' ')
            .replace(/\\s+([，。：、；？！）】」』])/g,'$1')
            .replace(/([（【「『])\\s+/g,'$1').trim();
  }

  var host=document.getElementById('subtoc');
  var heads=[];
  if(host){
    var page=document.body.getAttribute('data-page');
    if(page==='roadmap'){
      heads=[].slice.call(document.querySelectorAll('.content section.stage[id]'));
      heads.forEach(function(s){
        var h=s.querySelector('h2'), n=s.querySelector('.num');
        s.__n=n?n.textContent.replace(/stage/i,'').trim():'';
        s.__t=h?tidy(readText(h)):s.id;
      });
    }else{
      heads=[].slice.call(document.querySelectorAll('.content h2'));
      heads.forEach(function(h,i){
        if(!h.id) h.id='sec-'+(i+1);
        var n=h.querySelector('.n,.num'), lab=tidy(readText(h));
        h.__n=String(i+1);
        if(n){ var t=tidy(n.textContent);
               h.__n=t.replace(/^§\\s*/,'');
               lab=tidy(lab.slice(t.length)); }
        h.__t=lab;
      });
    }
    heads.forEach(function(el){
      var li=document.createElement('li'), a=document.createElement('a');
      a.href='#'+el.id;
      a.innerHTML='<span class="sn"></span><span class="st"></span>';
      a.firstChild.textContent=el.__n;
      a.lastChild.textContent=el.__t;
      a.title=(el.__n?el.__n+'. ':'')+el.__t;
      /* 长页面上平滑滚动会走很久，目录跳转改成即时定位 */
      a.addEventListener('click',function(e){
        e.preventDefault();
        jump(el.getBoundingClientRect().top+window.scrollY-14);
        history.replaceState(null,'','#'+el.id);
        if(window.innerWidth<=1080) toggle(false);
      });
      li.appendChild(a); host.appendChild(li);
    });
  }

  /* ---- 滚动高亮 + 回到顶部 ---- */
  var links=host?[].slice.call(host.querySelectorAll('a')):[];
  function upd(){
    if(links.length){
      var y=window.scrollY+130, cur=-1;
      heads.forEach(function(el,k){ if(el.getBoundingClientRect().top+window.scrollY<=y) cur=k; });
      links.forEach(function(a,k){ a.classList.toggle('cur',k===cur); });
    }
    if(totop) totop.classList.toggle('show', window.scrollY>700);
  }
  window.addEventListener('scroll',upd,{passive:true});
  window.addEventListener('resize',upd); upd();
  if(totop) totop.addEventListener('click',function(e){ e.preventDefault(); jump(0); });

  /* 带 #hash 打开时，同样即时定位（正文很长，平滑滚动会走很久） */
  if(location.hash){
    var t=document.getElementById(location.hash.slice(1));
    if(t) setTimeout(function(){ jump(t.getBoundingClientRect().top+window.scrollY-14); },0);
  }

  /* ---- ← / → 翻章 ---- */
  document.addEventListener('keydown',function(e){
    if(e.target.matches('input,textarea,select')||e.metaKey||e.ctrlKey||e.altKey) return;
    var k=e.key==='ArrowLeft'?'prev':e.key==='ArrowRight'?'next':null;
    if(!k) return;
    var a=document.querySelector('.pagenav a[data-key="'+k+'"]');
    if(a) location.href=a.getAttribute('href');
  });

  /* ---- 记住侧边栏滚动位置 ---- */
  try{
    var key='rlbook-sb-scroll';
    var v=sessionStorage.getItem(key); if(v) sb.scrollTop=+v;
    window.addEventListener('beforeunload',function(){ sessionStorage.setItem(key,sb.scrollTop); });
  }catch(err){}
})();
"""
io.open(os.path.join(OUT, "assets", "book.js"), "w", encoding="utf-8", newline="\n").write(BOOK_JS)

# ----- GitHub Pages：关掉 Jekyll，原样发布静态文件 -----
io.open(os.path.join(OUT, ".nojekyll"), "w", encoding="utf-8", newline="\n").write("")

# ----- SUMMARY.md / README.md (GitBook 结构) -----
sm = [u"# Summary\n", u"* [路线图](index.html)"]
for label, sids in GROUPS[1:]:
    sm.append(u"\n## %s\n" % label)
    for sid in sids:
        sm.append(u"* [第 %s 课 · %s](%s)" % (nums[sid], titles[sid], file_of[sid]))
io.open(os.path.join(OUT, "SUMMARY.md"), "w", encoding="utf-8", newline="\n").write("\n".join(sm) + "\n")

readme = u"""# 强化学习学习手册（CartPole 主线）

由 `RL_Handbook_CartPole.html` 单页文件切分而成的多页版本，正文内容逐字未改，
只增加了侧边栏目录、章节索引与上一章/下一章导航。

从 [`index.html`](index.html) 开始阅读；目录见 [`SUMMARY.md`](SUMMARY.md)。

| 文件 | 内容 |
|---|---|
""" + "\n".join(u"| `%s` | %s |" % (file_of[sid], (u"第 %s 课 · " % nums[sid] if nums[sid] else u"") + titles[sid])
                for fn, sid in PAGES) + u"""

`assets/book.css` = 原文件 `<style>` 原样 + 书本版式；`assets/book.js` 负责侧边栏与本章小目录。
数学公式的 SVG 字形定义按页面实际用到的部分分发到每一页，离线可直接双击打开。
"""
io.open(os.path.join(OUT, "README.md"), "w", encoding="utf-8", newline="\n").write(readme)
print("done ->", OUT)
