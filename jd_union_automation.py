"""
京东联盟自动化 - 使用Playwright直接操控Edge浏览器
"""
import asyncio, json, sys, re, os
from playwright.async_api import async_playwright

CDP_URL = 'http://127.0.0.1:9222'
OUTPUT_FILE = r'C:\Users\yu\Desktop\earbuds-review\jd_links.json'

async def main():
    products_to_search = [
        # Apple series
        "苹果 AirPods Pro 2 USB-C",
        "苹果 AirPods 4 主动降噪",
        "苹果 AirPods 4 标准版",
        "苹果 AirPods Max",
        # Sony
        "索尼 WH-1000XM5",
        # Bose
        "Bose 博士 QC Ultra 大鲨",
        # OPPO
        "OPPO Enco Air 5 Pro",
        # 漫步者
        "漫步者 NeoBuds Pro 2",
        "漫步者 LolliPro 3",
        "漫步者 Comfo Run",
        "漫步者 X5 Pro",
        "漫步者 TWS1 Air 2",
        "漫步者 W820NB 双金标版",
        # 小米
        "小米 Buds 5 Pro",
        "小米 Buds 5",
        "Redmi Buds 6 Pro",
        "小米 Buds 5 半入耳版",
        "Redmi Buds 6",
    ]

    p = await async_playwright().__aenter__()
    browser = await p.chromium.connect_over_cdp(CDP_URL)
    context = browser.contexts[0]
    
    # Use new tab
    page = await context.new_page()
    
    all_links = {}
    
    for product_name in products_to_search:
        print(f"\n{'='*60}")
        print(f"🔍 搜索: {product_name}")
        
        try:
            await page.goto(
                f'https://union.jd.com/proManager/index?keywords={product_name}&pageNo=1',
                wait_until='domcontentloaded'
            )
            await asyncio.sleep(4)
            await page.wait_for_load_state('networkidle', timeout=15000)
            await asyncio.sleep(2)
            
            # Get page text
            text = await page.evaluate('() => document.body?.innerText || ""')
            
            # Check if search results loaded
            if '共' in text and '件商品' in text:
                # Extract product count
                match = re.search(r'共(\d+)件商品', text)
                count = match.group(1) if match else '?'
                print(f"   找到 {count} 件商品 (前5件)")
                
                # Show top products found
                lines = text.split('\n')
                products_found = []
                for i, line in enumerate(lines):
                    if any(kw in line for kw in ['到手价¥', '预估收益']):
                        # Get product name from surrounding text
                        if i > 0:
                            name_line = lines[i-1].strip()
                            if name_line and not name_line.startswith('预估') and not name_line.startswith('到手'):
                                products_found.append(name_line)
                
                for pf in products_found[:5]:
                    print(f"   - {pf[:80]}")
                
                # Store the first found product info
                all_links[product_name] = {
                    'results_count': count,
                    'products': products_found[:5],
                    'url': page.url
                }
            else:
                print(f"   未找到结果或页面未正确加载")
                all_links[product_name] = {'error': 'No results', 'text_preview': text[:300]}
                
        except Exception as e:
            print(f"   ❌ 错误: {str(e)}")
            all_links[product_name] = {'error': str(e)}
    
    # Save results
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_links, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 结果已保存到: {OUTPUT_FILE}")
    
    await page.close()
    await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
