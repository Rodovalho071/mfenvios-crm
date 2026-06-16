import pathlib, re
f = pathlib.Path(r"C:\mfcrm\index.html")
html = f.read_text(encoding="utf-8")
# Reverte o carregamento com parseMoeda - volta para o original
OLD = "vendas = JSON.parse(localStorage.getItem('crm-vendas')||'[]').map(function(v){v.valor=parseMoeda(v.valor);return v;});"
NEW = "vendas = JSON.parse(localStorage.getItem('crm-vendas')||'[]');"
if OLD in html:
    html = html.replace(OLD, NEW, 1)
    print("OK revertido")
else:
    print("-- nao encontrado")
f.write_text(html, encoding="utf-8")
