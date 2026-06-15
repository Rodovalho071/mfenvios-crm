"""
patch_mascara_moeda.py
----------------------
Corrige o módulo Financeiro do CRM MF Envios:

  1. parseMoeda() — lê qualquer formato e converte para float correto
     (150075  →  1500.75,   "R$ 1.500,75"  →  1500.75)

  2. formatMoeda() — exibe sempre "R$ 1.500,75"

  3. Máscara ao digitar — campo de valor formata enquanto o usuário digita
     (só dígitos, vírgula automática nas casas decimais)

  4. Salvar no banco — valor gravado SEMPRE como número puro (ex: 1500.75)

Uso em C:\\mfcrm:
  python patch_mascara_moeda.py
  git add -A && git commit -m "fix: mascara monetaria e parseMoeda no Financeiro"
  git push origin main
  → Manual Deploy no Render
"""

import pathlib, shutil, re, sys

APP = pathlib.Path("app.py")
if not APP.exists():
    print("❌  app.py não encontrado. Execute dentro de C:\\mfcrm.")
    sys.exit(1)

shutil.copy(APP, "app.py.bak")
print("✅  Backup: app.py.bak")

src = APP.read_text(encoding="utf-8")

# ─────────────────────────────────────────────────────────────────────────────
# BLOCO JS — funções parseMoeda / formatMoeda + máscara de input
# ─────────────────────────────────────────────────────────────────────────────

JS_MOEDA = r"""
// ══════════════════════════════════════════════════════════════════════════════
//  UTILITÁRIOS DE MOEDA
// ══════════════════════════════════════════════════════════════════════════════

/**
 * parseMoeda — converte QUALQUER representação para float
 *
 * Exemplos:
 *   150075        → 1500.75   (int "colado", divide por 100)
 *   "150075"      → 1500.75
 *   "1500,75"     → 1500.75
 *   "R$ 1.500,75" → 1500.75
 *   1500.75       → 1500.75   (já está correto)
 *   "1500.75"     → 1500.75
 */
function parseMoeda(v) {
    if (v === null || v === undefined || v === '') return 0;

    // Já é número float com casas decimais razoáveis → ok
    if (typeof v === 'number') {
        // Heurística: se for inteiro >= 1000, provavelmente está "colado"
        if (Number.isInteger(v) && v >= 1000) return v / 100;
        return v;
    }

    // String: limpa símbolo e espaços
    let s = String(v).trim().replace(/R\$\s*/g, '').replace(/\s/g, '');

    // Formato BR com vírgula decimal: "1.500,75" ou "1500,75"
    if (s.includes(',')) {
        // remove pontos de milhar, troca vírgula por ponto
        s = s.replace(/\./g, '').replace(',', '.');
        return parseFloat(s) || 0;
    }

    // Ponto como decimal já correto: "1500.75"
    if (s.includes('.')) {
        const partes = s.split('.');
        // se parte decimal tem 1-2 dígitos → é decimal real
        if (partes.length === 2 && partes[1].length <= 2) {
            return parseFloat(s) || 0;
        }
        // ponto como milhar sem vírgula, ex "1.500" → inteiro
        s = s.replace(/\./g, '');
    }

    // Número puro: se >= 1000 e sem decimais, divide por 100
    const n = parseFloat(s) || 0;
    if (Number.isInteger(n) && n >= 1000) return n / 100;
    return n;
}

/**
 * formatMoeda — formata float para "R$ 1.500,75"
 */
function formatMoeda(v) {
    const n = parseMoeda(v);
    return 'R$ ' + n.toLocaleString('pt-BR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

/**
 * mascaraMoeda — aplica máscara enquanto o usuário digita
 * Use: <input oninput="mascaraMoeda(this)">
 *
 * Só aceita dígitos; formata automaticamente com vírgula decimal.
 * Ex.: usuário digita 150075 → exibe 1.500,75
 *      valor interno (dataset.valor) = "1500.75"
 */
function mascaraMoeda(el) {
    let digits = el.value.replace(/\D/g, '');
    if (!digits) { el.value = ''; el.dataset.valor = '0'; return; }

    // Garante pelo menos 3 dígitos para ter "0,01"
    digits = digits.padStart(3, '0');

    const cents = parseInt(digits, 10);
    const reais = (cents / 100).toFixed(2);

    // Formata BR
    el.value = parseFloat(reais).toLocaleString('pt-BR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });

    // Guarda valor numérico puro no dataset para envio ao backend
    el.dataset.valor = reais;
}

/**
 * valorParaSalvar — retorna o float limpo de um input com máscara
 * Usa dataset.valor se disponível, senão parseMoeda do value
 */
function valorParaSalvar(el) {
    if (el.dataset && el.dataset.valor) return parseFloat(el.dataset.valor);
    return parseMoeda(el.value);
}
// ══════════════════════════════════════════════════════════════════════════════
"""

# ─────────────────────────────────────────────────────────────────────────────
# CSS — campo de valor com estilo de moeda
# ─────────────────────────────────────────────────────────────────────────────

CSS_MOEDA = """
        /* ── Input de valor monetário ────────────────────────────── */
        .input-moeda {
            font-family: 'Courier New', monospace;
            text-align: right;
            letter-spacing: .03em;
            font-size: .95rem;
            color: #f1f5f9;
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 6px;
            padding: 6px 10px;
            width: 100%;
            box-sizing: border-box;
            transition: border-color .2s;
        }
        .input-moeda:focus {
            outline: none;
            border-color: #f97316;
        }
        .input-moeda::placeholder { color: #475569; }
"""

# ─────────────────────────────────────────────────────────────────────────────
# Injeções no arquivo
# ─────────────────────────────────────────────────────────────────────────────

changed = False

# 1. CSS
if '.input-moeda' not in src:
    novo = src.replace("</style>", CSS_MOEDA + "\n        </style>", 1)
    if novo != src:
        src = novo; changed = True
        print("✅  CSS .input-moeda injetado.")
    else:
        print("⚠   </style> não encontrado para CSS.")
else:
    print("ℹ   CSS .input-moeda já existe.")

# 2. JS utilitários
if 'function parseMoeda' not in src:
    idx = src.find("</script>")
    if idx != -1:
        src = src[:idx] + JS_MOEDA + src[idx:]
        changed = True
        print("✅  parseMoeda / formatMoeda / mascaraMoeda injetados.")
    else:
        print("⚠   </script> não encontrado para JS.")
else:
    # Substituir versão antiga de parseMoeda pela nova robusta
    old_pattern = re.compile(
        r'function parseMoeda\s*\(.*?\)\s*\{.*?\}',
        re.DOTALL
    )
    new_fn = """function parseMoeda(v) {
    if (v === null || v === undefined || v === '') return 0;
    if (typeof v === 'number') {
        if (Number.isInteger(v) && v >= 1000) return v / 100;
        return v;
    }
    let s = String(v).trim().replace(/R\\$\\s*/g, '').replace(/\\s/g, '');
    if (s.includes(',')) {
        s = s.replace(/\\./g, '').replace(',', '.');
        return parseFloat(s) || 0;
    }
    if (s.includes('.')) {
        const partes = s.split('.');
        if (partes.length === 2 && partes[1].length <= 2) return parseFloat(s) || 0;
        s = s.replace(/\\./g, '');
    }
    const n = parseFloat(s) || 0;
    if (Number.isInteger(n) && n >= 1000) return n / 100;
    return n;
}"""
    novo, count = old_pattern.subn(new_fn, src, count=1)
    if count:
        src = novo; changed = True
        print("✅  parseMoeda() existente substituído pela versão robusta.")
    else:
        print("ℹ   parseMoeda encontrado mas padrão não casou — verifique manualmente.")

# 3. Adicionar oninput="mascaraMoeda(this)" nos inputs de valor do Financeiro
#    Procura padrões comuns de input de valor nas vendas
patterns_input = [
    # input com name/id contendo "valor"
    (
        re.compile(r'(<input[^>]*(?:name|id)=["\'][^"\']*valor[^"\']*["\'][^>]*?)(\s*/?>)', re.IGNORECASE),
        r'\1 oninput="mascaraMoeda(this)" class="input-moeda"\2'
    ),
]

for pattern, replacement in patterns_input:
    novo, count = pattern.subn(replacement, src)
    if count and novo != src:
        src = novo; changed = True
        print(f"✅  {count} input(s) de valor receberam máscara mascaraMoeda.")
        break
else:
    print("ℹ   Inputs de valor não encontrados pelo padrão automático.")
    print("   Adicione manualmente: oninput=\"mascaraMoeda(this)\" nos inputs de valor.")

# ─────────────────────────────────────────────────────────────────────────────
# Salva
# ─────────────────────────────────────────────────────────────────────────────
if changed:
    APP.write_text(src, encoding="utf-8")
    print("\n✅  app.py atualizado.")
else:
    print("\nℹ   Nenhuma alteração necessária.")

print("""
Próximos passos:
  git add -A && git commit -m "fix: mascara monetaria e parseMoeda Financeiro"
  git push origin main
  → Manual Deploy no Render

Como usar mascaraMoeda nos inputs HTML:
  <input type="text" oninput="mascaraMoeda(this)" class="input-moeda" placeholder="0,00">

Como pegar o valor ao salvar:
  const val = valorParaSalvar(document.getElementById('inputValor'));
  // val = 1500.75  (float puro para o banco)
""")
