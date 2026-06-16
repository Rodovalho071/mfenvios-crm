import pathlib, re
f = pathlib.Path(r"C:\mfcrm\index.html")
html = f.read_text(encoding="utf-8")
novo, n = re.subn(
    r'function formatMoeda\(v\) \{[\s\S]*?\}',
    'function formatMoeda(v) {\n  var n = parseMoeda(v);\n  if(isNaN(n)) return \'R$ 0,00\';\n  return \'R$ \' + n.toLocaleString(\'pt-BR\', {minimumFractionDigits:2, maximumFractionDigits:2});\n}',
    html, count=1)
if n:
    f.write_text(novo, encoding="utf-8")
    print("OK formatMoeda corrigida")
else:
    print("-- nao encontrado")
