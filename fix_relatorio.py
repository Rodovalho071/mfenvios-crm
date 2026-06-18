with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old_relatorio = """function abrirRelatorio(){
  const hoje=new Date();hoje.setHours(0,0,0,0);
  const leadsHoje=leads.filter(l=>new Date(l.ts)>=hoje).sort((a,b)=>a.ts-b.ts);
  const dataStr=new Date().toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit',year:'numeric'});
  const novos=leadsHoje.filter(l=>l.stage==='Primeiro contato').length;
  const proposta=leadsHoje.filter(l=>l.stage==='Proposta enviada').length;
  const negociacao=leadsHoje.filter(l=>l.stage==='Negociação').length;
  const qualificacao=leadsHoje.filter(l=>l.stage==='Qualificação').length;
  const perdidos=leadsHoje.filter(l=>l.stage==='Perdido').length;
  const followupsPendentes=leads.flatMap(l=>(l.followups||[]).filter(f=>!f.done).map(f=>({...f,leadName:l.name,leadTel:l.tel,leadId:l.id,valor:l.valorNF,rota:l.rota})));"""

new_relatorio = """function abrirRelatorio(){
  const hoje=new Date();hoje.setHours(0,0,0,0);
  const leadsHoje=leads.filter(l=>new Date(l.ts)>=hoje).sort((a,b)=>a.ts-b.ts);
  const dataStr=new Date().toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit',year:'numeric'});
  const diaSemana=new Date().toLocaleDateString('pt-BR',{weekday:'long'});
  const novos=leadsHoje.filter(l=>l.stage==='Primeiro contato').length;
  const proposta=leadsHoje.filter(l=>l.stage==='Proposta enviada').length;
  const negociacao=leadsHoje.filter(l=>l.stage==='Negociação').length;
  const qualificacao=leadsHoje.filter(l=>l.stage==='Qualificação').length;
  const perdidos=leadsHoje.filter(l=>l.stage==='Perdido').length;
  const followupsPendentes=leads.flatMap(l=>(l.followups||[]).filter(f=>!f.done).map(f=>({...f,leadName:l.name,leadTel:l.tel,leadId:l.id,valor:l.valorNF,rota:l.rota})));
  // Financeiro do dia
  const vendasHoje=vendas.filter(v=>{var d=new Date(v.ts||0);d.setHours(0,0,0,0);return d>=hoje;});
  const faturadoHoje=vendasHoje.reduce((s,v)=>s+(parseFloat(v.valor)||0),0);
  const recebidoHoje=vendasHoje.filter(v=>v.pago).reduce((s,v)=>s+(parseFloat(v.valor)||0),0);
  const aReceberHoje=faturadoHoje-recebidoHoje;
  const fmt=v=>'R$ '+v.toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2});"""

if old_relatorio in html:
    html = html.replace(old_relatorio, new_relatorio)
    print("OK 1/3 - financeiro do dia adicionado")
else:
    print("X 1/3 - inicio relatorio nao encontrado")

# 2. Substituir HTML do relatório — visual MF Envios + financeiro
old_html_rel = """  const html=`<!DOCTYPE html><html><head><meta charset=\"UTF-8\"><title>Relatório ${dataStr}</title>
  <style>
    body{font-family:'Segoe UI',Arial,sans-serif;margin:0;padding:32px;background:#fff;color:#1a1a2e;font-size:13px}
    .header{margin-bottom:24px}.header h1{font-size:22px;font-weight:700;color:#1a1a2e;margin-bottom:4px}
    .header p{color:#666;font-size:13px}
    .counters{display:flex;gap:0;border:1px solid #e2e8f0;border-radius:8px;overflow:hidden;margin-bottom:28px}
    .counter{flex:1;padding:16px;text-align:center;border-right:1px solid #e2e8f0}.counter:last-child{border-right:none}
    .counter-val{font-size:28px;font-weight:700;color:#f97316;line-height:1}.counter-label{font-size:11px;color:#888;text-transform:uppercase;letter-spacing:.05em;margin-top:3px}
    .section-title{font-size:14px;font-weight:700;color:#1a1a2e;margin:24px 0 14px;padding-bottom:8px;border-bottom:2px solid #f97316}
    .lead-card{border:1px solid #e2e8f0;border-radius:8px;padding:16px;margin-bottom:12px;page-break-inside:avoid}
    .lead-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px}
    .lead-name{font-size:15px;font-weight:700;color:#1a1a2e}.lead-stage{padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600}
    .lead-phone{font-size:12px;color:#666;margin-bottom:10px}
    .lead-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:10px}
    .lead-field label{font-size:10px;color:#888;text-transform:uppercase;letter-spacing:.05em;display:block;margin-bottom:2px}
    .lead-field span{font-size:13px;color:#1a1a2e;font-weight:500}
    .lead-obs{font-size:12px;color:#444;background:#f8fafc;padding:10px;border-radius:6px;line-height:1.6}
    .lead-horario{font-size:11px;color:#888;margin-bottom:8px}
    .recomendacoes{margin-top:28px}
    .rec-item{display:flex;gap:12px;padding:12px;border:1px solid #e2e8f0;border-radius:8px;margin-bottom:8px}
    .rec-num{width:24px;height:24px;border-radius:50%;background:#f97316;color:#fff;font-size:12px;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0}
    .rec-text{font-size:13px;color:#1a1a2e;line-height:1.5}
    .footer{margin-top:32px;padding-top:16px;border-top:1px solid #e2e8f0;font-size:11px;color:#888;text-align:center}
    .stage-proposta{background:#fef3c7;color:#92400e}.stage-negociacao{background:#fee2e2;color:#991b1b}
    .stage-qualificacao{background:#ede9fe;color:#5b21b6}.stage-novo{background:#dbeafe;color:#1e40af}
    .stage-fechado{background:#dcfce7;color:#166534}.stage-perdido{background:#fee2e2;color:#991b1b}
    @media print{body{padding:16px}}
  </style></head><body>
  <div class=\"header\">
    <h1>Leads novos — ${dataStr}</h1>
    <p>${dataStr} &nbsp;·&nbsp; Atendente: ${agentName||'MF Envios'} &nbsp;·&nbsp; MF Envios · Clientes captados via Google / WhatsApp</p>
  </div>
  <div class=\"counters\">
    <div class=\"counter\"><div class=\"counter-val\">${leadsHoje.length}</div><div class=\"counter-label\">Leads novos</div></div>
    <div class=\"counter\"><div class=\"counter-val\">${proposta}</div><div class=\"counter-label\">Proposta enviada</div></div>
    <div class=\"counter\"><div class=\"counter-val\">${negociacao}</div><div class=\"counter-label\">Negociação</div></div>
    <div class=\"counter\"><div class=\"counter-val\">${qualificacao}</div><div class=\"counter-label\">Qualificação</div></div>
    <div class=\"counter\"><div class=\"counter-val\">${perdidos}</div><div class=\"counter-label\">Perdidos</div></div>
  </div>"""

new_html_rel = """  const html=`<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Relatório MF Envios — ${dataStr}</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    *{box-sizing:border-box;margin:0;padding:0}
    body{font-family:'Inter','Helvetica Neue',Arial,sans-serif;background:#F4F5FA;color:#1E2456;font-size:13px}
    .page{max-width:900px;margin:0 auto;padding:32px 24px}
    /* HEADER */
    .header{background:#1E2456;border-radius:12px;padding:28px 32px;margin-bottom:24px;position:relative;overflow:hidden}
    .header::before{content:'';position:absolute;top:-30px;left:50%;transform:translateX(-50%);width:500px;height:100px;border-radius:50%;border:2px solid rgba(249,115,22,0.6);box-shadow:0 0 20px rgba(249,115,22,0.3)}
    .header-logo{font-size:22px;font-weight:800;color:#fff;letter-spacing:3px;margin-bottom:4px}
    .header-logo span{color:#F97316}
    .header-sub{font-size:12px;color:rgba(255,255,255,0.6);letter-spacing:0.05em;text-transform:uppercase}
    .header-date{font-size:13px;color:rgba(255,255,255,0.8);margin-top:12px}
    .header-right{position:absolute;right:32px;top:50%;transform:translateY(-50%);text-align:right}
    .header-agent{font-size:12px;color:rgba(255,255,255,0.6);text-transform:uppercase;letter-spacing:0.05em}
    .header-agent-name{font-size:16px;font-weight:700;color:#F97316}
    /* SEÇÃO FINANCEIRO */
    .fin-cards{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:24px}
    .fin-card{background:#fff;border-radius:10px;padding:16px 20px;border-left:4px solid #F97316;box-shadow:0 2px 8px rgba(0,0,0,0.06)}
    .fin-card.green{border-left-color:#22c55e}.fin-card.blue{border-left-color:#3b82f6}
    .fin-label{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#8B8FA8;margin-bottom:6px}
    .fin-val{font-size:24px;font-weight:800;color:#1E2456}
    .fin-val.orange{color:#F97316}.fin-val.green{color:#22c55e}.fin-val.blue{color:#3b82f6}
    /* CONTADORES LEADS */
    .counters{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-bottom:24px}
    .counter{background:#fff;border-radius:10px;padding:14px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.06)}
    .counter-val{font-size:28px;font-weight:800;color:#F97316;line-height:1}
    .counter-label{font-size:10px;color:#8B8FA8;text-transform:uppercase;letter-spacing:0.05em;margin-top:4px}
    /* SECTION */
    .section-title{font-size:12px;font-weight:800;color:#1E2456;text-transform:uppercase;letter-spacing:0.08em;margin:0 0 14px;padding-bottom:8px;border-bottom:2px solid #F97316;display:flex;align-items:center;gap:8px}
    .section-block{margin-bottom:28px}
    /* LEAD CARD */
    .lead-card{background:#fff;border-radius:10px;padding:16px 20px;margin-bottom:10px;box-shadow:0 2px 8px rgba(0,0,0,0.06);border-left:4px solid #F97316;page-break-inside:avoid}
    .lead-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:8px}
    .lead-name{font-size:15px;font-weight:700;color:#1E2456}
    .lead-stage{padding:3px 10px;border-radius:20px;font-size:10px;font-weight:700;letter-spacing:0.05em;text-transform:uppercase}
    .lead-phone{font-size:12px;color:#8B8FA8;margin-bottom:10px}
    .lead-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:8px}
    .lead-field label{font-size:10px;color:#8B8FA8;text-transform:uppercase;letter-spacing:0.05em;display:block;margin-bottom:2px;font-weight:600}
    .lead-field span{font-size:13px;color:#1E2456;font-weight:500}
    .lead-obs{font-size:12px;color:#555;background:#F4F5FA;padding:10px 12px;border-radius:6px;line-height:1.6;margin-top:8px;border-left:3px solid #F97316}
    .lead-horario{font-size:11px;color:#8B8FA8;margin-bottom:6px}
    /* VENDA CARD */
    .venda-card{background:#fff;border-radius:10px;padding:14px 18px;margin-bottom:8px;box-shadow:0 2px 8px rgba(0,0,0,0.06);display:flex;align-items:center;justify-content:space-between}
    .venda-cliente{font-size:14px;font-weight:700;color:#1E2456}
    .venda-desc{font-size:12px;color:#8B8FA8;margin-top:2px}
    .venda-valor{font-size:16px;font-weight:800;color:#22c55e}
    .venda-status{padding:3px 10px;border-radius:20px;font-size:10px;font-weight:700}
    .venda-pago{background:#dcfce7;color:#166534}.venda-pendente{background:#fef3c7;color:#92400e}.venda-atrasado{background:#fee2e2;color:#991b1b}
    /* FOLLOWUP */
    .rec-item{display:flex;gap:12px;padding:12px 14px;background:#fff;border-radius:8px;margin-bottom:8px;box-shadow:0 2px 8px rgba(0,0,0,0.05);align-items:flex-start}
    .rec-num{width:24px;height:24px;border-radius:50%;background:#F97316;color:#fff;font-size:12px;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:1px}
    .rec-text{font-size:13px;color:#1E2456;line-height:1.5}
    /* STAGE PILLS */
    .stage-proposta{background:#fef3c7;color:#92400e}.stage-negociacao{background:#fee2e2;color:#991b1b}
    .stage-qualificacao{background:#ede9fe;color:#5b21b6}.stage-novo{background:#dbeafe;color:#1e40af}
    .stage-fechado{background:#dcfce7;color:#166534}.stage-perdido{background:#fee2e2;color:#991b1b}
    /* FOOTER */
    .footer{margin-top:32px;padding-top:16px;border-top:1px solid #e2e8f0;font-size:11px;color:#8B8FA8;text-align:center}
    @media print{body{background:#fff}.page{padding:16px}.header{-webkit-print-color-adjust:exact;print-color-adjust:exact}.fin-card,.counter,.lead-card,.venda-card,.rec-item{box-shadow:none}}
  </style></head><body><div class="page">
  <div class="header">
    <div class="header-logo">MF <span>ENVIOS</span></div>
    <div class="header-sub">Relatório Diário de Operações</div>
    <div class="header-date">${diaSemana.charAt(0).toUpperCase()+diaSemana.slice(1)}, ${dataStr}</div>
    <div class="header-right">
      <div class="header-agent">Atendente</div>
      <div class="header-agent-name">${agentName||'MF Envios'}</div>
    </div>
  </div>
  <!-- FINANCEIRO DO DIA -->
  <div class="section-block">
    <div class="section-title">💰 Financeiro do Dia</div>
    <div class="fin-cards">
      <div class="fin-card"><div class="fin-label">Faturado hoje</div><div class="fin-val orange">${fmt(faturadoHoje)}</div></div>
      <div class="fin-card green"><div class="fin-label">Recebido hoje</div><div class="fin-val green">${fmt(recebidoHoje)}</div></div>
      <div class="fin-card blue"><div class="fin-label">A receber hoje</div><div class="fin-val blue">${fmt(aReceberHoje)}</div></div>
    </div>
    ${vendasHoje.length?vendasHoje.map(v=>{
      const hoje2=new Date();hoje2.setHours(0,0,0,0);
      const venc=v.vencimento?new Date(v.vencimento+'T00:00:00'):null;
      const atrasado=venc&&venc<hoje2&&!v.pago;
      const stClass=v.pago?'venda-pago':atrasado?'venda-atrasado':'venda-pendente';
      const stText=v.pago?'Recebido':atrasado?'Atrasado':'Pendente';
      return `<div class="venda-card"><div><div class="venda-cliente">${v.cliente||'—'}</div><div class="venda-desc">${v.descricao||v.formaPag||''}</div></div><div style="text-align:right"><div class="venda-valor">${fmt(parseFloat(v.valor)||0)}</div><div class="venda-status ${stClass}">${stText}</div></div></div>`;
    }).join(''):'<div style="color:#8B8FA8;font-size:13px;padding:12px 0">Nenhuma venda registrada hoje.</div>'}
  </div>
  <!-- LEADS -->
  <div class="section-block">
    <div class="section-title">📋 Leads do Dia</div>
    <div class="counters">
      <div class="counter"><div class="counter-val">${leadsHoje.length}</div><div class="counter-label">Total</div></div>
      <div class="counter"><div class="counter-val">${novos}</div><div class="counter-label">Novos</div></div>
      <div class="counter"><div class="counter-val">${proposta}</div><div class="counter-label">Proposta</div></div>
      <div class="counter"><div class="counter-val">${negociacao}</div><div class="counter-label">Negociação</div></div>
      <div class="counter"><div class="counter-val">${perdidos}</div><div class="counter-label">Perdidos</div></div>
    </div>"""

if old_html_rel in html:
    html = html.replace(old_html_rel, new_html_rel)
    print("OK 2/3 - HTML do relatório atualizado")
else:
    print("X 2/3 - HTML antigo do relatório nao encontrado")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("OK 3/3 - index.html salvo")
print("\ngit add index.html && git commit -m 'feat: relatorio MF Envios v2 com financeiro' && git push origin main")
