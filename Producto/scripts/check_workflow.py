import json
with open(r'n8n\Trato Hecho - Chat Agent (2).json', encoding='utf-8') as f:
    wf = json.load(f)

conns = wf['connections']
print('=== CONNECTIONS ===')
for src, targets in conns.items():
    for branch_idx, branch in enumerate(targets.get('main', [])):
        for t in branch:
            dest = t['node']
            print('  {} --[{}]--> {}'.format(src, branch_idx, dest))

# Also check webhook node response mode
print()
print('=== WEBHOOK NODE ===')
for n in wf['nodes']:
    if 'webhook' in n['type'].lower() and n['name'] == 'Webhook Chat':
        print(json.dumps(n['parameters'], indent=2))

# Check Respuesta Simple node
print()
print('=== RESPUESTA SIMPLE ===')
for n in wf['nodes']:
    if n['name'] == 'Respuesta Simple':
        print(json.dumps(n['parameters'], indent=2))

# Check Responder Webhook (Simple) node
print()
print('=== RESPONDER WEBHOOK SIMPLE ===')
for n in wf['nodes']:
    if 'Simple' in n['name'] and 'Responder' in n['name']:
        print(json.dumps(n['parameters'], indent=2))
