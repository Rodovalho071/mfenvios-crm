import base64, os, sys

# Ler o index.html atual
path = r'C:\mfcrm\index.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

original = c
erros = []

# === FIX 1: opTab - corrigir display:'' para display:'block' e adicionar color reset ===
old1 = """function opTab(tab) {
  opCurrentTab = tab;
  ['tarefas','fretes','agenda','docs'].forEach(function(t){
    var v=document.getElementById('op-view-'+t);
    if(v) v.style.display='none';
    var el=document.getElementById('op-tab-'+t);
    if(el){el.style.borderBottomColor='transparent';el.style.color='';}
  });
  ['nfse'].forEach(function(t){
    var c=document.getElementById('op-content-'+t);
    if(c) c.style.display='none';
    var el=document.getElementById('op-tab-'+t);
    if(el){el.style.borderBottomColor='transparent';el.style.color='';}
  });
  if(['tarefas','fretes','agenda','docs'].indexOf(tab)>=0){
    var v=document.getElementById('op-view-'+tab);
    if(v) v.style.display='';
  } else {
    var c=document.getElementById('op-content-'+tab);
    if(c) c.style.display='block';
  }
  var active=document.getElementById('op-tab-'+tab);
  if(active){active.style.borderBottomColor='var(--orange)';active.style.color='var(--orange)';}
  if(tab==='tarefas') loadTarefas();
  if(tab==='fretes') loadFretes();
  if(tab==='agenda') loadAgenda();
  if(tab==='docs') loadDocs();
  if(tab==='nfse'&&typeof renderNFSeLeads==='function') renderNFSeLeads();
}"""
new1 = """function opTab(tab) {
  opCurrentTab = tab;
  ['tarefas','fretes','agenda','docs'].forEach(function(t){
    var v=document.getElementById('op-view-'+t);
    if(v) v.style.display='none';
    var el=document.getElementById('op-tab-'+t);
    if(el){el.style.borderBottomColor='transparent';el.style.color='var(--text2)';}
  });
  ['nfse'].forEach(function(t){
    var c=document.getElementById('op-content-'+t);
    if(c) c.style.display='none';
    var el=document.getElementById('op-tab-'+t);
    if(el){el.style.borderBottomColor='transparent';el.style.color='var(--text2)';}
  });
  if(['tarefas','fretes','agenda','docs'].indexOf(tab)>=0){
    var v=document.getElementById('op-view-'+tab);
    if(v) v.style.display='block';
  } else {
    var c=document.getElementById('op-content-'+tab);
    if(c) c.style.display='block';
  }
  var active=document.getElementById('op-tab-'+tab);
  if(active){active.style.borderBottomColor='var(--orange)';active.style.color='var(--orange)';}
  if(tab==='tarefas') loadTarefas();
  if(tab==='fretes') loadFretes();
  if(tab==='agenda') loadAgenda();
  if(tab==='docs') loadDocs();
  if(tab==='nfse'&&typeof renderNFSeLeads==='function') renderNFSeLeads();
}"""
if old1 in c:
    c = c.replace(old1, new1, 1)
    print('[OK] Fix 1: opTab display corrigido')
else:
    erros.append('Fix 1 nao encontrado')

# === FIX 2: Remover segunda declaracao opTab ===
old2 = """function opTab(tab) {
  document.querySelectorAll('[id^="op-tab-"]').forEach(function(t) {
    t.style.borderBottomColor = 'transparent';
    t.style.color = 'var(--text2)';
  });
  document.querySelectorAll('[id^="op-content-"]').forEach(function(c) { c.style.display = 'none'; });
  var tabEl = document.getElementById('op-tab-' + tab);
  var contEl = document.getElementById('op-content-' + tab);
  if(tabEl) { tabEl.style.borderBottomColor = 'var(--orange)'; tabEl.style.color = 'var(--orange)'; }
  if(contEl) { contEl.style.display = 'block'; }
  if(tab === 'nfse') renderNFSeLeads();
  if(tab === 'financeiro') { renderFinanceiro(); renderFinLeadsProntos(); }
}"""
new2 = """// opTab duplicado removido"""
if old2 in c:
    c = c.replace(old2, new2, 1)
    print('[OK] Fix 2: opTab duplicado removido')
else:
    erros.append('Fix 2 nao encontrado')

# === FIX 3: showView - inicializar operacional com tarefas ===
old3 = "if(v==='financeiro'){carregarVendas().then(function(){renderFinanceiro();});}"
new3 = "if(v==='financeiro'){carregarVendas().then(function(){renderFinanceiro();});}if(v==='operacional'){opTab('tarefas');}"
if old3 in c:
    c = c.replace(old3, new3, 1)
    print('[OK] Fix 3: showView operacional init')
else:
    erros.append('Fix 3 nao encontrado')

# === FIX 4: Mover op-content-nfse para dentro de view-operacional ===
nfse_marker = '<!-- NFSe SUB-TAB -->'
nfse_block_end = '  </div>\n\n  <!-- MODAL NFSe -->'
nfse_fora = nfse_marker in c and c.find(nfse_marker) > c.find('</div>\n<div class="view" id="view-financeiro"')

if nfse_fora:
    start = c.find(nfse_marker)
    end = c.find(nfse_block_end)
    if end != -1:
        nfse_block = c[start:end+8]
        c = c[:start] + '\n  <!-- MODAL NFSe -->' + c[end+len('  </div>\n\n  <!-- MODAL NFSe -->'):]
        # Inserir dentro de view-operacional
        insert_marker = '\n</div>\n<div class="view" id="view-financeiro"'
        ip = c.find(insert_marker)
        if ip != -1:
            c = c[:ip] + '\n\n  ' + nfse_block + c[ip:]
            print('[OK] Fix 4: op-content-nfse movido para dentro de view-operacional')
        else:
            erros.append('Fix 4: marcador de insercao nao encontrado')
    else:
        erros.append('Fix 4: fim do bloco nfse nao encontrado')
else:
    print('[OK] Fix 4: op-content-nfse ja esta correto (ou nao precisa mover)')

# === FIX 5: Borda vermelha para cotacao/anuncio ===
old5 = "      const hasFu=lead.followups?.some(f=>!f.done);\n      const card=document.createElement('div');card.className='card';"
new5 = """      const hasFu=lead.followups?.some(f=>!f.done);
      const textoObs=(lead.obs||'').toLowerCase();
      const palavrasCotacao=['cotacao','cotacao','anuncio','anuncio','tabela','quanto fica','quanto custa','me passa','me manda','preciso enviar','quero enviar','valor do frete','preco do frete'];
      const isAnuncio=palavrasCotacao.some(function(p){return textoObs.includes(p);});
      const card=document.createElement('div');card.className='card';
      if(isAnuncio) card.style.borderColor='var(--red)';"""
if old5 in c:
    c = c.replace(old5, new5, 1)
    print('[OK] Fix 5: borda vermelha cotacao')
else:
    erros.append('Fix 5 nao encontrado')

# === FIX 6: sincronizarLeadsServidor - servidor tem prioridade ===
old6 = """      serverLeads.forEach(function(sl){
        var local = leads.find(function(l){ return l.id === sl.id; });
        if(!local) {
          leads.push(sl);
        }
      });"""
new6 = """      serverLeads.forEach(function(sl){
        var idx = leads.findIndex(function(l){ return l.id === sl.id; });
        if(idx < 0) {
          leads.push(sl);
        } else {
          leads[idx] = Object.assign({}, leads[idx], sl);
        }
      });"""
if old6 in c:
    c = c.replace(old6, new6, 1)
    print('[OK] Fix 6: sincronizacao servidor tem prioridade')
else:
    erros.append('Fix 6 nao encontrado')

# === FIX 7: autoPreencherClienteFin - preencher endereco ===
old7 = """function autoPreencherClienteFin(nome) {
  if(!nome || !window.clientesFin) return;
  var cli = (window.clientesFin||[]).find(function(c){ return c.nome === nome; });
  if(!cli) return;
  var cnpj = document.getElementById('fin-cnpj');
  if(cnpj && cli.cnpj) cnpj.value = cli.cnpj;
}"""
new7 = """function autoPreencherClienteFin(nome) {
  if(!nome) return;
  var fontes = (window.clientesFin||[]);
  var cli = fontes.find(function(c){ return (c.nome||c.razao||c.fantasia||'') === nome; });
  if(!cli) cli = fontes.find(function(c){ return (c.nome||c.razao||c.fantasia||'').toLowerCase().includes(nome.toLowerCase()); });
  if(!cli) return;
  var cnpj = document.getElementById('fin-cnpj');
  if(cnpj && (cli.cnpj||cli.cpf)) cnpj.value = cli.cnpj||cli.cpf||'';
  var end = '';
  if(cli.logradouro) {
    end = (cli.logradouro||'') + (cli.numero?', '+cli.numero:'') +
          (cli.comp?' '+cli.comp:'') + (cli.bairro?' - '+cli.bairro:'') +
          (cli.cidade?' - '+cli.cidade:'') + (cli.estado?' / '+cli.estado:'') +
          (cli.cep?' CEP: '+cli.cep:'');
  } else if(cli.endereco) { end = cli.endereco; }
  var endEl = document.getElementById('fin-endereco');
  if(endEl && end) endEl.value = end.trim();
}"""
if old7 in c:
    c = c.replace(old7, new7, 1)
    print('[OK] Fix 7: autoPreencherClienteFin com endereco')
else:
    erros.append('Fix 7 nao encontrado')

# === FIX 8: overflow-y em view-operacional ===
old8 = '<div class="view" id="view-operacional" style="padding:20px;max-width:1100px;margin:0 auto">'
new8 = '<div class="view" id="view-operacional" style="padding:20px;max-width:1100px;margin:0 auto;overflow-y:auto;">'
if old8 in c:
    c = c.replace(old8, new8, 1)
    print('[OK] Fix 8: overflow-y operacional')
else:
    erros.append('Fix 8 nao encontrado (pode ja estar correto)')

# Resultado
print()
if erros:
    print('ATENCAO - nao encontrados:')
    for e in erros: print(' -', e)
else:
    print('Todos os fixes aplicados com sucesso!')

if c != original:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)
    print('Arquivo salvo:', path)
else:
    print('AVISO: nenhuma alteracao foi feita no arquivo')
