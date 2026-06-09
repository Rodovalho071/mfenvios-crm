path='C:/mfcrm/public/index.html'
s=open(path,'r',encoding='utf-8',errors='ignore').read()
print('Tamanho:',len(s))
OLD='<div class="kanban-board" id="kanban-board">'
BOTOES='<div style="display:flex;align-items:center;gap:10px;padding:8px 20px;flex-shrink:0"><button class="btn btn-sm" onclick="funiNavegar(-1)">&#9664;</button><span id="funil-mes-label" style="font-size:14px;font-weight:700;min-width:140px;text-align:center;color:var(--text)"></span><button class="btn btn-sm" onclick="funiNavegar(1)">&#9654;</button><span id="funil-count" style="margin-left:auto;font-size:12px;color:var(--text3)"></span></div>\n'
s=s.replace(OLD,BOTOES+OLD,1)
print('OK1')
JS='\nvar funiMesOffset=0;\nfunction funiGetMesInicio(){var d=new Date();d.setDate(1);d.setHours(0,0,0,0);d.setMonth(d.getMonth()+funiMesOffset);return d.getTime();}\nfunction funiGetMesFim(){var d=new Date();d.setDate(1);d.setHours(0,0,0,0);d.setMonth(d.getMonth()+funiMesOffset+1);return d.getTime();}\nfunction funiAtualizarLabel(){var d=new Date();d.setDate(1);d.setMonth(d.getMonth()+funiMesOffset);var m=["Janeiro","Fevereiro","Marco","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"];var el=document.getElementById("funil-mes-label");if(el)el.textContent=m[d.getMonth()]+" "+d.getFullYear();var cnt=document.getElementById("funil-count");if(cnt){var mi=funiGetMesInicio(),mf=funiGetMesFim();var tot=leads.filter(function(l){return(l.ts||0)>=mi&&(l.ts||0)<mf;});cnt.textContent=tot.length+" lead(s)";}}\nfunction funiNavegar(delta){var n=funiMesOffset+delta;if(n>0)return;funiMesOffset=n;renderKanban();}\n'
anchor="var opTabAtual = 'fretes';"
if anchor not in s:
    anchor="let opTabAtual = 'fretes';"
s=s.replace(anchor,anchor+JS,1)
print('OK2')
OLD2='let cards=leads.filter(l=>l.stage===stage);'
NEW2='funiAtualizarLabel();var _mi=funiGetMesInicio(),_mf=funiGetMesFim();let cards=leads.filter(l=>l.stage===stage&&(l.ts||0)>=_mi&&(l.ts||0)<_mf);'
if OLD2 in s:
    s=s.replace(OLD2,NEW2,1)
    print('OK3')
else:
    print('ERRO3')
open(path,'w',encoding='utf-8').write(s)
print('SALVO!')
