with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re

# Logo SVG inline — arco laranja + wordmark branco, fiel ao manual
new_logo_svg = '''  <div class="logo"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 180 48" width="150" height="40">
  <defs>
    <linearGradient id="arco" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%"   stop-color="#F97316" stop-opacity="0"/>
      <stop offset="30%"  stop-color="#F97316" stop-opacity="0.7"/>
      <stop offset="50%"  stop-color="#F97316" stop-opacity="1"/>
      <stop offset="70%"  stop-color="#F97316" stop-opacity="0.7"/>
      <stop offset="100%" stop-color="#F97316" stop-opacity="0"/>
    </linearGradient>
    <filter id="glow"><feGaussianBlur stdDeviation="1" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  </defs>
  <path d="M14 22 Q90 -4 166 22" fill="none" stroke="url(#arco)" stroke-width="2" stroke-linecap="round" filter="url(#glow)"/>
  <text x="90" y="42" text-anchor="middle" font-family="Inter,Nourd,Helvetica Neue,Arial,sans-serif" font-size="18" font-weight="800" fill="#FFFFFF" letter-spacing="3">MF ENVIOS</text>
</svg></div>'''

# Substituir qualquer versão do logo div
old = re.search(r'  <div class="logo">.*?</div>', html, re.DOTALL)
if old:
    html = html[:old.start()] + new_logo_svg + html[old.end():]
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('OK - logo SVG inline aplicado')
    print('git add index.html && git commit -m "fix: logo SVG inline" && git push origin main')
else:
    print('X - div logo nao encontrado')
