import json

with open('.brand-tracker.json', 'r') as f:
    tracker = json.load(f)

# Mark 三星 as done
marked = False
for brand in tracker['brands']:
    if brand['name'] == '三星':
        brand['done'] = True
        marked = True
        print(f'Marked {brand["name"]} as done')
        break

if not marked:
    print('Brand 三星 not found!')
    
with open('.brand-tracker.json', 'w') as f:
    json.dump(tracker, f, ensure_ascii=False, indent=2)

# Show remaining
remaining = [b['name'] for b in tracker['brands'] if not b['done']]
print(f'Remaining: {len(remaining)} brands')
for r in remaining:
    print(f'  - {r}')
