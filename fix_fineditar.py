with open('index.html', 'r', encoding='utf-8') as f:
    h = f.read()

old = """  document.getElementById('fin-lead-id').value = v.leadId || '';
  document.getElementById('fin-prazo-noop').value = '0';
  document.getElementById('modal-financeiro').style.display = 'flex';"""

new = """  document.getElementById('fin-lead-id').value = v.leadId || '';
  document.getElementById('modal-financeiro').style.display = 'flex';"""

if old in h:
    h = h.replace(old, new)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(h)
    print('OK - finEditar corrigida')
    print('git add index.html && git commit -m "fix: botao editar venda" && git push origin main')
else:
    print('X - nao encontrado')
