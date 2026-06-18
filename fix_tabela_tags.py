with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Adicionar coluna Tipo no cabeçalho
old_th = "    <table><thead><tr><th>Nome</th><th>Rota</th><th>Etapa</th><th>Valor NF</th><th>Responsável</th><th>Horário</th><th>Follow-up</th></tr></thead><tbody id=\"leads-tbody\"></tbody></table>"
new_th = "    <table><thead><tr><th>Nome</th><th>Tipo</th><th>Rota</th><th>Etapa</th><th>Valor NF</th><th>Responsável</th><th>Horário</th></tr></thead><tbody id=\"leads-tbody\"></tbody></table>"

if old_th in html:
    html = html.replace(old_th, new_th)
    print("OK 1/2 - coluna Tipo adicionada no cabeçalho")
else:
    print("X 1/2 - cabeçalho não encontrado")

# 2. Adicionar célula de tipo na linha da tabela
old_tr = """    return `<tr onclick=\"openLead('${l.id}')\">\n      <td><strong>${l.name}</strong></td>\n      <td style=\"color:var(--blue);font-size:12px\">${l.rota||l.prod||'—'}</td>\n      <td><span class=\"stage-pill\" style=\"${STAGE_PILL[l.stage]||''}\">${l.stage}</span></td>\n      <td style=\"color:var(--green)\">${l.valorNF?'R$ '+l.valorNF:'—'}</td>\n      <td style=\"color:var(--text2)\">${l.agent||'—'}</td>\n      <td style=\"color:var(--text3)\">${fmtTime(l.ts)}</td>\n      <td style=\"color:${fu?'var(--amber)':'var(--text3)'}\">${fu?fu.text:'—'}</td>\n    </tr>`;"""

new_tr = """    const tipoTag=l.tipoContato==='salvo'?'<span style=\"background:rgba(34,197,94,.2);color:#22c55e;padding:2px 7px;border-radius:20px;font-size:10px;font-weight:700\">🟢 Salvo</span>':l.tipoContato==='novo'?'<span style=\"background:rgba(59,130,246,.2);color:#3b82f6;padding:2px 7px;border-radius:20px;font-size:10px;font-weight:700\">🔵 Novo</span>':'<span style=\"color:var(--text3);font-size:11px\">—</span>';
    return `<tr onclick=\"openLead('${l.id}')\">\n      <td><strong>${l.name}</strong>${l.hot?' 🔥':''}</td>\n      <td>${tipoTag}</td>\n      <td style=\"color:var(--blue);font-size:12px\">${l.rota||l.prod||'—'}</td>\n      <td><span class=\"stage-pill\" style=\"${STAGE_PILL[l.stage]||''}\">${l.stage}</span></td>\n      <td style=\"color:var(--green)\">${l.valorNF?'R$ '+l.valorNF:'—'}</td>\n      <td style=\"color:var(--text2)\">${l.agent||'—'}</td>\n      <td style=\"color:var(--text3)\">${fmtTime(l.ts)}</td>\n    </tr>`;"""

if old_tr in html:
    html = html.replace(old_tr, new_tr)
    print("OK 2/2 - tags Salvo/Novo/Quente na tabela")
else:
    print("X 2/2 - linha da tabela não encontrada")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("\ngit add index.html && git commit -m 'feat: tags salvo/novo na tabela clientes' && git push origin main")
