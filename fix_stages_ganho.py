with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Etapas operacionais que são consideradas "ganho" para Beatriz e Davi
# Beatriz: Aguardando Retorno, Aguardando Coleta, Nota Fiscal, Fechado / Ganho
# Davi: Aguardando Retorno, Cotação Enviada, Emissão, Coleta, Cobrança, Nota Fiscal, Fechado / Ganho

old1 = "    const ganhosOutro = leadsOutro.filter(l=>l.stage==='Fechado / Ganho');"
new1 = "    const _stagesGanhoOutro=['Fechado / Ganho','Aguardando Retorno','Aguardando Coleta','Nota Fiscal','Cotação Enviada','Emissão','Coleta','Cobrança'];\n    const ganhosOutro = leadsOutro.filter(l=>_stagesGanhoOutro.includes(l.stage));"

old2 = "  const ganhos = leadsMes.filter(l=>l.stage==='Fechado / Ganho');"
new2 = "  const _stagesGanho=['Fechado / Ganho','Aguardando Retorno','Aguardando Coleta','Nota Fiscal','Cotação Enviada','Emissão','Coleta','Cobrança'];\n  const ganhos = leadsMes.filter(l=>_stagesGanho.includes(l.stage));"

ok = True
if old1 in html:
    html = html.replace(old1, new1)
    print("OK 1/2 - ganhosOutro atualizado")
else:
    print("X 1/2 - ganhosOutro nao encontrado")
    ok = False

if old2 in html:
    html = html.replace(old2, new2)
    print("OK 2/2 - ganhos principal atualizado")
else:
    print("X 2/2 - ganhos nao encontrado")
    ok = False

if ok:
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('\nindex.html atualizado!')
    print('git add index.html && git commit -m "fix: etapas operacionais somam em ganho" && git push origin main')
