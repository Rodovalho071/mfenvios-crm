import pathlib
f=pathlib.Path(r"C:\mfcrm\index.html")
html=f.read_text(encoding="utf-8")
OLD="function somaFrete(arr){\n  return arr.reduce((s,l)=>{\n    const v=parseFloat((l.valorFrete||'0').replace(/\\./g,'').replace(',','.'));\n    return s+(isNaN(v)?0:v);\n  },0);\n}"
NEW='function somaFrete(arr){\n  return arr.reduce((s,l)=>s+parseMoeda(l.valorFrete||0),0);\n}'
if OLD in html:
    f.write_text(html.replace(OLD,NEW,1),encoding="utf-8")
    print("OK somaFrete corrigida")
else:
    print("-- somaFrete nao encontrada")
