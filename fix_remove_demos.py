with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old = """if(!leads.length){
  const demo=[
    {id:uid(),name:'Wanderley Cruz',tel:'5513992062157',material:'Caixas',origem:'Tijucas/SC',destino:'Macapá/AP',rota:'Tijucas/SC → Macapá/AP',volumes:'1 volume',peso:'33kg',medidas:'82x52x64cm',valorNF:'80.948,57',stage:'Proposta enviada',agent:agentName||'Beatriz',source:'whatsapp',obs:'Proposta: R$ 8.212,96 · 2 a 3 dias úteis. Intermediário — aguardando retorno.',urgencia:'',hot:false,ts:Date.now()-3600000,followups:[{text:'Confirmar fechamento',date:'',done:false}],history:[{text:'Lead captado via WhatsApp.',ts:Date.now()-3600000,agent:'Beatriz'}]},
    {id:uid(),name:'Isabella Guarnier',tel:'5511982517687',material:'Volumes',origem:'São Paulo/SP',destino:'Itacoatiara/AM',rota:'São Paulo/SP → Itacoatiara/AM',volumes:'2 volumes',peso:'42kg',medidas:'47x47x50cm',valorNF:'3.258,75',stage:'Negociação',agent:agentName||'Beatriz',source:'whatsapp',obs:'Proposta: R$ 1.717,00 · 6 dias úteis. Lead disse \"Perfeito. Obrigada!\" Aguardando confirmação.',urgencia:'',hot:true,ts:Date.now()-7200000,followups:[{text:'Confirmar fechamento — R$ 1.717,00',date:'',done:false}],history:[{text:'Proposta enviada.',ts:Date.now()-7200000,agent:'Beatriz'}]},
  ];
  leads=demo;saveLeads();activity=[{msg:'Lead <strong>Wanderley Cruz</strong> em proposta',ts:Date.now()-3600000},{msg:'Lead <strong>Isabella Guarnier</strong> em negociação 🔥',ts:Date.now()-7200000}];saveActivity();updateAgentFilters();updateStats();
}"""

if old in html:
    html = html.replace(old, '// leads carregados do MongoDB via sincronizarLeadsServidor()')
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('OK - leads demo removidos')
    print('git add index.html && git commit -m "fix: remover leads demo" && git push origin main')
else:
    print('X - bloco demo nao encontrado')
