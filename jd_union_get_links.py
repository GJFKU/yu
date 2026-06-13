"""
京东联盟: 在已登录的Edge浏览器中搜索商品并获取推广链接
"""
import asyncio, json, sys, re
from playwright.async_api import async_playwright

PRODUCTS = [
    "苹果 AirPods Pro 2 USB-C",
    "苹果 AirPods 4 主动降噪版",
    "苹果 AirPods 4 标准版",
    "苹果 AirPods Max",
    "索尼 WH-1000XM5",
    "Bose QC Ultra Earbuds",
    "OPPO Enco Air 5 Pro",
    "漫步者 NeoBuds Pro 2",
    "漫步者 LolliPro 3",
    "漫步者 Comfo Run",
    "漫步者 X5 Pro",
    "漫步者 TWS1 Air 2",
    "漫步者 W820NB 双金标版",
    "小米 Buds 5 Pro",
    "小米 Buds 5",
    "Redmi Buds 6 Pro",
    "小米 Buds 5 半入耳版",
    "Redmi Buds 6",
]

async def search_one(page, keyword):
    """Search for a product in JD Union and return page text"""
    await page.goto(
        f'https://union.jd.com/proManager/index?keywords={keyword}&pageNo=1',
        wait_until='domcontentloaded'
    )
    await asyncio.sleep(3)
    try:
        await page.wait_for_load_state('networkidle', timeout=15000)
    except:
        pass
    await asyncio.sleep(2)
    
    text = await page.evaluate('() => document.body?.innerText || ""')
    title = await page.title()
    url = page.url
    return {'text': text, 'title': title, 'url': url}

async def main():
    p = await async_playwright().__aenter__()
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    context = browser.contexts[0]
    
    # Use existing tab 0 (JD union page)
    page = context.pages[0]
    
    results = {}
    
    for keyword in PRODUCTS:
        print(f"\n{'='*50}")
        print(f"🔍 搜索: {keyword}")
        try:
            data = await search_one(page, keyword)
            text = data['text']
            
            # Parse products from text
            lines = text.split('\n')
            
            # Extract products with prices 
            products_found = []
            for i, line in enumerate(lines):
                if '到手价¥' in line:
                    # Get product name from previous non-empty lines
                    for j in range(i-3, i):
                        if j >= 0 and lines[j].strip():
                            name = lines[j].strip()
                            if name and len(name) > 3 and not name.startswith('预估') and not name.startswith('佣金') and not name.startswith('京东'):
                                products_found.append(name)
                            break
            
            # Show top results
            print(f"   找到相关商品:")
            for pf in products_found[:3]:
                print(f"   • {pf[:80]}")
            
            # Check count
            count_match = re.search(r'共(\d+)件商品', text)
            count = count_match.group(1) if count_match else '?'
            print(f"   共 {count} 件商品")
            
            results[keyword] = {
                'count': count,
                'top_products': products_found[:3],
                'url': data['url']
            }
            
        except Exception as e:
            print(f"   ❌ 错误: {e}")
            results[keyword] = {'error': str(e)}
    
    # Save results
    out = r'C:\Users\yu\Desktop\earbuds-review\jd_search_results.json'
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 结果保存至: {out}")
    
    # Keep browser open
    await p.stop()

if __name__ == '__main__':
    asyncio.run(main())
