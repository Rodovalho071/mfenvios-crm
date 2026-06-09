const fs = require('fs');
let c = fs.readFileSync('public/index.html', 'utf8');
const linhasAntes = c.split('\n').length;

// Adicionar Valor do Frete no relatório
const busca = '<div class="lead-field"><label>Valor da NF</label><span>${l.valorNF';
const idx = c.indexOf(busca);
if (idx > -1) {
  const fechamento = c.indexOf('</div>\n      </div>', idx);
  const antes = c.substring(0, fechamento + 6);
  const depois = c.substring(fechamento + 6);
  const insercao = '\n        <div class="lead-field"><label style="color:#f97316">Frete</label><span style="color:#f97316;font-weight:700">${l.valorFrete ? "R$ "+l.valorFrete : "—"}</span></div>';
  c = antes + insercao + depois;
  console.log('Valor do Frete adicionado!');
} else {
  console.log('Valor do Frete já existe ou string não encontrada');
}

// Adicionar anotações
const buscaObs = "lead-obs";
const idxObs = c.lastIndexOf(buscaObs);
if (idxObs > -1) {
  const fimObs = c.indexOf("</div>`:''}", idxObs);
  if (fimObs > -1) {
    const insAno = `\n      \${(l.history||[]).filter(h=>h.text&&!h.text.includes('captado')&&!h.text.includes('Etapa:')).length?\`<div style="margin-top:8px;border-top:1px solid #e5e7eb;padding-top:8px"><div style="font-size:10px;color:#888;margin-bottom:4px">ANOTAÇÕES</div>\${(l.history||[]).filter(h=>h.text&&!h.text.includes('captado')&&!h.text.includes('Etapa:')).map(h=>\`<div style="font-size:12px;background:#f8fafc;padding:8px;border-radius:6px;margin-bottom:4px;border-left:3px solid #f97316">\${h.text}</div>\`).join('')}</div>\`:''}`;
    c = c.substring(0, fimObs + 11) + insAno + c.substring(fimObs + 11);
    console.log('Anotações adicionadas!');
  }
}

fs.writeFileSync('public/index.html', c, 'utf8');
console.log('Linhas antes:', linhasAntes, '| Depois:', c.split('\n').length);
