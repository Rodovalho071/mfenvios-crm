with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Corrigir stageOpts no renderLeadModal para usar etapas do perfil correto
old = "  const stageOpts=STAGES.map(s=>`<option value=\"${s}\" ${s===l.stage?'selected':''}>${s}</option>`).join('');"

new = """  // Usar etapas do perfil do lead (ou do perfil ativo)
  var _leadAgent=(l.agent||'').toLowerCase();
  var _stagesModal;
  if(_leadAgent==='davi'||(_leadAgent===''&&perfilAtivo==='davi')){
    _stagesModal=PERFIS.davi.stages;
  } else if(_leadAgent==='beatriz'||(_leadAgent===''&&perfilAtivo==='beatriz')){
    _stagesModal=PERFIS.beatriz.stages;
  } else {
    // Incluir etapas dos dois perfis para não perder nenhuma
    _stagesModal=[...new Set([...PERFIS.beatriz.stages,...PERFIS.davi.stages])];
  }
  // Garantir que a etapa atual do lead aparece mesmo que não esteja na lista
  if(l.stage && !_stagesModal.includes(l.stage)) _stagesModal=[l.stage,..._stagesModal];
  const stageOpts=_stagesModal.map(s=>`<option value="${s}" ${s===l.stage?'selected':''}>${s}</option>`).join('');"""

if old in html:
    html = html.replace(old, new)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('OK - modal mostra etapas corretas por perfil')
    print('git add index.html && git commit -m "fix: etapas corretas no modal por perfil" && git push origin main')
else:
    print('X - stageOpts nao encontrado')
