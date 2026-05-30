import json

path = r'n8n\Trato Hecho - Chat Agent (2).json'
with open(path, encoding='utf-8') as f:
    wf = json.load(f)

MAP = {
    # (tipo, id_viejo): (id_nuevo, nombre_nuevo)
    ('redis',       '4ADNLvnpaQgNcFbA'): ('1B4cJUL85vbG4mJH', 'Redis - Trato Hecho'),
    ('httpHeaderAuth', 'nUlyMNdwPOejsLBT'): ('GoQq4Na0MeD7nLo1', 'Claude - Trato Hecho'),
    ('telegramApi', 'bvAxWV1D9HlkPRKc'): ('telegram-trato-hecho-001', 'Telegram Bot - Trato Hecho'),
}

count = 0
for node in wf['nodes']:
    creds = node.get('credentials', {})
    for ctype, cval in creds.items():
        key = (ctype, cval.get('id'))
        if key in MAP:
            new_id, new_name = MAP[key]
            cval['id'] = new_id
            cval['name'] = new_name
            count += 1
            print('  Corregido: {} | {} -> {}'.format(node['name'], key[1], new_id))

with open(path, 'w', encoding='utf-8') as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)

print('Total corregidos:', count)
