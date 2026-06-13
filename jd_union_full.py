"""
京东联盟完整自动化 - 持续连接Edge，搜索商品，获取推广链接
"""
import asyncio, json, sys, re, os
from playwright.async_api import async_playwright

CDP_URL = 'http://127.0.0.1:9222'
RESULTS_FILE = r'C:\Users\yu\Desktop\earbuds-review\jd_links_result.json'

# Product search keywords
SEARCH_QUERIES = {
    "AirPods Pro 2": "苹果 AirPods Pro 2 USB-C",
    "AirPods 4(降噪版)": "苹果 AirPods 4 主动降噪", 
    "AirPods 4(标准版)": "苹果 AirPods 4 标准版",
    "AirPods Max": "苹果 AirPods Max",
    "Sony WH-1000XM5": "索尼 WH-1000XM5 头戴式",
    "Bose QC Ultra": "Bose QC Ultra Earbuds",
    "OPPO Enco Air 5 Pro": "OPPO Enco Air 5 Pro",
    "漫步者 NeoBuds Pro 2": "漫步者 NeoBuds Pro 2",
    "漫步者 LolliPro 3": "漫步者 LolliPro 3",
    "漫步者 Comfo Run": "漫步者 Comfo Run 开放式",
    "漫步者 X5 Pro": "漫步者 X5 Pro",
    "漫步者 TWS1 Air 2": "漫步者 TWS1 Air 2",
    "漫步者 W820NB": "漫步者 W820NB 双金标",
    "小米 Buds 5 Pro": "小米 Buds 5 Pro",
    "小米 Buds 5": "小米 Buds 5 入耳式",
    "Redmi Buds 6 Pro": "Redmi Buds 6 Pro",
    "小米 Buds 5(半入耳版)": "小米 Buds 5 半入耳",
    "Redmi Buds 6": "Redmi Buds 6",
}

async def get_promotion_links():
    p = await async_playwright().__aenter__()
    browser = await p.chromium.connect_over_cdp(CDP_URL)
    context = browser.contexts[0]
    page = context.pages[0]  # Use the existing JD union tab
    
    results = {}
    
    for prod_label, search_term in SEARCH_QUERIES.items():
        print(f"\n{'='*60}")
        print(f"[{prod_label}] 搜索: {search_term}")
        
        try:
            # Navigate to search results
            url = f'https://union.jd.com/proManager/index?keywords={search_term}&pageNo=1'
            await page.goto(url, wait_until='domcontentloaded')
            await asyncio.sleep(3)
            
            # Wait for data to load
            try:
                await page.wait_for_load_state('networkidle', timeout=15000)
            except:
                pass
            await asyncio.sleep(2)
            
            # Get all visible product data from the DOM
            html = await page.content()
            text = await page.evaluate('() => document.body?.innerText || ""')
            
            # Parse products: find all "到手价¥..." occurrences with context
            products = []
            lines = text.split('\n')
            
            for i, line in enumerate(lines):
                # Check for "一键领链" / "我要推广" buttons = this is a product row
                if '我要推广' in line or '一键领链' in line:
                    # Go backwards to find product info
                    product_name = ''
                    price = ''
                    for j in range(i-1, max(0, i-6), -1):
                        l = lines[j].strip()
                        if not l:
                            continue
                        if '到手价¥' in l:
                            price = l
                        elif l.startswith('预估收益') or l.startswith('佣金比例'):
                            continue
                        elif '好评' in l:
                            continue
                        elif l in ['超级补贴', '自营', '百亿补贴', '京配', 'PLUS', '定向', '券', '促销', '便宜包邮', '星选', '奖励']:
                            continue
                        elif l and len(l) > 5 and '京东' not in l and not l.startswith('¥'):
                            product_name = l
                            break
                    
                    if product_name:
                        products.append({
                            'name': product_name,
                            'price': price,
                            'has_link_btn': True
                        })
            
            # Remove duplicates (keep unique product names)
            seen = set()
            unique_products = []
            for p in products:
                if p['name'] not in seen:
                    seen.add(p['name'])
                    unique_products.append(p)
            
            print(f"  找到 {len(unique_products)} 个商品:")
            for p in unique_products[:5]:
                print(f"  • {p['name'][:60]} | {p['price'][:30] if p['price'] else 'N/A'}")
            
            results[prod_label] = {
                'search_term': search_term,
                'product_count': len(unique_products),
                'top_products': unique_products[:5],
                'url': page.url
            }
            
        except Exception as e:
            print(f"  ❌ 错误: {e}")
            results[prod_label] = {'error': str(e)}
    
    # Save results
    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 结果已保存: {RESULTS_FILE}")
    await p.stop()

if __name__ == '__main__':
    asyncio.run(get_promotion_links())
