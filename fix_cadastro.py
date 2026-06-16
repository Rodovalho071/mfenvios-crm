import sys

path = r'C:\mfcrm\index.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Remover view-cadastro duplicado (o segundo, linha ~2589)
# O segundo começa com a mesma string e vai ate o modal-cadastro duplicado
dup_marker = '\n<div class="view" id="view-cadastro" style="padding:20px;max-width:900px;margin:0 auto">'
first = c.find(dup_marker)
second = c.find(dup_marker, first + 1)
if second != -1:
    # Encontrar o fim do segundo view-cadastro + modal-cadastro duplicado
    # Procurar o proximo </div>\n</div>\n depois do segundo modal-cadastro
    modal_dup = c.find('\n<!-- MODAL CADASTRO -->', second)
    if modal_dup != -1:
        end_search = c.find('\n</div>\n</div>\n\n</body>', modal_dup)
        if end_search != -1:
            bloco_dup = c[second:end_search + len('\n</div>\n</div>')]
            c = c[:second] + c[second + len(bloco_dup):]
            print('[OK] Removido view-cadastro duplicado')
        else:
            # Tentar outro fim
            end_search2 = c.find('</body>', modal_dup)
            bloco_dup = c[second:end_search2]
            c = c[:second] + c[second + len(bloco_dup):]
            print('[OK] Removido view-cadastro duplicado (v2)')
    else:
        print('[SKIP] Modal cadastro duplicado nao encontrado')
else:
    print('[OK] Sem duplicado de view-cadastro')

# Injetar o JS do modulo Cadastro antes do fechamento do </script> principal
js_cadastro = """
// ═══════════════════════════════════════════
// MÓDULO CADASTRO DE CLIENTES
// ═══════════════════════════════════════════
var cadastros = [];
var cadastroEditandoId = null;

function carregarCadastro() {
  fetch('/clientes').then(function(r){ return r.json(); }).then(function(d){
    cadastros = Array.isArray(d) ? d : [];
    // Sincronizar com clientesFin tambem
    window.clientesFin = cadastros;
    renderCadastro();
  }).catch(function(){
    cadastros = JSON.parse(localStorage.getItem('crm-cadastros')||'[]');
    window.clientesFin = cadastros;
    renderCadastro();
  });
}

function renderCadastro() {
  var busca = (document.getElementById('cad-busca')||{}).value || '';
  var tipo = (document.getElementById('cad-tipo-filter')||{}).value || '';
  busca = busca.toLowerCase();
  var lista = cadastros.filter(function(c){
    var match = !busca || (c.razao||'').toLowerCase().includes(busca) ||
      (c.fantasia||'').toLowerCase().includes(busca) ||
      (c.cnpj||'').includes(busca) ||
      (c.cidade||'').toLowerCase().includes(busca);
    var matchTipo = !tipo || c.tipo === tipo;
    return match && matchTipo;
  });
  var el = document.getElementById('cadastro-lista');
  if(!el) return;
  if(!lista.length) {
    el.innerHTML = '<div style="text-align:center;padding:48px;color:var(--text3);font-size:14px;">Nenhum cliente cadastrado ainda.<br><br><button onclick="abrirModalCadastro(null)" style="background:var(--orange);color:white;border:none;border-radius:6px;padding:10px 20px;font-size:13px;font-weight:700;cursor:pointer;">+ Cadastrar primeiro cliente</button></div>';
    return;
  }
  el.innerHTML = lista.map(function(c){
    var doc = c.tipo==='pf' ? (c.cpf||'') : (c.cnpj||'');
    var cidade = [c.cidade, c.estado].filter(Boolean).join(' / ');
    return '<div style="background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:16px 20px;display:flex;align-items:center;gap:16px;margin-bottom:10px;cursor:pointer;" onclick="abrirModalCadastro(\''+c.id+'\')">' +
      '<div style="width:44px;height:44px;border-radius:50%;background:var(--blue-bg);color:var(--blue);display:flex;align-items:center;justify-content:center;font-size:16px;font-weight:700;flex-shrink:0;">' +
        (c.razao||c.fantasia||'?')[0].toUpperCase() +
      '</div>' +
      '<div style="flex:1;min-width:0;">' +
        '<div style="font-size:14px;font-weight:700;">' + (c.razao||c.fantasia||'Sem nome') + '</div>' +
        (c.fantasia && c.razao ? '<div style="font-size:12px;color:var(--text3);">' + c.fantasia + '</div>' : '') +
        '<div style="display:flex;gap:12px;margin-top:4px;flex-wrap:wrap;">' +
          (doc ? '<span style="font-size:11px;color:var(--text3);">📄 ' + doc + '</span>' : '') +
          (cidade ? '<span style="font-size:11px;color:var(--text3);">📍 ' + cidade + '</span>' : '') +
          (c.cel||c.tel ? '<span style="font-size:11px;color:var(--text3);">📱 ' + (c.cel||c.tel) + '</span>' : '') +
        '</div>' +
      '</div>' +
      '<div style="display:flex;gap:8px;flex-shrink:0;">' +
        '<button onclick="event.stopPropagation();deletarCadastro(\''+c.id+'\')" style="background:var(--red-bg);color:var(--red);border:1px solid var(--red-bg);border-radius:6px;padding:6px 10px;font-size:12px;cursor:pointer;">🗑</button>' +
      '</div>' +
    '</div>';
  }).join('');
}

function abrirModalCadastro(id) {
  cadastroEditandoId = id;
  var modal = document.getElementById('modal-cadastro');
  if(!modal) return;
  // Limpar campos
  ['cad-doc','cad-razao','cad-fantasia','cad-ie','cad-im','cad-cnae',
   'cad-cel','cad-tel','cad-email','cad-email-cob',
   'cad-cep','cad-estado','cad-cidade','cad-bairro','cad-logradouro','cad-numero','cad-comp','cad-obs'].forEach(function(fid){
    var el = document.getElementById(fid); if(el) el.value = '';
  });
  document.getElementById('cad-tipo-pj').checked = true;
  toggleCadTipo();
  if(id) {
    var cad = cadastros.find(function(x){ return x.id === id; });
    if(cad) {
      document.getElementById('cad-modal-titulo').textContent = 'Editar Cliente';
      if(cad.tipo==='pf') { document.getElementById('cad-tipo-pf').checked=true; toggleCadTipo(); }
      var set = function(fid,val){ var el=document.getElementById(fid); if(el&&val) el.value=val; };
      set('cad-doc', cad.cnpj||cad.cpf);
      set('cad-razao', cad.razao);
      set('cad-fantasia', cad.fantasia);
      set('cad-ie', cad.ie);
      set('cad-im', cad.im);
      set('cad-cnae', cad.cnae);
      set('cad-cel', cad.cel);
      set('cad-tel', cad.tel);
      set('cad-email', cad.email);
      set('cad-email-cob', cad.emailCob);
      set('cad-cep', cad.cep);
      set('cad-estado', cad.estado);
      set('cad-cidade', cad.cidade);
      set('cad-bairro', cad.bairro);
      set('cad-logradouro', cad.logradouro);
      set('cad-numero', cad.numero);
      set('cad-comp', cad.comp);
      set('cad-obs', cad.obs);
    }
  } else {
    document.getElementById('cad-modal-titulo').textContent = 'Novo Cliente';
  }
  modal.style.display = 'flex';
}

function fecharModalCadastro() {
  var modal = document.getElementById('modal-cadastro');
  if(modal) modal.style.display = 'none';
}

function toggleCadTipo() {
  var pj = document.getElementById('cad-tipo-pj');
  var label = document.getElementById('cad-doc-label');
  var input = document.getElementById('cad-doc');
  if(!pj || !label || !input) return;
  if(pj.checked) {
    label.textContent = 'CNPJ';
    input.placeholder = '00.000.000/0000-00';
  } else {
    label.textContent = 'CPF';
    input.placeholder = '000.000.000-00';
  }
}

function salvarCadastro() {
  var tipo = document.getElementById('cad-tipo-pj').checked ? 'pj' : 'pf';
  var doc = (document.getElementById('cad-doc')||{}).value||'';
  var razao = (document.getElementById('cad-razao')||{}).value||'';
  if(!razao.trim()) { alert('Preencha a Razão Social / Nome.'); return; }
  var obj = {
    id: cadastroEditandoId || (Date.now().toString(36)+Math.random().toString(36).slice(2,6)),
    tipo: tipo,
    cnpj: tipo==='pj' ? doc : '',
    cpf:  tipo==='pf' ? doc : '',
    razao: razao.trim(),
    nome: razao.trim(),
    fantasia: (document.getElementById('cad-fantasia')||{}).value||'',
    ie: (document.getElementById('cad-ie')||{}).value||'',
    im: (document.getElementById('cad-im')||{}).value||'',
    cnae: (document.getElementById('cad-cnae')||{}).value||'',
    cel: (document.getElementById('cad-cel')||{}).value||'',
    tel: (document.getElementById('cad-tel')||{}).value||'',
    email: (document.getElementById('cad-email')||{}).value||'',
    emailCob: (document.getElementById('cad-email-cob')||{}).value||'',
    cep: (document.getElementById('cad-cep')||{}).value||'',
    estado: (document.getElementById('cad-estado')||{}).value||'',
    cidade: (document.getElementById('cad-cidade')||{}).value||'',
    bairro: (document.getElementById('cad-bairro')||{}).value||'',
    logradouro: (document.getElementById('cad-logradouro')||{}).value||'',
    numero: (document.getElementById('cad-numero')||{}).value||'',
    comp: (document.getElementById('cad-comp')||{}).value||'',
    obs: (document.getElementById('cad-obs')||{}).value||'',
    ts: Date.now()
  };
  var idx = cadastros.findIndex(function(x){ return x.id === obj.id; });
  if(idx >= 0) {
    cadastros[idx] = obj;
    fetch('/clientes/'+obj.id, {method:'PUT', headers:{'Content-Type':'application/json'}, body:JSON.stringify(obj)}).catch(function(){});
  } else {
    cadastros.unshift(obj);
    fetch('/clientes', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(obj)}).catch(function(){});
  }
  localStorage.setItem('crm-cadastros', JSON.stringify(cadastros));
  window.clientesFin = cadastros;
  fecharModalCadastro();
  renderCadastro();
  if(typeof showToast==='function') showToast('Cliente salvo — '+obj.razao);
  else if(typeof toast==='function') toast('Cliente salvo — '+obj.razao);
}

function deletarCadastro(id) {
  var cad = cadastros.find(function(x){ return x.id===id; });
  if(!cad) return;
  if(!confirm('Excluir cliente "'+cad.razao+'"?')) return;
  cadastros = cadastros.filter(function(x){ return x.id!==id; });
  fetch('/clientes/'+id, {method:'DELETE'}).catch(function(){});
  localStorage.setItem('crm-cadastros', JSON.stringify(cadastros));
  renderCadastro();
  if(typeof showToast==='function') showToast('Cliente removido.');
}

function buscarCNPJ(cnpj) {
  cnpj = cnpj.replace(/\\D/g,'');
  if(cnpj.length !== 14) return;
  fetch('https://brasilapi.com.br/api/cnpj/v1/'+cnpj)
    .then(function(r){ return r.json(); })
    .then(function(d){
      if(d.razao_social) {
        var set = function(id,val){ var el=document.getElementById(id); if(el&&val) el.value=val; };
        set('cad-razao', d.razao_social);
        set('cad-fantasia', d.nome_fantasia||'');
        set('cad-cnae', d.cnae_fiscal||'');
        set('cad-cep', (d.cep||'').replace(/\\D/g,''));
        set('cad-logradouro', d.logradouro||'');
        set('cad-numero', d.numero||'');
        set('cad-comp', d.complemento||'');
        set('cad-bairro', d.bairro||'');
        set('cad-cidade', d.municipio||'');
        set('cad-estado', d.uf||'');
        set('cad-email', d.email||'');
        if(typeof showToast==='function') showToast('CNPJ encontrado — dados preenchidos!');
      }
    }).catch(function(){});
}

function buscarCEP(cep) {
  cep = cep.replace(/\\D/g,'');
  if(cep.length !== 8) return;
  fetch('https://viacep.com.br/ws/'+cep+'/json/')
    .then(function(r){ return r.json(); })
    .then(function(d){
      if(!d.erro) {
        var set = function(id,val){ var el=document.getElementById(id); if(el&&val) el.value=val; };
        set('cad-logradouro', d.logradouro||'');
        set('cad-bairro', d.bairro||'');
        set('cad-cidade', d.localidade||'');
        set('cad-estado', d.uf||'');
      }
    }).catch(function(){});
}
"""

# Inserir o JS antes do fechamento do </script> principal (antes de </script>\n\n\n<!-- OPERACIONAL VIEW -->)
marker = '</script>\n\n\n\n<!-- OPERACIONAL VIEW -->'
alt_marker = '</script>\n\n\n<!-- OPERACIONAL VIEW -->'

if marker in c:
    c = c.replace(marker, js_cadastro + '\n</script>\n\n\n\n<!-- OPERACIONAL VIEW -->', 1)
    print('[OK] JS Cadastro injetado')
elif alt_marker in c:
    c = c.replace(alt_marker, js_cadastro + '\n</script>\n\n\n<!-- OPERACIONAL VIEW -->', 1)
    print('[OK] JS Cadastro injetado (alt)')
else:
    # Tentar com qualquer variação
    import re
    m = re.search(r'</script>\s+<!-- OPERACIONAL VIEW -->', c)
    if m:
        c = c[:m.start()] + js_cadastro + '\n' + c[m.start():]
        print('[OK] JS Cadastro injetado (regex)')
    else:
        print('[ERRO] Marcador para injetar JS nao encontrado')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('Arquivo salvo:', path)
