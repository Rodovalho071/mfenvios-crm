import subprocess,sys
subprocess.run([sys.executable,"-m","pip","install","pymongo","--break-system-packages","-q"],capture_output=True)
from pymongo import MongoClient
uri="mongodb+srv://contato_db_user:MFenvios2026@cluster0.6bauzwx.mongodb.net/mfenvios?retryWrites=true&w=majority"
client=MongoClient(uri,serverSelectionTimeoutMS=10000)
col=client["mfenvios"]["kanban"]
# Buscar leads que NAO sao do Davi (sao da Beatriz)
leads=list(col.find({"agent":{"$ne":"Davi"}},{"_id":0}))
print("Leads Beatriz encontrados:",len(leads))
import json
export={"leads":leads,"activity":[],"exportedAt":"2026-06-09T00:00:00.000Z"}
with open("leads_beatriz_backup.json","w",encoding="utf-8") as f:
    json.dump(export,f,ensure_ascii=False,indent=2)
print("[OK] Arquivo leads_beatriz_backup.json gerado!")
print("Agora importe esse arquivo no CRM pelo botao Importar.")