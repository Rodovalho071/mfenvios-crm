import pathlib, re, urllib.request
html = urllib.request.urlopen("https://raw.githubusercontent.com/Rodovalho071/mfenvios-crm/main/index.html").read().decode("utf-8")
changes = 0

OLD1 = '<input id="fin-cliente" type="text" placeholder="Nome do cliente" style="width:100%;background:var(--bg3);border:1px solid var(--border);border-radius:6px;color:var(--text);padding:8px 10px;font-size:13px;">'
NEW1 = '<input id="fin-cliente" type="text" placeholder="Nome do cliente" list="fin-clientes-list" autocomplete="off" style="width:100%;background:var(--bg3);border:1px solid var(--border);border-radius:6px;color:var(--text);padding:8px 10px;font-size:13px;"><datalist id="fin-clientes-list"></datalist>'
OLD2 = '<input id="fin-cnpj" type="text" placeholder="00.000.000/0000-00" style="width:100%;background:var(--bg3);border:1px solid var(--border);border-radius:6px;color:var(--text);padding:8px 10px;font-size:13px;">'
NEW2 = '<input id="fin-cnpj" type="text" placeholder="00.000.000/0000-00" list="fin-cnpj-list" autocomplete="off" style="width:100%;background:var(--bg3);border:1px solid var(--border);border-radius:6px;color:var(--text);padding:8px 10px;font-size:13px;"><datalist id="fin-cnpj-list"></datalist>'
OLD3 = "function abrirModalVenda(leadId, leadNome, leadCnpj) {"
NEW3 = """function atualizarDatalistClientes() {
  var dl = document.getElementById('fin-clientes-list');
  var dlc = document.getElementById('fin-cnpj-list');
  if(!dl||!dlc) return;
  var vistos = {};
  dl.innerHTML = ''; dlc.innerHTML = '';
  vendas.forEach(function(v) {
    if(v.cliente && !vistos[v.cliente]) { vistos[v.cliente]=true; var o=document.createElement('option'); o.value=v.cliente; dl.appendChild(o); }
    if(v.cnpj) { var o2=document.createElement('option'); o2.value=v.cnpj; o2.label=v.cliente||''; dlc.appendChild(o2); }
  });
  leads.forEach(function(l) {
    if(l.nome && !vistos[l.nome]) { vistos[l.nome]=true; var o=document.createElement('option'); o.value=l.nome; dl.appendChild(o); }
  });
}
function abrirModalVenda(leadId, leadNome, leadCnpj) {"""
OLD4 = "document.getElementById('modal-financeiro').style.display = 'flex';"
NEW4 = "document.getElementById('modal-financeiro').style.display = 'flex'; atualizarDatalistClientes();"

for old, new, label in [(OLD1,NEW1,"datalist-cliente"),(OLD2,NEW2,"datalist-cnpj"),(OLD3,NEW3,"autocomplete-fn"),(OLD4,NEW4,"chama-datalist")]:
    if old in html: html=html.replace(old,new,1); changes+=1; print("OK",label)
    else: print("--",label)

pathlib.Path(r"C:\mfcrm\index.html").write_text(html, encoding="utf-8")
print(f"\n{changes} mudancas salvas")
