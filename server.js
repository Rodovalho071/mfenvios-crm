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

let db = null;
let messagesCol = null, kanbanCol = null;
let tarefasCol = null, fretesCol = null, agendaCol = null, docsCol = null;

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
    await messagesCol.createIndex({ id: 1 }, { unique: true });
    await messagesCol.createIndex({ ts: -1 });
    await kanbanCol.createIndex({ phone: 1 }, { unique: true });
    await tarefasCol.createIndex({ id: 1 }, { unique: true });
    await fretesCol.createIndex({ id: 1 }, { unique: true });
    await agendaCol.createIndex({ id: 1 }, { unique: true });
    await docsCol.createIndex({ id: 1 }, { unique: true });
    console.log('[DB] MongoDB Atlas conectado!');
  } catch(e) {
    console.error('[DB] Erro:', e.message);
    db=null; messagesCol=null; kanbanCol=null; tarefasCol=null; fretesCol=null; agendaCol=null; docsCol=null;
  }
}

let memMessages = [];
let memKanban = { colunas:['Novo Lead','Em Atendimento','Proposta','Fechado'], cards:[] };
let memTarefas=[], memFretes=[], memAgenda=[], memDocs=[];

function nowId() { return Date.now().toString(36)+Math.random().toString(36).slice(2,6); }
async function colFind(col,mem) { return col ? col.find({}).sort({ts:-1}).toArray() : [...mem]; }
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
  if(kanbanCol){ try{ await kanbanCol.updateOne({phone:card.phone},{$set:card,$setOnInsert:{ts:Date.now()}},{upsert:true}); }catch(e){} }
  else{ if(!memKanban.cards.find(c=>c.phone===card.phone)) memKanban.cards.unshift(card); }
}
async function updateKanbanColuna(id,coluna) {
  if(kanbanCol) await kanbanCol.updateOne({id},{$set:{coluna}});
  else{ const card=memKanban.cards.find(c=>c.id===id); if(card) card.coluna=coluna; }
}

const sseClients=[];
function broadcast(event,data){ const p=event: \ndata: \n\n; sseClie
@"
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

let db = null;
let messagesCol = null, kanbanCol = null;
let tarefasCol = null, fretesCol = null, agendaCol = null, docsCol = null;

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
    await messagesCol.createIndex({ id: 1 }, { unique: true });
    await messagesCol.createIndex({ ts: -1 });
    await kanbanCol.createIndex({ phone: 1 }, { unique: true });
    await tarefasCol.createIndex({ id: 1 }, { unique: true });
    await fretesCol.createIndex({ id: 1 }, { unique: true });
    await agendaCol.createIndex({ id: 1 }, { unique: true });
    await docsCol.createIndex({ id: 1 }, { unique: true });
    console.log('[DB] MongoDB Atlas conectado!');
  } catch(e) {
    console.error('[DB] Erro:', e.message);
    db=null; messagesCol=null; kanbanCol=null; tarefasCol=null; fretesCol=null; agendaCol=null; docsCol=null;
  }
}

let memMessages = [];
let memKanban = { colunas:['Novo Lead','Em Atendimento','Proposta','Fechado'], cards:[] };
let memTarefas=[], memFretes=[], memAgenda=[], memDocs=[];

function nowId() { return Date.now().toString(36)+Math.random().toString(36).slice(2,6); }
async function colFind(col,mem) { return col ? col.find({}).sort({ts:-1}).toArray() : [...mem]; }
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
  if(kanbanCol){ try{ await kanbanCol.updateOne({phone:card.phone},{$set:card,$setOnInsert:{ts:Date.now()}},{upsert:true}); }catch(e){} }
  else{ if(!memKanban.cards.find(c=>c.phone===card.phone)) memKanban.cards.unshift(card); }
}
async function updateKanbanColuna(id,coluna) {
  if(kanbanCol) await kanbanCol.updateOne({id},{$set:{coluna}});
  else{ const card=memKanban.cards.find(c=>c.id===id); if(card) card.coluna=coluna; }
}

const sseClients=[];
function broadcast(event,data){ const p=event: \ndata: \n\n; sseClients.forEach(r=>{try{r.write(p);}catch(e){}}); }
function cleanPhone(jid){ if(!jid)return''; return jid.replace('@s.whatsapp.net','').replace('@lid','').replace('@g.us','').trim(); }

async function callGroq(messages,max_tokens=500) {
  if(!GROQ_KEY) throw new Error('GROQ_KEY nao definida');
  const key=GROQ_KEY.replace(/[\x00-\x1F\x7F]/g,'');
  const payload=JSON.stringify({model:'llama3-8b-8192',messages,max_tokens,temperature:0.7});
  const options={hostname:'api.groq.com',path:'/openai/v1/chat/completions',method:'POST',headers:{'Content-Type':'application/json','Authorization':'Bearer '+key,'Content-Length':Buffer.byteLength(payload)}};
  return new Promise((resolve,reject)=>{
    const req=https.request(options,res=>{let d='';res.on('data',c=>d+=c);res.on('end',()=>{try{const j=JSON.parse(d);if(j.error)return reject(new Error(j.error.message));resolve(j.choices?.[0]?.message?.content||null);}catch(e){reject(e);}});});
    req.on('error',reject);req.write(payload);req.end();
  });
}

async function enviarMensagemWhatsApp(phone,texto) {
  const payload=JSON.stringify({number:phone,textMessage:{text:texto}});
  const url=new URL(${EVOLUTION_URL}/message/sendText/);
  const options={hostname:url.hostname,path:url.pathname,method:'POST',headers:{'Content-Type':'application/json','apikey':EVOLUTION_KEY,'Content-Length':Buffer.byteLength(payload)}};
  return new Promise(resolve=>{const req=https.request(options,res=>{let d='';res.on('data',c=>d+=c);res.on('end',()=>resolve(d));});req.on('error',e=>{console.error('Erro WA:',e.message);resolve(null);});req.write(payload);req.end();});
}

app.get('/',(req,res)=>res.sendFile(path.join(__dirname,'index.html')));

app.get('/health',async(req,res)=>{
  const msgs=await getMessages();const kanban=await getKanban();
  res.json({ok:true,db:db?'MongoDB Atlas':'Memoria',messages:msgs.length,cards:kanban.cards.length,groq:GROQ_KEY?'OK':'AUSENTE',uptime:Math.floor(process.uptime())+'s'});
});

app.get('/events',(req,res)=>{
  res.setHeader('Content-Type','text/event-stream');res.setHeader('Cache-Control','no-cache');res.setHeader('Connection','keep-alive');
  res.flushHeaders();res.write('event: connected\ndata: ok\n\n');sseClients.push(res);
  req.on('close',()=>{const i=sseClients.indexOf(res);if(i!==-1)sseClients.splice(i,1);});
});

app.post('/webhook',async(req,res)=>{
  const b=req.body;console.log('[WH] Evento:',b.event,JSON.stringify(b).substring(0,150));
  if(b.event==='messages.upsert'&&b.data){
    const m=b.data;
    if(m.key&&!m.key.fromMe){
      const texto=m.message?.conversation||m.message?.extendedTextMessage?.text||'[midia]';
      const msg={id:m.key.id||Date.now().toString(),name:m.pushName||'Desconhecido',phone:cleanPhone(m.key.remoteJid),text:texto,ts:Date.now()};
      await saveMessage(msg);broadcast('nova-mensagem',msg);console.log('[WH] Msg de',msg.name,':',msg.text.substring(0,60));
      if(texto!=='[midia]'){try{const r=await callGroq([{role:'system',content:'Voce e Beatriz, atendente virtual da MF Envios. Seja simpatica e objetiva. Quando pedirem cotacao pergunte: Peso, Medidas em cm, Volumes, Valor NF, CEP origem, CEP destino, coleta e urgencia. Responda em portugues sem markdown.'},{role:'user',content:texto}]);if(r){await enviarMensagemWhatsApp(msg.phone,r);const bm={id:'bot_'+Date.now(),name:'Beatriz (Bot)',phone:msg.phone,text:r,ts:Date.now()+1,fromBot:true};await saveMessage(bm);broadcast('nova-mensagem',bm);}}catch(e){console.error('[BOT] Erro:',e.message);}}
    }
  }
  res.json({ok:true});
});

app.get('/messages',async(req,res)=>{res.json(await getMessages());});
app.delete('/messages/:id',async(req,res)=>{await deleteMessage(req.params.id);res.json({ok:true});});
app.post('/send',async(req,res)=>{
  const{phone,text}=req.body;if(!phone||!text)return res.status(400).json({error:'phone e text obrigatorios'});
  await enviarMensagemWhatsApp(phone,text);
  const msg={id:'manual_'+Date.now(),name:'Voce (Manual)',phone,text,ts:Date.now(),manual:true};
  await saveMessage(msg);broadcast('nova-mensagem',msg);res.json({ok:true});
});

app.get('/kanban',async(req,res)=>{res.json(await getKanban());});
app.patch('/kanban/:id',async(req,res)=>{await updateKanbanColuna(req.params.id,req.body.coluna);broadcast('kanban-update',await getKanban());res.json({ok:true});});
app.post('/funil',async(req,res)=>{
  const{messageId}=req.body;const msgs=await getMessages();const msg=msgs.find(m=>m.id===messageId);
  if(!msg)return res.status(404).json({error:'nao encontrada'});
  const card={id:Date.now().toString(),name:msg.name,phone:msg.phone,coluna:'Novo Lead',ts:Date.now(),mensagens:[msg.text]};
  await upsertKanbanCard(card);broadcast('novo-lead',card);res.json({ok:true,kanban:await getKanban()});
});

app.post('/analisar',async(req,res)=>{
  const{mensagem}=req.body;if(!mensagem)return res.status(400).json({error:'vazio'});
  try{const txt=await callGroq([{role:'user',content:'Analise esta mensagem de frete e responda APENAS JSON sem markdown:{nome,tel,material,origem,destino,volumes,peso,medidas,valorNF,etapa,obs}. Etapa:Primeiro contato/Qualificacao/Proposta enviada/Negociacao/Fechado/Ganho/Perdido. Msg:'+mensagem}],500);const m=txt.match(/\{[\s\S]*\}/);if(!m)return res.status(500).json({error:'sem JSON'});res.json({ok:true,dados:JSON.parse(m[0])});}
  catch(e){res.status(500).json({error:e.message});}
});

app.get('/tarefas',async(req,res)=>{res.json(await colFind(tarefasCol,memTarefas));});
app.post('/tarefas',async(req,res)=>{const item={id:nowId(),ts:Date.now(),...req.body};await colUpsert(tarefasCol,memTarefas,item);res.json({ok:true,item});});
app.put('/tarefas/:id',async(req,res)=>{const item={id:req.params.id,ts:Date.now(),...req.body};await colUpsert(tarefasCol,memTarefas,item);res.json({ok:true,item});});
app.delete('/tarefas/:id',async(req,res)=>{await colDelete(tarefasCol,memTarefas,req.params.id);res.json({ok:true});});

app.get('/fretes',async(req,res)=>{res.json(await colFind(fretesCol,memFretes));});
app.post('/fretes',async(req,res)=>{const item={id:nowId(),ts:Date.now(),...req.body};await colUpsert(fretesCol,memFretes,item);res.json({ok:true,item});});
app.put('/fretes/:id',async(req,res)=>{const item={id:req.params.id,ts:Date.now(),...req.body};await colUpsert(fretesCol,memFretes,item);res.json({ok:true,item});});
app.delete('/fretes/:id',async(req,res)=>{await colDelete(fretesCol,memFretes,req.params.id);res.json({ok:true});});

app.get('/agenda',async(req,res)=>{res.json(await colFind(agendaCol,memAgenda));});
app.post('/agenda',async(req,res)=>{const item={id:nowId(),ts:Date.now(),...req.body};await colUpsert(agendaCol,memAgenda,item);res.json({ok:true,item});});
app.put('/agenda/:id',async(req,res)=>{const item={id:req.params.id,ts:Date.now(),...req.body};await colUpsert(agendaCol,memAgenda,item);res.json({ok:true,item});});
app.delete('/agenda/:id',async(req,res)=>{await colDelete(agendaCol,memAgenda,req.params.id);res.json({ok:true});});

app.get('/documentos',async(req,res)=>{res.json(await colFind(docsCol,memDocs));});
app.post('/documentos',async(req,res)=>{const item={id:nowId(),ts:Date.now(),...req.body};await colUpsert(docsCol,memDocs,item);res.json({ok:true,item});});
app.put('/documentos/:id',async(req,res)=>{const item={id:req.params.id,ts:Date.now(),...req.body};await colUpsert(docsCol,memDocs,item);res.json({ok:true,item});});
app.delete('/documentos/:id',async(req,res)=>{await colDelete(docsCol,memDocs,req.params.id);res.json({ok:true});});

const PORT=process.env.PORT||3000;
connectMongo().then(()=>{app.listen(PORT,'0.0.0.0',()=>{console.log([MF CRM] Porta );console.log([DB] Modo: );console.log([BOT] Groq: );});});
