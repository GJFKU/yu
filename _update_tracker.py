import json

path = r'C:\Users\yu\Desktop\earbuds-review\.brand-tracker.json'
with open(path) as f:
    data = json.load(f)

for b in data['brands']:
    if b['name'] == 'Beats':
        b['done'] = True
        print(f'Marked {b["name"]} as done')
        break

with open(path, 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print('Tracker updated.')
print(f'Remaining undone: {sum(1 for b in data["brands"] if not b["done"])}')
