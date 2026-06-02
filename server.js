const express = require('express');
const cors = require('cors');
const path = require('path');
const https = require('https');
const { MongoClient } = require('mongodb');

const app = express();
app.use(cors());
app.use(express.json());

const GROQ_KEY = process.env.GROQ_KEY || '';
const MONGODB_URI = process.env.MONGODB_URI || '';
const EVOLUTION_URL = process.env.EVOLUTION_URL || 'https://traps-ovary-sandy.ngrok-free.dev';
const EVOLUTION_KEY = process.env.EVOLUTION_APIKEY || 'mfenvios2024';
const INSTANCE = process.env.EVOLUTION_INSTANCE || 'mfenvios';

let db = null, messagesCol = null, kanbanCol = null;

async function connectMongo() {
  if (!MONGODB_URI) { console.log('[DB] Sem MONGODB_URI - memoria'); return; }
  try {
    const client = new MongoClient(MONGODB_URI);
    await client.connect();
    db = client.db('mfenvios');
    messagesCol = db.collection('messages');
    kanbanCol = db.collection('kanban');
    await messagesCol.createIndex({ id: 1 }, { unique: true });
    await messagesCol.createIndex({ ts: -1 });
    await kanbanCol.createIndex({ phone: 1 }, { unique: true });
    console.log('[DB] MongoDB conectado!');
  } catch(e) { console.error('[DB] Erro:', e.message); db=null; messagesCol=null; kanbanCol=null; }
}

let memMessages = [];
let memKanban = { colunas: ['Novo Lead','Em Atendimento','Proposta','Fechado'], cards: [] };

async function getMessages() {
  if (messagesCol) return await messagesCol.find({}).sort({ts:-1}).limit(500).toArray();
  return memMessages;
}
async function saveMessage(msg) {
  if (messagesCol) { try { await messagesCol.updateOne({id:msg.id},{$set:msg},{upsert:true}); } catch(e){} }
  else { if (!memMessages.find(x=>x.id===msg.id)) { memMessages.unshift(msg); if(memMessages.length>500) memMessages=memMessages.slice(0,500); } }
}
async function deleteMessage(id) {
  if (messagesCol) await messagesCol.deleteOne({id});
  else memMessages = memMessages.filter(m=>m.id!==id);
}
async function getKanban() {
  if (kanbanCol) { const cards = await kanbanCol.find({}).sort({ts:-1}).toArray(); return {colunas:['Novo Lead','Em Atendimento','Proposta','Fechado'],cards}; }
  return memKanban;
}
async function upsertKanbanCard(card) {
  if (kanbanCol) { try { await kanbanCol.updateOne({phone:card.phone},{$set:card,$setOnInsert:{ts:Date.now()}},{upsert:true}); } catch(e){} }
  else { if (!memKanban.cards.find(c=>c.phone===card.phone)) memKanban.cards.unshift(card); }
}
async function updateKanbanColuna(id, coluna) {
  if (kanbanCol) await kanbanCol.updateOne({id},{$set:{coluna}});
  else { const card=memKanban.cards.find(c=>c.id===id); if(card) card.coluna=coluna; }
}

const sseClients = [];
function broadcast(event, data) {
  const payload = `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`;
  sseClients.forEach(res=>{ try{res.write(payload);}catch(e){} });
}

function cleanPhone(jid) {
  if (!jid) return '';
  return jid.replace('@s.whatsapp.net','').replace('@lid','').replace('@g.us','').trim();
}

async function responderComBeatriz(phone, texto) {
  if (!GROQ_KEY) return null;
  const payload = JSON.stringify({ model:'llama3-8b-8192', messages:[{role:'system',content:'Voce e Beatriz, atendente virtual da MF Envios, transportadora de fretes e logistica. Seja simpatica e objetiva. Quando pedirem cotacao pergunte: Peso, Medidas em cm, Quantidade de volumes, Valor de NF, CEP origem, CEP destino, coleta e urgencia. Responda em portugues brasileiro sem markdown.'},{role:'user',content:texto}], max_tokens:500 });
  const options = { hostname:'api.groq.com', path:'/openai/v1/chat/completions', method:'POST', headers:{'Content-Type':'application/json','Authorization':`Bearer ${GROQ_KEY}`,'Content-Length':Buffer.byteLength(payload)} };
  return new Promise(resolve=>{ const req=https.request(options,res=>{ let d=''; res.on('data',c=>d+=c); res.on('end',()=>{ try{resolve(JSON.parse(d).choices?.[0]?.message?.content||null);}catch{resolve(null);} }); }); req.on('error',()=>resolve(null)); req.write(payload); req.end(); });
}

async function enviarMensagemWhatsApp(phone, texto) {
  const payload = JSON.stringify({number:phone,textMessage:{text:texto}});
  const url = new URL(`${EVOLUTION_URL}/message/sendText/${INSTANCE}`);
  const options = { hostname:url.hostname, path:url.pathname, method:'POST', headers:{'Content-Type':'application/json','apikey':EVOLUTION_KEY,'Content-Length':Buffer.byteLength(payload)} };
  return new Promise(resolve=>{ const req=https.request(options,res=>{ let d=''; res.on('data',c=>d+=c); res.on('end',()=>resolve(d)); }); req.on('error',e=>{console.error('Erro WA:',e.message);resolve(null);}); req.write(payload); req.end(); });
}

app.get('/', (req,res) => res.sendFile(path.join(__dirname,'index.html')));

app.get('/events', (req,res) => {
  res.setHeader('Content-Type','text/event-stream');
  res.setHeader('Cache-Control','no-cache');
  res.setHeader('Connection','keep-alive');
  res.flushHeaders();
  res.write('event: connected\ndata: ok\n\n');
  sseClients.push(res);
  req.on('close',()=>{ const i=sseClients.indexOf(res); if(i!==-1) sseClients.splice(i,1); });
});

app.post('/webhook', async (req,res) => {
  const b = req.body;
  console.log('[WH] Evento:', b.event, JSON.stringify(b).substring(0,150));
  if (b.event==='messages.upsert' && b.data) {
    const m = b.data;
    if (m.key && !m.key.fromMe) {
      const texto = m.message?.conversation || m.message?.extendedTextMessage?.text || '[midia]';
      const msg = { id:m.key.id||Date.now().toString(), name:m.pushName||'Desconhecido', phone:cleanPhone(m.key.remoteJid), text:texto, ts:Date.now() };
      await saveMessage(msg);
      broadcast('nova-mensagem', msg);
      console.log('[WH] Msg de', msg.name, ':', msg.text.substring(0,60));
      if (texto!=='[midia]') {
        try {
          const resposta = await responderComBeatriz(msg.phone, texto);
          if (resposta) {
            await enviarMensagemWhatsApp(msg.phone, resposta);
            const botMsg = { id:'bot_'+Date.now(), name:'Beatriz (Bot)', phone:msg.phone, text:resposta, ts:Date.now()+1, fromBot:true };
            await saveMessage(botMsg);
            broadcast('nova-mensagem', botMsg);
          }
        } catch(e) { console.error('[BOT] Erro:', e.message); }
      }
    }
  }
  res.json({ok:true});
});

app.get('/messages', async (req,res) => { res.json(await getMessages()); });
app.delete('/messages/:id', async (req,res) => { await deleteMessage(req.params.id); res.json({ok:true}); });

app.post('/send', async (req,res) => {
  const {phone,text} = req.body;
  if (!phone||!text) return res.status(400).json({error:'phone e text obrigatorios'});
  await enviarMensagemWhatsApp(phone, text);
  const msg = {id:'manual_'+Date.now(),name:'Voce (Manual)',phone,text,ts:Date.now(),manual:true};
  await saveMessage(msg);
  broadcast('nova-mensagem', msg);
  res.json({ok:true});
});

app.get('/kanban', async (req,res) => { res.json(await getKanban()); });

app.post('/funil', async (req,res) => {
  const {messageId} = req.body;
  const msgs = await getMessages();
  const msg = msgs.find(m=>m.id===messageId);
  if (!msg) return res.status(404).json({error:'Mensagem nao encontrada'});
  const card = {id:Date.now().toString(),name:msg.name,phone:msg.phone,coluna:'Novo Lead',ts:Date.now(),mensagens:[msg.text]};
  await upsertKanbanCard(card);
  broadcast('novo-lead', card);
  res.json({ok:true, kanban: await getKanban()});
});

app.patch('/kanban/:id', async (req,res) => {
  await updateKanbanColuna(req.params.id, req.body.coluna);
  const kanban = await getKanban();
  broadcast('kanban-update', kanban);
  res.json({ok:true});
});

app.get('/health', async (req,res) => {
  const msgs = await getMessages();
  const kanban = await getKanban();
  res.json({ok:true, db: db ? 'MongoDB Atlas' : 'Memoria', messages:msgs.length, cards:kanban.cards.length, uptime:Math.floor(process.uptime())+'s'});
});


app.post('/analisar',async(req,res)=>{const{mensagem}=req.body;if(!mensagem)return res.status(400).json({error:'vazio'});if(!GROQ_KEY)return res.status(500).json({error:'sem GROQ_KEY'});const p=JSON.stringify({model:'llama3-8b-8192',messages:[{role:'user',content:'Analise esta mensagem de frete e responda APENAS JSON:{nome,tel,material,origem,destino,volumes,peso,medidas,valorNF,etapa,obs}. Etapa:Primeiro contato/Qualificacao/Proposta enviada/Negociacao/Fechado / Ganho/Perdido. Msg:'+mensagem}],max_tokens:500,temperature:0.1});const o={hostname:'api.groq.com',path:'/openai/v1/chat/completions',method:'POST',headers:{'Content-Type':'application/json','Authorization':'Bearer '+GROQ_KEY,'Content-Length':Buffer.byteLength(p)}};try{const d=await new Promise((res,rej)=>{const r=https.request(o,rp=>{let d='';rp.on('data',c=>d+=c);rp.on('end',()=>{try{const j=JSON.parse(d);const t=j.choices?.[0]?.message?.content||'';;const m=t.match(/\{[\s\S]*\}/);if(m)res(JSON.parse(m[0]));else rej(new Error('no json'));}catch(e){rej(e);}});});r.on('error',rej);r.write(p);r.end();});return res.json({ok:true,dados:d});}catch(e){res.status(500).json({error:e.message});}});
const PORT = process.env.PORT || 3000;
connectMongo().then(()=>{ app.listen(PORT,'0.0.0.0',()=>{ console.log(`[MF CRM] Porta ${PORT}`); console.log(`[DB] Modo: ${db?'MongoDB Atlas':'Memoria'}`); }); });
/ /   t r i m   f i x  
 