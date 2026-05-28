const express = require('express');
const cors = require('cors');
const path = require('path');
const https = require('https');

const app = express();
app.use(cors());
app.use(express.json());

app.get('/', function(req, res) {
  res.sendFile(path.join(__dirname, 'index.html'));
});

let messages = [];
let kanban = {
  colunas: ['Novo Lead', 'Em Atendimento', 'Proposta', 'Fechado'],
  cards: []
};

function cleanPhone(jid) {
  if (!jid) return '';
  return jid.replace('@s.whatsapp.net', '').replace('@lid', '').replace('@g.us', '').trim();
}

async function responderComBeatriz(phone, texto) {
  const groqKey = process.env.GROQ_KEY;
  if (!groqKey) return;
  const payload = JSON.stringify({
    model: 'llama3-8b-8192',
    messages: [
      { role: 'system', content: 'Você é Beatriz, atendente virtual da MF Envios, transportadora especializada em fretes e logística. Seja simpática, profissional e objetiva. Sempre peça os dados para cotação: Peso, Medidas, Quantidade de volumes, Valor de NF, CEP origem, CEP destino, Coleta na origem, Tipo de Material, Urgência. Responda em português brasileiro.' },
      { role: 'user', content: texto }
    ],
    max_tokens: 500
  });
  const options = {
    hostname: 'api.groq.com',
    path: '/openai/v1/chat/completions',
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${groqKey}`, 'Content-Length': Buffer.byteLength(payload) }
  };
  return new Promise((resolve) => {
    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => { try { resolve(JSON.parse(data).choices?.[0]?.message?.content || null); } catch { resolve(null); } });
    });
    req.on('error', () => resolve(null));
    req.write(payload);
    req.end();
  });
}

async function enviarMensagemWhatsApp(phone, texto) {
  const evolutionUrl = process.env.EVOLUTION_URL || 'https://traps-ovary-sandy.ngrok-free.dev';
  const apiKey = process.env.EVOLUTION_APIKEY || 'mfenvios2024';
  const instancia = process.env.EVOLUTION_INSTANCE || 'mfenvios';
  const payload = JSON.stringify({ number: phone, textMessage: { text: texto } });
  const url = new URL(`${evolutionUrl}/message/sendText/${instancia}`);
  const options = {
    hostname: url.hostname,
    path: url.pathname,
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'apikey': apiKey, 'Content-Length': Buffer.byteLength(payload) }
  };
  return new Promise((resolve) => {
    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(data));
    });
    req.on('error', (e) => { console.error('Erro ao enviar:', e.message); resolve(null); });
    req.write(payload);
    req.end();
  });
}

const sseClients = [];
function broadcast(event, data) {
  const payload = `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`;
  sseClients.forEach(res => res.write(payload));
}

app.get('/events', (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.flushHeaders();
  res.write('event: connected\ndata: ok\n\n');
  sseClients.push(res);
  req.on('close', () => { const i = sseClients.indexOf(res); if (i !== -1) sseClients.splice(i, 1); });
});

app.post('/webhook', async (req, res) => {
  const b = req.body;
  console.log('Webhook recebido:', JSON.stringify(b).substring(0, 200));
  if (b.event === 'messages.upsert' && b.data) {
    const m = b.data;
    if (m.key && !m.key.fromMe) {
      const texto = m.message?.conversation || m.message?.extendedTextMessage?.text || '[midia]';
      const msg = { id: m.key.id || Date.now().toString(), name: m.pushName || 'Desconhecido', phone: cleanPhone(m.key.remoteJid), text: texto, ts: Date.now() };
      if (!messages.find(x => x.id === msg.id)) { messages.unshift(msg); if (messages.length > 500) messages = messages.slice(0, 500); }
      broadcast('nova-mensagem', msg);
      console.log('Nova mensagem:', msg.name, '-', msg.text);
      if (texto !== '[midia]') {
        try {
          const resposta = await responderComBeatriz(msg.phone, texto);
          if (resposta) { await enviarMensagemWhatsApp(msg.phone, resposta); console.log('Beatriz respondeu para', msg.phone); }
        } catch (e) { console.error('Erro Beatriz:', e.message); }
      }
    }
  }
  res.json({ ok: true });
});

app.get('/messages', (req, res) => { res.json(messages); });
app.delete('/messages/:id', (req, res) => { messages = messages.filter(m => m.id !== req.params.id); res.json({ ok: true }); });

app.post('/funil', (req, res) => {
  const { messageId } = req.body;
  const msg = messages.find(m => m.id === messageId);
  if (!msg) return res.status(404).json({ error: 'Mensagem nao encontrada' });
  const jaExiste = kanban.cards.find(c => c.phone === msg.phone);
  if (!jaExiste) { kanban.cards.unshift({ id: Date.now().toString(), name: msg.name, phone: msg.phone, coluna: kanban.colunas[0], ts: Date.now(), mensagens: [msg.text] }); broadcast('novo-lead', kanban.cards[0]); }
  res.json({ ok: true, kanban });
});

app.get('/kanban', (req, res) => { res.json(kanban); });
app.patch('/kanban/:id', (req, res) => {
  const { coluna } = req.body;
  const card = kanban.cards.find(c => c.id === req.params.id);
  if (!card) return res.status(404).json({ error: 'Card nao encontrado' });
  card.coluna = coluna;
  broadcast('kanban-update', kanban);
  res.json({ ok: true });
});

app.get('/health', (req, res) => { res.json({ ok: true, messages: messages.length, cards: kanban.cards.length }); });

const PORT = process.env.PORT || 3000;
app.listen(PORT, '0.0.0.0', () => console.log(`Servidor MF CRM rodando na porta ${PORT}`));
