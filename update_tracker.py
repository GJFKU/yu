import json

f = r'C:\Users\yu\Desktop\earbuds-review\.brand-tracker.json'
data = json.load(open(f, encoding='utf-8'))
for b in data['brands']:
    if b['name'] == '瓷音未来':
        b['done'] = True
        print('Marked', b['name'], 'as done')
        break

with open(f, 'w', encoding='utf-8') as fh:
    json.dump(data, fh, ensure_ascii=False, indent=2)
print('Tracker updated')
