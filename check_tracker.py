import json

with open(r'C:\Users\yu\Desktop\earbuds-review\.brand-tracker.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for b in data['brands']:
    status = 'DONE' if b['done'] else 'PENDING'
    print(f'{status}: {b["name"]}')

print(f'\nTotal: {len(data["brands"])} brands')
undone = sum(1 for b in data['brands'] if not b['done'])
print(f'Undone: {undone}')
if undone == 0:
    print('ALL BRANDS COMPLETED!')
