lines = open('C:/mfcrm/index.html', encoding='utf-8').readlines()
out = open('C:/mfcrm/resultado.txt', 'w', encoding='utf-8')
for i, l in enumerate(lines[1099:1137]):
    out.write(str(i+1100) + ' ' + l[:250])
out.close()
