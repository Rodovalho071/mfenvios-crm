with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old = """function saveLeads(){
  updateStats();
  // Salvar cada lead no MongoDB (fonte principal)
  leads.forEach(function(lead){
    fetch('/kanban-import',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(lead)}).catch(function(){});
  });
}"""

new = """function saveLeads(){
  updateStats();
  // Salvar cada lead no MongoDB via PUT (upsert seguro)
  leads.forEach(function(lead){
    fetch('/kanban/'+lead.id,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(lead)}).catch(function(){});
  });
}"""

if old in html:
    html = html.replace(old, new)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('OK - saveLeads usa PUT agora')
    print('git add index.html && git commit -m "fix: saveLeads usa PUT" && git push origin main')
else:
    print('X - saveLeads nao encontrado')
