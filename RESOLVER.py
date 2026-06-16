#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRIPT DEFINITIVO - MF Envios CRM
Execute em cmd.exe (NAO PowerShell):
  cd C:\mfcrm
  python RESOLVER.py
"""
import os, sys, shutil

BASE = r"C:\mfcrm"
os.chdir(BASE)

print("=== INICIANDO RESOLVER.py ===\n")

# PASSO 1: Deletar public/index.html que sobrescreve tudo
pub = os.path.join(BASE, "public", "index.html")
if os.path.exists(pub):
    os.remove(pub)
    print("[OK] Deletado public/index.html")
else:
    print("[OK] public/index.html nao existe (OK)")

# PASSO 2: Verificar se index.html esta correto
idx = os.path.join(BASE, "index.html")
with open(idx, "rb") as f:
    content = f.read()
if content.startswith(b'\xef\xbb\xbf'):
    content = content[3:]
txt = content.decode("utf-8")

ok = all([
    'tab-financeiro' in txt,
    'op-tab-clientes-fin' in txt,
    'op-view-clientes-fin' in txt,
    'selecionarPerfil' in txt,
    'renderKanban' in txt,
])

if not ok:
    print("[ERRO] index.html nao tem todos os elementos necessarios")
    print("  tab-financeiro:", 'tab-financeiro' in txt)
    print("  op-tab-clientes-fin:", 'op-tab-clientes-fin' in txt)
    print("  op-view-clientes-fin:", 'op-view-clientes-fin' in txt)
    print("  selecionarPerfil:", 'selecionarPerfil' in txt)
    sys.exit(1)

print("[OK] index.html verificado - todos os elementos presentes")

# PASSO 3: Remover chamada solta que trava o JS
if 'carregarClientesFin();\nfunction carregarClientesFin' in txt:
    txt = txt.replace(
        'carregarClientesFin();\nfunction carregarClientesFin',
        'function carregarClientesFin'
    )
    print("[OK] Removida chamada JS solta (carregarClientesFin)")
elif 'carregarClientesFin();\r\nfunction carregarClientesFin' in txt:
    txt = txt.replace(
        'carregarClientesFin();\r\nfunction carregarClientesFin',
        'function carregarClientesFin'
    )
    print("[OK] Removida chamada JS solta (carregarClientesFin)")
else:
    print("[OK] Chamada solta ja estava corrigida")

# PASSO 4: Salvar index.html limpo
with open(idx, "w", encoding="utf-8") as f:
    f.write(txt)
print("[OK] index.html salvo")

# PASSO 5: Git add + commit + push
print("\n=== FAZENDO PUSH ===")
os.system('git add -A')
os.system('git commit -m "fix definitivo: remove public/index.html, corrige JS"')
os.system('git push origin main')

print("\n=== PRONTO ===")
print("Agora va ao Render e clique em Manual Deploy")
print("Depois abra em aba anonima: mf-envios-crm.onrender.com")
