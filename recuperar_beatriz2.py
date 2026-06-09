import subprocess,sys,json
subprocess.run([sys.executable,"-m","pip","install","pymongo","--break-system-packages","-q"],capture_output=True)
from pymongo import MongoClient
from datetime import datetime
uri="mongodb+srv://contato_db_user:MFenvios2026@cluster0.6bauzwx.mongodb.net/mfenvios?retryWrites=true&w=majority"
client=MongoClient(uri,serverSelectionTimeoutMS=10000)
db=client["mfenvios"]

# Buscar todas as mensagens do WhatsApp
msgs=list(db["messages"].find({},{"_id":0}).sort("ts",-1).limit(2000))
print("Mensagens encontradas:",len(msgs))

# Agrupar por phone
contatos={}
for m in msgs:
    phone=m.get("phone","").strip()
    if not phone or m.get("fromBot"): continue
    if phone not in contatos:
        contatos[phone]={"name":m.get("name","Desconhecido"),"phone":phone,"msgs":[],"lastTs":0}
    contatos[phone]["msgs"].append(m.get("text",""))
    if m.get("ts",0)>contatos[phone]["lastTs"]:
        contatos[phone]["lastTs"]=m.get("ts",0)
        contatos[phone]["name"]=m.get("name",contatos[phone]["name"])

# Buscar leads existentes no kanban (Beatriz e sem agente)
kanban_leads=list(db["kanban"].find({"agent":{"$ne":"Davi"}},{"_id":0}))
print("Leads kanban Beatriz:",len(kanban_leads))

# Criar leads a partir das mensagens, usando dados do kanban se existir
import random,string
def uid(): return "".join(random.choices(string.ascii_lowercase+string.digits,k=8))

leads=[]
for kl in kanban_leads:
    leads.append(kl)

# Adicionar contatos do WhatsApp que nao estao no kanban
phones_existentes={l.get("tel","").replace("+","").replace(" ","") for l in leads}
phones_existentes.update({l.get("phone","") for l in leads})

for phone,c in contatos.items():
    ph_clean=phone.replace("+","").replace(" ","")
    if ph_clean in phones_existentes: continue
    if phone in phones_existentes: continue
    ultima_msg=c["msgs"][0] if c["msgs"] else ""
    lead={
        "id":uid(),
        "name":c["name"],
        "tel":phone,
        "phone":phone,
        "stage":"Primeiro contato",
        "agent":"Beatriz",
        "source":"whatsapp",
        "material":"","origem":"","destino":"","rota":"",
        "volumes":"","peso":"","medidas":"",
        "valorNF":"","valorFrete":"","transportadora":"",
        "obs":ultima_msg[:200] if ultima_msg else "",
        "hot":False,
        "ts":c["lastTs"],
        "followups":[],"history":[]
    }
    leads.append(lead)

print("Total leads reconstruidos:",len(leads))

# Salvar arquivo para importar
export={"leads":leads,"activity":[],"exportedAt":"2026-06-09T00:00:00.000Z"}
with open("leads_beatriz_recuperados.json","w",encoding="utf-8") as f:
    json.dump(export,f,ensure_ascii=False,indent=2)
print("[OK] Arquivo leads_beatriz_recuperados.json gerado!")
print("Abra o CRM perfil Beatriz e clique em Importar para restaurar.")