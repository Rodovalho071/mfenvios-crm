import pathlib
f = pathlib.Path(r"C:\mfcrm\index.html")
html = f.read_text(encoding="utf-8")
# Fix formatMoeda para usar parseMoeda
OLD = "function formatMoeda(v) {\n  var n = parseFloat((v||'0').toString().replace(/\\./g,'').replace(',','.'));\n  if(isNaN(n)) return 'R$ 0,00';\n  return 'R$ ' + n.toLocaleString('pt-BR', {minimumFractionDigits:2, maximumFractionDigits:3});\n}"
NEW = "function formatMoeda(v);\n  var n = parseMoeda(v);\n  if(isNaN(n) || n === 0 && !v)return 'R$ 0,00';\n  return 'R$ ' + n.toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:3});\n}"
if OLD in html:
    html = html.replace(OLD,NEW,1)
    print("OK formatMoeda")
else:
    print("-- nao encontrado")
f.write_text(html,encoding="utf-8")
