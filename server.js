const express = require('express');
const cors = require('cors');
const https = require('https');
const app = express();
app.use(cors());
app.use(express.json());

const GROQ_KEY = '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';
const EVOLUTION_KEY = 'mfenvios2024';
const INSTANCE = 'mfenvios';

const SYSTEM_PROMPT = 'Voce e um assistente virtual da MF Envios, empresa de transporte e logistica. Responda de forma profissional e objetiva em portugues brasileiro. Quando pedirem cotacao, pergunte: peso, medidas em cm, quantidade de volumes, valor da nota fiscal, CEP de origem, CEP de destino, se precisa de coleta e urgencia. Respostas curtas e sem formatacao markdown.';

var messages = [];
var botConfig = { botAtivo: true, pausados: {} };
var conversas = {};
var kanban = { colunas: ['Novo Lead','Em Contato','Proposta Enviada','Fechado','Perdido'], cards: [] };

function chamarGroq(historico, cb) {
  var body = JSON.stringify({ model:'llama3-8b-8192', messages:[{role:'system',content:SYSTEM_PROMPT}].concat(historico), max_tokens:300, temperature:0.7 });
  var opts = { hostname:'api.groq.com', path:'/openai/v1/chat/completions', method:'POST', headers:{'Content-Type':'application/json','Authorization':'Bearer '+GROQ_KEY,'Content-Length':Buffer.byteLength(body)} };
  var req = https.request(opts, function(res){ var d=''; res.on('data',function(c){d+=c;}); res.on('end',function(){ try{ cb(null,JSON.parse(d).choices[0].message.content.trim()); }catch(e){cb(e,null);} }); });
  req.on('error',function(e){cb(e,null);});
  req.write(body); req.end();
}

app.post('/webhook', function(req, res) {
  try {
    var b = req.body;
    var data = b.data || b;
    var key = data.key || {};
    if (key.fromMe) return res.json({ok:true});
    var phone = (key.remoteJid||'').replace('@s.whatsapp.net','').replace('@lid','');
    var name = data.pushName || 'Desconhecido';
    var msgObj = data.message || {};
    var text = msgObj.conversation || (msgObj.extendedTextMessage && msgObj.extendedTextMessage.text) || null;
    if (!text || !phone) return res.json({ok:true});
    messages.unshift({id:Date.now().toString(), name:name, phone:phone, text:text, ts:Date.now()});
    if (messages.length > 500) messages = messages.slice(0,500);
    console.log('Nova mensagem:', name, '-', text.substring(0,50));
    if (botConfig.botAtivo && !botConfig.pausados[phone]) {
      if (!conversas[phone]) conversas[phone] = [];
      conversas[phone].push({role:'user',content:text});
      if (conversas[phone].length > 20) conversas[phone] = conversas[phone].slice(-20);
      chamarGroq(conversas[phone], function(err, resposta) {
        if (!err && resposta) {
          conversas[phone].push({role:'assistant',content:resposta});
          console.log('[BOT] Resposta para', name, ':', resposta.substring(0,60));
        }
      });
    }
    res.json({ok:true});
  } catch(e) {
    console.error('Erro webhook:', e.message);
    res.status(500).json({error:e.message});
  }
});

app.get('/messages', function(req,res){ res.json(messages); });
app.delete('/messages/:id', function(req,res){ messages=messages.filter(function(m){return m.id!==req.params.id;}); res.json({ok:true}); });
app.get('/bot/status', function(req,res){ res.json(botConfig); });
app.post('/bot/toggle', function(req,res){ botConfig.botAtivo=!botConfig.botAtivo; res.json(botConfig); });
app.post('/bot/pausar/:phone', function(req,res){ botConfig.pausados[req.params.phone]=true; res.json({ok:true}); });
app.post('/bot/retomar/:phone', function(req,res){ delete botConfig.pausados[req.params.phone]; res.json({ok:true}); });
app.get('/kanban', function(req,res){ res.json(kanban); });
app.post('/funil', function(req,res){
  var msg = messages.find(function(m){return m.id===req.body.messageId;});
  if (!msg) return res.status(404).json({error:'nao encontrado'});
  if (!kanban.cards.some(function(c){return c.phone===msg.phone;})) {
    kanban.cards.unshift({id:Date.now().toString(),name:msg.name,phone:msg.phone,coluna:kanban.colunas[0],ts:Date.now()});
  }
  res.json({ok:true,kanban:kanban});
});
app.patch('/kanban/:id', function(req,res){
  var card=kanban.cards.find(function(c){return c.id===req.params.id;});
  if (card) card.coluna=req.body.coluna;
  res.json({ok:true});
});

var PORT = process.env.PORT || 3000;
app.listen(PORT, '0.0.0.0', function(){ console.log('Servidor MF CRM rodando na porta '+PORT); });
