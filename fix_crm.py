import re

print("Lendo index.html...")
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

original = html

# ══════════════════════════════════════════════════════════
# CORREÇÃO 1: somaFrete — usar mesma lógica do parseMoeda
# Bug: remove pontos ANTES de trocar vírgula, destruindo milhar
# Ex: "1.200,00" vira "120000" em vez de "1200.00"
# ══════════════════════════════════════════════════════════
old_soma = """function somaFrete(arr){
  return arr.reduce((s,l)=>{
    const v=parseFloat((l.valorFrete||'0').replace(/\\./g,'').replace(',','.'));
    return s+(isNaN(v)?0:v);
  },0);
}"""

new_soma = """function parseFrete(val){
  if(!val && val!==0) return 0;
  var s = val.toString().replace(/[R$\\s]/g,'').trim();
  if(s.indexOf(',') !== -1){
    s = s.replace(/\\./g,'').replace(',','.');
  }
  var n = parseFloat(s);
  return isNaN(n) ? 0 : n;
}
function somaFrete(arr){
  return arr.reduce((s,l)=>{
    return s + parseFrete(l.valorFrete||'0');
  },0);
}"""

if old_soma in html:
    html = html.replace(old_soma, new_soma)
    print("✅ CORREÇÃO 1: somaFrete com centavos — OK")
else:
    print("⚠️  CORREÇÃO 1: somaFrete não encontrada exatamente — pulando")

# ══════════════════════════════════════════════════════════
# CORREÇÃO 2: setInterval do WhatsApp — filtrar por instância
# Bug: busca /messages sem ?instance= sobrescrevendo wppMsgs
# a cada 30s com mensagens de TODOS os perfis
# ══════════════════════════════════════════════════════════
old_interval = """setInterval(()=>{fetch(WPP_SERVER+'/messages').then(r=>r.json()).then(msgs=>{wppMsgs=msgs;const b=document.getElementById('wpp-badge');if(msgs.length>0){b.style.display='inline';b.textContent=msgs.length;}else b.style.display='none';if(chatAtivo)renderConvList();}).catch(()=>{});},30000);"""

new_interval = """setInterval(()=>{
  var _inst2=(typeof perfilAtivo!=='undefined'&&perfilAtivo&&typeof PERFIS!=='undefined'&&PERFIS[perfilAtivo])?PERFIS[perfilAtivo].instancia:'';
  var _url2=WPP_SERVER+'/messages'+(_inst2?'?instance='+_inst2:'');
  fetch(_url2).then(r=>r.json()).then(msgs=>{wppMsgs=msgs;const b=document.getElementById('wpp-badge');if(msgs.length>0){b.style.display='inline';b.textContent=msgs.length;}else b.style.display='none';if(chatAtivo)renderConvList();}).catch(()=>{});
},30000);"""

if old_interval in html:
    html = html.replace(old_interval, new_interval)
    print("✅ CORREÇÃO 2: setInterval filtrado por instância — OK")
else:
    print("⚠️  CORREÇÃO 2: setInterval não encontrado exatamente — pulando")

# ══════════════════════════════════════════════════════════
# CORREÇÃO 3: CRM central — mostrar de qual instância veio
# Adicionar tag na lista de conversas mostrando Beatriz/Davi
# ══════════════════════════════════════════════════════════
old_conv_tag = """        <div style=\"font-size:11px;color:${cor};margin-bottom:3px;font-weight:600\">${cliente?'● Cliente MF':'● Novo lead'}</div>"""

new_conv_tag = """        <div style=\"font-size:11px;color:${cor};margin-bottom:3px;font-weight:600\">${cliente?'● Cliente MF':'● Novo lead'}</div>
        <div style=\"font-size:10px;color:var(--text3);\">${g.msgs[0]&&g.msgs[0].instance?'📱 '+(g.msgs[0].instance==='mfenvios'?'Beatriz':'Davi'):''}</div>"""

if old_conv_tag in html:
    html = html.replace(old_conv_tag, new_conv_tag)
    print("✅ CORREÇÃO 3: Tag de instância na lista de conversas — OK")
else:
    print("⚠️  CORREÇÃO 3: Tag de conversa não encontrada — pulando")

# ══════════════════════════════════════════════════════════
# CORREÇÃO 4: aplicarPerfil — recarregar WhatsApp ao trocar perfil
# Garantir que ao selecionar perfil, mensagens filtram corretamente
# ══════════════════════════════════════════════════════════
old_aplicar_fim = """  renderKanban();
  updateStats();
  updateAgentFilters();
  atualizarSino();
}"""

new_aplicar_fim = """  renderKanban();
  updateStats();
  updateAgentFilters();
  atualizarSino();
  // Recarregar WhatsApp com instância do perfil selecionado
  if(typeof loadWppMessages === 'function') loadWppMessages();
}"""

if old_aplicar_fim in html:
    html = html.replace(old_aplicar_fim, new_aplicar_fim, 1)
    print("✅ CORREÇÃO 4: WhatsApp recarrega ao trocar perfil — OK")
else:
    print("⚠️  CORREÇÃO 4: Final de aplicarPerfil não encontrado — pulando")

# ══════════════════════════════════════════════════════════
# VERIFICAÇÃO FINAL
# ══════════════════════════════════════════════════════════
if html == original:
    print("\n❌ NENHUMA alteração foi feita. Verifique os textos acima.")
else:
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("\n✅ index.html atualizado com sucesso!")
    print("   Próximo passo: git add index.html && git commit -m 'fix: centavos, whatsapp instancia' && git push origin main")
