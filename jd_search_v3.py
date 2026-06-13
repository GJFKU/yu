"""
京东联盟 v3 - 单击侧边栏商品推广后搜索，单页连接完成所有搜索
"""
import asyncio, json, sys, re, urllib.parse
from playwright.async_api import async_playwright

CDP = 'http://127.0.0.1:9222'

SEARCHES = [
    "AirPods Pro 2", "AirPods 4 主动降噪", "AirPods 4 标准版",
    "AirPods Max", "索尼 WH-1000XM5", "Bose QC Ultra",
    "OPPO Enco Air 5 Pro", "漫步者 NeoBuds Pro 2", "漫步者 LolliPro 3",
    "漫步者 Comfo Run", "漫步者 X5 Pro", "漫步者 TWS1 Air 2",
    "漫步者 W820NB 双金标", "小米 Buds 5 Pro", "小米 Buds 5",
    "Redmi Buds 6 Pro", "小米 Buds 5 半入耳版", "Redmi Buds 6",
]

async def main():
    p = await async_playwright().__aenter__()
    b = await p.chromium.connect_over_cdp(CDP)
    ctx = b.contexts[0]
    page = ctx.pages[0]
    
    # Start from overview
    await page.goto('https://union.jd.com/overview', wait_until='domcontentloaded', timeout=15000)
    await asyncio.sleep(3)
    
    # Click sidebar items to get to product search
    await page.evaluate("""
        () => {
            const items = document.querySelectorAll('.el-submenu__title');
            for (const item of items) {
                if (item.textContent.includes('我要推广')) {
                    item.click();
                    return;
                }
            }
        }
    """)
    await asyncio.sleep(1)
    
    await page.evaluate("""
        () => {
            const items = document.querySelectorAll('.el-menu-item');
            for (const item of items) {
                if (item.textContent.trim() === '商品推广') {
                    item.click();
                    return;
                }
            }
        }
    """)
    await asyncio.sleep(3)
    
    results = {}
    
    for keyword in SEARCHES:
        print(f"\n🔍 {keyword}")
        
        try:
            # Fill search input
            encoded = urllib.parse.quote(keyword)
            await page.evaluate(f"""
                () => {{
                    const input = document.querySelector('.el-input__inner[placeholder*="商品名称"]');
                    if (!input) return;
                    const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    setter.call(input, '{keyword}');
                    input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                }}
            """)
            await asyncio.sleep(0.5)
            
            # Press Enter
            await page.keyboard.press('Enter')
            await asyncio.sleep(4)
            try:
                await page.wait_for_load_state('networkidle', timeout=10000)
            except:
                pass
            await asyncio.sleep(3)
            
            text = await page.evaluate('() => document.body?.innerText || ""')
            
            count_match = re.search(r'共(\d+)件商品', text)
            count = count_match.group(1) if count_match else '0'
            has_items = '我要推广' in text or '一键领链' in text
            
            lines = text.split('\n')
            first = ''
            for i, line in enumerate(lines):
                if '到手价¥' in line:
                    for j in range(i-3, i):
                        if j >= 0:
                            n = lines[j].strip()
                            if n and len(n) > 3 and '预估' not in n and '佣金' not in n and '好评' not in n:
                                first = n[:60]
                                break
                    break
            
            results[keyword] = {'count': count, 'found': has_items, 'first': first}
            print(f"   {'✅' if has_items else '❌'} 共{count}件 | {first[:40] if first else '无'}")
            
        except Exception as e:
            print(f"   ❌ {e}")
            results[keyword] = {'error': str(e)}
    
    out = r'C:\Users\yu\Desktop\earbuds-review\jd_results_v3.json'
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ {out}")
    await b.close()

if __name__ == '__main__':
    asyncio.run(main())
