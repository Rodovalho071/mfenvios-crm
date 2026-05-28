const express = require('express');
const cors = require('cors');
const fs = require('fs');

const app = express();
app.use(cors());
app.use(express.json());

const DATA_FILE = 'C:/mfcrm/messages.json';
const KANBAN_FILE = 'C:/mfcrm/kanban.json';

// ─── Helpers ────────────────────────────────────────────────────────────────

function cleanPhone(jid) {
  if (!jid) return '';
  return jid
    .replace('@s.whatsapp.net', '')
    .replace('@lid', '')
    .replace('@g.us', '')
    .trim();
}

function loadMessages() {
  try { return JSON.parse(fs.readFileSync(DATA_FILE, 'utf8')); }
  catch (e) { return []; }
}

function saveMessages(msgs) {
  fs.writeFileSync(DATA_FILE, JSON.stringify(msgs));
}

function loadKanban() {
  try { return JSON.parse(fs.readFileSync(KANBAN_FILE, 'utf8')); }
  catch (e) { return { colunas: ['Novo Lead', 'Em Atendimento', 'Proposta', 'Fechado'] , cards: [] }; }
}

function saveKanban(data) {
  fs.writeFileSync(KANBAN_FILE, JSON.stringify(data));
}

// ─── SSE — clientes conectados para tempo real ───────────────────────────────

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
  req.on('close', () => {
    const i = sseClients.indexOf(res);
    if (i !== -1) sseClients.splice(i, 1);
  });
});

// ─── Webhook Evolution API ───────────────────────────────────────────────────

app.post('/webhook', (req, res) => {
  const b = req.body;

  if (b.event === 'messages.upsert' && b.data) {
    const m = b.data;
    if (m.key && !m.key.fromMe) {
      const messages = loadMessages();
      const msg = {
        id: m.key.id,
        name: m.pushName || 'Desconhecido',
        phone: cleanPhone(m.key.remoteJid),   // ← limpa @lid e @s.whatsapp.net
        text: m.message?.conversation
           || m.message?.extendedTextMessage?.text
           || '[mídia]',
        ts: Date.now()
      };
      messages.unshift(msg);
      saveMessages(messages);
      broadcast('nova-mensagem', msg);         // ← tempo real para o browser
      console.log('Nova mensagem:', msg.name, '-', msg.text);
    }
  }

  res.json({ ok: true });
});

// ─── Mensagens ───────────────────────────────────────────────────────────────

app.get('/messages', (req, res) => {
  res.json(loadMessages());
});

app.delete('/messages/:id', (req, res) => {
  const msgs = loadMessages().filter(m => m.id !== req.params.id);
  saveMessages(msgs);
  res.json({ ok: true });
});

// ─── Funil / Kanban ──────────────────────────────────────────────────────────

// Adicionar lead ao kanban a partir de uma mensagem
app.post('/funil', (req, res) => {
  const { messageId } = req.body;
  const messages = loadMessages();
  const msg = messages.find(m => m.id === messageId);
  if (!msg) return res.status(404).json({ error: 'Mensagem não encontrada' });

  const kanban = loadKanban();
  const jaExiste = kanban.cards.find(c => c.phone === msg.phone);
  if (!jaExiste) {
    kanban.cards.unshift({
      id: Date.now().toString(),
      name: msg.name,
      phone: msg.phone,
      coluna: kanban.colunas[0],
      ts: Date.now(),
      mensagens: [msg.text]
    });
    saveKanban(kanban);
    broadcast('novo-lead', kanban.cards[0]);
  }
  res.json({ ok: true, kanban });
});

// Listar kanban
app.get('/kanban', (req, res) => {
  res.json(loadKanban());
});

// Mover card entre colunas
app.patch('/kanban/:id', (req, res) => {
  const { coluna } = req.body;
  const kanban = loadKanban();
  const card = kanban.cards.find(c => c.id === req.params.id);
  if (!card) return res.status(404).json({ error: 'Card não encontrado' });
  card.coluna = coluna;
  saveKanban(kanban);
  broadcast('kanban-update', kanban);
  res.json({ ok: true });
});

// ─── Start ───────────────────────────────────────────────────────────────────

app.listen(3000, '0.0.0.0', () =>
  console.log('Servidor MF CRM rodando na porta 3000'));
 
