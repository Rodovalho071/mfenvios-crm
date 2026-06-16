import pathlib, re, urllib.request

print("Baixando index.html do GitHub...")
html = urllib.request.urlopen("https://raw.githubusercontent.com/Rodovalho071/mfenvios-crm/main/index.html").read().decode("utf-8")

PARSE = "function parseMoeda(v){if(v===null||v===undefined||v==='')return 0;if(typeof v==='number')return v;var s=v.toString().replace(/R[$]\\s*/g,'').replace(/\\s/g,'').trim();if(!s)return 0;if(s.indexOf(',')!==-1){s=s.replace(/[.]/g,'').replace(',','.');return parseFloat(s)||0;}if(s.indexOf('.')!==-1){var p=s.split('.');if(p.length===2&&p[1].length<=2)return parseFloat(s)||0;s=s.replace(/[.]/g,'');}return parseFloat(s)||0;}"
FORMAT = "function formatMoeda(v){var n=parseMoeda(v);if(isNaN(n))return 'R$ 0,00';return 'R$ '+n.toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2});}"
SOMA = "function somaFrete(arr){return arr.reduce(function(s,l){return s+parseMoeda(l.valorFrete||0);},0);}"

changes = 0
for pat, rep, label in [
    (r'function parseMoeda\(v\)\{[^}]+(?:\{[^}]*\}[^}]*)*\}', PARSE, "parseMoeda"),
    (r'function formatMoeda\(v\) \{[^}]+(?:\{[^}]*\}[^}]*)*\}', FORMAT, "formatMoeda"),
    (r'function somaFrete\(arr\)\{[^}]+(?:\{[^}]*\}[^}]*)*\}', SOMA, "somaFrete"),
]:
    m = re.search(pat, html)
    if m:
        html = html[:m.start()] + rep + html[m.end():]
        changes += 1
        print("OK", label)
    else:
        print("--", label, "nao encontrado")

pathlib.Path(r"C:\mfcrm\index.html").write_text(html, encoding="utf-8")
print(f"\n{changes} mudancas aplicadas em C:\\mfcrm\\index.html")
