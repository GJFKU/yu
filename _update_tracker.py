import json

with open(r'C:\Users\yu\Desktop\earbuds-review\.brand-tracker.json', 'r') as f:
    data = json.load(f)

# Mark 韶音 as done (article already exists)
for brand in data['brands']:
    if brand['name'] == '韶音':
        brand['done'] = True
        break

# Show next undone brand
for b in data['brands']:
    if not b['done']:
        print(f'Next brand: {b["name"]}')
        break

with open(r'C:\Users\yu\Desktop\earbuds-review\.brand-tracker.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('Tracker updated - 韶音 marked as done')
