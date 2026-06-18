with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

erros = []

# 1. Modal — adicionar campos rastreio e comprovante
old1 = "      <div><label style=\"font-size:12px;color:var(--text3)\">STATUS</label>\n        <select id=\"op-f-status\" class=\"form-input\" style=\"width:100%;margin-top:4px\">\n          ${FRETE_COLS.map(c=>`<option value=\"${c}\">${c}</option>`).join('')}\n        </select>\n      </div>\n    </div>`;"
new1 = "      <div><label style=\"font-size:12px;color:var(--text3)\">STATUS</label>\n        <select id=\"op-f-status\" class=\"form-input\" style=\"width:100%;margin-top:4px\">\n          ${FRETE_COLS.map(c=>`<option value=\"${c}\">${c}</option>`).join('')}\n        </select>\n      </div>\n      <div><label style=\"font-size:12px;color:var(--text3)\">RASTREIO (AWB / Tracking)</label><input id=\"op-f-rastreio\" class=\"form-input\" placeholder=\"Ex: 123456789BR\" style=\"width:100%;margin-top:4px\"></div>\n      <div><label style=\"font-size:12px;color:var(--text3)\">COMPROVANTE (link)</label><input id=\"op-f-comprovante\" class=\"form-input\" placeholder=\"Link Google Drive, WhatsApp, etc.\" style=\"width:100%;margin-top:4px\"></div>\n    </div>`;"
if old1 in html: html=html.replace(old1,new1); print("OK 1/3 - campos modal")
else: erros.append("1"); print("X 1/3")

# 2. POST — salvar rastreio e comprovante
old2 = "body:JSON.stringify({titulo,origem:document.getElementById('op-f-origem').value,destino:document.getElementById('op-f-destino').value,valor:document.getElementById('op-f-valor').value,status:document.getElementById('op-f-status').value||'Aguardando coleta',perfil:getOpPerfil()})})"
new2 = "body:JSON.stringify({titulo,origem:document.getElementById('op-f-origem').value,destino:document.getElementById('op-f-destino').value,valor:document.getElementById('op-f-valor').value,status:document.getElementById('op-f-status').value||'Aguardando coleta',rastreio:(document.getElementById('op-f-rastreio')||{}).value||'',comprovante:(document.getElementById('op-f-comprovante')||{}).value||'',perfil:getOpPerfil()})})"
if old2 in html: html=html.replace(old2,new2); print("OK 2/3 - POST salva rastreio")
else: erros.append("2"); print("X 2/3")

# 3. Card — exibir rastreio e comprovante
old3 = "            ${f.valor?`<div style=\"font-size:12px;color:var(--green);margin-top:4px\">R$ ${f.valor}</div>`:''}"
new3 = "            ${f.valor?`<div style=\"font-size:12px;color:var(--green);margin-top:4px\">R$ ${f.valor}</div>`:''}\n            ${f.rastreio?`<div style=\"font-size:11px;color:var(--blue);margin-top:4px\">\U0001f4e6 Rastreio: ${f.rastreio}</div>`:''}\n            ${f.comprovante?`<div style=\"margin-top:4px\"><a href=\"${f.comprovante}\" target=\"_blank\" style=\"font-size:11px;color:var(--orange);text-decoration:none\">\U0001f517 Ver comprovante</a></div>`:''}"
if old3 in html: html=html.replace(old3,new3); print("OK 3/3 - card exibe rastreio")
else: erros.append("3"); print("X 3/3")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("\nindex.html atualizado!")
print("git add index.html && git commit -m 'feat: rastreio e comprovante no frete' && git push origin main")
