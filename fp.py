import pathlib, re, urllib.request

html = urllib.request.urlopen("https://raw.githubusercontent.com/Rodovalho071/mfenvios-crm/main/index.html").read().decode("utf-8")

# Substitui a parseMoeda corrompida (duplicada) pela versao limpa
PARSE_LIMPA = "function parseMoeda(v){if(v===null||v===undefined||v==='')return 0;if(typeof v==='number')return v;var s=v.toString().replace(/R[$]\\s*/g,'').replace(/\\s/g,'').trim();if(!s)return 0;if(s.indexOf(',')!==-1){s=s.replace(/[.]/g,'').replace(',','.');return parseFloat(s)||0;}if(s.indexOf('.')!==-1){var p=s.split('.');if(p.length===2&&p[1].length<=2)return parseFloat(s)||0;s=s.replace(/[.]/g,'');}return parseFloat(s)||0;}"

m = re.search(r'function parseMoeda\(v\)\{.+?\}(?=function|\n)', html, re.DOTALL)
if m:
    html = html[:m.start()] + PARSE_LIMPA + "\n" + html[m.end():]
    print("OK parseMoeda corrigida")
else:
    print("-- nao encontrada")

pathlib.Path(r"C:\mfcrm\index.html").write_text(html, encoding="utf-8")
print("Salvo!")
