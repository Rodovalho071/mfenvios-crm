lines = open('C:/mfcrm/index.html', encoding='utf-8').readlines()
for i, l in enumerate(lines):
    if 'tel' in l.lower() and ('input' in l.lower() or 'label' in l.lower()):
        print(i+1, l.rstrip()[:120])
