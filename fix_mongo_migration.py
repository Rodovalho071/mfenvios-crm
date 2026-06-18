print("Iniciando migracao localStorage -> MongoDB...")

# ── LER ARQUIVOS ────────────────────────────────────────────
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

with open('server.js', 'r', encoding='utf-8') as f:
    srv = f.read()

html_orig = html
srv_orig = srv

erros = []

# ════════════════════════════════════════════════════════════
# CORREÇÃO 1 — server.js: adicionar PUT e DELETE /kanban/:id
# ════════════════════════════════════════════════════════════
old_kanban_patch = "app.patch('/kanban/:id',async function(req,res){\n  await updateKanbanColuna(req.params.id,req.body.coluna);\n  broadcast('kanban-update',await getKanban());\n  res.json({ok:true});\n});"

new_kanban_patch = """app.patch('/kanban/:id',async function(req,res){
  await updateKanbanColuna(req.params.id,req.body.coluna);
  broadcast('kanban-update',await getKanban());
  res.json({ok:true});
});
app.put('/kanban/:id',async function(req,res){
  const lead=Object.assign({},req.body,{id:req.params.id});
  try{
    if(kanbanCol){ await kanbanCol.updateOne({id:req.params.id},{$set:lead},{upsert:true}); }
    else{ const i=memKanban.cards.findIndex(c=>c.id===req.params.id); if(i>=0) memKanban.cards[i]=lead; else memKanban.cards.push(lead); }
    res.json({ok:true});
  }catch(e){res.status(500).json({error:e.message});}
});
app.delete('/kanban/:id',async function(req,res){
  try{
    if(kanbanCol){ await kanbanCol.deleteOne({id:req.params.id}); }
    else{ memKanban.cards=memKanban.cards.filter(c=>c.id!==req.params.id); }
    res.json({ok:true});
  }catch(e){res.status(500).json({error:e.message});}
});"""

if old_kanban_patch in srv:
    srv = srv.replace(old_kanban_patch, new_kanban_patch)
    print("OK 1/6 - server.js: PUT e DELETE /kanban/:id adicionados")
else:
    erros.append("1 - patch kanban nao encontrado no server.js")

# ════════════════════════════════════════════════════════════
# CORREÇÃO 2 — index.html: formatMoeda corrigida
# ════════════════════════════════════════════════════════════
old_fmt = "function formatMoeda(v) {\n  var n = parseFloat((v||'0').toString().replace(/\\./g,'').replace(',','.'));\n  if(isNaN(n)) return 'R$ 0,00';\n  return 'R$ ' + n.toLocaleString('pt-BR', {minimumFractionDigits:2, maximumFractionDigits:2});\n}"

new_fmt = """function formatMoeda(v) {
  if(typeof v==='number'){if(isNaN(v))return 'R$ 0,00';return 'R$ '+v.toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2});}
  var s=(v||'0').toString().replace(/[R$\\s]/g,'').trim();
  var n;if(s.indexOf(',')!==-1){n=parseFloat(s.replace(/\\./g,'').replace(',','.'));}else{n=parseFloat(s);}
  if(isNaN(n))return 'R$ 0,00';
  return 'R$ '+n.toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2});
}"""

if old_fmt in html:
    html = html.replace(old_fmt, new_fmt)
    print("OK 2/6 - formatMoeda corrigida")
else:
    erros.append("2 - formatMoeda nao encontrada")

# ════════════════════════════════════════════════════════════
# CORREÇÃO 3 — index.html: saveLeads salva no MongoDB
# ════════════════════════════════════════════════════════════
old_saveLeads = """function saveLeads(){
  save('crm-leads',leads);
  updateStats();
  // Sincronizar cada lead com MongoDB
  leads.forEach(function(lead){
    fetch('/kanban-import',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(lead)}).catch(function(){});
  });
}"""

new_saveLeads = """function saveLeads(){
  updateStats();
  // Salvar cada lead no MongoDB (fonte principal)
  leads.forEach(function(lead){
    fetch('/kanban-import',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(lead)}).catch(function(){});
  });
}"""

if old_saveLeads in html:
    html = html.replace(old_saveLeads, new_saveLeads)
    print("OK 3/6 - saveLeads: removido localStorage, salva no MongoDB")
else:
    erros.append("3 - saveLeads nao encontrada")

# ════════════════════════════════════════════════════════════
# CORREÇÃO 4 — index.html: deleteLead deleta no MongoDB
# ════════════════════════════════════════════════════════════
old_deleteLead = "function deleteLead(id){if(!confirm('Excluir este lead?'))return;const l=leads.find(x=>x.id===id);leads=leads.filter(x=>x.id!==id);saveLeads();addActivity(`Lead <strong>${l?.name}</strong> excluído.`);closeModal();renderKanban();toast('Lead excluído.');}"

new_deleteLead = """function deleteLead(id){
  if(!confirm('Excluir este lead?'))return;
  const l=leads.find(x=>x.id===id);
  leads=leads.filter(x=>x.id!==id);
  updateStats();
  fetch('/kanban/'+id,{method:'DELETE'}).catch(function(){});
  addActivity('Lead <strong>'+(l?l.name:'')+'</strong> excluído.');
  closeModal();renderKanban();toast('Lead excluído.');
}"""

if old_deleteLead in html:
    html = html.replace(old_deleteLead, new_deleteLead)
    print("OK 4/6 - deleteLead: exclui no MongoDB")
else:
    erros.append("4 - deleteLead nao encontrada")

# ════════════════════════════════════════════════════════════
# CORREÇÃO 5 — index.html: inicialização carrega do MongoDB
# ════════════════════════════════════════════════════════════
old_init_leads = "let leads=load('crm-leads',[]),activity=load('crm-activity',[]),agentName=load('crm-agent',''),iaKey=load('crm-ia-key',''),iaPreview=null;"

new_init_leads = "let leads=[],activity=load('crm-activity',[]),agentName=load('crm-agent',''),iaKey=load('crm-ia-key',''),iaPreview=null;"

if old_init_leads in html:
    html = html.replace(old_init_leads, new_init_leads)
    print("OK 5/6 - inicializacao: leads comeca vazio, carrega do MongoDB")
else:
    erros.append("5 - init leads nao encontrada")

# ════════════════════════════════════════════════════════════
# CORREÇÃO 6 — index.html: sincronizarLeadsServidor é a fonte principal
# ════════════════════════════════════════════════════════════
old_sinc = """function sincronizarLeadsServidor() {
  fetch('/kanban').then(function(r){return r.json();}).then(function(data){
    if(data && data.cards && data.cards.length > 0) {
      var serverLeads = data.cards;
      serverLeads.forEach(function(sl){
        var idx = leads.findIndex(function(l){ return l.id === sl.id; });
        if(idx < 0) {
          leads.push(sl);
        } else {
          leads[idx] = Object.assign({}, leads[idx], sl);
        }
      });
      save('crm-leads', leads);
      updateStats();
      if(typeof renderKanban === 'function') renderKanban();
    }
  }).catch(function(){});
}"""

new_sinc = """function sincronizarLeadsServidor() {
  fetch('/kanban').then(function(r){return r.json();}).then(function(data){
    if(data && data.cards) {
      leads = data.cards;
      updateStats();
      if(typeof renderKanban === 'function') renderKanban();
      if(typeof renderLeads === 'function') renderLeads();
      if(typeof updateAgentFilters === 'function') updateAgentFilters();
    }
  }).catch(function(){});
}"""

if old_sinc in html:
    html = html.replace(old_sinc, new_sinc)
    print("OK 6/6 - sincronizarLeadsServidor: MongoDB e a fonte principal")
else:
    erros.append("6 - sincronizarLeadsServidor nao encontrada")

# ════════════════════════════════════════════════════════════
# RESULTADO
# ════════════════════════════════════════════════════════════
print("")
if erros:
    print("ATENCAO - Itens nao encontrados:")
    for e in erros:
        print("  X " + e)

if html != html_orig:
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("index.html atualizado!")
else:
    print("index.html sem alteracoes")

if srv != srv_orig:
    with open('server.js', 'w', encoding='utf-8') as f:
        f.write(srv)
    print("server.js atualizado!")
else:
    print("server.js sem alteracoes")

if not erros:
    print("")
    print("Proximo passo:")
    print("git add index.html server.js && git commit -m 'feat: leads 100pct MongoDB, sem localStorage' && git push origin main")

