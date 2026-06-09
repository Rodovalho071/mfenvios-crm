const fs = require('fs');
let h = fs.readFileSync('public/index.html', 'utf8');
h = h.replace('<div class="form-group"><label class="form-label">Chave da API Anthropic</label><input type="password" id="ia-key" placeholder="sk-ant-..." oninput="saveKey()"/></div>', '');
const idx = h.indexOf('async function analisarMsg(){');
const idxEnd = h.indexOf('\nfunction ', idx + 10);
const nova = 'async function analisarMsg(){\n  const msg=document.getElementById(\'ia-msg\').value.trim();\n  if(!msg){toast(\'Cole uma mensagem.\');return;}\n  const out=document.getElementById(\'ia-output\');\n  out.style.display=\'block\';\n  out.innerHTML=\'Analisando...\';\n  fetch(\'/analisar\',{method:\'POST\',headers:{\'Content-Type\':\'application/json\'},body:JSON.stringify({mensagem:msg})}).then(r=>r.json()).then(d=>{if(!d.ok)throw new Error(d.error);const p=d.dados;iaPreview=p;out.innerHTML=\'<b>\'+p.nome+\'</b><br>\'+p.tel+\'<br>\'+p.material+\'<br>\'+(p.origem?p.origem+\' a \'+p.destino:\'\')+'<br>Etapa: \'+p.etapa+\'<br>Obs: \'+p.obs+\'<br><button class=btn btn-primary onclick=addLeadFromIA()>+ Adicionar</button>\';save(\'crm-ia-hist\',[{...p,ts:Date.now()},...load(\'crm-ia-hist\',[]).slice(0,9)]);renderIAHistory();}).catch(e=>out.innerHTML=\'Erro: \'+e.message);\n}\n';
h = h.substring(0, idx) + nova + h.substring(idxEnd);
fs.writeFileSync('public/index.html', h, 'utf8');
console.log('OK! Linhas:', h.split('\n').length);
