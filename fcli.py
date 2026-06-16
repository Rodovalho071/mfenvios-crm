import pathlib, re, urllib.request, json

html = urllib.request.urlopen("https://raw.githubusercontent.com/Rodovalho071/mfenvios-crm/main/index.html").read().decode("utf-8")
changes = 0

VIEW = """  <!-- CLIENTES FINANCEIRO -->
  <div id="op-view-clientes-fin" style="display:none;padding:16px">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
      <h3 style="margin:0;font-size:15px">\U0001f465 Clientes Cadastrados</h3>
      <button onclick="abrirModalCliente()" style="background:var(--orange);color:white;border:none;border-radius:6px;padding:8px 14px;font-size:13px;font-weight:700;cursor:pointer">+ Novo Cliente</button>
    </div>
    <input id="busca-cliente-fin" type="text" placeholder="Buscar por nome ou CNPJ/CPF..." oninput="renderClientesFin()" style="width:100%;background:var(--bg3);border:1px solid var(--border);border-radius:6px;color:var(--text);padding:8px 12px;font-size:13px;margin-bottom:12px;box-sizing:border-box">
    <div id="lista-clientes-fin"></div>
  </div>
  <div id="modal-cliente-fin" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.6);z-index:999;justify-content:center;align-items:center">
    <div style="background:var(--surface);border-radius:12px;padding:24px;width:100%;max-width:480px;max-height:90vh;overflow-y:auto">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
        <h3 style="margin:0;font-size:16px" id="modal-cliente-titulo">Novo Cliente</h3>
        <button onclick="fecharModalCliente()" style="background:none;border:none;color:var(--text2);font-size:20px;cursor:pointer">\u2715</button>
      </div>
      <div style="display:grid;gap:12px">
        <div><label style="display:block;font-size:11px;font-weight:600;color:var(--text2);margin-bottom:4px;text-transform:uppercase">Nome / Razao Social *</label><input id="cli-nome" type="text" placeholder="Nome completo" style="width:100%;background:var(--bg3);border:1px solid var(--border);border-radius:6px;color:var(--text);padding:8px 10px;font-size:13px;box-sizing:border-box"></div>
        <div><label style="display:block;font-size:11px;font-weight:600;color:var(--text2);margin-bottom:4px;text-transform:uppercase">CNPJ / CPF</label><input id="cli-cnpj" type="text" placeholder="00.000.000/0000-00" style="width:100%;background:var(--bg3);border:1px solid var(--border);border-radius:6px;color:var(--text);padding:8px 10px;font-size:13px;box-sizing:border-box"></div>
        <div><label style="display:block;font-size:11px;font-weight:600;color:var(--text2);margin-bottom:4px;text-transform:uppercase">Telefone</label><input id="cli-tel" type="text" placeholder="(00) 00000-0000" style="width:100%;background:var(--bg3);border:1px solid var(--border);border-radius:6px;color:var(--text);padding:8px 10px;font-size:13px;box-sizing:border-box"></div>
        <div><label style="display:block;font-size:11px;font-weight:600;color:var(--text2);margin-bottom:4px;text-transform:uppercase">Email</label><input id="cli-email" type="text" placeholder="email@empresa.com" style="width:100%;background:var(--bg3);border:1px solid var(--border);border-radius:6px;color:var(--text);padding:8px 10px;font-size:13px;box-sizing:border-box"></div>
        <div><label style="display:block;font-size:11px;font-weight:600;color:var(--text2);margin-bottom:4px;text-transform:uppercase">Endereco</label><input id="cli-end" type="text" placeholder="Rua, numero, cidade" style="width:100%;background:var(--bg3);border:1px solid var(--border);border-radius:6px;color:var(--text);padding:8px 10px;font-size:13px;box-sizing:border-box"></div>
        <div><label style="display:block;font-size:11px;font-weight:600;color:var(--text2);margin-bottom:4px;text-transform:uppercase">Observacoes</label><textarea id="cli-obs" rows="3" style="width:100%;background:var(--bg3);border:1px solid var(--border);border-radius:6px;color:var(--text);padding:8px 10px;font-size:13px;box-sizing:border-box;resize:vertical"></textarea></div>
      </div>
      <div style="display:flex;gap:8px;margin-top:16px;justify-content:flex-end">
        <button onclick="fecharModalCliente()" style="background:var(--surface2);color:var(--text);border:none;border-radius:6px;padding:9px 18px;font-size:13px;cursor:pointer">Cancelar</button>
        <button onclick="salvarClienteFin()" style="background:var(--orange);color:white;border:none;border-radius:6px;padding:9px 18px;font-size:13px;font-weight:700;cursor:pointer">\u2714 Salvar</button>
      </div>
    </div>
  </div>"""

JS = """
var clientesFin=[];var clienteEditandoFin=null;
function carregarClientesFin(){return fetch('/clientes').then(function(r){return r.json();}).then(function(d){clientesFin=Array.isArray(d)?d:[];renderClientesFin();}).catch(function(){clientesFin=JSON.parse(localStorage.getItem('crm-clientes-fin')||'[]');renderClientesFin();});}
function salvarClientesFinLocal(){localStorage.setItem('crm-clientes-fin',JSON.stringify(clientesFin));}
function renderClientesFin(){var b=(document.getElementById('busca-cliente-fin')||{}).value||'';b=b.toLowerCase();var l=clientesFin.filter(function(c){return !b||(c.nome||'').toLowerCase().includes(b)||(c.cnpj||'').includes(b);});var el=document.getElementById('lista-clientes-fin');if(!el)return;if(!l.length){el.innerHTML='<div style="text-align:center;color:var(--text3);padding:32px;font-size:13px">Nenhum cliente encontrado.</div>';return;}el.innerHTML=l.map(function(c){var vc=vendas.filter(function(v){return v.cliente===c.nome;});var tc=vc.reduce(function(s,v){return s+parseMoeda(v.valor||0);},0);return '<div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:14px 16px;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center"><div><div style="font-weight:700;font-size:14px">'+c.nome+'</div>'+(c.cnpj?'<div style="font-size:12px;color:var(--text3)">'+c.cnpj+'</div>':'')+(c.tel?'<div style="font-size:12px;color:var(--text3)">'+c.tel+'</div>':'')+(c.email?'<div style="font-size:12px;color:var(--text3)">'+c.email+'</div>':'')+(tc?'<div style="font-size:12px;color:var(--green);font-weight:600">Total: R$ '+tc.toLocaleString("pt-BR",{minimumFractionDigits:2})+'</div>':'')+'</div><div style="display:flex;gap:8px"><button onclick="editarClienteFin(\''+c.id+'\')" style="background:var(--surface2);color:var(--text);border:none;border-radius:6px;padding:6px 12px;font-size:12px;cursor:pointer">\u270f\ufe0f</button><button onclick="deletarClienteFin(\''+c.id+'\')" style="background:rgba(239,68,68,.15);color:#ef4444;border:none;border-radius:6px;padding:6px 12px;font-size:12px;cursor:pointer">\U0001f5d1\ufe0f</button></div></div>';}).join('');}
function abrirModalCliente(id){clienteEditandoFin=id||null;['cli-nome','cli-cnpj','cli-tel','cli-email','cli-end','cli-obs'].forEach(function(f){var e=document.getElementById(f);if(e)e.value='';});if(id){var c=clientesFin.find(function(x){return x.id===id;});if(c){document.getElementById('modal-cliente-titulo').textContent='Editar Cliente';document.getElementById('cli-nome').value=c.nome||'';document.getElementById('cli-cnpj').value=c.cnpj||'';document.getElementById('cli-tel').value=c.tel||'';document.getElementById('cli-email').value=c.email||'';document.getElementById('cli-end').value=c.end||'';document.getElementById('cli-obs').value=c.obs||'';}}else{document.getElementById('modal-cliente-titulo').textContent='Novo Cliente';}document.getElementById('modal-cliente-fin').style.display='flex';}
function fecharModalCliente(){document.getElementById('modal-cliente-fin').style.display='none';}
function salvarClienteFin(){var nome=document.getElementById('cli-nome').value.trim();if(!nome){alert('Nome obrigatorio!');return;}var obj={id:clienteEditandoFin||(Date.now().toString(36)+Math.random().toString(36).slice(2,6)),nome:nome,cnpj:document.getElementById('cli-cnpj').value.trim(),tel:document.getElementById('cli-tel').value.trim(),email:document.getElementById('cli-email').value.trim(),end:document.getElementById('cli-end').value.trim(),obs:document.getElementById('cli-obs').value.trim(),ts:Date.now()};if(clienteEditandoFin){var idx=clientesFin.findIndex(function(c){return c.id===clienteEditandoFin;});if(idx>=0)clientesFin[idx]=obj;fetch('/clientes/'+obj.id,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(obj)}).catch(function(){});}else{clientesFin.push(obj);fetch('/clientes',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(obj)}).catch(function(){});}salvarClientesFinLocal();fecharModalCliente();renderClientesFin();if(typeof atualizarDatalistClientes==='function')atualizarDatalistClientes();if(typeof showToast==='function')showToast('Cliente salvo: '+nome);}
function editarClienteFin(id){abrirModalCliente(id);}
function deletarClienteFin(id){if(!confirm('Excluir este cliente?'))return;clientesFin=clientesFin.filter(function(c){return c.id!==id;});fetch('/clientes/'+id,{method:'DELETE'}).catch(function(){});salvarClientesFinLocal();renderClientesFin();}
"""

# 1. Aba
m = re.search(r'<div class="tab" id="op-tab-financeiro"[^>]+>[^<]+</div>', html)
if m:
    html = html[:m.end()] + '\n    <div class="tab" id="op-tab-clientes-fin" onclick="opTab(\'clientes-fin\')" style="border-bottom:3px solid transparent;padding:8px 16px;cursor:pointer;font-size:13px;font-weight:600">\U0001f465 Clientes</div>' + html[m.end():]
    changes+=1; print("OK aba")

# 2. View
if "<!-- MODAL NFSe -->" in html:
    html = html.replace("  <!-- MODAL NFSe -->", VIEW+"\n\n  <!-- MODAL NFSe -->", 1); changes+=1; print("OK view")

# 3. JS
for end_tag in ["</script>\n</body>", "</script>\n\n</body>"]:
    if end_tag in html:
        html = html.replace(end_tag, JS+"\n"+end_tag, 1); changes+=1; print("OK js"); break

# 4. opTab
if "function opTab(tab) {" in html:
    html = html.replace("function opTab(tab) {", "function opTab(tab) {\n  if(tab==='clientes-fin'){carregarClientesFin();}", 1); changes+=1; print("OK optab")

pathlib.Path(r"C:\mfcrm\index.html").write_text(html, encoding="utf-8")
print(f"\n{changes} mudancas")
