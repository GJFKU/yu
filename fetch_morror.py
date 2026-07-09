import requests, re, json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Try Amazon search
try:
    r = requests.get('https://www.amazon.com/s?k=MORRORART', headers=headers, timeout=10)
    if r.status_code == 200:
        titles = re.findall(r'<span[^>]*class="a-size-medium[^"]*"[^>]*>(.*?)</span>', r.text, re.DOTALL)
        for t in titles:
            clean = re.sub(r'<[^>]+>', '', t).strip()
            if clean:
                print(f'Product: {clean}')
except Exception as e:
    print(f'Amazon error: {e}')

# Try tmall search
try:
    r = requests.get('https://list.tmall.com/search_product.htm?q=MORROR+ART', headers=headers, timeout=10)
    if r.status_code == 200:
        print(f'tmall status: {r.status_code}, len: {len(r.text)}')
except Exception as e:
    print(f'tmall error: {e}')

# Try jd search
try:
    r = requests.get('https://search.jd.com/Search?keyword=MORROR%20ART&enc=utf-8', headers=headers, timeout=10)
    if r.status_code == 200:
        print(f'jd status: {r.status_code}, len: {len(r.text)}')
        # look for product names
        names = re.findall(r'<em[^>]*class="sku-name"[^>]*>(.*?)</em>', r.text, re.DOTALL)
        for n in names[:10]:
            clean = re.sub(r'<[^>]+>', '', n).strip()
            if clean:
                print(f'JD product: {clean}')
except Exception as e:
    print(f'jd error: {e}')

# Try baidu search
try:
    r = requests.get('https://www.baidu.com/s?wd=MORROR+ART+蓝牙耳机', headers=headers, timeout=10)
    if r.status_code == 200:
        print(f'baidu status: {r.status_code}, len: {len(r.text)}')
except Exception as e:
    print(f'baidu error: {e}')

# Try smzdm
try:
    r = requests.get('https://search.smzdm.com/?c=home&s=MORROR+ART', headers=headers, timeout=10)
    if r.status_code == 200:
        print(f'smzdm status: {r.status_code}, len: {len(r.text)}')
except Exception as e:
    print(f'smzdm error: {e}')
