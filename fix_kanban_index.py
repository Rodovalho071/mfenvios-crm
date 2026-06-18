with open('server.js', 'r', encoding='utf-8') as f:
    s = f.read()

# Trocar índice unique de phone para id
old1 = "    await kanbanCol.createIndex({ phone: 1 }, { unique: true });"
new1 = "    await kanbanCol.createIndex({ id: 1 }, { unique: true });"

# Trocar upsert de phone para id
old2 = "  if(kanbanCol){ try{ await kanbanCol.updateOne({phone:card.phone},{$set:card,$setOnInsert:{ts:Date.now()}},{upsert:true}); }catch(e){} }"
new2 = "  if(kanbanCol){ try{ await kanbanCol.updateOne({id:card.id},{$set:card,$setOnInsert:{ts:Date.now()}},{upsert:true}); }catch(e){console.error('[KANBAN]',e.message);} }"

ok = True
if old1 in s:
    s = s.replace(old1, new1)
    print("OK 1/2 - indice kanban trocado de phone para id")
else:
    print("X 1/2 - indice nao encontrado")
    ok = False

if old2 in s:
    s = s.replace(old2, new2)
    print("OK 2/2 - upsert kanban trocado de phone para id")
else:
    print("X 2/2 - upsert nao encontrado")
    ok = False

if ok:
    with open('server.js', 'w', encoding='utf-8') as f:
        f.write(s)
    print("\nserver.js atualizado!")
    print("IMPORTANTE: va no MongoDB Atlas e apague o indice 'phone_1' da colecao kanban")
    print("Ou rode: git add server.js && git commit -m 'fix: kanban index por id' && git push origin main")
