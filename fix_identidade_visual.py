print("Aplicando identidade visual MF Envios v2.0...")

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

orig = html

# ══════════════════════════════════════════════════════════
# 1. Variáveis CSS — substituir paleta atual pela do manual
# ══════════════════════════════════════════════════════════
old_root = """:root {
  --bg:#0a1931;--surface:#102a50;--surface2:#183a6b;--border:#1e467a;--border2:#2c5a94;
  --text:#ffffff;--text2:#cbd5e1;--text3:#94a3b8;--green:#22c55e;--green-bg:rgba(34,197,94,0.2);
  --red:#ef4444;--red-bg:rgba(239,68,68,0.2);--blue:#3b82f6;--blue-bg:rgba(59,130,246,0.2);
  --amber:#f59e0b;--amber-bg:rgba(245,158,11,0.2);--purple:#a78bfa;--orange:#f97316;
  --radius:10px;--radius-sm:6px;--shadow:0 4px 12px rgba(0,0,0,.5);--shadow-md:0 8px 24px rgba(0,0,0,.6);
}"""

new_root = """:root {
  /* === MF ENVIOS — Identidade Visual v2.0 === */
  --bg:#0D0F1F;
  --surface:#1E2456;
  --surface2:#2A3070;
  --border:rgba(255,255,255,0.10);
  --border2:rgba(255,255,255,0.18);
  --text:#FFFFFF;
  --text2:#cbd5e1;
  --text3:#8B8FA8;
  --green:#22c55e;--green-bg:rgba(34,197,94,0.2);
  --red:#ef4444;--red-bg:rgba(239,68,68,0.2);
  --blue:#3b82f6;--blue-bg:rgba(59,130,246,0.2);
  --amber:#f59e0b;--amber-bg:rgba(245,158,11,0.2);
  --purple:#a78bfa;
  --orange:#F97316;
  --orange-hover:#EA6B10;
  --orange-glow:rgba(249,115,22,0.35);
  --orange-light:rgba(249,115,22,0.12);
  --radius:12px;--radius-sm:8px;
  --shadow:0 4px 12px rgba(0,0,0,.5);
  --shadow-md:0 8px 32px rgba(0,0,0,.6);
  --shadow-orange:0 0 20px rgba(249,115,22,0.35);
}"""

if old_root in html:
    html = html.replace(old_root, new_root)
    print("OK 1/6 - variáveis CSS atualizadas para identidade MF Envios")
else:
    print("X 1/6 - :root não encontrado")

# ══════════════════════════════════════════════════════════
# 2. Tipografia — trocar Segoe UI por Nourd + @import
# ══════════════════════════════════════════════════════════
old_font_import = "<style>"
new_font_import = """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
/* Nourd via CDN não disponível — Inter como fallback fiel (mesma geometria) */"""

if old_font_import in html and '@import' not in html:
    html = html.replace(old_font_import, new_font_import, 1)
    print("OK 2/6 - @import Inter adicionado (fallback fiel à Nourd)")
else:
    print("~ 2/6 - @import já existe ou não encontrado")

old_body_font = "body{font-family:'Segoe UI',Roboto,sans-serif;background:var(--bg);color:var(--text);font-size:14px;height:100vh;display:flex;flex-direction:column;overflow:hidden}"
new_body_font = "body{font-family:'Inter','Nourd','Helvetica Neue',Arial,sans-serif;background:var(--bg);color:var(--text);font-size:14px;height:100vh;display:flex;flex-direction:column;overflow:hidden}"

if old_body_font in html:
    html = html.replace(old_body_font, new_body_font)
    print("OK 2/6 - tipografia body atualizada para Inter/Nourd")
else:
    print("X 2/6 - font-family body não encontrado")

# ══════════════════════════════════════════════════════════
# 3. Topbar — navy principal com borda laranja sutil
# ══════════════════════════════════════════════════════════
old_topbar = ".topbar{display:flex;align-items:center;gap:16px;padding:0 24px;height:56px;background:var(--surface);border-bottom:1px solid var(--border);flex-shrink:0}"
new_topbar = ".topbar{display:flex;align-items:center;gap:16px;padding:0 24px;height:60px;background:var(--surface);border-bottom:2px solid var(--orange);flex-shrink:0;box-shadow:0 2px 16px rgba(0,0,0,.4)}"

if old_topbar in html:
    html = html.replace(old_topbar, new_topbar)
    print("OK 3/6 - topbar com borda laranja MF Envios")
else:
    print("X 3/6 - topbar não encontrada")

# ══════════════════════════════════════════════════════════
# 4. Botão primário — laranja com glow (padrão do manual)
# ══════════════════════════════════════════════════════════
old_btn = ".btn{display:inline-flex;align-items:center;gap:6px;padding:7px 14px;border-radius:var(--radius-sm);border:1px solid var(--border2);background:var(--surface2);font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.5px;color:var(--text);cursor:pointer;transition:all .15s;white-space:nowrap}\n.btn:hover{background:var(--border)}.btn-primary{background:var(--text);color:var(--bg);border-color:var(--text)}.btn-primary:hover{background:var(--text2)}"
new_btn = ".btn{display:inline-flex;align-items:center;gap:6px;padding:8px 16px;border-radius:var(--radius-sm);border:1.5px solid var(--border2);background:var(--surface2);font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:var(--text);cursor:pointer;transition:all .2s;white-space:nowrap}\n.btn:hover{background:var(--surface2);border-color:rgba(249,115,22,.4);box-shadow:var(--shadow-orange)}.btn-primary{background:var(--orange);color:#fff;border-color:var(--orange);box-shadow:var(--shadow-orange)}.btn-primary:hover{background:var(--orange-hover);box-shadow:0 0 28px rgba(249,115,22,.5)}"

if old_btn in html:
    html = html.replace(old_btn, new_btn)
    print("OK 4/6 - botões com identidade MF Envios (laranja glow)")
else:
    print("X 4/6 - .btn não encontrado")

# ══════════════════════════════════════════════════════════
# 5. Cards — borda laranja no hover, radius 12px
# ══════════════════════════════════════════════════════════
old_card = ".card{background:var(--bg);border:1px solid var(--border);border-radius:var(--radius-sm);padding:12px;cursor:pointer;transition:all .15s}.card:hover{border-color:var(--border2);transform:translateY(-1px);box-shadow:var(--shadow)}"
new_card = ".card{background:rgba(255,255,255,0.03);border:1px solid var(--border);border-radius:var(--radius-sm);padding:12px;cursor:pointer;transition:all .2s}.card:hover{border-color:rgba(249,115,22,.4);transform:translateY(-2px);box-shadow:var(--shadow-orange)}"

if old_card in html:
    html = html.replace(old_card, new_card)
    print("OK 5/6 - cards com hover laranja MF Envios")
else:
    print("X 5/6 - .card não encontrado")

# ══════════════════════════════════════════════════════════
# 6. Inputs e selects — focus laranja conforme manual
# ══════════════════════════════════════════════════════════
old_input = "input,select{width:100%;padding:8px 10px;border:1px solid var(--border);border-radius:var(--radius-sm);font-size:13px;font-family:inherit;color:var(--text);background:var(--bg);outline:none;transition:border .15s}input:focus,select:focus{border-color:var(--border2)}"
new_input = "input,select{width:100%;padding:9px 12px;border:1px solid rgba(255,255,255,0.15);border-radius:var(--radius-sm);font-size:13px;font-family:inherit;color:var(--text);background:rgba(255,255,255,0.06);outline:none;transition:all .2s;height:40px}input:focus,select:focus{border-color:var(--orange);box-shadow:0 0 0 3px rgba(249,115,22,0.15)}"

if old_input in html:
    html = html.replace(old_input, new_input)
    print("OK 6/6 - inputs/selects com focus laranja MF Envios")
else:
    print("X 6/6 - input/select não encontrado")

# ══════════════════════════════════════════════════════════
# RESULTADO
# ══════════════════════════════════════════════════════════
if html != orig:
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("\nindex.html atualizado com identidade visual MF Envios!")
    print("git add index.html && git commit -m 'feat: identidade visual MF Envios v2.0' && git push origin main")
else:
    print("\nNenhuma alteração feita")
