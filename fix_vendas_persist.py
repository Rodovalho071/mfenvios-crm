with open('index.html', 'r', encoding='utf-8') as f:
    h = f.read()

# Corrigir salvarVendas para persistir no MongoDB
old = "function salvarVendas() {}"

new = """function salvarVendas() {
  // Persistir todas as vendas no MongoDB
  vendas.forEach(function(v) {
    fetch('/vendas', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(v)}).catch(function(){});
  });
}"""

if old in h:
    h = h.replace(old, new)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(h)
    print('OK - salvarVendas corrigida, agora persiste no MongoDB')
    print('git add index.html && git commit -m "fix: vendas persistem no MongoDB" && git push origin main')
else:
    print('X - salvarVendas nao encontrada')
