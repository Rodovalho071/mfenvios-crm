with open('public/index.html', 'r', encoding='utf-8') as f:
    h = f.read()

# Remover campo chave Anthropic
h = h.replace(
    '<div class="form-group"><label class="form-label">Chave da API Anthropic</label><input type="password" id="ia-key" placeholder="sk-ant-..." oninput="saveKey()"/></div>',
    ''
)

# Substituir funcao analisarMsg
idx = h.find('async function analisarMsg(){')
idx_end = h.find('\nfunction ', idx + 10)

nova = """async function analisarMsg(){
  const msg=document.getElementById('ia-msg').value.trim();
  if(!msg){toast('Cole uma mensagem.');return;}
  const out=document.getElementById('ia-output');
  out.style.display='block';
  out.innerHTML='<div style="color:var(--text3)">Analisando com Groq...</div>';
  fetch('/analisar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mensagem:msg})})
  .then(r=>r.json())
  .then(d=>{
    if(!d.ok)throw new Error(d.error);
    const p=d.dados;iaPreview=p;
    const rota=p.origem&&p.destino?p.origem+' \u2192 '+p.destino:'--';
    out.innerHTML='<div class="field"><span class="field-label">Nome</span>'+(p.nome||'--')+'</div>'
      +'<div class="field"><span class="field-label">Telefone</span>'+(p.tel||'--')+'</div>'
      +'<div class="field"><span class="field-label">Material</span>'+(p.material||'--')+'</div>'
      +'<div class="field"><span class="field-label">Rota</span>'+rota+'</div>'
      +'<div class="field"><span class="field-label">Etapa</span>'+(p.etapa||'--')+'</div>'
      +'<div class="field"><span class="field-label">Obs</span>'+(p.obs||'--')+'</div>'
      +'<div style="margin-top:12px"><button class="btn btn-primary" onclick="addLeadFromIA()">+ Adicionar ao Funil</button></div>';
    save('crm-ia-hist',[{...p,ts:Date.now()},...load('crm-ia-hist',[]).slice(0,9)]);
    renderIAHistory();
  })
  .catch(e=>out.innerHTML='<div style="color:var(--red)">Erro: '+e.message+'</div>');
}
"""

h = h[:idx] + nova + h[idx_end:]

with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(h)

print('OK! Linhas:', len(h.splitlines()))
print('Chave removida:', 'Chave da API Anthropic' not in h)
print('/analisar:', '/analisar' in h)
