s=open('C:/mfcrm/public/index.html','r',encoding='utf-8').read()

JS_START='let funiMesOffset=0;'
JS_END='function renderKanban'

i1=s.find(JS_START)
i2=s.find(JS_END)
bloco=s[i1:i2]
print('Bloco encontrado:',len(bloco),'chars')

# Remove o bloco de onde estava
s=s[:i1]+s[i2:]

# Insere depois de 'let opTabAtual'
ANCHOR="let opTabAtual = 'fretes';"
if ANCHOR in s:
    s=s.replace(ANCHOR,ANCHOR+'\n'+bloco,1)
    print('OK: JS do funil movido para depois de opTabAtual')
else:
    print('ERRO: anchor nao encontrado')

open('C:/mfcrm/public/index.html','w',encoding='utf-8').write(s)
print('SALVO!')
