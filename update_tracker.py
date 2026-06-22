import json
with open('.brand-tracker.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)
for b in data['brands']:
    if b['name'] == '倍思':
        b['done'] = True
        name = b['name']
        print(f'Marked {name} as done')
with open('.brand-tracker.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('Tracker updated')
