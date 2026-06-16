import pathlib, re, urllib.request

html = urllib.request.urlopen("https://raw.githubusercontent.com/Rodovalho071/mfenvios-crm/main/index.html").read().decode("utf-8")
changes = 0

# 1. fmtValorStat - mostra valor completo em vez de k/M
OLD = "function fmtValorStat(v){\n  if(!v||v===0) return 'R$ 0';\n  if(v>=1000000) return 'R$'+(v/1000000).toFixed(1)+'M';\n  if(v>=1000) return 'R$'+(v/1000).toFixed(0)+'k';\n  return 'R$'+Math.round(v);\n}"
NEW = "function fmtValorStat(v){\n  if(!v||v===0) return 'R$ 0,00';\n  return 'R$ '+v.toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2});\n}"
if OLD in html:
    html = html.replace(OLD, NEW, 1); changes+=1; print("OK fmtValorStat")
else:
    print("-- fmtValorStat nao encontrado")

# 2. parseMoeda sem dividir por 100
PARSE = "function parseMoeda(v){if(v===null||v===undefined||v==='')return 0;if(typeof v==='number')return v;var s=v.toString().replace(/R[$]\\s*/g,'').replace(/\\s/g,'').trim();if(!s)return 0;if(s.indexOf(',')!==-1){s=s.replace(/[.]/g,'').replace(',','.');return parseFloat(s)||0;}if(s.indexOf('.')!==-1){var p=s.split('.');if(p.length===2&&p[1].length<=2)return parseFloat(s)||0;s=s.replace(/[.]/g,'');}return parseFloat(s)||0;}"
m = re.search(r'function parseMoeda\(v\)\{[^}]+(?:\{[^}]*\}[^}]*)*\}', html)
if m:
    html = html[:m.start()] + PARSE + html[m.end():]
    changes+=1; print("OK parseMoeda")
else:
    print("-- parseMoeda nao encontrado")

pathlib.Path(r"C:\mfcrm\index.html").write_text(html, encoding="utf-8")
print(f"\n{changes} mudancas aplicadas")
