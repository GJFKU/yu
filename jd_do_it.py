"""京东联盟自动化：搜索商品 -> 获取推广链接 -> 更新项目文件"""
import asyncio, json, sys, os, re
from playwright.async_api import async_playwright

CDP = 'http://127.0.0.1:9222'

PRODUCT_KEYWORDS = [
    ("AirPods Pro 2", "苹果 AirPods Pro 2 USB-C"),
    ("AirPods 4降噪", "苹果 AirPods 4 主动降噪"), 
    ("AirPods 4标准", "苹果 AirPods 4 标准版"),
    ("AirPods Max", "苹果 AirPods Max"),
    ("Sony XM5", "索尼 WH-1000XM5"),
    ("Bose QC Ultra", "Bose QC Ultra Earbuds"),
    ("OPPO Enco Air 5 Pro", "OPPO Enco Air 5 Pro"),
    ("NeoBuds Pro 2", "漫步者 NeoBuds Pro 2"),
    ("LolliPro 3", "漫步者 LolliPro 3 半入耳"),
    ("Comfo Run", "漫步者 Comfo Run"),
    ("X5 Pro", "漫步者 X5 Pro"),
    ("TWS1 Air 2", "漫步者 TWS1 Air 2"),
    ("W820NB", "漫步者 W820NB"),
    ("小米Buds 5 Pro", "小米 Buds 5 Pro"),
    ("小米Buds 5", "小米 Buds 5"),
    ("Redmi Buds 6 Pro", "Redmi Buds 6 Pro"),
    ("小米Buds 5半入耳", "小米 Buds 5 半入耳"),
    ("Redmi Buds 6", "Redmi Buds 6"),
]

async def run():
    p = await async_playwright().__aenter__()
    b = await p.chromium.connect_over_cdp(CDP)
    ctx = b.contexts[0]
    page = await ctx.new_page()
    
    results = {}
    
    for label, keyword in PRODUCT_KEYWORDS:
        print(f"\n🔍 [{label}] 搜索: {keyword}")
        try:
            await page.goto(
                f'https://union.jd.com/proManager/index?keywords={keyword}&pageNo=1',
                wait_until='domcontentloaded',
                timeout=20000
            )
            await asyncio.sleep(4)
            try:
                await page.wait_for_load_state('networkidle', timeout=12000)
            except:
                pass
            await asyncio.sleep(2)
            
            text = await page.evaluate('() => document.body?.innerText || ""')
            count_m = re.search(r'共(\d+)件商品', text)
            count = count_m.group(1) if count_m else '?'
            
            # Extract product names near "到手价"
            lines = text.split('\n')
            found = []
            for i, line in enumerate(lines):
                if '到手价¥' in line:
                    for j in range(i-3, i):
                        if j >= 0:
                            name = lines[j].strip()
                            if name and len(name) > 3 and '预估' not in name and '佣金' not in name and '好评' not in name and '京东' not in name and name not in ['超级补贴','自营','京配','PLUS','定向','券','促销','便宜包邮','星选','奖励']:
                                found.append(name[:50])
                                break
            
            results[label] = {'count': count, 'products': found[:3]}
            if found:
                print(f"   ✓ 找到 {count} 件, 前3: {found[:3]}")
            else:
                print(f"   ⚠ 未找到匹配商品 (共{count}件)")
                
        except Exception as e:
            print(f"   ✗ 错误: {e}")
            results[label] = {'error': str(e)}
    
    out = r'C:\Users\yu\Desktop\earbuds-review\jd_search_final.json'
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 结果保存至: {out}")
    await page.close()
    await b.close()

asyncio.run(run())
