"""
京东联盟搜索 - 使用Playwright完整API进行搜索操作
保持单一连接，每个操作等待页面加载
"""
import asyncio, json, sys, re, os
from playwright.async_api import async_playwright

CDP = 'http://127.0.0.1:9222'

SEARCH_TERMS = [
    "苹果 AirPods Pro 2",
    "苹果 AirPods 4 主动降噪",
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
    "漫步者 W820NB",
    "小米 Buds 5 Pro",
    "小米 Buds 5",
    "Redmi Buds 6 Pro",
    "小米 Buds 5 半入耳版",
    "Redmi Buds 6",
]

async def main():
    p = await async_playwright().__aenter__()
    b = await p.chromium.connect_over_cdp(CDP)
    ctx = b.contexts[0]
    
    # Use a fresh page to avoid SPA state issues
    page = await ctx.new_page()
    
    # Navigate to base product page first
    await page.goto('https://union.jd.com/proManager/index', 
                    wait_until='domcontentloaded', timeout=15000)
    await asyncio.sleep(4)
    try:
        await page.wait_for_load_state('networkidle', timeout=10000)
    except:
        pass
    await asyncio.sleep(2)
    
    results = {}
    
    for keyword in SEARCH_TERMS:
        print(f"\n{'='*50}")
        print(f"🔍 {keyword}")
        
        try:
            # Find and fill search input
            search_input = await page.query_selector('.el-input__inner[placeholder*="商品名称"]')
            if not search_input:
                print("   ❌ 找不到搜索框")
                continue
            
            await search_input.click()
            await search_input.fill('')
            await asyncio.sleep(0.5)
            await search_input.type(keyword, delay=30)
            await asyncio.sleep(0.5)
            
            # Press Enter to search
            await page.keyboard.press('Enter')
            await asyncio.sleep(4)
            try:
                await page.wait_for_load_state('networkidle', timeout=10000)
            except:
                pass
            await asyncio.sleep(2)
            
            # Get results
            text = await page.evaluate('() => document.body?.innerText || ""')
            
            count_match = re.search(r'共(\d+)件商品', text)
            count = count_match.group(1) if count_match else '0'
            
            # Check for products
            has_products = '我要推广' in text or '一键领链' in text
            has_no_results = '没有找到相关商品' in text
            
            # Find first product name
            first_product = ''
            lines = text.split('\n')
            for i, line in enumerate(lines):
                if '到手价¥' in line:
                    for j in range(i-3, i):
                        if j >= 0:
                            n = lines[j].strip()
                            if n and len(n) > 3 and '预估' not in n and '佣金' not in n and '好评' not in n:
                                first_product = n[:60]
                                break
                    break
            
            status = ''
            if has_no_results:
                status = '无结果'
            elif has_products:
                status = f'有结果(共{count}件)'
            
            print(f"   {status}")
            if first_product:
                print(f"   首件: {first_product}")
            
            results[keyword] = {
                'count': count,
                'has_products': has_products,
                'first_product': first_product,
                'status': status
            }
            
        except Exception as e:
            print(f"   ❌ 错误: {e}")
            results[keyword] = {'error': str(e)}
    
    out = r'C:\Users\yu\Desktop\earbuds-review\jd_search_final2.json'
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ {out}")
    
    await page.close()
    await b.close()

if __name__ == '__main__':
    asyncio.run(main())
