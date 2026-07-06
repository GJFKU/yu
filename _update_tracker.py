import json
path = r'C:\Users\yu\Desktop\earbuds-review\.brand-tracker.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)
for b in data['brands']:
    if b['name'] == '粤声':
        b['done'] = True
        print('Marked 粤声 as done')
        break
with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('Tracker updated')
