content = open('C:/mfcrm/index.html', encoding='utf-8').read()

# CSS a adicionar antes de </style>
css = """
.cnpj-row{display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid #2a3045;font-size:.75rem}
.cnpj-label{color:#8492b4}
.cnpj-val{color:#e8ecf5;font-weight:500;text-align:right;max-width:60%}
.cnpj-status-ok{color:#22c55e;font-weight:600}
.cnpj-status-bad{color:#ef4444;font-weight:600}
.cnpj-result{background:var(--surface2);border-radius:8px;padding:10px;margin-top:8px;display:none}
"""

content = content.replace('</style>', css + '</style>', 1)

# HTML a adicionar após o campo Telefone (linha 1119)
old_tel = '<div class="form-group"><label class="form-label">Telef'
# Precisamos achar a div completa do telefone e adicionar depois dela
tel_field = '<div class="form-group"><label class="form-label">Telefone</label><input id="d-tel" value="${l.tel||\'\'}" onblur="updateLeadField(\'${l.id}\',\'tel\',this.value)"/></div>'

cnpj_block = tel_field + '''
        <div class="form-group" style="grid-column:1/-1">
          <label class="form-label">CNPJ</label>
          <div style="display:flex;gap:8px;align-items:center">
            <input id="d-cnpj" value="${l.cnpj||\'\'}" placeholder="00.000.000/0001-00" style="flex:1" oninput="formatCNPJ(this)" onblur="updateLeadField(\'${l.id}\',\'cnpj\',this.value)"/>
            <button class="btn btn-primary" type="button" onclick="prospectAI(\'${l.id}\')" style="white-space:nowrap;padding:6px 12px">&#128269; ProspectAI</button>
          </div>
          <div id="cnpj-result-${l.id}" class="cnpj-result"></div>
        </div>'''

if tel_field in content:
    content = content.replace(tel_field, cnpj_block, 1)
    print('Tel field replaced OK')
else:
    print('Tel field NOT found - trying partial match')
    # try to find partial
    idx = content.find('id="d-tel"')
    print('d-tel at index:', idx)
    print('context:', content[idx-100:idx+200])

# JavaScript a adicionar antes de </script> final
js = """
function formatCNPJ(el){
  var v=el.value.replace(/\\D/g,'').substring(0,14);
  v=v.replace(/(\\d{2})(\\d)/,'$1.$2');
  v=v.replace(/(\\d{3})(\\d)/,'$1.$2');
  v=v.replace(/(\\d{3})(\\/)(\\d)/,'$1/$3');
  v=v.replace(/(\\/\\d{4})(\\d)/,'$1-$2');
  el.value=v;
}
async function prospectAI(leadId){
  var el=document.getElementById('d-cnpj');
  if(!el)return;
  var cnpj=el.value.replace(/\\D/g,'');
  if(cnpj.length!==14){alert('CNPJ deve ter 14 digitos');return;}
  var btn=event.target;
  btn.textContent='Consultando...';btn.disabled=true;
  try{
    var r=await fetch('https://brasilapi.com.br/api/cnpj/v1/'+cnpj);
    var d=await r.json();
    if(d.message){alert('CNPJ nao encontrado: '+d.message);return;}
    var ok=d.descricao_situacao_cadastral==='ATIVA';
    var html='<div class="cnpj-row"><span class="cnpj-label">Razao Social</span><span class="cnpj-val">'+( d.razao_social||'-')+'</span></div>'+
      '<div class="cnpj-row"><span class="cnpj-label">Nome Fantasia</span><span class="cnpj-val">'+(d.nome_fantasia||'-')+'</span></div>'+
      '<div class="cnpj-row"><span class="cnpj-label">Situacao</span><span class="cnpj-val '+(ok?'cnpj-status-ok':'cnpj-status-bad')+'">'+(d.descricao_situacao_cadastral||'-')+'</span></div>'+
      '<div class="cnpj-row"><span class="cnpj-label">CNAE</span><span class="cnpj-val">'+(d.cnae_fiscal_descricao||'-')+'</span></div>'+
      '<div class="cnpj-row"><span class="cnpj-label">Porte</span><span class="cnpj-val">'+(d.porte||'-')+'</span></div>'+
      '<div class="cnpj-row"><span class="cnpj-label">Municipio/UF</span><span class="cnpj-val">'+(d.municipio||'-')+'/'+(d.uf||'-')+'</span></div>'+
      '<div class="cnpj-row"><span class="cnpj-label">Telefone</span><span class="cnpj-val">'+(d.ddd_telefone_1||'-')+'</span></div>'+
      '<div class="cnpj-row"><span class="cnpj-label">Email</span><span class="cnpj-val">'+(d.email||'-')+'</span></div>'+
      '<div class="cnpj-row"><span class="cnpj-label">Endereco</span><span class="cnpj-val">'+(d.logradouro||'')+(d.numero?' '+d.numero:'')+'</span></div>'+
      '<button class="btn btn-primary" style="width:100%;margin-top:8px" onclick="usarDadosCNPJ(\\\''+leadId+'\\\','+JSON.stringify(d).replace(/'/g,"\\\\'")+')">&#8601;&#65039; Usar dados no lead</button>';
    var res=document.getElementById('cnpj-result-'+leadId);
    if(res){res.innerHTML=html;res.style.display='block';}
  }catch(e){alert('Erro na consulta: '+e.message);}
  finally{btn.textContent='\\uD83D\\uDD0D ProspectAI';btn.disabled=false;}
}
function usarDadosCNPJ(leadId,d){
  var l=leads.find(x=>x.id===leadId);if(!l)return;
  if(d.razao_social){l.name=d.razao_social;var nel=document.getElementById('d-name');if(nel)nel.value=d.razao_social;}
  if(d.municipio&&d.uf){l.origem=d.municipio+'/'+d.uf;var oel=document.getElementById('d-origem');if(oel)oel.value=l.origem;}
  if(d.ddd_telefone_1){l.tel=d.ddd_telefone_1.replace(/\\D/g,'');var tel=document.getElementById('d-tel');if(tel)tel.value=l.tel;}
  saveLeads();toast('Dados preenchidos!');
}
"""

# Add JS before last </script>
last_script = content.rfind('</script>')
if last_script != -1:
    content = content[:last_script] + js + content[last_script:]
    print('JS added OK')

open('C:/mfcrm/index.html', 'w', encoding='utf-8').write(content)
print('Done - size:', len(content))
