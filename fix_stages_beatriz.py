with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old = "    stages: ['Primeiro contato','Qualificação','Proposta enviada','Negociação','Fechado / Ganho','Perdido'],\n    stageColors: {'Primeiro contato':'#3b82f6','Qualificação':'#8b5cf6','Proposta enviada':'#f59e0b','Negociação':'#f97316','Fechado / Ganho':'#22c55e','Perdido':'#ef4444'}"

new = "    stages: ['Primeiro contato','Negociação','Aguardando Retorno','Aguardando Coleta','Nota Fiscal','Fechado / Ganho','Perdido'],\n    stageColors: {'Primeiro contato':'#3b82f6','Negociação':'#f97316','Aguardando Retorno':'#f59e0b','Aguardando Coleta':'#06b6d4','Nota Fiscal':'#84cc16','Fechado / Ganho':'#22c55e','Perdido':'#ef4444'}"

if old in html:
    html = html.replace(old, new)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('OK - etapas da Beatriz atualizadas')
    print('git add index.html && git commit -m "feat: etapas Beatriz atualizadas" && git push origin main')
else:
    print('X - nao encontrado')
