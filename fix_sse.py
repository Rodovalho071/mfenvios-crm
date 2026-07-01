# -*- coding: utf-8 -*-
"""
Corrige o bug do SSE no index.html:
- Adiciona listener para o evento 'novo-lead' (antes era ignorado)
- Faz 'nova-mensagem' tambem sincronizar o kanban
- Reconecta e resincroniza quando a aba volta a ficar visivel
- Adiciona sincronizacao de seguranca a cada 60s
Rode este arquivo dentro da pasta do projeto (onde esta o index.html).
"""
import io

CAMINHO = "index.html"

OLD = """function conectarSSE(){try{const es=new EventSource(WPP_SERVER+'/events');es.addEventListener('nova-mensagem',function(e){
    try{
      var d=JSON.parse(e.data);
      var inst=(typeof perfilAtivo!=='undefined'&&perfilAtivo&&typeof PERFIS!=='undefined'&&PERFIS[perfilAtivo])?PERFIS[perfilAtivo].instancia:'';
      if(!inst||!d.instance||d.instance===inst) loadWppMessages();
    }catch(ex){loadWppMessages();}
  });es.onerror=()=>{es.close();setTimeout(conectarSSE,5000)};}catch(e){}}
conectarSSE();
setInterval(()=>{
  var _inst2=(typeof perfilAtivo!=='undefined'&&perfilAtivo&&typeof PERFIS!=='undefined'&&PERFIS[perfilAtivo])?PERFIS[perfilAtivo].instancia:'';
  var _url2=WPP_SERVER+'/messages'+(_inst2?'?instance='+_inst2:'');
  fetch(_url2).then(r=>r.json()).then(msgs=>{wppMsgs=msgs;const b=document.getElementById('wpp-badge');if(msgs.length>0){b.style.display='inline';b.textContent=msgs.length;}else b.style.display='none';if(chatAtivo)renderConvList();}).catch(()=>{});
},30000);"""

NEW = """var _sseInstance=null;
function conectarSSE(){
  try{
    if(_sseInstance){try{_sseInstance.close();}catch(_e){}}
    const es=new EventSource(WPP_SERVER+'/events');
    _sseInstance=es;
    es.addEventListener('nova-mensagem',function(e){
      try{
        var d=JSON.parse(e.data);
        var inst=(typeof perfilAtivo!=='undefined'&&perfilAtivo&&typeof PERFIS!=='undefined'&&PERFIS[perfilAtivo])?PERFIS[perfilAtivo].instancia:'';
        if(!inst||!d.instance||d.instance===inst){loadWppMessages();sincronizarLeadsServidor();}
      }catch(ex){loadWppMessages();sincronizarLeadsServidor();}
    });
    es.addEventListener('novo-lead',function(e){
      try{
        var d=JSON.parse(e.data);
        var inst=(typeof perfilAtivo!=='undefined'&&perfilAtivo&&typeof PERFIS!=='undefined'&&PERFIS[perfilAtivo])?PERFIS[perfilAtivo].instancia:'';
        if(!inst||!d.instance||d.instance===inst){sincronizarLeadsServidor();toast('Novo lead recebido!');}
      }catch(ex){sincronizarLeadsServidor();}
    });
    es.onerror=function(){es.close();if(_sseInstance===es)_sseInstance=null;setTimeout(conectarSSE,5000);};
  }catch(e){setTimeout(conectarSSE,5000);}
}
conectarSSE();

// Reconecta e resincroniza sempre que a aba volta a ficar visivel/ativa
// (evita ficar com a conexao de eventos "morta" depois de horas em segundo plano)
document.addEventListener('visibilitychange',function(){
  if(document.visibilityState==='visible'){
    if(!_sseInstance||_sseInstance.readyState===2){conectarSSE();}
    sincronizarLeadsServidor();
    loadWppMessages();
  }
});
window.addEventListener('online',function(){conectarSSE();sincronizarLeadsServidor();loadWppMessages();});

setInterval(()=>{
  var _inst2=(typeof perfilAtivo!=='undefined'&&perfilAtivo&&typeof PERFIS!=='undefined'&&PERFIS[perfilAtivo])?PERFIS[perfilAtivo].instancia:'';
  var _url2=WPP_SERVER+'/messages'+(_inst2?'?instance='+_inst2:'');
  fetch(_url2).then(r=>r.json()).then(msgs=>{wppMsgs=msgs;const b=document.getElementById('wpp-badge');if(msgs.length>0){b.style.display='inline';b.textContent=msgs.length;}else b.style.display='none';if(chatAtivo)renderConvList();}).catch(()=>{});
},30000);

// Sincronizacao de seguranca: garante que o funil se atualize mesmo se o
// canal de eventos (SSE) cair silenciosamente sem disparar erro
setInterval(()=>{sincronizarLeadsServidor();},60000);"""

with io.open(CAMINHO, "r", encoding="utf-8") as f:
    conteudo = f.read()

qtd = conteudo.count(OLD)

if qtd == 0:
    print("ERRO: nao encontrei o trecho original no index.html.")
    print("Isso pode significar que o arquivo ja foi alterado antes, ou e uma versao diferente.")
    print("Nenhuma mudanca foi feita. Me avise para eu investigar.")
elif qtd > 1:
    print("ERRO: encontrei o trecho " + str(qtd) + " vezes (esperava 1). Abortando por seguranca.")
else:
    novo_conteudo = conteudo.replace(OLD, NEW)
    with io.open(CAMINHO, "w", encoding="utf-8") as f:
        f.write(novo_conteudo)
    print("OK! index.html corrigido com sucesso.")
    print("Agora rode: git add -A && git commit -m \"fix: SSE escuta novo-lead e resincroniza kanban automaticamente\" && git push")
