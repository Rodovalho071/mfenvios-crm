print("Unificando WhatsApp e qualificando leads...")

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

orig = html

# ══════════════════════════════════════════════════════════
# 1. Esconder aba WhatsApp (manter funcionalidade)
# ══════════════════════════════════════════════════════════
old_tab_wpp = '  <div class="tab" onclick="showView(\'wpp\')" id="tab-wpp">💬 WhatsApp <span class="tab-badge" id="wpp-badge" style="display:none">0</span></div>'
new_tab_wpp = '  <div class="tab" onclick="showView(\'wpp\')" id="tab-wpp" style="display:none">💬 WhatsApp <span class="tab-badge" id="wpp-badge" style="display:none">0</span></div>'

if old_tab_wpp in html:
    html = html.replace(old_tab_wpp, new_tab_wpp)
    print("OK 1/4 - aba WhatsApp escondida")
else:
    print("X 1/4 - aba WhatsApp nao encontrada")

# ══════════════════════════════════════════════════════════
# 2. Qualificação automática ao criar lead via WhatsApp
# Detecta: número salvo (nome ≠ número) ou novo (nome = número)
# Detecta: lead quente (palavras urgentes ou valor alto)
# ══════════════════════════════════════════════════════════
old_wpp_lead = "    const nl={id:uid(),name,tel:phone,material:'',origem:'',destino:'',rota:'',volumes:'',peso:'',medidas:'',valorNF:'',stage:'Primeiro contato',agent:agentName||'',source:'whatsapp',obs:text,hot:false,ts:Date.now(),followups:[],history:[{text:'Lead captado via WhatsApp.',ts:Date.now(),agent:agentName||''}]};leads.unshift(nl);saveLeads();addActivity(`Lead <strong>${name}</strong> adicionado via WhatsApp`);"

new_wpp_lead = """    // Qualificação automática
    var nomeEhNumero = /^[\\d\\s\\+\\-\\(\\)]+$/.test((name||'').trim());
    var tipoContato = nomeEhNumero ? 'novo' : 'salvo';
    var palavrasQuentes = ['urgente','urgência','hoje','agora','preciso','quanto custa','me passa','quanto fica','valor','fechado','confirma','aceito','pode ser','vamos','combinado'];
    var textoLower = (text||'').toLowerCase();
    var isHot = palavrasQuentes.some(function(p){return textoLower.includes(p);});
    var nl={id:uid(),name,tel:phone,material:'',origem:'',destino:'',rota:'',volumes:'',peso:'',medidas:'',valorNF:'',stage:'Primeiro contato',agent:agentName||'',source:'whatsapp',obs:text,hot:isHot,tipoContato:tipoContato,ts:Date.now(),followups:[],history:[{text:'Lead captado via WhatsApp.',ts:Date.now(),agent:agentName||''}]};
    leads.unshift(nl);saveLeads();addActivity(`Lead <strong>${name}</strong> adicionado via WhatsApp`+(isHot?' 🔥':'')+(tipoContato==='salvo'?' (contato salvo)':' (número novo)'));"""

if old_wpp_lead in html:
    html = html.replace(old_wpp_lead, new_wpp_lead)
    print("OK 2/4 - qualificação automática no wppToLead")
else:
    print("X 2/4 - wppToLead nao encontrado")

# ══════════════════════════════════════════════════════════
# 3. Qualificação no lead captado via IA também
# ══════════════════════════════════════════════════════════
old_ia_lead = "  const lead={id:uid(),name:iaPreview.nome||'Desconhecido',tel:iaPreview.tel||'',material:iaPreview.material||'',origem:iaPreview.origem||'',destino:iaPreview.destino||'',rota,volumes:iaPreview.volumes||'',peso:iaPreview.peso||'',medidas:iaPreview.medidas||'',valorNF:iaPreview.valorNF||'',stage:iaPreview.etapa||'Primeiro contato',agent:agentName,source:'whatsapp',obs:iaPreview.obs||'',hot:false,ts:Date.now(),followups:[],history:[{text:`Captado via WhatsApp: ${iaPreview.obs}`,ts:Date.now(),agent:agentName}]};"

new_ia_lead = """  var _nomeIA=(iaPreview.nome||'');
  var _nomeEhNumeroIA=/^[\\d\\s\\+\\-\\(\\)]+$/.test(_nomeIA.trim());
  var _tipoContatoIA=_nomeEhNumeroIA?'novo':'salvo';
  var _palavrasQuentesIA=['urgente','urgência','hoje','agora','preciso','fechado','confirma','aceito','combinado'];
  var _obsIA=(iaPreview.obs||'').toLowerCase();
  var _isHotIA=_palavrasQuentesIA.some(function(p){return _obsIA.includes(p);});
  const lead={id:uid(),name:_nomeIA||'Desconhecido',tel:iaPreview.tel||'',material:iaPreview.material||'',origem:iaPreview.origem||'',destino:iaPreview.destino||'',rota,volumes:iaPreview.volumes||'',peso:iaPreview.peso||'',medidas:iaPreview.medidas||'',valorNF:iaPreview.valorNF||'',stage:iaPreview.etapa||'Primeiro contato',agent:agentName,source:'whatsapp',obs:iaPreview.obs||'',hot:_isHotIA,tipoContato:_tipoContatoIA,ts:Date.now(),followups:[],history:[{text:`Captado via WhatsApp: ${iaPreview.obs}`,ts:Date.now(),agent:agentName}]};"""

if old_ia_lead in html:
    html = html.replace(old_ia_lead, new_ia_lead)
    print("OK 3/4 - qualificação automática no lead via IA")
else:
    print("X 3/4 - lead via IA nao encontrado")

# ══════════════════════════════════════════════════════════
# 4. Mostrar tag de tipo contato no card do Kanban
# ══════════════════════════════════════════════════════════
old_card_tags = "          ${lead.source==='whatsapp'?'<span class=\"tag tag-wpp\">WhatsApp</span>':''}"
new_card_tags = """          ${lead.source==='whatsapp'?'<span class=\"tag tag-wpp\">WhatsApp</span>':''}
          ${lead.tipoContato==='salvo'?'<span class=\"tag\" style=\"background:rgba(34,197,94,.2);color:#22c55e\">🟢 Salvo</span>':lead.tipoContato==='novo'?'<span class=\"tag\" style=\"background:rgba(59,130,246,.2);color:#3b82f6\">🔵 Novo</span>':''}"""

if old_card_tags in html:
    html = html.replace(old_card_tags, new_card_tags)
    print("OK 4/4 - tags salvo/novo no card Kanban")
else:
    print("X 4/4 - card tags nao encontrado")

if html != orig:
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("\nindex.html atualizado!")
    print("git add index.html && git commit -m 'feat: qualificacao leads WA, aba WA escondida' && git push origin main")
else:
    print("\nNenhuma alteracao feita")
