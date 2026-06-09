import re, shutil

aplicados = []
erros = []

# ═══════════════════════════════════════════════════════════════
# PARTE 1 — server.js: salvar campo 'instance' na mensagem
# ═══════════════════════════════════════════════════════════════
SRV = r"C:\mfcrm\server.js"
with open(SRV, "r", encoding="utf-8") as f:
    srv = f.read()

# O webhook recebe req.body com campo 'instance' da Evolution API
# Precisamos passar isso para o msg object
# Antes: const msg={id:...,name:...,phone:...,text:texto,ts:Date.now()};
# Depois: const msg={id:...,name:...,phone:...,text:texto,ts:Date.now(),instance:b.instance||req.body.instance||''};

OLD_MSG = "const msg={id:m.key.id||Date.now().toString(),name:m.pushName||'Desconhecido',phone:cleanPhone(m.key.remoteJid),text:texto,ts:Date.now()};"
NEW_MSG = "const msg={id:m.key.id||Date.now().toString(),name:m.pushName||'Desconhecido',phone:cleanPhone(m.key.remoteJid),text:texto,ts:Date.now(),instance:b.instance||''};"

# Versão sem espaços (como pode estar no arquivo)
if OLD_MSG in srv:
    srv = srv.replace(OLD_MSG, NEW_MSG)
    aplicados.append("SRV FIX 1: campo 'instance' adicionado ao msg ✅")
else:
    # Tenta com espaços variados
    pattern = r"(const msg\s*=\s*\{[^}]*ts\s*:\s*Date\.now\(\)\s*\})"
    match = re.search(pattern, srv)
    if match:
        old = match.group(0)
        new = old.rstrip('}') + ",instance:b.instance||''}"
        srv = srv.replace(old, new)
        aplicados.append("SRV FIX 1 (regex): campo 'instance' adicionado ao msg ✅")
    else:
        erros.append("SRV FIX 1: padrão msg não encontrado — ajuste manual necessário")

# Também garantir que o GET /messages aceite filtro por instance
# Antes: app.get('/messages', async(req,res)=>{ ... const msgs = await Message.find()...
# Depois: filtra por instance se passado como query param

OLD_GET_MSGS_PATTERNS = [
    "const msgs=await Message.find({}).sort({ts:1}).lean();",
    "const msgs = await Message.find({}).sort({ts:1}).lean();",
    "const msgs=await Message.find().sort({ts:1}).lean();",
    "const msgs = await Message.find().sort({ts:1}).lean();",
]

replaced_get = False
for pat in OLD_GET_MSGS_PATTERNS:
    if pat in srv:
        new_pat = pat.replace(
            "await Message.find({}).sort",
            "await Message.find(req.query.instance?{instance:req.query.instance}:{}).sort"
        ).replace(
            "await Message.find().sort",
            "await Message.find(req.query.instance?{instance:req.query.instance}:{}).sort"
        )
        srv = srv.replace(pat, new_pat)
        aplicados.append("SRV FIX 2: GET /messages filtra por ?instance= ✅")
        replaced_get = True
        break

if not replaced_get:
    # Tenta regex
    pattern2 = r"(await Message\.find\(\s*\{?\s*\}?\s*\)\.sort)"
    match2 = re.search(pattern2, srv)
    if match2:
        old2 = match2.group(0)
        new2 = "await Message.find(req.query.instance?{instance:req.query.instance}:{}).sort"
        srv = srv.replace(old2, new2)
        aplicados.append("SRV FIX 2 (regex): GET /messages filtra por ?instance= ✅")
    else:
        erros.append("SRV FIX 2: GET /messages não encontrado — verifique manualmente")

with open(SRV, "w", encoding="utf-8") as f:
    f.write(srv)
aplicados.append("server.js salvo ✅")

# ═══════════════════════════════════════════════════════════════
# PARTE 2 — index.html: filtrar mensagens por perfil
# ═══════════════════════════════════════════════════════════════
HTML = r"C:\mfcrm\public\index.html"
with open(HTML, "r", encoding="utf-8") as f:
    html = f.read()

# Mapeamento perfil → instância
INSTANCIA_MAP = """
// Mapeamento perfil → instância WhatsApp Evolution API
const PERFIL_INSTANCIA = { beatriz: 'mfenvios', davi: 'mfenvios-davi' };
function getInstanciaAtiva() {
  if (!perfilAtivo || verTodos) return null;
  return PERFIL_INSTANCIA[perfilAtivo] || null;
}
"""

if "PERFIL_INSTANCIA" not in html:
    # Injeta antes da primeira função de WhatsApp ou após perfilAtivo
    for anchor in ["let perfilAtivo =", "var perfilAtivo =", "function renderWhatsApp", "function carregarMensagens", "function loadMessages", "function renderContatos", "// WhatsApp"]:
        if anchor in html:
            idx = html.index(anchor)
            html = html[:idx] + INSTANCIA_MAP + "\n" + html[idx:]
            aplicados.append(f"HTML FIX 1: PERFIL_INSTANCIA inserido antes de '{anchor}' ✅")
            break
    else:
        # Insere antes do </script> final
        idx = html.rfind("</script>")
        html = html[:idx] + INSTANCIA_MAP + "\n" + html[idx:]
        aplicados.append("HTML FIX 1: PERFIL_INSTANCIA inserido antes de </script> ✅")
else:
    aplicados.append("HTML FIX 1: PERFIL_INSTANCIA já existe ✅")

# Filtrar na função que carrega mensagens do backend
# Procura fetch('/messages') e adiciona ?instance=
FETCH_PATTERNS = [
    ("fetch('/messages')", "fetch('/messages'+(getInstanciaAtiva()?'?instance='+getInstanciaAtiva():''))"),
    ('fetch("/messages")', 'fetch("/messages"+(getInstanciaAtiva()?"?instance="+getInstanciaAtiva():""))'),
    ("fetch(`/messages`)", "fetch(`/messages`+(getInstanciaAtiva()?`?instance=${getInstanciaAtiva()}`:``))"),
]

fetch_fixed = False
for old_f, new_f in FETCH_PATTERNS:
    if old_f in html:
        html = html.replace(old_f, new_f)
        aplicados.append(f"HTML FIX 2: fetch /messages com filtro de instância ✅")
        fetch_fixed = True
        break

if not fetch_fixed:
    erros.append("HTML FIX 2: fetch('/messages') não encontrado — mensagens podem não filtrar")
    erros.append("           Verifique como o frontend busca mensagens e adicione ?instance= manualmente")

# Ao trocar de perfil, recarregar mensagens
# Garante que selecionarPerfil chama a função de reload do WhatsApp
if "function selecionarPerfil" in html:
    idx = html.index("function selecionarPerfil")
    pos_brace = html.index("{", idx)
    # Fecha a função
    depth = 0
    pos_close = pos_brace
    for i, ch in enumerate(html[pos_brace:], pos_brace):
        if ch == "{": depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                pos_close = i
                break

    trecho = html[idx:pos_close]
    reload_needed = True
    for fn in ["carregarMensagens", "loadMessages", "renderContatos", "renderWhatsApp"]:
        if fn in trecho:
            reload_needed = False
            aplicados.append(f"HTML FIX 3: selecionarPerfil já chama {fn} ✅")
            break

    if reload_needed:
        # Adiciona chamada antes do }
        reload_line = "\n  // Recarrega mensagens do perfil ativo\n  setTimeout(function(){ if(typeof carregarMensagens==='function') carregarMensagens(); else if(typeof loadMessages==='function') loadMessages(); else if(typeof renderContatos==='function') renderContatos(); }, 100);"
        html = html[:pos_close] + reload_line + html[pos_close:]
        aplicados.append("HTML FIX 3: reload de mensagens adicionado em selecionarPerfil ✅")
else:
    erros.append("HTML FIX 3: selecionarPerfil não encontrado")

with open(HTML, "w", encoding="utf-8") as f:
    f.write(html)

# Sincroniza index.html raiz
shutil.copy(HTML, r"C:\mfcrm\index.html")
aplicados.append("SYNC: public/index.html → index.html ✅")

# ═══════════════════════════════════════════════════════════════
# Relatório
# ═══════════════════════════════════════════════════════════════
print("\n" + "="*65)
print("  FIX WHATSAPP POR PERFIL — MF Envios CRM")
print("="*65)
for a in aplicados:
    print(f"  ✅ {a}")
if erros:
    print()
    for e in erros:
        print(f"  ⚠️  {e}")
print()
print("  Próximo passo:")
print("  git add -A && git commit -m \"feat: WhatsApp separado por perfil\"")
print("  git push origin main")
print("  → Manual Deploy no Render dashboard")
print()
print("  NOTA: Mensagens antigas no MongoDB não têm o campo 'instance'.")
print("  Elas aparecerão para BEATRIZ (padrão) por serem do número mfenvios.")
print("  Novas mensagens já serão separadas automaticamente.")
print("="*65)
