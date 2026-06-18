with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old_classif = "    var nomeEhNumero = /^[\\\\d\\\\s\\\\+\\\\-\\\\(\\\\)]+$/.test((name||'').trim());\n    var tipoContato = nomeEhNumero ? 'novo' : 'salvo';"

new_classif = """    var _nome = (name||'').trim();
    var _nomeEhNumero = /^[\\d\\s\\+\\-\\(\\)]+$/.test(_nome);
    var _palavrasNaoSalvo = ['telefone','celular','número','numero','contato','unknown','desconhecido','sem nome','whatsapp'];
    var _nomeEhDesconhecido = _palavrasNaoSalvo.some(function(p){return _nome.toLowerCase().includes(p);});
    var tipoContato = (_nomeEhNumero || _nomeEhDesconhecido) ? 'novo' : 'salvo';"""

if old_classif in html:
    html = html.replace(old_classif, new_classif)
    print("OK 1/2 - classificação wppToLead melhorada")
else:
    print("X 1/2 - wppToLead nao encontrado")
    # Tentar versão alternativa
    old2 = "    var nomeEhNumero = /^[\\d\\s\\+\\-\\(\\)]+$/.test((name||'').trim());\n    var tipoContato = nomeEhNumero ? 'novo' : 'salvo';"
    if old2 in html:
        new2 = """    var _nome = (name||'').trim();
    var _nomeEhNumero = /^[\\d\\s\\+\\-\\(\\)]+$/.test(_nome);
    var _palavrasNaoSalvo = ['telefone','celular','número','numero','contato','unknown','desconhecido','sem nome','whatsapp'];
    var _nomeEhDesconhecido = _palavrasNaoSalvo.some(function(p){return _nome.toLowerCase().includes(p);});
    var tipoContato = (_nomeEhNumero || _nomeEhDesconhecido) ? 'novo' : 'salvo';"""
        html = html.replace(old2, new2)
        print("OK 1/2 - classificação wppToLead melhorada (v2)")

# Mesma melhoria na classificação via IA
old_ia = "  var _nomeEhNumeroIA=/^[\\\\d\\\\s\\\\+\\\\-\\\\(\\\\)]+$/.test(_nomeIA.trim());\n  var _tipoContatoIA=_nomeEhNumeroIA?'novo':'salvo';"

new_ia = """  var _nomeEhNumeroIA=/^[\\d\\s\\+\\-\\(\\)]+$/.test(_nomeIA.trim());
  var _palavrasNaoSalvoIA=['telefone','celular','número','numero','contato','unknown','desconhecido','sem nome'];
  var _nomeDesconhecidoIA=_palavrasNaoSalvoIA.some(function(p){return _nomeIA.toLowerCase().includes(p);});
  var _tipoContatoIA=(_nomeEhNumeroIA||_nomeDesconhecidoIA)?'novo':'salvo';"""

if old_ia in html:
    html = html.replace(old_ia, new_ia)
    print("OK 2/2 - classificação IA melhorada")
else:
    old_ia2 = "  var _nomeEhNumeroIA=/^[\\d\\s\\+\\-\\(\\)]+$/.test(_nomeIA.trim());\n  var _tipoContatoIA=_nomeEhNumeroIA?'novo':'salvo';"
    if old_ia2 in html:
        html = html.replace(old_ia2, new_ia)
        print("OK 2/2 - classificação IA melhorada (v2)")
    else:
        print("X 2/2 - classificação IA nao encontrada")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("\ngit add index.html && git commit -m 'fix: classificacao contato melhorada' && git push origin main")
