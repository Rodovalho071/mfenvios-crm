with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old = "  const stagesNeg = typeof PERFIS !== 'undefined' && perfilAtivo && PERFIS[perfilAtivo]\n    ? PERFIS[perfilAtivo].stages.filter(s=>s!=='Fechado / Ganho'&&s!=='Perdido')\n    : ['Proposta enviada','Negociação','Qualificação','Cotação Enviada','Emissão','Coleta','Cobrança','Nota Fiscal'];"

new = "  const _stagesGanhoCalc=['Fechado / Ganho','Aguardando Retorno','Aguardando Coleta','Nota Fiscal','Cotação Enviada','Emissão','Coleta','Cobrança'];\n  const stagesNeg = typeof PERFIS !== 'undefined' && perfilAtivo && PERFIS[perfilAtivo]\n    ? PERFIS[perfilAtivo].stages.filter(s=>!_stagesGanhoCalc.includes(s)&&s!=='Perdido')\n    : ['Negociação','Primeiro contato','Novo'];"

if old in html:
    html = html.replace(old, new)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('OK - stagesNeg corrigido')
    print('git add index.html && git commit -m "fix: emNeg exclui etapas pos-ganho" && git push origin main')
else:
    print('X - nao encontrado')
