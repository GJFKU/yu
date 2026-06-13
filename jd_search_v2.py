"""
京东联盟搜索 v2 - 每次搜索重新加载页面，保持连接
"""
import asyncio, json, sys, re
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
    
    results = {}
    
    for keyword in SEARCH_TERMS:
        print(f"\n🔍 {keyword}")
        page = await ctx.new_page()
        
        try:
            await page.goto('https://union.jd.com/proManager/index',
                          wait_until='domcontentloaded', timeout=15000)
            await asyncio.sleep(4)
            try:
                await page.wait_for_load_state('networkidle', timeout=10000)
            except:
                pass
            await asyncio.sleep(2)
            
            # Try URL-based search first
            await page.goto(
                f'https://union.jd.com/proManager/index?keywords={keyword}&pageNo=1',
                wait_until='domcontentloaded', timeout=15000
            )
            await asyncio.sleep(4)
            try:
                await page.wait_for_load_state('networkidle', timeout=10000)
            except:
                pass
            await asyncio.sleep(3)
            
            text = await page.evaluate('() => document.body?.innerText || ""')
            count_match = re.search(r'共(\d+)件商品', text)
            count = count_match.group(1) if count_match else '0'
            
            has_products = '我要推广' in text or '一键领链' in text
            has_no_results = '没有找到相关商品' in text or '系统繁忙' in text
            
            lines = text.split('\n')
            first_product = ''
            for i, line in enumerate(lines):
                if '到手价¥' in line:
                    for j in range(i-3, i):
                        if j >= 0:
                            n = lines[j].strip()
                            if n and len(n) > 3 and '预估' not in n and '佣金' not in n and '好评' not in n and '京东' not in n:
                                first_product = n[:60]
                                break
                    break
            
            status = '❌ 无结果' if has_no_results else f'✅ {count}件 首件:{first_product[:30]}'
            print(f"   {status}")
            
            results[keyword] = {'count': count, 'has_products': has_products, 'first_product': first_product}
            
        except Exception as e:
            print(f"   ❌ 错误: {e}")
            results[keyword] = {'error': str(e)}
        finally:
            await page.close()
    
    out = r'C:\Users\yu\Desktop\earbuds-review\jd_final_results.json'
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ {out}")
    await b.close()

if __name__ == '__main__':
    asyncio.run(main())
