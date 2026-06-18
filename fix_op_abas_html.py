with open('index.html', 'r', encoding='utf-8') as f:
    h = f.read()

old = '  <!-- Sub-tabs -->\n  <div style="display:flex;gap:8px;margin-bottom:20px;border-bottom:1px solid var(--border);padding-bottom:0">\n    <div class="tab active" id="op-tab-tarefas" onclick="opTab(\'tarefas\')" style="border-bottom:3px solid transparent;padding:8px 16px;cursor:pointer;font-size:13px;font-weight:600">✅ Tarefas</div>'

new = '  <!-- Sub-tabs -->\n  <div style="display:flex;gap:8px;margin-bottom:20px;border-bottom:1px solid var(--border);padding-bottom:0;flex-wrap:wrap;align-items:center">\n    <div id="op-abas-perfil" style="display:none;gap:4px;margin-right:8px">\n      <button id="op-aba-beatriz" onclick="selecionarOpPerfil(\'beatriz\')" style="padding:4px 12px;border-radius:20px;border:1px solid var(--border);background:var(--orange);color:#fff;font-size:11px;font-weight:700;cursor:pointer">👩\u200d💼 Beatriz</button>\n      <button id="op-aba-davi" onclick="selecionarOpPerfil(\'davi\')" style="padding:4px 12px;border-radius:20px;border:1px solid var(--border);background:var(--surface2);color:var(--text2);font-size:11px;font-weight:700;cursor:pointer">👨\u200d💼 Davi</button>\n    </div>\n    <div class="tab active" id="op-tab-tarefas" onclick="opTab(\'tarefas\')" style="border-bottom:3px solid transparent;padding:8px 16px;cursor:pointer;font-size:13px;font-weight:600">✅ Tarefas</div>'

if old in h:
    h = h.replace(old, new)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(h)
    print('OK - abas HTML adicionadas no Operacional')
else:
    print('X - nao encontrado')
