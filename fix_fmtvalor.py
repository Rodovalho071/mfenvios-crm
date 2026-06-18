with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old = """function fmtValorStat(v){
  if(!v||v===0) return 'R$ 0';
  if(v>=1000000) return 'R$'+(v/1000000).toFixed(1)+'M';
  if(v>=1000) return 'R$'+(v/1000).toFixed(0)+'k';
  return 'R$'+Math.round(v);
}"""

new = """function fmtValorStat(v){
  if(!v||v===0) return 'R$ 0,00';
  return 'R$ '+v.toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2});
}"""

if old in html:
    html = html.replace(old, new)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('OK - valores com centavos no header')
    print('git add index.html && git commit -m "fix: valores completos no header" && git push origin main')
else:
    print('X - fmtValorStat nao encontrada')
