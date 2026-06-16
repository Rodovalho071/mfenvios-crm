#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RESTAURACAO LIMPA - MF Envios CRM
Execute em cmd.exe: python RESTAURAR.py
Pasta: C:\mfcrm
"""
import os, sys

BASE = r"C:\mfcrm"
os.chdir(BASE)
print("=== RESTAURACAO LIMPA ===\n")

# 1. Deletar public/index.html que sobrescreve o arquivo no build
pub = os.path.join(BASE, "public", "index.html")
if os.path.exists(pub):
    os.remove(pub)
    print("[OK] Deletado public/index.html (causava sobrescrita no deploy)")
else:
    print("[OK] public/index.html nao existe")

# 2. Verificar index.html
idx = os.path.join(BASE, "index.html")
with open(idx, 'rb') as f:
    content = f.read()
if content.startswith(b'\xef\xbb\xbf'):
    content = content[3:]
txt = content.decode('utf-8')

checks = {
    'selecionarPerfil (login)': 'selecionarPerfil' in txt,
    'renderKanban (funil)': 'renderKanban' in txt,
    'op-tab-tarefas (operacional)': 'op-tab-tarefas' in txt,
    'carregarVendas (financeiro)': 'carregarVendas' in txt,
    'SEM erro formatMoeda': '});});\r\n});\r\n}' not in txt and '});});\n});\n}' not in txt,
    'SEM carregarClientesFin solta': 'carregarClientesFin();\nfunction' not in txt and 'carregarClientesFin();\r\nfunction' not in txt,
}

ok = True
for desc, result in checks.items():
    status = "[OK]" if result else "[ERRO]"
    print(f"{status} {desc}")
    if not result:
        ok = False

if not ok:
    print("\n[ATENCAO] Arquivo com problemas. Abortando.")
    sys.exit(1)

print("\n[OK] index.html verificado\n")

# 3. Git push
os.system('git add -A')
r = os.system('git commit -m "restauracao: index limpo sem bugs JS"')
if r != 0:
    print("[INFO] Nada mudou no git (arquivo ja estava correto)")
os.system('git push origin main')

print("\n=== PRONTO ===")
print("1. Va ao Render: https://dashboard.render.com")
print("2. Clique em Manual Deploy")  
print("3. Aguarde 'Your service is live'")
print("4. Abra em aba anonima (Ctrl+Shift+N): mf-envios-crm.onrender.com")
