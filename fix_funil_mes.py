path="C:/mfcrm/public/index.html"
s=open(path,"r",encoding="utf-8").read()
print("Lido:",len(s),"chars")

# 1. Botoes de mes
OLD='<div class="kanban-board" id="kanban-board">'
BTN='<div style="display:flex;align-items:center;gap:10px;padding:8px 20px;flex-shrink:0"><button class="btn btn-sm" onclick="funiNavegar(-1)">&#9664;</button><span id="funil-mes-label" style="font-size:14px;font-weight:700;min-width:130px;text-align:center"></span><button class="btn btn-sm" onclick="funiNavegar(1)">&#9654;</button><span id="funil-count" style="margin-left:auto;font-size:12px;color:var(--text3)"></span></div>'
s=s.replace(OLD,BTN+"\n"+OLD,1)
print("OK1")

# 2. JS de mes
JS='\nlet funiMesOffset=0;\nfunction funiGetMesInicio(){const d=new Date();d.setDate(1);d.setHours(0,0,0,0);d.setMonth(d.getMonth()+funiMesOffset);return d.getTime();}\nfunction funiGetMesFim(){const d=new Date();d.setDate(1);d.setHours(0,0,0,0);d.setMonth(d.getMonth()+funiMesOffset+1);return d.getTime();}\nfunction funiAtualizarLabel(){const d=new Date();d.setDate(1);d.setMonth(d.getMonth()+funiMesOffset);const m=["Janeiro","Fevereiro","Marco","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"];const el=document.getElementById("funil-mes-label");if(el)el.textContent=m[d.getMonth()]+" "+d.getFullYear();}\nfunction funiNavegar(delta){const n=funiMesOffset+delta;if(n>0)return;funiMesOffset=n;renderKanban();}\n'
s=s.replace("function renderKanban",JS+"function renderKanban",1)
print("OK2")

# 3. Filtro de mes
OLD2='let cards=leads.filter(l=>l.stage===stage);'
NEW2='funiAtualizarLabel();const _mi=funiGetMesInicio(),_mf=funiGetMesFim();const _cnt=document.getElementById("funil-count");const _tot=leads.filter(l=>(l.ts||0)>=_mi&&(l.ts||0)<_mf);if(_cnt)_cnt.textContent=_tot.length+" lead(s)";let cards=leads.filter(l=>l.stage===stage&&(l.ts||0)>=_mi&&(l.ts||0)<_mf);'
if OLD2 in s:
    s=s.replace(OLD2,NEW2,1)
    print("OK3")
else:
    print("ERRO3")

open(path,"w",encoding="utf-8").write(s)
print("SALVO!")
