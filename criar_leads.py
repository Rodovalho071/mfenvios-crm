import urllib.request
import json

BASE = "https://mf-envios-crm.onrender.com"

# Buscar mensagens de cada instancia
def get_msgs(instance):
    url = f"{BASE}/messages?instance={instance}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

# Buscar leads existentes
def get_leads():
    url = f"{BASE}/kanban"
    with urllib.request.urlopen(url) as r:
        data = json.loads(r.read())
        return data.get('cards', [])

# Criar lead
def criar_lead(lead):
    data = json.dumps(lead).encode('utf-8')
    req = urllib.request.Request(
        f"{BASE}/kanban-import",
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

import random, time

def now_id():
    return hex(int(time.time()*1000))[2:] + hex(random.randint(0, 65535))[2:]

# Mapa instancia -> agente
INSTANCIA_AGENTE = {
    'mfenvios': 'Beatriz',
    'mfenvios-davi': 'Davi'
}

leads = get_leads()
print(f"Leads existentes: {len(leads)}")

# Indexar leads por (tel, agent)
existentes = set()
for l in leads:
    tel = l.get('tel') or l.get('phone') or ''
    agent = l.get('agent') or l.get('perfil') or ''
    if tel and agent:
        existentes.add((tel.strip(), agent.strip()))

print(f"Pares (tel, agent) existentes: {len(existentes)}")

criados = 0
for instancia, agente in INSTANCIA_AGENTE.items():
    msgs = get_msgs(instancia)
    print(f"\nInstancia {instancia}: {len(msgs)} mensagens")
    
    # Agrupar por phone, pegar primeira mensagem de cada
    vistos = {}
    for m in reversed(msgs):  # reversed = mais antigas primeiro
        phone = m.get('phone', '').strip()
        nome = m.get('name', 'Desconhecido')
        if not phone:
            continue
        if m.get('fromBot'):
            continue
        if phone not in vistos:
            vistos[phone] = {'name': nome, 'phone': phone, 'ts': m.get('ts', 0)}
    
    print(f"  Contatos unicos: {len(vistos)}")
    
    for phone, info in vistos.items():
        chave = (phone, agente)
        if chave in existentes:
            continue
        
        novo_lead = {
            'id': now_id(),
            'name': info['name'],
            'tel': phone,
            'phone': phone,
            'stage': 'Primeiro contato',
            'coluna': 'Novo Lead',
            'agent': agente,
            'perfil': agente,
            'instance': instancia,
            'source': 'whatsapp',
            'ts': info['ts'],
            'followups': [],
            'history': []
        }
        
        try:
            criar_lead(novo_lead)
            existentes.add(chave)
            criados += 1
            print(f"  + Lead criado: {info['name']} ({phone}) -> {agente}")
        except Exception as e:
            print(f"  ! Erro ao criar lead {info['name']}: {e}")

print(f"\nTotal criados: {criados}")
