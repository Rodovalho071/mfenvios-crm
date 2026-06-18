print("Separando Operacional por perfil...")

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

with open('server.js', 'r', encoding='utf-8') as f:
    srv = f.read()

html_orig = html
srv_orig = srv

# ══════════════════════════════════════════════════════════
# 1. server.js — rotas GET filtram por ?perfil=
# ══════════════════════════════════════════════════════════
old_get_tarefas = "app.get('/tarefas',async function(req,res){res.json(await colFind(tarefasCol,memTarefas));});"
new_get_tarefas = "app.get('/tarefas',async function(req,res){const p=req.query.perfil;const all=await colFind(tarefasCol,memTarefas);res.json(p?all.filter(x=>x.perfil===p):all);});"

old_get_fretes = "app.get('/fretes',async function(req,res){res.json(await colFind(fretesCol,memFretes));});"
new_get_fretes = "app.get('/fretes',async function(req,res){const p=req.query.perfil;const all=await colFind(fretesCol,memFretes);res.json(p?all.filter(x=>x.perfil===p):all);});"

old_get_agenda = "app.get('/agenda',async function(req,res){res.json(await colFind(agendaCol,memAgenda));});"
new_get_agenda = "app.get('/agenda',async function(req,res){const p=req.query.perfil;const all=await colFind(agendaCol,memAgenda);res.json(p?all.filter(x=>x.perfil===p):all);});"

old_get_docs = "app.get('/documentos',async function(req,res){res.json(await colFind(docsCol,memDocs));});"
new_get_docs = "app.get('/documentos',async function(req,res){const p=req.query.perfil;const all=await colFind(docsCol,memDocs);res.json(p?all.filter(x=>x.perfil===p):all);});"

for old, new, nome in [
    (old_get_tarefas, new_get_tarefas, "GET /tarefas"),
    (old_get_fretes, new_get_fretes, "GET /fretes"),
    (old_get_agenda, new_get_agenda, "GET /agenda"),
    (old_get_docs, new_get_docs, "GET /documentos"),
]:
    if old in srv:
        srv = srv.replace(old, new)
        print(f"OK - server.js: {nome} filtra por perfil")
    else:
        print(f"X - server.js: {nome} nao encontrado")

# ══════════════════════════════════════════════════════════
# 2. index.html — toolbar do Operacional com abas Beatriz/Davi
# ══════════════════════════════════════════════════════════
old_optab_header = """function opTab(tab) {"""

new_optab_before = """var opPerfilAtivo = 'beatriz'; // aba ativa no operacional

function selecionarOpPerfil(p) {
  opPerfilAtivo = p;
  ['beatriz','davi'].forEach(function(x){
    var btn = document.getElementById('op-aba-'+x);
    if(!btn) return;
    if(x===p){ btn.style.background=x==='davi'?'var(--blue)':'var(--orange)'; btn.style.color='#fff'; }
    else{ btn.style.background='var(--surface2)'; btn.style.color='var(--text2)'; }
  });
  opTab(document.querySelector('.op-tab-btn.active')?.dataset?.tab||'tarefas');
}

function getOpPerfil() {
  // Beatriz pode ver qualquer aba; Davi sempre o próprio
  if(perfilAtivo==='davi') return 'davi';
  return opPerfilAtivo;
}

function opTab(tab) {"""

if old_optab_header in html:
    html = html.replace(old_optab_header, new_optab_before, 1)
    print("OK - index.html: funcoes opPerfil adicionadas")
else:
    print("X - index.html: opTab nao encontrada")

# ══════════════════════════════════════════════════════════
# 3. index.html — adicionar abas no HTML do Operacional
# ══════════════════════════════════════════════════════════
old_op_tabs_html = """      <button class="op-tab-btn" data-tab="tarefas" onclick="opTab('tarefas')">✅ Tarefas</button>"""

new_op_tabs_html = """      <!-- Abas de perfil Operacional — só para Beatriz -->
      <div id="op-abas-perfil" style="display:none;gap:4px;margin-right:8px">
        <button id="op-aba-beatriz" onclick="selecionarOpPerfil('beatriz')" style="padding:4px 12px;border-radius:20px;border:1px solid var(--border);background:var(--orange);color:#fff;font-size:11px;font-weight:700;cursor:pointer">👩‍💼 Beatriz</button>
        <button id="op-aba-davi" onclick="selecionarOpPerfil('davi')" style="padding:4px 12px;border-radius:20px;border:1px solid var(--border);background:var(--surface2);color:var(--text2);font-size:11px;font-weight:700;cursor:pointer">👨‍💼 Davi</button>
      </div>
      <button class="op-tab-btn" data-tab="tarefas" onclick="opTab('tarefas')">✅ Tarefas</button>"""

if old_op_tabs_html in html:
    html = html.replace(old_op_tabs_html, new_op_tabs_html)
    print("OK - index.html: abas HTML adicionadas no Operacional")
else:
    print("X - index.html: botao tarefas nao encontrado")

# ══════════════════════════════════════════════════════════
# 4. index.html — mostrar abas só para Beatriz ao entrar no Operacional
# ══════════════════════════════════════════════════════════
old_showview_op = "if(v==='operacional'){opTab('tarefas');}"
new_showview_op = """if(v==='operacional'){
    var opAbas=document.getElementById('op-abas-perfil');
    if(opAbas) opAbas.style.display=perfilAtivo==='beatriz'?'flex':'none';
    if(perfilAtivo==='beatriz') opPerfilAtivo='beatriz';
    opTab('tarefas');
  }"""

if old_showview_op in html:
    html = html.replace(old_showview_op, new_showview_op)
    print("OK - index.html: abas exibidas corretamente ao abrir Operacional")
else:
    print("X - index.html: showView operacional nao encontrado")

# ══════════════════════════════════════════════════════════
# 5. index.html — fetch de tarefas/fretes/agenda/docs passam ?perfil=
# ══════════════════════════════════════════════════════════
replacements = [
    (
        "const res = await fetch(OP_API+'/tarefas').then(r=>r.json()).catch(()=>[]);",
        "const res = await fetch(OP_API+'/tarefas?perfil='+getOpPerfil()).then(r=>r.json()).catch(()=>[]);"
    ),
    (
        "const res = await fetch(OP_API+'/fretes').then(r=>r.json()).catch(()=>[]);",
        "const res = await fetch(OP_API+'/fretes?perfil='+getOpPerfil()).then(r=>r.json()).catch(()=>[]);"
    ),
    (
        "const res = await fetch(OP_API+'/agenda').then(r=>r.json()).catch(()=>[]);",
        "const res = await fetch(OP_API+'/agenda?perfil='+getOpPerfil()).then(r=>r.json()).catch(()=>[]);"
    ),
    (
        "const res = await fetch(OP_API+'/documentos').then(r=>r.json()).catch(()=>[]);",
        "const res = await fetch(OP_API+'/documentos?perfil='+getOpPerfil()).then(r=>r.json()).catch(()=>[]);"
    ),
]

for old, new in replacements:
    if old in html:
        html = html.replace(old, new)
        print(f"OK - fetch filtrado: {old[30:60]}...")
    else:
        print(f"X - fetch nao encontrado: {old[30:60]}...")

# ══════════════════════════════════════════════════════════
# 6. index.html — POST de tarefas/fretes/agenda/docs salvam perfil
# ══════════════════════════════════════════════════════════
post_replacements = [
    (
        "body:JSON.stringify({titulo,desc:document.getElementById('op-f-desc').value,data:document.getElementById('op-f-data').value,done:false})})",
        "body:JSON.stringify({titulo,desc:document.getElementById('op-f-desc').value,data:document.getElementById('op-f-data').value,done:false,perfil:getOpPerfil()})})"
    ),
    (
        "body:JSON.stringify({titulo,origem:document.getElementById('op-f-origem').value,destino:document.getElementById('op-f-destino').value,valor:document.getElementById('op-f-valor').value,status:document.getElementById('op-f-status').value||'Aguardando coleta'})})",
        "body:JSON.stringify({titulo,origem:document.getElementById('op-f-origem').value,destino:document.getElementById('op-f-destino').value,valor:document.getElementById('op-f-valor').value,status:document.getElementById('op-f-status').value||'Aguardando coleta',perfil:getOpPerfil()})})"
    ),
    (
        "body:JSON.stringify({titulo,data:document.getElementById('op-f-data').value,hora:document.getElementById('op-f-hora').value,desc:document.getElementById('op-f-desc').value})})",
        "body:JSON.stringify({titulo,data:document.getElementById('op-f-data').value,hora:document.getElementById('op-f-hora').value,desc:document.getElementById('op-f-desc').value,perfil:getOpPerfil()})})"
    ),
    (
        "body:JSON.stringify({titulo,tipo:document.getElementById('op-f-tipo').value,link:document.getElementById('op-f-link').value,obs:document.getElementById('op-f-desc').value})})",
        "body:JSON.stringify({titulo,tipo:document.getElementById('op-f-tipo').value,link:document.getElementById('op-f-link').value,obs:document.getElementById('op-f-desc').value,perfil:getOpPerfil()})})"
    ),
]

for old, new in post_replacements:
    if old in html:
        html = html.replace(old, new)
        print(f"OK - POST salva perfil: {old[15:50]}...")
    else:
        print(f"X - POST nao encontrado: {old[15:50]}...")

# ══════════════════════════════════════════════════════════
# RESULTADO
# ══════════════════════════════════════════════════════════
print("")
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

print("\ngit add index.html server.js && git commit -m 'feat: operacional separado por perfil' && git push origin main")

# Correcao adicional — adicionar abas no HTML correto do Operacional
with open('index.html', 'r', encoding='utf-8') as f:
    html2 = f.read()

old_subtabs = '  <!-- Sub-tabs -->\n  <div style="display:flex;gap:8px;margin-bottom:20px;border-bottom:1px solid var(--border);padding-bottom:0">\n    <div class="tab active" id="op-tab-tarefas" onclick="opTab(\'tarefas\')" style="border-bottom:3px solid transparent;padding:8px 16px;cursor:pointer;font-size:13px;font-weight:600">✅ Tarefas</div>'

new_subtabs = '  <!-- Sub-tabs -->\n  <div style="display:flex;gap:8px;margin-bottom:20px;border-bottom:1px solid var(--border);padding-bottom:0;flex-wrap:wrap;align-items:center">\n    <!-- Abas perfil operacional -->\n    <div id="op-abas-perfil" style="display:none;gap:4px;margin-right:8px">\n      <button id="op-aba-beatriz" onclick="selecionarOpPerfil(\'beatriz\')" style="padding:4px 12px;border-radius:20px;border:1px solid var(--border);background:var(--orange);color:#fff;font-size:11px;font-weight:700;cursor:pointer">👩\u200d💼 Beatriz</button>\n      <button id="op-aba-davi" onclick="selecionarOpPerfil(\'davi\')" style="padding:4px 12px;border-radius:20px;border:1px solid var(--border);background:var(--surface2);color:var(--text2);font-size:11px;font-weight:700;cursor:pointer">👨\u200d💼 Davi</button>\n    </div>\n    <div class="tab active" id="op-tab-tarefas" onclick="opTab(\'tarefas\')" style="border-bottom:3px solid transparent;padding:8px 16px;cursor:pointer;font-size:13px;font-weight:600">✅ Tarefas</div>'

if old_subtabs in html2:
    html2 = html2.replace(old_subtabs, new_subtabs)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html2)
    print("OK - abas HTML adicionadas corretamente no Operacional")
else:
    print("X - subtabs nao encontrado")
