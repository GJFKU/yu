import urllib.request
import json
import re

url = 'https://shenzhenaudio.com/search?q=QoA&type=product'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=10) as f:
        html = f.read().decode('utf-8', errors='replace')
    
    # Find product titles in various patterns
    titles = re.findall(r'<h3[^>]*>([^<]+)</h3>', html)
    for t in titles:
        print(f"Title: {t.strip()}")
    
    # product-item class content
    items = re.findall(r'<div[^>]*class="[^"]*product-item[^"]*"[^>]*>', html)
    print(f"Product item divs: {len(items)}")
    
    # Find alt text in images (often product names)
    alts = re.findall(r'alt="([^"]+)"', html)
    for a in alts:
        if any(kw in a.lower() for kw in ['qoa', 'queen', 'adonis', 'vesper', 'aviation', 'mojito']):
            print(f"Alt: {a}")
    
    # Look for product card title spans 
    spans = re.findall(r'class="[^"]*card-title[^"]*"[^>]*>([^<]+)<', html)
    for s in spans:
        print(f"Card title: {s.strip()}")
    
    # Find script tags with product data
    scripts = re.findall(r'<script[^>]*>([^<]+QoA[^<]+)</script>', html)
    for s in scripts:
        print(f"Script: {s[:500]}")
    
    # Look for anything containing QoA in the HTML (case insensitive)
    qoa_mentions = re.findall(r'[^.]*QoA[^.]*\.', html, re.IGNORECASE)
    for m in qoa_mentions[:20]:
        clean = re.sub(r'<[^>]+>', '', m).strip()
        if clean:
            print(f"Mention: {clean[:200]}")
    
    print(f"HTML length: {len(html)} chars")
    
    # Save raw HTML for inspection
    with open(r'C:\Users\yu\Desktop\earbuds-review\qoa_search.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
except Exception as e:
    print(f"Error: {e}")
