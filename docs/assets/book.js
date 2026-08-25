/* 侧边栏交互 + 本章小目录（由 h2 自动生成，不修改正文内容） */
(function(){
  var sb=document.getElementById('sidebar'), btn=document.getElementById('menuBtn'),
      mask=document.getElementById('sbMask'), totop=document.getElementById('totop');

  /* CSS 里 html{scroll-behavior:smooth}，正文很长时平滑滚动会走很久，跳转一律用即时定位 */
  function jump(y){ try{ window.scrollTo({top:y,behavior:'instant'}); }
                    catch(e){ window.scrollTo(0,y); } }

  /* 吸顶条会盖住落点。h2 自带上边距还看得见，但 .substep 这种裸行会整条藏进去，
     所以落点统一把吸顶条的高度让出来 */
  function headroom(){
    var tb=document.querySelector('header.topbar');
    return (tb&&getComputedStyle(tb).position!=='static' ? tb.getBoundingClientRect().height : 0)+14;
  }

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
    return s.replace(/\s+/g,' ')
            .replace(/\s+([，。：、；？！）】」』])/g,'$1')
            .replace(/([（【「『])\s+/g,'$1').trim();
  }

  var host=document.getElementById('subtoc');
  var rail=null;
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
               h.__n=t.replace(/^§\s*/,'');
               lab=tidy(lab.slice(t.length)); }
        h.__t=lab;
      });
    }
    /* h3 的「N.M」前缀也给个 id，正文里的 §N.M 才跳得过去 */
    [].slice.call(document.querySelectorAll('.content h3')).forEach(function(h){
      var m=/^\s*(\d+)\.(\d+)/.exec(h.textContent);
      if(m && !h.id) h.id='sec-'+m[1]+'-'+m[2];
    });

    /* 同一份数据渲染两处：侧栏小目录 + 右侧「本页目录」 */
    function fill(box){
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
          jump(el.getBoundingClientRect().top+window.scrollY-headroom());
          history.replaceState(null,'','#'+el.id);
          if(window.innerWidth<=1080) toggle(false);
        });
        li.appendChild(a); box.appendChild(li);
      });
    }
    fill(host);
    /* 右侧「本页目录」：由 JS 建，各页 HTML 不用改；窄屏由 CSS 隐藏 */
    if(heads.length>1){
      rail=document.createElement('nav');
      rail.className='pagetoc'; rail.id='pagetoc';
      rail.setAttribute('aria-label','本页目录');
      rail.innerHTML='<div class="pt-h">本页目录</div><ol></ol>';
      document.body.appendChild(rail);
      fill(rail.querySelector('ol'));
    }
  }

  /* ---- 滚动高亮 + 回到顶部 ---- */
  var lists=[];
  if(host) lists.push([].slice.call(host.querySelectorAll('a')));
  if(rail) lists.push([].slice.call(rail.querySelectorAll('a')));
  function upd(){
    if(lists.length){
      var y=window.scrollY+130, cur=-1;
      heads.forEach(function(el,k){ if(el.getBoundingClientRect().top+window.scrollY<=y) cur=k; });
      lists.forEach(function(ls){ ls.forEach(function(a,k){ a.classList.toggle('cur',k===cur); }); });
    }
    if(totop) totop.classList.toggle('show', window.scrollY>700);
  }
  window.addEventListener('scroll',upd,{passive:true});
  window.addEventListener('resize',upd); upd();
  if(totop) totop.addEventListener('click',function(e){ e.preventDefault(); jump(0); });

  /* 带 #hash 打开时，同样即时定位（正文很长，平滑滚动会走很久）。
     目标若埋在折叠的 <details> 里（路线图的知识点清单就是），先把外层逐层展开再定位，
     然后闪一下——不然跳到长清单中间，读者不知道该看哪一行 */
  function reveal(id){
    var t=id&&document.getElementById(id);
    if(!t) return;
    for(var p=t.parentNode;p&&p.nodeType===1;p=p.parentNode)
      if(p.tagName.toLowerCase()==='details') p.open=true;
    jump(t.getBoundingClientRect().top+window.scrollY-headroom());
    t.classList.remove('hit'); void t.offsetWidth;   /* 连点同一个链接也要重新闪 */
    t.classList.add('hit');
  }
  if(location.hash) setTimeout(function(){ reveal(location.hash.slice(1)); },0);
  window.addEventListener('hashchange',function(){ reveal(location.hash.slice(1)); });

  /* ---- 正文里的 §N 交叉引用变成链接：可层层跳进去，再层层跳回来 ---- */
  (function(){
    var root=document.querySelector('.content'); if(!root) return;
    var RE=/(?:第\s*(\d+)\s*课\s*)?§\s*(\d+)(?:\.(\d+))?/g;
    /* 讲义页在 docs/，每日一问在 docs/daily/，跨章链接要带上对应前缀 */
    var css=document.querySelector('link[rel="stylesheet"]');
    var PRE=(css&&/^\.\.\//.test(css.getAttribute('href')))?'../':'';
    var SKIP={A:1,CODE:1,H1:1,H2:1,H3:1,SCRIPT:1,STYLE:1,BUTTON:1};

    /* ---- 把正文里的 §N 包成链接 ---- */
    var walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT,null), nodes=[], n;
    while((n=walker.nextNode())){
      if(!/§/.test(n.nodeValue)) continue;
      var bad=false;
      for(var q=n.parentNode;q&&q!==root;q=q.parentNode){ if(SKIP[q.tagName]){bad=true;break;} }
      if(!bad) nodes.push(n);
    }
    nodes.forEach(function(t){
      var out=document.createDocumentFragment(), last=0, m; RE.lastIndex=0;
      while((m=RE.exec(t.nodeValue))){
        out.appendChild(document.createTextNode(t.nodeValue.slice(last,m.index)));
        var ch=m[1], id='sec-'+m[2]+(m[3]?'-'+m[3]:'');
        if(ch===undefined && !document.getElementById(id)){      /* 本页没有这一节就不加链接 */
          out.appendChild(document.createTextNode(m[0])); last=RE.lastIndex; continue;
        }
        var a=document.createElement('a');
        a.className='xref'; a.href=(ch!==undefined?PRE+'ch'+ch+'.html#'+id:'#'+id); a.textContent=m[0];
        if(ch===undefined) a.setAttribute('data-inpage','1');
        out.appendChild(a); last=RE.lastIndex;
      }
      out.appendChild(document.createTextNode(t.nodeValue.slice(last)));
      t.parentNode.replaceChild(out,t);
    });

    /* ---- 跳转栈：每跳一层压一个来处，返回时逐层弹回 ---- */
    var KEY='rlbook-jump-stack', PEND='rlbook-jump-restore', NAV='rlbook-jump-nav';
    function get(k,d){ try{ return JSON.parse(sessionStorage.getItem(k)) || d; }catch(e){ return d; } }
    function set(k,v){ try{ sessionStorage.setItem(k,JSON.stringify(v)); }catch(e){} }
    function del(k){ try{ sessionStorage.removeItem(k); }catch(e){} }
    function here(){ return location.pathname; }

    /* 从别的章「返回」过来：恢复当时的位置 */
    var pend=get(PEND,null);
    if(pend && pend.url===here()){ del(PEND); setTimeout(function(){ jump(pend.y); },0); }
    /* 不是通过 §链接 跨页过来的（比如点了「下一章」），旧的栈就作废 */
    var viaXref=sessionStorage.getItem(NAV); del(NAV);
    if(!viaXref && !pend) set(KEY,[]);

    var back=document.createElement('button');
    back.className='backjump'; back.type='button';
    back.innerHTML='<span class="bj-i">↩</span><span class="bj-t"></span>';
    document.body.appendChild(back);

    function render(){
      var st=get(KEY,[]);
      if(!st.length){ back.classList.remove('show'); return; }
      var top=st[st.length-1];
      back.querySelector('.bj-t').textContent =
        '返回 ' + (top.label||'原处') + (st.length>1 ? ' · 还有 '+(st.length-1)+' 层' : '');
      back.title = '回到点击 '+(top.label||'')+' 之前的位置';
      back.classList.add('show');
    }

    root.addEventListener('click',function(e){
      var a=e.target.closest && e.target.closest('a.xref'); if(!a) return;
      var st=get(KEY,[]);
      st.push({url:here(), y:window.scrollY, label:a.textContent});
      set(KEY,st);
      if(a.getAttribute('data-inpage')){
        var el=document.getElementById(a.getAttribute('href').slice(1));
        if(!el){ st.pop(); set(KEY,st); return; }
        e.preventDefault();
        jump(el.getBoundingClientRect().top+window.scrollY-14);
        history.replaceState(null,'',a.getAttribute('href'));
        render();
      }else{
        set(NAV,1);            /* 跨章：让它正常跳走，新页加载后按钮接着出现 */
      }
    });

    back.addEventListener('click',function(){
      var st=get(KEY,[]), e=st.pop(); set(KEY,st);
      if(!e){ render(); return; }
      if(e.url===here()){ jump(e.y); render(); }
      else { set(PEND,e); set(NAV,1); location.href=e.url; }
    });

    render();
  })();

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
