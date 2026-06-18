with open('server.js', 'r', encoding='utf-8') as f:
    s = f.read()

old = """app.put('/kanban/:id',async function(req,res){
  const lead=Object.assign({},req.body,{id:req.params.id});
  try{
    if(kanbanCol){ await kanbanCol.updateOne({id:req.params.id},{$set:lead},{upsert:true}); }
    else{ const i=memKanban.cards.findIndex(c=>c.id===req.params.id); if(i>=0) memKanban.cards[i]=lead; else memKanban.cards.push(lead); }
    res.json({ok:true});
  }catch(e){res.status(500).json({error:e.message});}
});"""

new = """app.put('/kanban/:id',async function(req,res){
  const body=Object.assign({},req.body);
  delete body._id; // remover _id do MongoDB se vier no body
  const lead=Object.assign({},body,{id:req.params.id});
  try{
    if(kanbanCol){
      await kanbanCol.updateOne({id:req.params.id},{$set:lead},{upsert:true});
    } else {
      const i=memKanban.cards.findIndex(c=>c.id===req.params.id);
      if(i>=0) memKanban.cards[i]=Object.assign({},memKanban.cards[i],lead);
      else memKanban.cards.push(lead);
    }
    res.json({ok:true});
  }catch(e){console.error('[PUT kanban]',e.message);res.status(500).json({error:e.message});}
});"""

if old in s:
    s = s.replace(old, new)
    with open('server.js', 'w', encoding='utf-8') as f:
        f.write(s)
    print('OK - PUT /kanban/:id corrigido')
    print('git add server.js && git commit -m "fix: PUT kanban remove _id" && git push origin main')
else:
    print('X - nao encontrado')
