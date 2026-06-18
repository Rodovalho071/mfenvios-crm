print("Aplicando abas de perfil no Kanban...")

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

orig = html

# ══════════════════════════════════════════════════════════
# 1. Adicionar abas Beatriz/Davi na toolbar do Kanban
# ══════════════════════════════════════════════════════════
old_toolbar = """  <div class="kanban-toolbar">
    <div style="display:flex;align-items:center;gap:8px;background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-sm);padding:4px 8px">
      <button onclick="navMes(-1)" style="background:none;border:none;color:var(--text2);cursor:pointer;font-size:16px;padding:0 4px">&#9664;</button>
      <span id="mes-label" style="font-size:13px;font-weight:600;min-width:110px;text-align:center"></span>
      <button onclick="navMes(1)" style="background:none;border:none;color:var(--text2);cursor:pointer;font-size:16px;padding:0 4px">&#9654;</button>
    </div>
    <div class="search-box"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg><input placeholder="Buscar lead..." id="kanban-search" oninput="renderKanban()"/></div>
    <select class="filter-select" id="kanban-agent" onchange="renderKanban()"><option value="">Todos os responsáveis</option></select>
  </div>"""

new_toolbar = """  <div class="kanban-toolbar">
    <div style="display:flex;align-items:center;gap:8px;background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-sm);padding:4px 8px">
      <button onclick="navMes(-1)" style="background:none;border:none;color:var(--text2);cursor:pointer;font-size:16px;padding:0 4px">&#9664;</button>
      <span id="mes-label" style="font-size:13px;font-weight:600;min-width:110px;text-align:center"></span>
      <button onclick="navMes(1)" style="background:none;border:none;color:var(--text2);cursor:pointer;font-size:16px;padding:0 4px">&#9654;</button>
    </div>
    <!-- Abas de perfil — só aparece para Beatriz -->
    <div id="kanban-abas" style="display:none;gap:4px">
      <button id="aba-beatriz" onclick="selecionarAbaKanban('beatriz')" style="padding:5px 14px;border-radius:20px;border:1px solid var(--border);background:var(--orange);color:#fff;font-size:12px;font-weight:700;cursor:pointer">👩‍💼 Beatriz</button>
      <button id="aba-davi" onclick="selecionarAbaKanban('davi')" style="padding:5px 14px;border-radius:20px;border:1px solid var(--border);background:var(--surface2);color:var(--text2);font-size:12px;font-weight:700;cursor:pointer">👨‍💼 Davi</button>
      <button id="aba-todos" onclick="selecionarAbaKanban('todos')" style="padding:5px 14px;border-radius:20px;border:1px solid var(--border);background:var(--surface2);color:var(--text2);font-size:12px;font-weight:700;cursor:pointer">👥 Todos</button>
    </div>
    <div class="search-box"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg><input placeholder="Buscar lead..." id="kanban-search" oninput="renderKanban()"/></div>
    <select class="filter-select" id="kanban-agent" onchange="renderKanban()"><option value="">Todos os responsáveis</option></select>
  </div>"""

if old_toolbar in html:
    html = html.replace(old_toolbar, new_toolbar)
    print("OK 1/3 - abas adicionadas na toolbar")
else:
    print("X 1/3 - toolbar nao encontrada")

# ══════════════════════════════════════════════════════════
# 2. Adicionar variável e função selecionarAbaKanban
# ══════════════════════════════════════════════════════════
old_kanban_offset = "let kanbanMesOffset = 0; // 0 = mes atual, -1 = mes anterior, etc."

new_kanban_offset = """let kanbanMesOffset = 0; // 0 = mes atual, -1 = mes anterior, etc.
let kanbanAbaAtiva = 'proprio'; // 'proprio', 'beatriz', 'davi', 'todos'

function selecionarAbaKanban(aba) {
  kanbanAbaAtiva = aba;
  // Atualizar visual dos botões
  ['beatriz','davi','todos'].forEach(function(a) {
    var btn = document.getElementById('aba-'+a);
    if(!btn) return;
    if(a === aba) {
      btn.style.background = a==='davi' ? 'var(--blue)' : a==='todos' ? 'var(--text)' : 'var(--orange)';
      btn.style.color = a==='todos' ? 'var(--bg)' : '#fff';
    } else {
      btn.style.background = 'var(--surface2)';
      btn.style.color = 'var(--text2)';
    }
  });
  renderKanban();
  updateStats();
}

function atualizarAbasKanban() {
  var abas = document.getElementById('kanban-abas');
  if(!abas) return;
  // Mostrar abas só para Beatriz
  if(perfilAtivo === 'beatriz') {
    abas.style.display = 'flex';
  } else {
    abas.style.display = 'none';
  }
}"""

if old_kanban_offset in html:
    html = html.replace(old_kanban_offset, new_kanban_offset)
    print("OK 2/3 - funcao selecionarAbaKanban adicionada")
else:
    print("X 2/3 - kanbanMesOffset nao encontrado")

# ══════════════════════════════════════════════════════════
# 3. Atualizar renderKanban para respeitar aba ativa
# ══════════════════════════════════════════════════════════
old_render_filtro = """  // Filtrar por perfil ativo
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

new_render_filtro = """  // Filtrar por perfil ativo e aba selecionada
  let leadsPerfilMes;
  if(perfilAtivo === 'beatriz') {
    // Beatriz: respeita aba selecionada
    if(kanbanAbaAtiva === 'todos') {
      leadsPerfilMes = leadsMes;
      window.STAGES = [...new Set([...PERFIS.beatriz.stages, ...PERFIS.davi.stages])];
      window.STAGE_COLORS = Object.assign({}, PERFIS.beatriz.stageColors, PERFIS.davi.stageColors);
    } else if(kanbanAbaAtiva === 'davi') {
      const pDavi = PERFIS.davi;
      leadsPerfilMes = leadsMes.filter(l => {
        if(l.agent && l.agent !== '') return l.agent === pDavi.nome;
        return pDavi.stages.includes(l.stage);
      });
      window.STAGES = pDavi.stages;
      window.STAGE_COLORS = pDavi.stageColors;
    } else {
      // 'beatriz' ou 'proprio' — mostrar leads da Beatriz
      const pBeatriz = PERFIS.beatriz;
      leadsPerfilMes = leadsMes.filter(l => {
        if(l.agent && l.agent !== '') return l.agent === pBeatriz.nome;
        return pBeatriz.stages.includes(l.stage);
      });
      window.STAGES = pBeatriz.stages;
      window.STAGE_COLORS = pBeatriz.stageColors;
    }
  } else if(perfilAtivo === 'davi') {
    // Davi: sempre vê só os leads dele
    const pDavi = PERFIS.davi;
    leadsPerfilMes = leadsMes.filter(l => {
      if(l.agent && l.agent !== '') return l.agent === pDavi.nome;
      return pDavi.stages.includes(l.stage);
    });
    window.STAGES = pDavi.stages;
    window.STAGE_COLORS = pDavi.stageColors;
  } else {
    leadsPerfilMes = leadsMes;
  }"""

if old_render_filtro in html:
    html = html.replace(old_render_filtro, new_render_filtro)
    print("OK 3/3 - renderKanban atualizado com abas")
else:
    print("X 3/3 - filtro renderKanban nao encontrado")

# ══════════════════════════════════════════════════════════
# 4. Chamar atualizarAbasKanban ao aplicar perfil
# ══════════════════════════════════════════════════════════
old_aplicar_fim = """  renderKanban();
  updateStats();
  updateAgentFilters();
  atualizarSino();
  // Recarregar WhatsApp com instância do perfil selecionado
  if(typeof loadWppMessages === 'function') loadWppMessages();
}"""

new_aplicar_fim = """  // Resetar aba kanban ao trocar perfil
  if(perfilAtivo === 'davi') {
    kanbanAbaAtiva = 'proprio';
  } else {
    kanbanAbaAtiva = 'beatriz';
  }
  atualizarAbasKanban();
  renderKanban();
  updateStats();
  updateAgentFilters();
  atualizarSino();
  // Recarregar WhatsApp com instância do perfil selecionado
  if(typeof loadWppMessages === 'function') loadWppMessages();
}"""

if old_aplicar_fim in html:
    html = html.replace(old_aplicar_fim, new_aplicar_fim, 1)
    print("OK 4/4 - aplicarPerfil atualizado")
else:
    print("X 4/4 - fim de aplicarPerfil nao encontrado")

if html != orig:
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("\nindex.html atualizado!")
    print("git add index.html && git commit -m 'feat: abas Beatriz/Davi no Kanban' && git push origin main")
else:
    print("\nNenhuma alteracao feita")
