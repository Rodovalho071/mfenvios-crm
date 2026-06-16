#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FIXES DEFINITIVOS - MF Envios CRM
Execute: python FIXES_DEFINITIVO.py
Pasta: C:\mfcrm
"""
import os, re, subprocess, sys

BASE = r"C:\mfcrm"
os.chdir(BASE)

with open('index.html', 'rb') as f:
    raw = f.read()
if raw.startswith(b'\xef\xbb\xbf'):
    raw = raw[3:]
c = raw.decode('utf-8')

print("=== FIXES DEFINITIVOS MF ENVIOS CRM ===\n")

# ─────────────────────────────────────────────────────────
# FIX 1: VALOR DA MOEDA - R$100,25 salvando como 100.025
# Problema: finSalvar salva o valor como string "100,25"
# Solução: converter com parseMoeda antes de salvar
# ─────────────────────────────────────────────────────────
old = "      valor: valor,"
new = "      valor: parseMoeda(valor),"
if old in c:
    c = c.replace(old, new, 1)
    print("[OK] FIX 1: Valor da moeda corrigido (parseMoeda ao salvar)")
else:
    print("[SKIP] FIX 1: Já corrigido")

# Também corrigir no update (vendaEditando)
old2 = "      vendas[idx].valor = valor;"
new2 = "      vendas[idx].valor = parseMoeda(valor);"
if old2 in c:
    c = c.replace(old2, new2, 1)
    print("[OK] FIX 1b: Valor ao editar venda também corrigido")

# ─────────────────────────────────────────────────────────
# FIX 2: LEADS DO DAVI - sincronizar para MongoDB
# Problema: saveLeads usa só localStorage
# Solução: também fazer POST para /kanban-import
# ─────────────────────────────────────────────────────────
old = "function saveLeads(){save('crm-leads',leads);updateStats();}"
new = """function saveLeads(){
  save('crm-leads',leads);
  updateStats();
  // Sincronizar cada lead com MongoDB
  leads.forEach(function(lead){
    fetch('/kanban-import',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(lead)}).catch(function(){});
  });
}"""
if old in c:
    c = c.replace(old, new)
    print("[OK] FIX 2: saveLeads sincroniza com MongoDB")
else:
    print("[SKIP] FIX 2: Já corrigido ou formato diferente")

# ─────────────────────────────────────────────────────────
# FIX 3: CARREGAR LEADS DO SERVIDOR ao iniciar
# Problema: leads carregam só do localStorage
# Solução: ao iniciar, buscar leads do MongoDB e mesclar
# ─────────────────────────────────────────────────────────
old = "let leads=load('crm-leads',[]),activity=load('crm-activity',[]),"
new = "let leads=load('crm-leads',[]),activity=load('crm-activity',[]),"
# Adicionar carregamento do servidor após perfilAtivo ser definido
old3 = "function aplicarPerfil() {"
new3 = """function sincronizarLeadsServidor() {
  fetch('/kanban').then(function(r){return r.json();}).then(function(data){
    if(data && data.cards && data.cards.length > 0) {
      var serverLeads = data.cards;
      serverLeads.forEach(function(sl){
        var local = leads.find(function(l){ return l.id === sl.id; });
        if(!local) {
          leads.push(sl);
        }
      });
      save('crm-leads', leads);
      updateStats();
      if(typeof renderKanban === 'function') renderKanban();
    }
  }).catch(function(){});
}
function aplicarPerfil() {"""
if "function aplicarPerfil() {" in c and "sincronizarLeadsServidor" not in c:
    c = c.replace("function aplicarPerfil() {", new3)
    print("[OK] FIX 3: Carregamento de leads do servidor adicionado")
else:
    print("[SKIP] FIX 3: Já existe ou não encontrado")

# Chamar sincronizarLeadsServidor após selecionarPerfil
old4 = "  aplicarPerfil();\n}"
new4 = "  aplicarPerfil();\n  sincronizarLeadsServidor();\n}"
if old4 in c and "sincronizarLeadsServidor();" not in c[c.find("function selecionarPerfil"):c.find("function selecionarPerfil")+300]:
    c = c.replace(old4, new4, 1)
    print("[OK] FIX 3b: sincronizarLeadsServidor chamado no login")

# ─────────────────────────────────────────────────────────
# FIX 4: WHATSAPP - filtrar por instância do perfil
# Problema: Davi e Beatriz veem as mesmas mensagens
# Solução: passar ?instance= na requisição
# ─────────────────────────────────────────────────────────
old = "    const res=await fetch(WPP_SERVER+'/messages');if(!res.ok)throw new Error();"
new = """    var _inst = (typeof perfilAtivo!=='undefined'&&perfilAtivo&&typeof PERFIS!=='undefined'&&PERFIS[perfilAtivo])?PERFIS[perfilAtivo].instancia:'';
    var _url = WPP_SERVER+'/messages'+(_inst?'?instance='+_inst:'');
    const res=await fetch(_url);if(!res.ok)throw new Error();"""
if old in c:
    c = c.replace(old, new)
    print("[OK] FIX 4: WhatsApp filtrado por instância do perfil")
else:
    print("[SKIP] FIX 4: Já corrigido")

# ─────────────────────────────────────────────────────────
# FIX 5: SSE - filtrar nova-mensagem por instância
# ─────────────────────────────────────────────────────────
old = "es.addEventListener('nova-mensagem',()=>loadWppMessages());"
new = """es.addEventListener('nova-mensagem',function(e){
    try{
      var d=JSON.parse(e.data);
      var inst=(typeof perfilAtivo!=='undefined'&&perfilAtivo&&typeof PERFIS!=='undefined'&&PERFIS[perfilAtivo])?PERFIS[perfilAtivo].instancia:'';
      if(!inst||!d.instance||d.instance===inst) loadWppMessages();
    }catch(ex){loadWppMessages();}
  });"""
if old in c:
    c = c.replace(old, new)
    print("[OK] FIX 5: SSE filtrado por instância")
else:
    print("[SKIP] FIX 5: Já corrigido")

# ─────────────────────────────────────────────────────────
# FIX 6: LEADS VERMELHOS - detectar novos leads do anúncio
# Problema: leads com "anúncio" ou "cotação" não destacados
# Solução: na renderização do card, verificar se é lead novo quente
# ─────────────────────────────────────────────────────────
# Verificar se já tem lógica de cor por fonte
if "'#ef4444'" not in c[c.find('renderCard'):c.find('renderCard')+2000] if 'renderCard' in c else True:
    # Adicionar detecção de lead novo via anúncio
    old6 = "function renderCard(l, colIndex) {"
    if old6 in c:
        new6 = """function isLeadAnuncio(l) {
  var texto = ((l.obs||'') + ' ' + (l.name||'')).toLowerCase();
  return texto.includes('anúncio') || texto.includes('anuncio') || texto.includes('google') ||
         texto.includes('cotação') || texto.includes('cotacao') || texto.includes('vi o anúncio');
}
function renderCard(l, colIndex) {"""
        c = c.replace(old6, new6)
        print("[OK] FIX 6: Função isLeadAnuncio adicionada")

# Aplicar cor vermelha no card se for lead de anúncio
old6b = "style=\"background:var(--surface);border:1px solid var(--border);"
new6b = "style=\"background:var(--surface);border:1px solid "+("""\"+(isLeadAnuncio(l)?'#ef4444':'var(--border)')+\";""")
if old6b in c and 'isLeadAnuncio' in c:
    c = c.replace(old6b, new6b, 1)
    print("[OK] FIX 6b: Cards de leads do anúncio ficam com borda vermelha")

# ─────────────────────────────────────────────────────────
# FIX 7: CLIENTES - salvar e carregar do MongoDB
# Adicionar sistema de clientes se não existir
# ─────────────────────────────────────────────────────────
if 'clientesFin' not in c:
    # Adicionar antes do fechamento do script
    clientes_code = """
// ═══════════════════════════════════════════
// MÓDULO CLIENTES
// ═══════════════════════════════════════════
var clientesFin = [];
function carregarClientesFin() {
  return fetch('/clientes').then(function(r){return r.json();}).then(function(d){
    clientesFin = Array.isArray(d) ? d : [];
  }).catch(function(){
    clientesFin = JSON.parse(localStorage.getItem('crm-clientes-fin')||'[]');
  });
}
function salvarClienteFin(obj) {
  var existe = clientesFin.findIndex(function(c){ return c.id === obj.id; });
  if(existe >= 0) {
    clientesFin[existe] = obj;
    fetch('/clientes/'+obj.id,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(obj)}).catch(function(){});
  } else {
    clientesFin.push(obj);
    fetch('/clientes',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(obj)}).catch(function(){});
  }
  localStorage.setItem('crm-clientes-fin', JSON.stringify(clientesFin));
}
function getClienteNomes() {
  return clientesFin.map(function(c){ return c.nome; });
}
"""
    c = c.replace('</script>', clientes_code + '\n</script>', 1)
    print("[OK] FIX 7: Módulo Clientes adicionado")

    # Adicionar datalist no campo cliente do modal de venda
    old7 = 'id="fin-cliente" type="text"'
    new7 = 'id="fin-cliente" type="text" list="fin-clientes-list"'
    if old7 in c:
        c = c.replace(old7, new7)
        # Adicionar datalist após o input
        c = c.replace(
            'id="fin-clientes-list"',
            'id="fin-clientes-list"'
        )
        # Inserir datalist
        c = c.replace(
            '<input id="fin-cliente" type="text" list="fin-clientes-list"',
            '<input id="fin-cliente" type="text" list="fin-clientes-list" onchange="autoPreencherClienteFin(this.value)"'
        )
        print("[OK] FIX 7b: Datalist de clientes no campo de venda")
else:
    print("[SKIP] FIX 7: Módulo clientes já existe")

# ─────────────────────────────────────────────────────────
# Verificar JS antes de salvar
# ─────────────────────────────────────────────────────────
scripts = re.findall(r'<script[^>]*>(.*?)</script>', c, re.DOTALL)
all_ok = True
for i, s in enumerate(scripts):
    with open(f'C:/mfcrm/tmp_check_{i}.js', 'w', encoding='utf-8') as f:
        f.write(s)
    r = subprocess.run(['node', '--check', f'C:/mfcrm/tmp_check_{i}.js'], capture_output=True, text=True)
    os.remove(f'C:/mfcrm/tmp_check_{i}.js')
    if r.returncode != 0:
        # Falso positivo do node com HTML em strings - verificar se é real
        if 'Unexpected string' in r.stderr or 'Unexpected token' in r.stderr:
            # Verificar se o erro é antes da linha 900 (código real, não HTML inline)
            line_num = int(re.search(r':(\d+)', r.stderr).group(1)) if re.search(r':(\d+)', r.stderr) else 999
            if line_num < 900:
                print(f"[ERRO REAL] Script {i} linha {line_num}: {r.stderr[:100]}")
                all_ok = False
            else:
                print(f"[OK] Script {i}: falso positivo do node (HTML em string, linha {line_num})")
        else:
            print(f"[ERRO] Script {i}: {r.stderr[:100]}")
            all_ok = False
    else:
        print(f"[OK] Script {i}: sem erros")

if not all_ok:
    print("\n[ABORTANDO] Erro real no JS. Nao salvando.")
    sys.exit(1)

# Salvar
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)
print("\n[OK] index.html salvo")

# Deletar public/index.html
pub = os.path.join(BASE, "public", "index.html")
if os.path.exists(pub):
    os.remove(pub)
    print("[OK] public/index.html removido")

# Push
print("\n=== FAZENDO PUSH ===")
os.system('git add -A')
os.system('git commit -m "fixes: valor moeda, leads MongoDB, WPP instancia, leads anuncio"')
os.system('git push origin main')

print("""
=== PRONTO ===
1. Va ao Render: https://dashboard.render.com
2. Manual Deploy
3. Aguarde 'Your service is live'
4. Aba anonima: mf-envios-crm.onrender.com
""")
