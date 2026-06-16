#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MF Envios CRM - Script de Fixes
Execute em cmd.exe (nao PowerShell): python aplicar_fixes.py
Pasta: C:\mfcrm
"""

import re, os, sys

BASE = r"C:\mfcrm"
INDEX = os.path.join(BASE, "index.html")
SERVER = os.path.join(BASE, "server.js")

def ler(f):
    with open(f, encoding="utf-8") as fh:
        return fh.read()

def gravar(f, txt):
    with open(f, "w", encoding="utf-8") as fh:
        fh.write(txt)
    print(f"  [OK] {f}")

def substituir(txt, antigo, novo, desc):
    if antigo not in txt:
        print(f"  [AVISO] Nao encontrado: {desc}")
        return txt
    resultado = txt.replace(antigo, novo, 1)
    print(f"  [FIX] {desc}")
    return resultado

# ─────────────────────────────────────────
# FIXES NO SERVER.JS
# ─────────────────────────────────────────
print("\n=== FIXES server.js ===")
sv = ler(SERVER)

# FIX 1: Inicializar clientesCol no connectMongo
sv = substituir(sv,
    "vendasCol   = db.collection('vendas');",
    "vendasCol   = db.collection('vendas');\n    clientesCol = db.collection('clientes');",
    "Inicializar clientesCol no connectMongo"
)

# FIX 2: Criar index para clientes
sv = substituir(sv,
    "await vendasCol.createIndex({ id: 1 }, { unique: true });",
    "await vendasCol.createIndex({ id: 1 }, { unique: true });\n    await clientesCol.createIndex({ id: 1 }, { unique: true });",
    "Criar index para clientesCol"
)

# FIX 3: Declarar clientesCol junto com as outras colunas no topo
sv = substituir(sv,
    "let vendasCol = null;",
    "let vendasCol = null;\nlet clientesCol = null;",
    "Declarar clientesCol no topo (remover declaracao duplicada abaixo)"
)

# FIX 4: Remover declaracao duplicada de clientesCol dentro das rotas
sv = substituir(sv,
    "// VENDAS — salvas no MongoDB\nlet clientesCol = null;\n// rotas clientes",
    "// VENDAS — salvas no MongoDB\n// rotas clientes",
    "Remover declaracao duplicada de clientesCol"
)

# FIX 5: Corrigir rotas /clientes (POST e PUT estavam vazias)
sv = substituir(sv,
    """app.get('/clientes',async function(req,res){res.json(await colFind(clientesCol,[]));});
app.post('/clientes',async function(req,res){var item=req.body;await colFind(clientesCol,[]);res.json({ok:true});});
app.put('/clientes/:id',async function(req,res){res.json({ok:true});});
app.delete('/clientes/:id',async function(req,res){res.json({ok:true});});""",
    """let memClientes = [];
app.get('/clientes',async function(req,res){res.json(await colFind(clientesCol,memClientes));});
app.post('/clientes',async function(req,res){
  var item=Object.assign({id:req.body.id||(Date.now().toString(36)+Math.random().toString(36).slice(2,6)),ts:Date.now()},req.body);
  await colUpsert(clientesCol,memClientes,item);
  res.json({ok:true,item});
});
app.put('/clientes/:id',async function(req,res){
  var item=Object.assign({ts:Date.now()},req.body,{id:req.params.id});
  await colUpsert(clientesCol,memClientes,item);
  res.json({ok:true,item});
});
app.delete('/clientes/:id',async function(req,res){
  await colDelete(clientesCol,memClientes,req.params.id);
  res.json({ok:true});
});""",
    "Corrigir rotas /clientes (POST/PUT/DELETE funcionando com MongoDB)"
)

gravar(SERVER, sv)

# ─────────────────────────────────────────
# FIXES NO INDEX.HTML
# ─────────────────────────────────────────
print("\n=== FIXES index.html ===")
ix = ler(INDEX)

# FIX 6: mascaraMoeda - trocar por versao que aceita digitar livremente
# Problema: modo "caixa registradora" nao funciona quando usuario cola/digita "100,25"
# Solucao: detectar se tem virgula e tratar como valor final; senao usar modo centavos
ix = substituir(ix,
    """function mascaraMoeda(el){
  var d=el.value.replace(/\\D/g,'');if(!d){el.value='';el.dataset.valor='0';return;}
  d=d.replace(/^0+/,'')||'0';while(d.length<3)d='0'+d;
  var i=d.slice(0,-2)||'0',dc=d.slice(-2);
  i=i.replace(/\\B(?=(\\d{3})+(?!\\d))/g,'.');
  el.value=i+','+dc;el.dataset.valor=(parseInt(d)/100).toFixed(2);
}""",
    """function mascaraMoeda(el){
  var raw=el.value;
  // Remove tudo exceto digitos e virgula/ponto
  var cleaned=raw.replace(/[^\\d,]/g,'');
  if(!cleaned){el.value='';el.dataset.valor='0';return;}
  // Extrai parte inteira e decimal separadas por virgula
  var partes=cleaned.split(',');
  var intPart=partes[0].replace(/\\D/g,'').replace(/^0+/,'')||'0';
  var decPart=partes.length>1?partes[partes.length-1].replace(/\\D/g,'').substring(0,2):'';
  // Formata parte inteira com pontos de milhar
  intPart=intPart.replace(/\\B(?=(\\d{3})+(?!\\d))/g,'.');
  var displayVal=decPart!==''?intPart+','+decPart:intPart;
  // Preserva virgula no final para usuario continuar digitando
  if(raw.endsWith(',')&&!displayVal.includes(','))displayVal+=',';
  el.value=displayVal;
  // Calcula valor numerico para salvar
  var numStr=intPart.replace(/\\./g,'')+(decPart?'.'+decPart:'');
  el.dataset.valor=parseFloat(numStr)||'0';
}""",
    "Fix mascaraMoeda - aceita digitar 100,25 diretamente sem multiplicar por 100"
)

# FIX 7: Remover hack de divisao por 100 no carregarVendas (causa do R$100,25 -> R$100.025,00)
ix = substituir(ix,
    """    vendas = (Array.isArray(data) ? data : []).map(function(v){
      if(typeof v.valor === 'number' && Number.isInteger(v.valor) && v.valor >= 1000) v.valor = v.valor/100;
      return v;
    });""",
    """    vendas = Array.isArray(data) ? data : [];""",
    "Remover hack /100 que distorcia valores inteiros grandes"
)

# FIX 8: Adicionar funcao atualizarDatalistClientes (estava sendo chamada mas nao existia)
ix = substituir(ix,
    "function valorParaSalvar(el){return el.dataset&&el.dataset.valor?parseFloat(el.dataset.valor):parseMoeda(el.value);}",
    """function valorParaSalvar(el){return el.dataset&&el.dataset.valor?parseFloat(el.dataset.valor):parseMoeda(el.value);}
function atualizarDatalistClientes(){
  var dl=document.getElementById('fin-clientes-list');
  if(!dl)return;
  var nomes=[];
  if(typeof clientesFin!=='undefined'&&clientesFin.length){
    nomes=clientesFin.map(function(c){return c.nome;});
  }
  dl.innerHTML=nomes.map(function(n){return '<option value="'+n+'">';}).join('');
}""",
    "Adicionar funcao atualizarDatalistClientes que faltava"
)

# FIX 9: Abas do operacional com overflow-x para nao sumir
ix = substituir(ix,
    '  <div style="display:flex;gap:8px;margin-bottom:20px;border-bottom:1px solid var(--border);padding-bottom:0">',
    '  <div style="display:flex;gap:8px;margin-bottom:20px;border-bottom:1px solid var(--border);padding-bottom:0;overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:none;flex-wrap:nowrap;">',
    "Abas operacional com scroll horizontal (Clientes nao some)"
)

# FIX 10: Consulta CNPJ via BrasilAPI no campo cli-cnpj
# Adicionar onblur no input de CNPJ do modal de cliente
ix = substituir(ix,
    """<input id="cli-cnpj" type="text" """,
    """<input id="cli-cnpj" type="text" onblur="consultarCNPJ(this.value)" """,
    "Adicionar onblur para consulta CNPJ no modal de cliente"
)

# FIX 11: Funcao consultarCNPJ via BrasilAPI
ix = substituir(ix,
    "function salvarClienteFin(){",
    """function consultarCNPJ(cnpjRaw){
  var cnpj=cnpjRaw.replace(/\\D/g,'');
  if(cnpj.length!==14)return;
  fetch('https://brasilapi.com.br/api/cnpj/v1/'+cnpj)
    .then(function(r){return r.json();})
    .then(function(d){
      if(d.razao_social){
        var nomeEl=document.getElementById('cli-nome');
        if(nomeEl&&!nomeEl.value.trim()) nomeEl.value=d.razao_social;
        var endEl=document.getElementById('cli-end');
        if(endEl&&!endEl.value.trim()){
          var end=[d.logradouro,d.numero,d.complemento,d.bairro,d.municipio,d.uf].filter(Boolean).join(', ');
          endEl.value=end;
        }
        if(typeof showToast==='function') showToast('CNPJ encontrado: '+d.razao_social);
      }
    })
    .catch(function(){});
}
function salvarClienteFin(){""",
    "Adicionar consultarCNPJ via BrasilAPI"
)

# FIX 12: Carregar clientesFin ao iniciar (nao so quando abre a aba)
# Garante que o datalist de clientes funciona desde o primeiro uso
ix = substituir(ix,
    "var clientesFin=[];var clienteEditandoFin=null;",
    "var clientesFin=[];var clienteEditandoFin=null;\ncarregarClientesFin();",
    "Carregar clientes do servidor ao iniciar a pagina"
)

gravar(INDEX, ix)

print("\n=== RESUMO DOS FIXES ===")
print("server.js:")
print("  [1] clientesCol inicializado no connectMongo")
print("  [2] Index criado para clientes no MongoDB")
print("  [3/4] Declaracao duplicada de clientesCol removida")
print("  [5] Rotas POST/PUT/DELETE /clientes funcionando com MongoDB")
print("")
print("index.html:")
print("  [6] mascaraMoeda corrigida - 100,25 salva como 100.25")
print("  [7] Hack /100 removido do carregarVendas")
print("  [8] atualizarDatalistClientes criada (estava sendo chamada sem existir)")
print("  [9] Abas operacional com scroll - aba Clientes nao some mais")
print("  [10/11] Consulta CNPJ via BrasilAPI ao sair do campo")
print("  [12] Clientes carregados ao iniciar a pagina")
print("")
print("ATENCAO - O que ainda nao e corrigido automaticamente:")
print("  - Leads do Kanban ainda usam localStorage (migracao completa para MongoDB")
print("    requer refatoracao maior - pode ser feita em sessao separada)")
print("")
print("=== PROXIMO PASSO ===")
print("No cmd.exe em C:\\mfcrm:")
print('  git add -A && git commit -m "fix: valor moeda, clientes MongoDB, CNPJ lookup, abas operacional" && git push origin main')
print("Depois: Manual Deploy no Render")
