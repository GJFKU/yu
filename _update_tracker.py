import json

with open('.brand-tracker.json', 'r') as f:
    tracker = json.load(f)

# Mark Beats as done
for brand in tracker['brands']:
    if brand['name'] == 'Beats':
        brand['done'] = True
        print(f'Marked {brand["name"]} as done')
        break

with open('.brand-tracker.json', 'w') as f:
    json.dump(tracker, f, ensure_ascii=False, indent=2)

# Show next undone
for brand in tracker['brands']:
    if not brand['done']:
        print(f'Next brand: {brand["name"]}')
        break
else:
    print('ALL DONE')
