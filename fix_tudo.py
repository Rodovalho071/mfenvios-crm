import shutil, re

ARQUIVO = r"C:\mfcrm\public\index.html"

with open(ARQUIVO, "r", encoding="utf-8") as f:
    html = f.read()

ok = []
err = []

# ═══════════════════════════════════════════════════════════════
# BUG 1 — RELATÓRIO: o template literal captura HTML do Operacional
# O footer do relatório está na linha com "Gerado automaticamente"
# mas o backtick de fechamento só vem muito depois (após o Operacional view)
# Fix: fechar o template corretamente após o footer
# ═══════════════════════════════════════════════════════════════

OLD_FOOTER = """  <div class="footer">Gerado automaticamente · MF Envios · ${dataStr}</div>\n  \n<!-- OPERACIONAL VIEW -->"""
NEW_FOOTER = """  <div class="footer">Gerado automaticamente · MF Envios · ${dataStr}</div>\n</body></html>`;\n\n  const w=window.open('','_blank');w.document.write(html);w.document.close();\n  setTimeout(()=>w.print(),500);\n}\n\n<!-- OPERACIONAL VIEW -->"""

if OLD_FOOTER in html:
    html = html.replace(OLD_FOOTER, NEW_FOOTER)
    # Agora remover o backtick antigo que ficou na linha 921 (era </body></html>`)
    # e a chamada duplicada ao window.open
    OLD_CLOSING = """</body></html>`;

  const w=window.open('','_blank');w.document.write(html);w.document.close();
  setTimeout(()=>w.print(),500);
}"""
    NEW_CLOSING = "</div>\n}"  # só fecha a div do operacional e a função
    # Na verdade o que precisa é só remover o backtick+window.open duplicado
    # Vamos ser mais precisos:
    OLD_DUP = """</body></html>`;

  const w=window.open('','_blank');w.document.write(html);w.document.close();
  setTimeout(()=>w.print(),500);
}"""
    if OLD_DUP in html:
        # Substituir pelo fechamento limpo da função abrirRelatorio (que agora está vazia)
        html = html.replace(OLD_DUP, "")
        ok.append("BUG 1 ✅ Relatório: template literal corrigido (não captura mais o Operacional)")
    else:
        ok.append("BUG 1 ✅ Relatório: footer corrigido (backtick duplicado pode precisar ajuste manual)")
else:
    # Tenta abordagem alternativa via regex
    # Procura o footer do relatório seguido de conteúdo HTML não-relatório
    pattern = r'(<div class="footer">Gerado automaticamente[^<]*</div>\s*\n)(.*?)(</body></html>`;\s*\n\s*const w=window\.open)'
    match = re.search(pattern, html, re.DOTALL)
    if match:
        middle_junk = match.group(2)  # HTML do Operacional que vazou para dentro
        old_block = match.group(0)
        new_block = match.group(1) + '\n</body></html>`;\n\n  const w=window.open'
        html = html.replace(old_block, new_block + match.group(3)[len('</body></html>`;\n\n  const w=window.open'):] if False else '')
        # Simplifica: apenas insere fechamento após footer e remove duplicata
        idx_footer = html.index('<div class="footer">Gerado automaticamente')
        idx_end_footer = html.index('</div>', idx_footer) + len('</div>')
        idx_old_close = html.index('</body></html>`;', idx_footer)
        # Texto entre footer e antigo fechamento (é o HTML do Operacional que vazou)
        junk = html[idx_end_footer:idx_old_close]
        # Novo HTML: footer + fechamento + junk (agora fora do template)
        html = html[:idx_end_footer] + '\n</body></html>`;\n\n  const w=window.open(\'\',' + "'_blank');" + "w.document.write(html);w.document.close();\n  setTimeout(()=>w.print(),500);\n}\n\n" + junk + html[idx_old_close + len('</body></html>`;'):]
        # Remove window.open duplicado que ficou
        DUP2 = "\n  const w=window.open('','_blank');w.document.write(html);w.document.close();\n  setTimeout(()=>w.print(),500);\n}"
        if html.count("const w=window.open") > 1:
            # Remove segunda ocorrência
            first = html.index("const w=window.open")
            second = html.index("const w=window.open", first + 10)
            end_second = html.index("}", second) + 1
            html = html[:second-3] + html[end_second:]
        ok.append("BUG 1 ✅ Relatório: corrigido via regex")
    else:
        err.append("BUG 1 ⚠️  Relatório: padrão não encontrado — verifique manualmente")

# ═══════════════════════════════════════════════════════════════
# BUG 2 — STATS ZERADOS: updateStats filtra por agent mas leads
# do Davi têm agent='Davi' e a Beatriz não vê nenhum
# Fix: stats do perfil ativo mostram TODOS os leads (ganho/perdido/negociação)
# A mini-barra do outro perfil mostra os dados dele
# ═══════════════════════════════════════════════════════════════

OLD_FILTER_STATS = "    leadsMes = todosMes.filter(l => l.agent === p.nome || (!l.agent && p.stages.includes(l.stage)));\n    const leadsOutro = todosMes.filter(l => l.agent === pOutro.nome || (!l.agent && pOutro.stages.includes(l.stage)));"

NEW_FILTER_STATS = """    // Leads do perfil ativo: por agente (prioritário) OU por etapa (compatibilidade)
    leadsMes = todosMes.filter(l => {
      if(l.agent && l.agent !== '') return l.agent === p.nome;
      return p.stages.includes(l.stage);
    });
    // Leads do outro perfil
    const leadsOutro = todosMes.filter(l => {
      if(l.agent && l.agent !== '') return l.agent === pOutro.nome;
      return pOutro.stages.includes(l.stage) && !p.stages.includes(l.stage);
    });"""

if OLD_FILTER_STATS in html:
    html = html.replace(OLD_FILTER_STATS, NEW_FILTER_STATS)
    ok.append("BUG 2 ✅ Stats: filtro por agent corrigido (leads com agent vazio usam etapa como fallback)")
else:
    err.append("BUG 2 ⚠️  Stats: padrão exato não encontrado")

# ═══════════════════════════════════════════════════════════════
# BUG 3 — DAVI NÃO APARECE PARA BEATRIZ via "Ver todos"
# getLeadsPerfil com verTodos=true já retorna todos — OK
# Mas o renderKanban também filtra independentemente por perfilAtivo
# Fix: quando verTodos=true, renderKanban não deve filtrar por perfil
# (já está correto no código — o bug é que verTodos não é resetado ao trocar perfil)
# Também: getLeadsPerfil deve filtrar estritamente por agent quando definido
# ═══════════════════════════════════════════════════════════════

OLD_GET_LEADS = """function getLeadsPerfil() {
  if(verTodos) return leads;
  if(!perfilAtivo) return leads;
  // Filtra por responsável se definido, senão mostra todos
  const p = PERFIS[perfilAtivo];
  const doMeuPerfil = leads.filter(l => !l.agent || l.agent === p.nome || l.agent === '');
  return doMeuPerfil.length > 0 ? doMeuPerfil : leads;
}"""

NEW_GET_LEADS = """function getLeadsPerfil() {
  if(verTodos || !perfilAtivo) return leads;
  const p = PERFIS[perfilAtivo];
  if(!p) return leads;
  // Filtra por agent quando definido, usa etapa como fallback para leads antigos
  return leads.filter(l => {
    if(l.agent && l.agent !== '') return l.agent === p.nome;
    return p.stages.includes(l.stage);
  });
}"""

if OLD_GET_LEADS in html:
    html = html.replace(OLD_GET_LEADS, NEW_GET_LEADS)
    ok.append("BUG 3 ✅ getLeadsPerfil: filtro estrito por agent (com fallback por etapa)")
else:
    err.append("BUG 3 ⚠️  getLeadsPerfil: padrão não encontrado")

# ═══════════════════════════════════════════════════════════════
# BUG 4 — RENDERKANBAN também filtra por perfil independente
# Garante que quando verTodos=true, não filtra
# (já está implementado, mas garantir que usa getLeadsPerfil consistentemente)
# ═══════════════════════════════════════════════════════════════

OLD_KANBAN_FILTER = """  // Filtrar por perfil ativo
  let leadsParaFiltrar = leadsMes;
  if(typeof perfilAtivo !== 'undefined' && perfilAtivo && typeof PERFIS !== 'undefined' && !verTodos) {
    const pAtivo = PERFIS[perfilAtivo];
    leadsParaFiltrar = leadsMes.filter(l => l.agent === pAtivo.nome || (!l.agent && pAtivo.stages.includes(l.stage)));
  }
  const leadsPerfilMes = leadsParaFiltrar;"""

NEW_KANBAN_FILTER = """  // Filtrar por perfil ativo (consistente com getLeadsPerfil)
  let leadsPerfilMes;
  if(verTodos || !perfilAtivo) {
    leadsPerfilMes = leadsMes;
  } else {
    const pAtivo = PERFIS[perfilAtivo];
    leadsPerfilMes = pAtivo ? leadsMes.filter(l => {
      if(l.agent && l.agent !== '') return l.agent === pAtivo.nome;
      return pAtivo.stages.includes(l.stage);
    }) : leadsMes;
  }"""

if OLD_KANBAN_FILTER in html:
    html = html.replace(OLD_KANBAN_FILTER, NEW_KANBAN_FILTER)
    ok.append("BUG 4 ✅ renderKanban: filtro consistente com getLeadsPerfil")
else:
    err.append("BUG 4 ⚠️  renderKanban filtro: padrão não encontrado (pode já estar correto)")

# ═══════════════════════════════════════════════════════════════
# BUG 5 — WPP: separar mensagens por perfil (instance no fetch)
# ═══════════════════════════════════════════════════════════════

# Adicionar mapeamento de instância se não existir
if "PERFIL_INSTANCIA" not in html:
    anchor = "let perfilAtivo = localStorage.getItem"
    if anchor in html:
        idx = html.index(anchor)
        INSTANCIA_JS = """// Mapeamento perfil → instância WhatsApp
const PERFIL_INSTANCIA = { beatriz: 'mfenvios', davi: 'mfenvios-davi' };
function getInstanciaAtiva() {
  if (!perfilAtivo || verTodos) return null;
  return PERFIL_INSTANCIA[perfilAtivo] || null;
}

"""
        html = html[:idx] + INSTANCIA_JS + html[idx:]
        ok.append("BUG 5 ✅ WPP: PERFIL_INSTANCIA mapeamento adicionado")

# Filtrar fetch de mensagens por instância
OLD_FETCH = "const res=await fetch(WPP_SERVER+'/messages');if(!res.ok)throw new Error();"
NEW_FETCH = "const _inst=getInstanciaAtiva(); const res=await fetch(WPP_SERVER+'/messages'+(_inst?'?instance='+_inst:''));if(!res.ok)throw new Error();"

if OLD_FETCH in html:
    html = html.replace(OLD_FETCH, NEW_FETCH)
    ok.append("BUG 5 ✅ WPP: fetch /messages filtra por instância do perfil ativo")
else:
    err.append("BUG 5 ⚠️  WPP fetch: padrão não encontrado")

# Também no setInterval que atualiza o badge
OLD_INTERVAL = "setInterval(()=>{fetch(WPP_SERVER+'/messages').then(r=>r.json()).then(msgs=>{"
NEW_INTERVAL = "setInterval(()=>{const _i=getInstanciaAtiva();fetch(WPP_SERVER+'/messages'+(_i?'?instance='+_i:'')).then(r=>r.json()).then(msgs=>{"

if OLD_INTERVAL in html:
    html = html.replace(OLD_INTERVAL, NEW_INTERVAL)
    ok.append("BUG 5 ✅ WPP: setInterval badge também filtra por instância")

# ═══════════════════════════════════════════════════════════════
# SERVER.JS — adicionar campo instance e filtro no GET /messages
# ═══════════════════════════════════════════════════════════════
SRV_PATH = r"C:\mfcrm\server.js"
with open(SRV_PATH, "r", encoding="utf-8") as f:
    srv = f.read()

# Adicionar instance ao salvar mensagem no webhook
OLD_MSG_OBJ = "const msg={id:m.key.id||Date.now().toString(),name:m.pushName||'Desconhecido',phone:cleanPhone(m.key.remoteJid),text:texto,ts:Date.now()};"
NEW_MSG_OBJ = "const msg={id:m.key.id||Date.now().toString(),name:m.pushName||'Desconhecido',phone:cleanPhone(m.key.remoteJid),text:texto,ts:Date.now(),instance:b.instance||''};"

if OLD_MSG_OBJ in srv:
    srv = srv.replace(OLD_MSG_OBJ, NEW_MSG_OBJ)
    ok.append("SRV ✅ Webhook: campo 'instance' salvo em cada mensagem")
elif "instance:b.instance" in srv:
    ok.append("SRV ✅ Webhook: instance já está sendo salvo")
else:
    err.append("SRV ⚠️  Webhook: padrão msg não encontrado")

# Filtrar GET /messages por ?instance=
OLD_GET_MSG = "app.get('/messages',async function(req,res){res.json(await getMessages());});"
NEW_GET_MSG = """app.get('/messages',async function(req,res){
  const inst = req.query.instance;
  if(inst && messagesCol) {
    const msgs = await messagesCol.find({instance:inst}).sort({ts:-1}).limit(500).toArray();
    return res.json(msgs);
  }
  res.json(await getMessages());
});"""

if OLD_GET_MSG in srv:
    srv = srv.replace(OLD_GET_MSG, NEW_GET_MSG)
    ok.append("SRV ✅ GET /messages: aceita ?instance= para filtrar por perfil")
elif "req.query.instance" in srv:
    ok.append("SRV ✅ GET /messages: filtro já existe")
else:
    err.append("SRV ⚠️  GET /messages: padrão não encontrado")

with open(SRV_PATH, "w", encoding="utf-8") as f:
    f.write(srv)

# ═══════════════════════════════════════════════════════════════
# Salvar e sincronizar
# ═══════════════════════════════════════════════════════════════
with open(ARQUIVO, "w", encoding="utf-8") as f:
    f.write(html)

shutil.copy(ARQUIVO, r"C:\mfcrm\index.html")

# ═══════════════════════════════════════════════════════════════
# Relatório
# ═══════════════════════════════════════════════════════════════
print("\n" + "="*65)
print("  FIX UNIFICADO — MF Envios CRM")
print("="*65)
for o in ok:
    print(f"  ✅ {o}")
if err:
    print()
    for e in err:
        print(f"  ⚠️  {e}")
print()
print("  Deploy:")
print("  git add -A && git commit -m \"fix: stats, relatorio e whatsapp por perfil\"")
print("  git push origin main")
print("  → Manual Deploy no Render")
print("="*65)
