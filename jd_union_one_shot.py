"""
京东联盟一站式：搜索商品 -> 一键领链 -> 获取推广链接
使用已有Edge浏览器连接，保持连接不中断
"""
import asyncio, json, sys, re, os
from playwright.async_api import async_playwright

CDP = 'http://127.0.0.1:9222'

SEARCHES = [
    "Apple AirPods Pro 2",
    "Apple AirPods 4 主动降噪",
    "Apple AirPods 4",
    "Apple AirPods Max",
    "索尼 WH-1000XM5",
    "Bose QC Ultra Earbuds",
    "OPPO Enco Air 5 Pro",
    "漫步者 NeoBuds Pro 2",
    "漫步者 LolliPro 3",
    "漫步者 Comfo Run",
    "漫步者 X5 Pro",
    "漫步者 TWS1 Air 2",
    "漫步者 W820NB 双金标",
    "小米 Buds 5 Pro",
    "小米 Buds 5",
    "Redmi Buds 6 Pro",
    "小米 Buds 5 半入耳",
    "Redmi Buds 6",
]

async def main():
    p = await async_playwright().__aenter__()
    b = await p.chromium.connect_over_cdp(CDP)
    ctx = b.contexts[0]
    page = ctx.pages[0]  # Use existing tab
    
    results = {}
    
    for keyword in SEARCHES:
        short_name = keyword[:20]
        print(f"\n{'='*50}")
        print(f"🔍 [{short_name}]")
        
        try:
            # Navigate to search page on JD Union
            url = f'https://union.jd.com/proManager/index?keywords={keyword}&pageNo=1'
            await page.goto(url, wait_until='domcontentloaded', timeout=15000)
            await asyncio.sleep(4)
            try:
                await page.wait_for_load_state('networkidle', timeout=10000)
            except:
                pass
            await asyncio.sleep(2)
            
            # Get visible text for debugging
            text = await page.evaluate('() => document.body?.innerText || ""')
            count_match = re.search(r'共(\d+)件商品', text)
            count = count_match.group(1) if count_match else '?'
            
            lines = text.split('\n')
            
            # Check if "一键领链" buttons exist
            has_onekey = '一键领链' in text
            
            # Find first relevant product name
            first_product = ''
            for i, line in enumerate(lines):
                if '到手价¥' in line:
                    for j in range(i-3, i):
                        if j >= 0:
                            n = lines[j].strip()
                            if n and len(n) > 3 and '预估' not in n and '佣金' not in n:
                                first_product = n[:60]
                                break
                    if first_product:
                        break
            
            print(f"   共{count}件 | 一键领链:{'✓' if has_onekey else '✗'}")
            if first_product:
                print(f"   首件: {first_product}")
            
            results[keyword] = {
                'count': count,
                'has_onekey': has_onekey,
                'first_product': first_product,
                'url': page.url
            }
            
        except Exception as e:
            print(f"   ❌ {e}")
            results[keyword] = {'error': str(e)}
    
    out = r'C:\Users\yu\Desktop\earbuds-review\jd_search_all.json'
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 结果: {out}")
    
    await b.close()

if __name__ == '__main__':
    asyncio.run(main())
