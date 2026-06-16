import pathlib, re
f = pathlib.Path(r"C:\mfcrm\index.html")
html = f.read_text(encoding="utf-8")
# Corrige salvarVendas vazia
OLD = "function salvarVendas() {}"
NEW = "function salvarVendas() {localStorage.setItem('crm-vendas',JSON.stringify(vendas));}"
# Corrige carregamento - parseMoeda no localStorage
OLD2 = "vendas = JSON.parse(localStorage.getItem('crm-vendas')||'[]');"
NEW2 = "vendas = JSON.parse(localStorage.getItem('crm-vendas')||'[]').map(function(v){v.valor=parseMoeda(v.valor);return v;});"
if OLD in html:
    html = html.replace(OLD, NEW, 1)
    print("OK salvarVendas")
else:
    print("-- salvarVendas nao encontrada")
if OLD2 in html:
    html = html.replace(OLD2, NEW2, 1)
    print("OK carregamento corrigido")
else:
    print("-- carregamento nao encontrado")
f.write_text(html, encoding="utf-8")
print("OK")