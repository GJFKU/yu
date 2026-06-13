"""
京东联盟单次搜索 - 在Edge浏览器新标签页中搜索商品并获取结果
Usage: python jd_search_single.py <search_keyword>
"""
import asyncio, json, sys, re
from playwright.async_api import async_playwright

CDP = 'http://127.0.0.1:9222'

async def search(keyword):
    p = await async_playwright().__aenter__()
    b = await p.chromium.connect_over_cdp(CDP)
    ctx = b.contexts[0]
    page = await ctx.new_page()
    
    try:
        await page.goto('https://union.jd.com/overview', wait_until='domcontentloaded', timeout=15000)
        await asyncio.sleep(3)
        
        # Click "我要推广" to expand
        await page.evaluate("""() => {
            const items = document.querySelectorAll('.el-submenu__title');
            for (const item of items) {
                if (item.textContent.includes('我要推广')) { item.click(); return; }
            }
        }""")
        await asyncio.sleep(1)
        
        # Click "商品推广"
        await page.evaluate("""() => {
            const items = document.querySelectorAll('.el-menu-item');
            for (const item of items) {
                if (item.textContent.trim() === '商品推广') { item.click(); return; }
            }
        }""")
        await asyncio.sleep(3)
        
        # Fill search and submit
        await page.evaluate(f"""() => {{
            const inp = document.querySelector('.el-input__inner[placeholder*="商品名称"]');
            if (!inp) return;
            const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
            setter.call(inp, '{keyword}');
            inp.dispatchEvent(new Event('input', {{ bubbles: true }}));
        }}""")
        await asyncio.sleep(0.5)
        await page.keyboard.press('Enter')
        await asyncio.sleep(5)
        try:
            await page.wait_for_load_state('networkidle', timeout=10000)
        except:
            pass
        await asyncio.sleep(3)
        
        text = await page.evaluate('() => document.body?.innerText || ""')
        count_m = re.search(r'共(\d+)件商品', text)
        count = count_m.group(1) if count_m else '0'
        
        lines = text.split('\n')
        products = []
        for i, line in enumerate(lines):
            if '到手价¥' in line:
                for j in range(i-3, i):
                    if j >= 0:
                        n = lines[j].strip()
                        if n and len(n) > 3 and '预估' not in n and '佣金' not in n:
                            products.append(n[:60])
                            break
        
        return {'keyword': keyword, 'count': count, 'products': products[:5], 'has_links': '一键领链' in text}
        
    finally:
        await page.close()
        await b.close()

if __name__ == '__main__':
    kw = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else 'AirPods Pro 2'
    result = asyncio.run(search(kw))
    print(json.dumps(result, ensure_ascii=False, indent=2))
