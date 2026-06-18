const express = require('express');
const cors = require('cors');
const path = require('path');
const https = require('https');
const { MongoClient } = require('mongodb');

const app = express();
app.use(cors());
app.use(express.json());

const GROQ_KEY      = (process.env.GROQ_KEY || '').trim();
const MONGODB_URI   = (process.env.MONGODB_URI || '').trim();
const EVOLUTION_URL = (process.env.EVOLUTION_URL || 'https://traps-ovary-sandy.ngrok-free.dev').trim();
const EVOLUTION_KEY = (process.env.EVOLUTION_APIKEY || 'mfenvios2024').trim();
const INSTANCE      = (process.env.EVOLUTION_INSTANCE || 'mfenvios').trim();

// Mapa de instancia -> perfil
const INSTANCE_PERFIL = {
  'mfenvios': 'beatriz',
  'mfenvios-davi': 'davi'
};

let db = null;
let messagesCol = null, kanbanCol = null;
let tarefasCol = null, fretesCol = null, agendaCol = null, docsCol = null;
let vendasCol = null;

async function connectMongo() {
  if (!MONGODB_URI) { console.log('[DB] Sem MONGODB_URI - memoria'); return; }
  try {
    const client = new MongoClient(MONGODB_URI, { serverSelectionTimeoutMS:10000, connectTimeoutMS:10000 });
    await client.connect();
    await client.db('admin').command({ ping: 1 });
    db = client.db('mfenvios');
    messagesCol = db.collection('messages');
    kanbanCol   = db.collection('kanban');
    tarefasCol  = db.collection('tarefas');
    fretesCol   = db.collection('fretes');
    agendaCol   = db.collection('agenda');
    docsCol     = db.collection('documentos');
    vendasCol   = db.collection('vendas');
    await messagesCol.createIndex({ id: 1 }, { unique: true });
    await messagesCol.createIndex({ ts: -1 });
    await kanbanCol.createIndex({ id: 1 }, { unique: true });
    await tarefasCol.createIndex({ id: 1 }, { unique: true });
    await fretesCol.createIndex({ id: 1 }, { unique: true });
    await agendaCol.createIndex({ id: 1 }, { unique: true });
    await docsCol.createIndex({ id: 1 }, { unique: true });
    await vendasCol.createIndex({ id: 1 }, { unique: true });
    console.log('[DB] MongoDB Atlas conectado!');
  } catch(e) {
    console.error('[DB] Erro:', e.message);
    db=null; messagesCol=null; kanbanCol=null; tarefasCol=null; fretesCol=null; agendaCol=null; docsCol=null; vendasCol=null;
  }
}

let memMessages = [];
let memKanban = { colunas:['Novo Lead','Em Atendimento','Proposta','Fechado'], cards:[] };
let memTarefas=[], memFretes=[], memAgenda=[], memDocs=[], memVendas=[];

function nowId() { return Date.now().toString(36)+Math.random().toString(36).slice(2,6); }
async function colFind(col,mem,sort) { 
  sort = sort || {ts:-1};
  return col ? col.find({}).sort(sort).toArray() : [...mem]; 
}
async function colUpsert(col,mem,item) {
  if(col){ try{ await col.updateOne({id:item.id},{$set:item},{upsert:true}); }catch(e){console.error('[DB]',e.message);} }
  else{ const i=mem.findIndex(x=>x.id===item.id); if(i>=0) mem[i]=item; else mem.unshift(item); }
}
async function colDelete(col,mem,id) {
  if(col) await col.deleteOne({id});
  else { const i=mem.findIndex(x=>x.id===id); if(i>=0) mem.splice(i,1); }
}

async function getMessages() {
  if(messagesCol) return messagesCol.find({}).sort({ts:-1}).limit(500).toArray();
  return memMessages;
}
async function saveMessage(msg) {
  if(messagesCol){ try{ await messagesCol.updateOne({id:msg.id},{$set:msg},{upsert:true}); }catch(e){} }
  else{ if(!memMessages.find(x=>x.id===msg.id)){ memMessages.unshift(msg); if(memMessages.length>500) memMessages=memMessages.slice(0,500); } }
}
async function deleteMessage(id) {
  if(messagesCol) await messagesCol.deleteOne({id});
  else memMessages=memMessages.filter(m=>m.id!==id);
}
async function getKanban() {
  if(kanbanCol){ const cards=await kanbanCol.find({}).sort({ts:-1}).toArray(); return{colunas:['Novo Lead','Em Atendimento','Proposta','Fechado'],cards}; }
  return memKanban;
}
async function upsertKanbanCard(card) {
  if(kanbanCol){ try{ await kanbanCol.updateOne({id:card.id},{$set:card,$setOnInsert:{ts:Date.now()}},{upsert:true}); }catch(e){console.error('[KANBAN]',e.message);} }
  else{ if(!memKanban.cards.find(c=>c.phone===card.phone)) memKanban.cards.unshift(card); }
}
async function updateKanbanColuna(id,coluna) {
  if(kanbanCol) await kanbanCol.updateOne({id},{$set:{coluna}});
  else{ const card=memKanban.cards.find(c=>c.id===id); if(card) card.coluna=coluna; }
}

// Verifica se já existe lead com esse telefone e perfil no kanban
async function leadExistePorPhone(phone, perfil) {
  if(kanbanCol) {
    const found = await kanbanCol.findOne({phone: phone, perfil: perfil});
    return !!found;
  }
  return memKanban.cards.some(c => c.phone === phone && c.perfil === perfil);
}

const sseClients=[];
function broadcast(event,data){
  const payload = 'event: ' + event + '\ndata: ' + JSON.stringify(data) + '\n\n';
  sseClients.forEach(r=>{ try{r.write(payload);}catch(e){} });
}
function cleanPhone(jid){ if(!jid)return''; return jid.replace('@s.whatsapp.net','').replace('@lid','').replace('@g.us','').trim(); }

async function callGroq(messages,max_tokens) {
  if(!max_tokens) max_tokens=500;
  if(!GROQ_KEY) throw new Error('GROQ_KEY nao definida');
  const key=GROQ_KEY.replace(/[\x00-\x1F\x7F]/g,'');
  const payload=JSON.stringify({model:'llama-3.1-8b-instant',messages,max_tokens,temperature:0.7});
  const options={
    hostname:'api.groq.com',
    path:'/openai/v1/chat/completions',
    method:'POST',
    headers:{
      'Content-Type':'application/json',
      'Authorization':'Bearer '+key,
      'Content-Length':Buffer.byteLength(payload)
    }
  };
  return new Promise(function(resolve,reject){
    const req=https.request(options,function(res){
      let d='';
      res.on('data',function(c){d+=c;});
      res.on('end',function(){
        try{
          const j=JSON.parse(d);
          if(j.error) return reject(new Error(j.error.message));
          resolve(j.choices&&j.choices[0]&&j.choices[0].message&&j.choices[0].message.content||null);
        }catch(e){reject(e);}
      });
    });
    req.on('error',reject);
    req.write(payload);
    req.end();
  });
}

async function enviarMensagemWhatsApp(phone, texto, instancia) {
  const inst = instancia || INSTANCE;
  const payload=JSON.stringify({number:phone,textMessage:{text:texto}});
  const url=new URL(EVOLUTION_URL+'/message/sendText/'+inst);
  const options={
    hostname:url.hostname,
    path:url.pathname,
    method:'POST',
    headers:{'Content-Type':'application/json','apikey':EVOLUTION_KEY,'Content-Length':Buffer.byteLength(payload)}
  };
  return new Promise(function(resolve){
    const req=https.request(options,function(res){let d='';res.on('data',function(c){d+=c;});res.on('end',function(){resolve(d);});});
    req.on('error',function(e){console.error('Erro WA:',e.message);resolve(null);});
    req.write(payload);req.end();
  });
}

app.get('/',function(req,res){res.setHeader('Cache-Control','no-store, no-cache, must-revalidate');res.setHeader('Pragma','no-cache');res.setHeader('Expires','0');res.sendFile(path.join(__dirname,'index.html'));});

app.get('/health',async function(req,res){
  const msgs=await getMessages();
  const kanban=await getKanban();
  res.json({ok:true,db:db?'MongoDB Atlas':'Memoria',messages:msgs.length,cards:kanban.cards.length,groq:GROQ_KEY?'OK':'AUSENTE',uptime:Math.floor(process.uptime())+'s'});
});

app.get('/events',function(req,res){
  res.setHeader('Content-Type','text/event-stream');
  res.setHeader('Cache-Control','no-cache');
  res.setHeader('Connection','keep-alive');
  res.flushHeaders();
  res.write('event: connected\ndata: ok\n\n');
  sseClients.push(res);
  req.on('close',function(){const i=sseClients.indexOf(res);if(i!==-1)sseClients.splice(i,1);});
});

app.post('/webhook',async function(req,res){
  const b=req.body;
  console.log('[WH] Evento:',b.event,JSON.stringify(b).substring(0,150));
  if(b.event==='messages.upsert'&&b.data){
    const m=b.data;
    if(m.key&&!m.key.fromMe){
      const instancia = b.instance || '';
      const perfil = INSTANCE_PERFIL[instancia] || 'beatriz';
      const texto=m.message&&(m.message.conversation||m.message.extendedTextMessage&&m.message.extendedTextMessage.text)||'[midia]';
      const msg={id:m.key.id||Date.now().toString(),name:m.pushName||'Desconhecido',phone:cleanPhone(m.key.remoteJid),text:texto,ts:Date.now(),instance:instancia,perfil:perfil};
      await saveMessage(msg);
      broadcast('nova-mensagem',msg);
      console.log('[WH] Inst:'+instancia+' Perfil:'+perfil+' Msg de',msg.name,':',msg.text.substring(0,60));

      // Cria lead automaticamente no kanban se não existir ainda para esse perfil
      const jaExiste = await leadExistePorPhone(msg.phone, perfil);
      if(!jaExiste) {
        const novoLead = {
          id: nowId(),
          name: msg.name,
          phone: msg.phone,
          coluna: 'Novo Lead',
          perfil: perfil,
          instance: instancia,
          ts: Date.now(),
          mensagens: [texto]
        };
        await upsertKanbanCard(novoLead);
        broadcast('novo-lead', novoLead);
        console.log('[WH] Novo lead criado:', msg.name, 'perfil:', perfil);
      }

      // Bot Groq: apenas para instancia mfenvios (Beatriz)
      if(instancia === 'mfenvios' && texto !== '[midia]'){
        try{
          const r=await callGroq([
            {role:'system',content:'Voce e Beatriz, atendente virtual da MF Envios, transportadora de fretes e logistica. Seja simpatica e objetiva. Quando pedirem cotacao pergunte: Peso, Medidas em cm, Volumes, Valor NF, CEP origem, CEP destino, coleta e urgencia. Responda em portugues sem markdown.'},
            {role:'user',content:texto}
          ]);
          if(r){
            await enviarMensagemWhatsApp(msg.phone, r, instancia);
            const bm={id:'bot_'+Date.now(),name:'Beatriz (Bot)',phone:msg.phone,text:r,ts:Date.now()+1,fromBot:true,instance:instancia,perfil:perfil};
            await saveMessage(bm);
            broadcast('nova-mensagem',bm);
          }
        }catch(e){console.error('[BOT] Erro:',e.message);}
      }
    }
  }
  res.json({ok:true});
});

app.get('/messages',async function(req,res){
  const inst = req.query.instance;
  if(inst && messagesCol) {
    const msgs = await messagesCol.find({instance:inst}).sort({ts:-1}).limit(500).toArray();
    return res.json(msgs);
  }
  res.json(await getMessages());
});
app.delete('/messages/:id',async function(req,res){await deleteMessage(req.params.id);res.json({ok:true});});

app.post('/send',async function(req,res){
  const phone=req.body.phone, text=req.body.text, instancia=req.body.instance||INSTANCE;
  if(!phone||!text) return res.status(400).json({error:'phone e text obrigatorios'});
  await enviarMensagemWhatsApp(phone,text,instancia);
  const msg={id:'manual_'+Date.now(),name:'Voce (Manual)',phone,text,ts:Date.now(),manual:true,instance:instancia};
  await saveMessage(msg);
  broadcast('nova-mensagem',msg);
  res.json({ok:true});
});

app.get('/kanban',async function(req,res){res.json(await getKanban());});
app.patch('/kanban/:id',async function(req,res){
  await updateKanbanColuna(req.params.id,req.body.coluna);
  broadcast('kanban-update',await getKanban());
  res.json({ok:true});
});
app.put('/kanban/:id',async function(req,res){
  const body=Object.assign({},req.body);
  delete body._id;
  const lead=Object.assign({},body,{id:req.params.id});
  try{
    if(kanbanCol){
      await kanbanCol.updateOne({id:req.params.id},{$set:lead},{upsert:true});
    } else {
      const i=memKanban.cards.findIndex(c=>c.id===req.params.id);
      if(i>=0) memKanban.cards[i]=Object.assign({},memKanban.cards[i],lead);
      else memKanban.cards.push(lead);
    }
    res.json({ok:true});
  }catch(e){console.error('[PUT kanban]',e.message);res.status(500).json({error:e.message});}
});
app.delete('/kanban/:id',async function(req,res){
  try{
    if(kanbanCol){ await kanbanCol.deleteOne({id:req.params.id}); }
    else{ memKanban.cards=memKanban.cards.filter(c=>c.id!==req.params.id); }
    res.json({ok:true});
  }catch(e){res.status(500).json({error:e.message});}
});
app.post('/funil',async function(req,res){
  const messageId=req.body.messageId;
  const msgs=await getMessages();
  const msg=msgs.find(function(m){return m.id===messageId;});
  if(!msg) return res.status(404).json({error:'nao encontrada'});
  const card={id:Date.now().toString(),name:msg.name,phone:msg.phone,coluna:'Novo Lead',ts:Date.now(),mensagens:[msg.text]};
  await upsertKanbanCard(card);
  broadcast('novo-lead',card);
  res.json({ok:true,kanban:await getKanban()});
});

app.post('/analisar',async function(req,res){
  const mensagem=req.body.mensagem;
  if(!mensagem) return res.status(400).json({error:'vazio'});
  try{
    const txt=await callGroq([{role:'user',content:'Analise esta mensagem de frete e responda APENAS JSON sem markdown:{nome,tel,material,origem,destino,volumes,peso,medidas,valorNF,etapa,obs}. Etapa:Primeiro contato/Qualificacao/Proposta enviada/Negociacao/Fechado/Ganho/Perdido. Msg:'+mensagem}],500);
    const m=txt.match(/\{[\s\S]*\}/);
    if(!m) return res.status(500).json({error:'sem JSON'});
    res.json({ok:true,dados:JSON.parse(m[0])});
  }catch(e){res.status(500).json({error:e.message});}
});

app.post('/kanban-import',async function(req,res){
  const lead = req.body;
  if(!lead||!lead.id) return res.status(400).json({error:'lead invalido'});
  try {
    if(kanbanCol) {
      await kanbanCol.updateOne({id:lead.id},{$set:lead},{upsert:true});
    } else {
      const i = memKanban.cards.findIndex(c=>c.id===lead.id);
      if(i>=0) memKanban.cards[i]=lead; else memKanban.cards.push(lead);
    }
    res.json({ok:true});
  } catch(e) { res.status(500).json({error:e.message}); }
});

// TAREFAS
app.get('/tarefas',async function(req,res){const p=req.query.perfil;const all=await colFind(tarefasCol,memTarefas);res.json(p?all.filter(x=>x.perfil===p):all);});
app.post('/tarefas',async function(req,res){const item=Object.assign({id:nowId(),ts:Date.now()},req.body);await colUpsert(tarefasCol,memTarefas,item);res.json({ok:true,item});});
app.put('/tarefas/:id',async function(req,res){const item=Object.assign({ts:Date.now()},req.body,{id:req.params.id});await colUpsert(tarefasCol,memTarefas,item);res.json({ok:true,item});});
app.delete('/tarefas/:id',async function(req,res){await colDelete(tarefasCol,memTarefas,req.params.id);res.json({ok:true});});

// FRETES
app.get('/fretes',async function(req,res){const p=req.query.perfil;const all=await colFind(fretesCol,memFretes);res.json(p?all.filter(x=>x.perfil===p):all);});
app.post('/fretes',async function(req,res){const item=Object.assign({id:nowId(),ts:Date.now()},req.body);await colUpsert(fretesCol,memFretes,item);res.json({ok:true,item});});
app.put('/fretes/:id',async function(req,res){const item=Object.assign({ts:Date.now()},req.body,{id:req.params.id});await colUpsert(fretesCol,memFretes,item);res.json({ok:true,item});});
app.delete('/fretes/:id',async function(req,res){await colDelete(fretesCol,memFretes,req.params.id);res.json({ok:true});});

// AGENDA
app.get('/agenda',async function(req,res){const p=req.query.perfil;const all=await colFind(agendaCol,memAgenda);res.json(p?all.filter(x=>x.perfil===p):all);});
app.post('/agenda',async function(req,res){const item=Object.assign({id:nowId(),ts:Date.now()},req.body);await colUpsert(agendaCol,memAgenda,item);res.json({ok:true,item});});
app.put('/agenda/:id',async function(req,res){const item=Object.assign({ts:Date.now()},req.body,{id:req.params.id});await colUpsert(agendaCol,memAgenda,item);res.json({ok:true,item});});
app.delete('/agenda/:id',async function(req,res){await colDelete(agendaCol,memAgenda,req.params.id);res.json({ok:true});});

// DOCUMENTOS
app.get('/documentos',async function(req,res){const p=req.query.perfil;const all=await colFind(docsCol,memDocs);res.json(p?all.filter(x=>x.perfil===p):all);});
app.post('/documentos',async function(req,res){const item=Object.assign({id:nowId(),ts:Date.now()},req.body);await colUpsert(docsCol,memDocs,item);res.json({ok:true,item});});
app.put('/documentos/:id',async function(req,res){const item=Object.assign({ts:Date.now()},req.body,{id:req.params.id});await colUpsert(docsCol,memDocs,item);res.json({ok:true,item});});
app.delete('/documentos/:id',async function(req,res){await colDelete(docsCol,memDocs,req.params.id);res.json({ok:true});});

// VENDAS
let clientesCol = null;
app.get('/clientes',async function(req,res){res.json(await colFind(clientesCol,[]));});
app.post('/clientes',async function(req,res){var item=req.body;await colFind(clientesCol,[]);res.json({ok:true});});
app.put('/clientes/:id',async function(req,res){res.json({ok:true});});
app.delete('/clientes/:id',async function(req,res){res.json({ok:true});});
app.get('/vendas',async function(req,res){res.json(await colFind(vendasCol,memVendas));});
app.post('/vendas',async function(req,res){
  const item=Object.assign({id:nowId(),ts:Date.now(),pago:false},req.body);
  await colUpsert(vendasCol,memVendas,item);
  res.json({ok:true,item});
});
app.put('/vendas/:id',async function(req,res){
  const item=Object.assign({},req.body,{id:req.params.id,updatedAt:Date.now()});
  await colUpsert(vendasCol,memVendas,item);
  res.json({ok:true,item});
});
app.delete('/vendas/:id',async function(req,res){
  await colDelete(vendasCol,memVendas,req.params.id);
  res.json({ok:true});
});

const PORT=process.env.PORT||3000;
connectMongo().then(function(){
  app.listen(PORT,'0.0.0.0',function(){
    console.log('[MF CRM] Porta '+PORT);
    console.log('[DB] Modo: '+(db?'MongoDB Atlas':'Memoria'));
    console.log('[BOT] Groq: '+(GROQ_KEY?'OK ('+GROQ_KEY.substring(0,8)+'...)':'AUSENTE'));
  });
});
