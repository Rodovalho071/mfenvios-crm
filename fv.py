import pathlib, re
f = pathlib.Path(r"C:\mfcrm\index.html")
html = f.read_text(encoding="utf-8")
changes = 0

# 1. salvarVendas - salva no MongoDB via API
OLD1 = "function salvarVendas() {localStorage.setItem('crm-vendas',JSON.stringify(vendas));}"
NEW1 = """function salvarVendas() {localStorage.setItem('crm-vendas',JSON.stringify(vendas));}
function salvarVendaAPI(venda) {
  return fetch('/vendas', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(venda)});
}
function deletarVendaAPI(id) {
  return fetch('/vendas/'+id, {method:'DELETE'});
}"""
if OLD1 in html:
    html = html.replace(OLD1, NEW1, 1); changes += 1; print("OK salvarVendas")
else:
    print("-- salvarVendas nao encontrado")

# 2. finSalvar - usa API ao criar/editar
OLD2 = "  salvarVendas();\n  fecharModalVenda();\n  renderFinanceiro();\n  if(typeof showToast === 'function') showToast('Venda salva — ' + cliente);"
NEW2 = """  salvarVendaAPI(vendaEditando ? vendas.find(function(v){return v.id===vendaEditando;}) : vendas[vendas.length-1])
    .catch(function(){});
  salvarVendas();
  fecharModalVenda();
  renderFinanceiro();
  if(typeof showToast === 'function') showToast('Venda salva — ' + cliente);"""
if OLD2 in html:
    html = html.replace(OLD2, NEW2, 1); changes += 1; print("OK finSalvar API")
else:
    print("-- finSalvar nao encontrado")

# 3. finDeletar - usa API ao deletar
OLD3 = "function finDeletar(id) {\n  vendas = vendas.filter(function(v){ return v.id!==id; });\n  salvarVendas();\n  renderFinanceiro();"
NEW3 = """function finDeletar(id) {
  deletarVendaAPI(id).catch(function(){});
  vendas = vendas.filter(function(v){ return v.id!==id; });
  salvarVendas();
  renderFinanceiro();"""
if OLD3 in html:
    html = html.replace(OLD3, NEW3, 1); changes += 1; print("OK finDeletar API")
else:
    print("-- finDeletar nao encontrado (ok se nao existe)")

# 4. carregarVendas - limpa localStorage corrompido
OLD4 = "    vendas = Array.isArray(data) ? data : [];"
NEW4 = """    vendas = (Array.isArray(data) ? data : []).map(function(v){
      if(typeof v.valor === 'number' && Number.isInteger(v.valor) && v.valor >= 1000) v.valor = v.valor/100;
      return v;
    });
    localStorage.removeItem('crm-vendas');"""
if OLD4 in html:
    html = html.replace(OLD4, NEW4, 1); changes += 1; print("OK carregarVendas limpa localStorage")
else:
    print("-- carregarVendas nao encontrado")

f.write_text(html, encoding="utf-8")
print(f"\n{changes} mudancas aplicadas")
