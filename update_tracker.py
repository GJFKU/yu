import json

path = r'C:\Users\yu\Desktop\earbuds-review\.brand-tracker.json'
with open(path, encoding='utf-8') as f:
    data = json.load(f)

for brand in data['brands']:
    if brand['name'] == 'IKF':
        brand['done'] = True
        print(f'Marked {brand["name"]} as done')
        break

with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('Tracker updated')
