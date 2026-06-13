"""
京东联盟 - 一次性完整搜索流程
"""
import asyncio, json, re, sys
from playwright.async_api import async_playwright

CDP = 'http://127.0.0.1:9222'

async def do_search(keyword, tab_id=0):
    p = await async_playwright().__aenter__()
    b = await p.chromium.connect_over_cdp(CDP)
    ctx = b.contexts[0]
    page = ctx.pages[tab_id]
    
    try:
        # Step 1: Overview
        await page.goto('https://union.jd.com/overview', wait_until='domcontentloaded', timeout=15000)
        await asyncio.sleep(3)
        
        # Step 2: Click "我要推广" submenu
        await page.evaluate("""
            document.querySelectorAll('.el-submenu__title').forEach(el => {
                if (el.textContent.includes('我要推广')) el.click();
            });
        """)
        await asyncio.sleep(1)
        
        # Step 3: Click "商品推广"
        await page.evaluate("""
            document.querySelectorAll('.el-menu-item').forEach(el => {
                if (el.textContent.trim() === '商品推广') el.click();
            });
        """)
        await asyncio.sleep(3)
        
        # Step 4: Fill search box
        await page.evaluate(f"""
            const inp = document.querySelector('.el-input__inner[placeholder*="商品名称"]');
            if (inp) {{
                Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call(inp, '{keyword}');
                inp.dispatchEvent(new Event('input', {{bubbles: true}}));
            }}
        """)
        await asyncio.sleep(0.5)
        
        # Step 5: Press Enter
        await page.keyboard.press('Enter')
        await asyncio.sleep(5)
        try:
            await page.wait_for_load_state('networkidle', timeout=10000)
        except:
            pass
        await asyncio.sleep(3)
        
        # Step 6: Read results
        url = page.url
        text = await page.evaluate('() => document.body?.innerText || ""')
        
        count_m = re.search(r'共(\d+)件商品', text)
        count = count_m.group(1) if count_m else '0'
        has_results = '我要推广' in text and '到手价¥' in text
        
        # Extract products
        lines = text.split('\n')
        products = []
        for i, line in enumerate(lines):
            if '到手价¥' in line:
                for j in range(i-3, i):
                    if j >= 0:
                        n = lines[j].strip()
                        if n and len(n) > 3 and '预估' not in n and '佣金' not in n and '好评' not in n and '京东' not in n:
                            products.append(n[:60])
                            break
        
        return {
            'keyword': keyword,
            'count': count, 
            'has_results': has_results,
            'products': products[:5],
            'url': url[:150]
        }
    
    finally:
        await b.close()

if __name__ == '__main__':
    kw = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else 'AirPods Pro 2'
    r = asyncio.run(do_search(kw))
    print(json.dumps(r, ensure_ascii=False, indent=2))
