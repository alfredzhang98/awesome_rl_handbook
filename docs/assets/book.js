/* 侧边栏交互 + 本章小目录（由 h2 自动生成，不修改正文内容） */
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
    return s.replace(/\s+/g,' ')
            .replace(/\s+([，。：、；？！）】」』])/g,'$1')
            .replace(/([（【「『])\s+/g,'$1').trim();
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
               h.__n=t.replace(/^§\s*/,'');
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
