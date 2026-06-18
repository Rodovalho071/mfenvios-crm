with open('/tmp/logo_b64.txt') as f:
    b64 = f.read().strip()

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old_logo = '  <div class="logo"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 44" width="130" height="34"><defs><linearGradient id="ag1" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#f97316" stop-opacity="0.3"/><stop offset="50%" stop-color="#f97316"/><stop offset="100%" stop-color="#f97316" stop-opacity="0.3"/></linearGradient></defs><path d="M18 22 Q80 -2 142 22" fill="none" stroke="url(#ag1)" stroke-width="2.5" stroke-linecap="round"/><text x="80" y="39" text-anchor="middle" font-family="Segoe UI,Arial,sans-serif" font-size="17" font-weight="800" fill="white" letter-spacing="2.5">MF ENVIOS</text></svg></div>'

new_logo = f'  <div class="logo"><img src="data:image/png;base64,{b64}" alt="MF Envios" style="height:40px;width:auto;object-fit:contain;" /></div>'

if old_logo in html:
    html = html.replace(old_logo, new_logo)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('OK - logo PNG embutido no HTML')
    print('git add index.html && git commit -m "feat: logo MF Envios v2.0" && git push origin main')
else:
    print('X - logo SVG nao encontrado')
