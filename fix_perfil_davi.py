print("Configurando perfil automatico para Davi...")

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

orig = html

# ══════════════════════════════════════════════════════════
# 1. selecionarPerfil — definir agentName automaticamente
# ══════════════════════════════════════════════════════════
old_sel = """function selecionarPerfil(perfil) {
  perfilAtivo = perfil;
  localStorage.setItem('crm-perfil', perfil);
  document.getElementById('splash-perfil').style.display = 'none';
  aplicarPerfil();
  sincronizarLeadsServidor();
}"""

new_sel = """function selecionarPerfil(perfil) {
  perfilAtivo = perfil;
  localStorage.setItem('crm-perfil', perfil);
  // Definir agentName automaticamente pelo perfil
  agentName = PERFIS[perfil].nome;
  save('crm-agent', agentName);
  document.getElementById('splash-perfil').style.display = 'none';
  aplicarPerfil();
  sincronizarLeadsServidor();
}"""

if old_sel in html:
    html = html.replace(old_sel, new_sel)
    print("OK 1/3 - agentName definido automaticamente ao selecionar perfil")
else:
    print("X 1/3 - selecionarPerfil nao encontrada")

# ══════════════════════════════════════════════════════════
# 2. openNewLead — preencher agent pelo perfil ativo
# ══════════════════════════════════════════════════════════
old_agent_input = '        <div class="form-group"><label class="form-label">Responsável</label><input id="nl-agent" value="${agentName}" placeholder="Seu nome"/></div>'

new_agent_input = '        <div class="form-group"><label class="form-label">Responsável</label><input id="nl-agent" value="${perfilAtivo&&PERFIS[perfilAtivo]?PERFIS[perfilAtivo].nome:agentName}" placeholder="Seu nome" ${perfilAtivo?"readonly style=\\"opacity:0.7\\"":""}  /></div>'

if old_agent_input in html:
    html = html.replace(old_agent_input, new_agent_input)
    print("OK 2/3 - campo Responsavel preenchido e bloqueado pelo perfil")
else:
    print("X 2/3 - campo nl-agent nao encontrado")

# ══════════════════════════════════════════════════════════
# 3. Tela de splash — lembrar perfil e entrar direto
# ══════════════════════════════════════════════════════════
old_perfil_init = "var perfilAtivo = localStorage.getItem('crm-perfil') || null;"

new_perfil_init = """var perfilAtivo = localStorage.getItem('crm-perfil') || null;
// Se já tem perfil salvo, entrar direto sem mostrar splash
if(perfilAtivo && PERFIS[perfilAtivo]) {
  document.addEventListener('DOMContentLoaded', function() {
    var splash = document.getElementById('splash-perfil');
    if(splash) splash.style.display = 'none';
    agentName = PERFIS[perfilAtivo].nome;
    save('crm-agent', agentName);
    aplicarPerfil();
    sincronizarLeadsServidor();
  });
}"""

if old_perfil_init in html:
    html = html.replace(old_perfil_init, new_perfil_init)
    print("OK 3/3 - perfil lembrado, entra direto sem splash")
else:
    print("X 3/3 - init perfilAtivo nao encontrado")

if html != orig:
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("\nindex.html atualizado!")
    print("git add index.html && git commit -m 'feat: perfil automatico, Davi entra direto' && git push origin main")
else:
    print("\nNenhuma alteracao feita")
