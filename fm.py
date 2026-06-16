import pathlib, re
f = pathlib.Path(r"C:\mfcrm\index.html")
html = f.read_text(encoding="utf-8")
changes = 0

# Quando preenche o valor do lead no modal, aplica a mascara
OLD1 = "      if(ev) ev.value = (lead.valorFrete||'').replace('R$','').trim();"
NEW1 = """      if(ev) {
        var vf = parseMoeda(lead.valorFrete||0);
        var digits = Math.round(vf*100).toString();
        while(digits.length<3) digits='0'+digits;
        var i=digits.slice(0,-2)||'0', dc=digits.slice(-2);
        i=i.replace(/\\B(?=(\\d{3})+(?!\\d))/g,'.');
        ev.value = i+','+dc;
        ev.dataset.valor = vf.toFixed(2);
      }"""
if OLD1 in html:
    html = html.replace(OLD1, NEW1, 1); changes+=1; print("OK abrirModalVenda")
else:
    print("-- abrirModalVenda nao encontrado")

# Quando edita venda existente, tambem aplica mascara
OLD2 = "  document.getElementById('fin-valor').value = v.valor || '';"
NEW2 = """  var evEdit = document.getElementById('fin-valor');
  if(evEdit) {
    var vEdit = parseMoeda(v.valor||0);
    var dEdit = Math.round(vEdit*100).toString();
    while(dEdit.length<3) dEdit='0'+dEdit;
    var iE=dEdit.slice(0,-2)||'0', dcE=dEdit.slice(-2);
    iE=iE.replace(/\\B(?=(\\d{3})+(?!\\d))/g,'.');
    evEdit.value = iE+','+dcE;
    evEdit.dataset.valor = vEdit.toFixed(2);
  }"""
if OLD2 in html:
    html = html.replace(OLD2, NEW2, 1); changes+=1; print("OK editarVenda mascara")
else:
    print("-- editarVenda nao encontrado")

f.write_text(html, encoding="utf-8")
print(f"\n{changes} mudancas aplicadas")
