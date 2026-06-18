with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re

# Logo fiel ao original — arco começa na letra M e termina na letra S
# O arco desce até quase tocar o topo das letras
new_logo_svg = '''  <div class="logo"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 180 50" width="155" height="42">
  <defs>
    <linearGradient id="arco2" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%"   stop-color="#F97316" stop-opacity="0.1"/>
      <stop offset="20%"  stop-color="#F97316" stop-opacity="0.8"/>
      <stop offset="50%"  stop-color="#F97316" stop-opacity="1"/>
      <stop offset="80%"  stop-color="#F97316" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="#F97316" stop-opacity="0.1"/>
    </linearGradient>
    <filter id="glow2" x="-20%" y="-100%" width="140%" height="400%">
      <feGaussianBlur stdDeviation="1.2" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <!-- Arco: extremidades saem de dentro das letras M e S -->
  <path d="M22 34 Q90 2 158 34" fill="none" stroke="url(#arco2)" stroke-width="1.8" stroke-linecap="round" filter="url(#glow2)"/>
  <text x="90" y="47" text-anchor="middle" font-family="Inter,Nourd,Helvetica Neue,Arial,sans-serif" font-size="19" font-weight="800" fill="#FFFFFF" letter-spacing="3.5">MF ENVIOS</text>
</svg></div>'''

old = re.search(r'  <div class="logo">.*?</div>', html, re.DOTALL)
if old:
    html = html[:old.start()] + new_logo_svg + html[old.end():]
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('OK - logo SVG fiel ao original')
    print('git add index.html && git commit -m "fix: logo arco fiel" && git push origin main')
else:
    print('X - nao encontrado')
