
import re
path = r'C:\mfcrm\index.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# FIX 1: abrirModalCadastro onclick - fix broken quotes
idx = c.find("abrirModalCadastro(")
while idx != -1:
    if 'c.id' in c[idx:idx+60]:
        end = c.find(')">', idx)
        if end != -1 and end - idx < 50:
            c = c[:idx] + "abrirModalCadastro('" + c.id + "')">" + c[end+3:]
            print('[OK] Fix 1: abrirModalCadastro onclick')
        break
    idx = c.find("abrirModalCadastro(", idx+1)

# FIX 2: deletarCadastro onclick
idx = c.find("deletarCadastro(")
while idx != -1:
    if 'c.id' in c[idx:idx+60]:
        end = c.find("')", idx)
        if end != -1 and end - idx < 50:
            c = c[:idx] + "deletarCadastro('" + c.id + "')" + c[end+2:]
            print('[OK] Fix 2: deletarCadastro onclick')
        break
    idx = c.find("deletarCadastro(", idx+1)

# FIX 3: CONTATOS_MF usando load antes de definicao
old3 = "const CONTATOS_MF = load('crm-contatos-mf', []);"
new3 = "var CONTATOS_MF = []; try { CONTATOS_MF = JSON.parse(localStorage.getItem('crm-contatos-mf')||'[]'); } catch(e) {}"
if old3 in c:
    c = c.replace(old3, new3, 1)
    print('[OK] Fix 3: CONTATOS_MF')
else:
    print('[SKIP] Fix 3')

# FIX 4: let perfilAtivo -> var
old4 = "let perfilAtivo = localStorage.getItem('crm-perfil') || null;"
if old4 in c:
    c = c.replace(old4, "var perfilAtivo = localStorage.getItem('crm-perfil') || null;", 1)
    print('[OK] Fix 4: perfilAtivo')
else:
    print('[SKIP] Fix 4')

# FIX 5: let verTodos -> var
if "let verTodos = false;" in c:
    c = c.replace("let verTodos = false;", "var verTodos = false;", 1)
    print('[OK] Fix 5: verTodos')
else:
    print('[SKIP] Fix 5')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('Arquivo salvo:', path)
