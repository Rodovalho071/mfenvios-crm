import pathlib, re
f = pathlib.Path(r"C:\mfcrm\index.html")
html = f.read_text(encoding="utf-8")
NEW = "function somaFrete(arr){\n  return arr.reduce((s,l)=>s+parseMoeda(l.valorFrete||0),0);\n}"
novo, n = re.subn(r'function somaFrete\(arr\)\{[\s\S]*?\}', NEW, html, count=1)
if n:
    f.write_text(novo, encoding="utf-8")
    print("OK somaFrete corrigida")
else:
    print("-- nao encontrada")
