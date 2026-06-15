import pathlib,sys
f=pathlib.Path(r"C:\mfcrm\index.html")
if not f.exists():print("ERRO: index.html nao encontrado");sys.exit(1)
html=f.read_text(encoding="utf-8")
changes=0
SUBS=[
("function parseMoeda(v) {\n  if(!v && v!==0) return 0;\n  var s = v.toString().replace(/[R$\\s]/g,'').trim();\n  // Remove tudo exceto n\u00fameros, ponto e v\u00edrgula\n  // Formato BR: 1.500,75 ou 1500,75\n  // Formato US: 1500.75\n  if(s.indexOf(',') !== -1) {\n    // Tem v\u00edrgula \u2014 formato brasileiro\n    s = s.replace(/\\./g,'').replace(',','.');\n  }\n  // Se n\u00e3o tem v\u00edrgula, pode ser inteiro ou formato US\n  var n = parseFloat(s);\n  return isNaN(n) ? 0 : n;\n}",
"function parseMoeda(v){\n  if(v===null||v===undefined||v==='')return 0;\n  if(typeof v==='number'){if(Number.isInteger(v)&&v>=1000)return v/100;return v;}\n  var s=v.toString().replace(/R\\$\\s*/g,'').replace(/\\s/g,'').trim();\n  if(s.indexOf(',')!==-1){s=s.replace(/\\./g,'').replace(',','.');return parseFloat(s)||0;}\n  if(s.indexOf('.')!==-1){var p=s.split('.');if(p.length===2&&p[1].length<=2)return parseFloat(s)||0;s=s.replace(/\\./g,'');}\n  var n=parseFloat(s)||0;if(Number.isInteger(n)&&n>=1000)return n/100;return n;\n}\nfunction mascaraMoeda(el){\n  var d=el.value.replace(/\\D/g,'');if(!d){el.value='';el.dataset.valor='0';return;}\n  d=d.replace(/^0+/,'')||'0';while(d.length<3)d='0'+d;\n  var i=d.slice(0,-2)||'0',dc=d.slice(-2);\n  i=i.replace(/\\B(?=(\\d{3})+(?!\\d))/g,'.');\n  el.value=i+','+dc;el.dataset.valor=(parseInt(d)/100).toFixed(2);\n}\nfunction valorParaSalvar(el){return el.dataset&&el.dataset.valor?parseFloat(el.dataset.valor):parseMoeda(el.value);}",
"parseMoeda"),
('id="fin-valor" type="text" placeholder="0,00" style="width:100%;background:var(--bg3);border:1px solid var(--border);border-radius:6px;color:var(--text);padding:8px 10px;font-size:13px;"',
'id="fin-valor" type="text" placeholder="0,00" oninput="mascaraMoeda(this)" style="width:100%;background:var(--bg3);border:1px solid var(--border);border-radius:6px;color:var(--text);padding:8px 10px;font-size:13px;text-align:right;font-family:monospace;"',
"fin-valor"),
('id="nf-valor" type="text" style="width:100%;background:var(--bg3);border:1px solid var(--border);border-radius:6px;color:var(--text);padding:8px 10px;font-size:13px;" placeholder="0,00"',
'id="nf-valor" type="text" placeholder="0,00" oninput="mascaraMoeda(this)" style="width:100%;background:var(--bg3);border:1px solid var(--border);border-radius:6px;color:var(--text);padding:8px 10px;font-size:13px;text-align:right;font-family:monospace;"',
"nf-valor"),
("var valor = document.getElementById('fin-valor').value.trim();",
"var valor = valorParaSalvar(document.getElementById('fin-valor'));",
"salvar-valor"),
]
for old,new,label in SUBS:
    if old in html:html=html.replace(old,new,1);changes+=1;print("OK",label)
    else:print("--",label,"nao encontrado")
if changes:f.write_text(html,encoding="utf-8");print(f"\nindex.html atualizado ({changes} mudancas). Faca git add/commit/push!")
else:print("Nada mudou - verifique se o arquivo e o correto")
