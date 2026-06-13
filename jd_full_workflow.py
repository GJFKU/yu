"""
京东联盟完整工作流：
1. 在京东主站搜索商品，获取商品详情页URL
2. 在京东联盟万能转链页面，粘贴商品URL获取推广链接
3. 保存所有推广链接
"""
import asyncio, json, sys, re, os
from playwright.async_api import async_playwright

CDP = 'http://127.0.0.1:9222'

# 商品名称 -> 搜索关键词 (JD.com搜索用)
JD_SEARCH = {
    "AirPods Pro 2": "Apple AirPods Pro 2 USB-C 耳机",
    "AirPods 4(降噪版)": "Apple AirPods 4 主动降噪 耳机",
    "AirPods 4(标准版)": "Apple AirPods 4 标准版 耳机",
    "AirPods Max": "Apple AirPods Max 耳机",
    "Sony WH-1000XM5": "索尼 WH-1000XM5 头戴式降噪耳机",
    "Bose QC Ultra Earbuds": "Bose QC Ultra 大鲨 降噪耳机",
    "OPPO Enco Air 5 Pro": "OPPO Enco Air 5 Pro 耳机",
    "NeoBuds Pro 2": "漫步者 NeoBuds Pro 2 降噪耳机",
    "LolliPro 3": "漫步者 LolliPro 3 耳机",
    "Comfo Run": "漫步者 Comfo Run 开放式耳机",
    "X5 Pro": "漫步者 X5 Pro 耳机",
    "TWS1 Air 2": "漫步者 TWS1 Air 2 耳机",
    "W820NB": "漫步者 W820NB 双金标 头戴式耳机",
    "小米Buds 5 Pro": "小米 Buds 5 Pro 降噪耳机",
    "小米Buds 5": "小米 Buds 5 入耳式耳机",
    "Redmi Buds 6 Pro": "Redmi Buds 6 Pro 耳机",
    "小米Buds 5(半入耳)": "小米 Buds 5 半入耳 耳机",
    "Redmi Buds 6": "Redmi Buds 6 耳机",
}

async def run():
    p = await async_playwright().__aenter__()
    b = await p.chromium.connect_over_cdp(CDP)
    ctx = b.contexts[0]
    
    # Create a new page for JD.com search
    jd_page = await ctx.new_page()
    # The union page (tab 0) will be used for link conversion
    union_page = ctx.pages[0]
    
    results = []
    
    for label, search_term in JD_SEARCH.items():
        print(f"\n{'='*60}")
        print(f"[{label}] 搜索: {search_term}")
        
        try:
            # Step 1: Search on JD.com to get the product URL
            await jd_page.goto(
                f'https://search.jd.com/Search?keyword={search_term}&enc=utf-8',
                wait_until='domcontentloaded',
                timeout=20000
            )
            await asyncio.sleep(3)
            try:
                await jd_page.wait_for_load_state('networkidle', timeout=10000)
            except:
                pass
            await asyncio.sleep(2)
            
            # Get the first product link
            product_url = await jd_page.evaluate("""
                () => {
                    const items = document.querySelectorAll('.gl-item, [class*="goods-item"], .search-result-item');
                    for (const item of items) {
                        const link = item.querySelector('a[href*="item.jd.com"]');
                        if (link && link.href) {
                            return link.href;
                        }
                    }
                    // Fallback: any link to item.jd.com
                    const links = document.querySelectorAll('a[href*="item.jd.com"]');
                    for (const link of links) {
                        if (link.href && !link.href.includes('search')) {
                            return link.href;
                        }
                    }
                    return null;
                }
            """)
            
            if not product_url:
                print(f"   ❌ 未找到商品链接")
                results.append({"name": label, "error": "no product URL found"})
                continue
            
            # Clean URL
            if product_url.startswith('//'):
                product_url = 'https:' + product_url
            product_url = product_url.split('?')[0]  # Remove query params
            print(f"   📦 商品URL: {product_url}")
            
            # Step 2: Convert to promotion link using union.jd.com 万能转链
            # First navigate to custom promotion page
            await union_page.goto(
                'https://union.jd.com/proManager/custompromotion',
                wait_until='domcontentloaded',
                timeout=20000
            )
            await asyncio.sleep(3)
            try:
                await union_page.wait_for_load_state('networkidle', timeout=10000)
            except:
                pass
            await asyncio.sleep(2)
            
            # Type product URL into textarea
            await union_page.evaluate(f"""
                () => {{
                    const ta = document.querySelector('textarea.el-textarea__inner');
                    if (!ta) return 'no textarea';
                    ta.value = '{product_url}';
                    ta.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    ta.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    return 'pasted URL';
                }}
            """)
            await asyncio.sleep(1)
            
            # Check if button is now enabled
            btn_enabled = await union_page.evaluate("""
                () => {
                    const btn = document.querySelector('button.el-button--primary');
                    if (!btn) return 'no button';
                    const isDisabled = btn.classList.contains('is-disabled') || btn.disabled;
                    return isDisabled ? 'disabled' : 'enabled';
                }
            """)
            print(f"   🔘 推广按钮状态: {btn_enabled}")
            
            if btn_enabled == 'enabled':
                # Click the button
                await union_page.evaluate("""
                    () => {
                        const btn = document.querySelector('button.el-button--primary');
                        if (btn) btn.click();
                    }
                """)
                await asyncio.sleep(3)
                
                # Wait for results
                try:
                    await union_page.wait_for_load_state('networkidle', timeout=10000)
                except:
                    pass
                await asyncio.sleep(2)
                
                # Get the promotion link from results
                promo_link = await union_page.evaluate("""
                    () => {
                        // Look for the generated link in various formats
                        const resultArea = document.querySelector('.el-textarea__inner, .result-area, [class*="result"]');
                        // Look for copy buttons that contain the link
                        const copyBtns = document.querySelectorAll('[class*="copy"], [class*="copy-btn"]');
                        // Look for input with readonly containing the link
                        const inputs = document.querySelectorAll('input[readonly]');
                        for (const inp of inputs) {
                            if (inp.value && inp.value.includes('u.jd.com')) {
                                return inp.value;
                            }
                        }
                        // Get page text to find the generated link
                        return null;
                    }
                """)
                
                if promo_link:
                    print(f"   ✅ 推广链接: {promo_link}")
                else:
                    # Try to extract from page text
                    page_text = await union_page.evaluate('() => document.body?.innerText || ""')
                    # Look for u.jd.com links
                    ujd_matches = re.findall(r'https?://u\.jd\.com/\w+', page_text)
                    if ujd_matches:
                        promo_link = ujd_matches[0]
                        print(f"   ✅ 推广链接(从页面提取): {promo_link}")
                    else:
                        # Try extracting from the result area
                        result_text = await union_page.evaluate("""
                            () => {
                                const ta = document.querySelector('textarea.el-textarea__inner');
                                if (ta) return ta.value;
                                // Check other textareas
                                const allTas = document.querySelectorAll('textarea');
                                for (const t of allTas) {
                                    if (t.value) return t.value;
                                }
                                return 'no results found';
                            }
                        """)
                        print(f"   ⚠ 结果区域: {result_text[:200]}")
                        promo_link = result_text[:200]
                
                results.append({
                    "name": label,
                    "product_url": product_url,
                    "promo_link": promo_link
                })
            else:
                print(f"   ⚠ 按钮不可用，尝试直接输入")
                results.append({
                    "name": label,
                    "product_url": product_url,
                    "promo_link": "BUTTON_DISABLED"
                })
                
        except Exception as e:
            print(f"   ❌ 错误: {e}")
            results.append({"name": label, "error": str(e)})
    
    # Save results
    out = r'C:\Users\yu\Desktop\earbuds-review\jd_links_output.json'
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"✅ 完成! 结果保存至: {out}")
    print(f"   共处理 {len(results)} 个商品")
    for r in results:
        if 'promo_link' in r:
            print(f"   ✓ {r['name']}: {r['promo_link']}")
        elif 'error' in r:
            print(f"   ✗ {r['name']}: {r['error']}")
    
    await jd_page.close()
    await b.close()

if __name__ == '__main__':
    asyncio.run(run())
