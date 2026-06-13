"""
京东联盟推广链接生成器
通过京东联盟页面搜索商品并获取推广链接
"""
import asyncio, json, re
from playwright.async_api import async_playwright

CDP_URL = 'http://127.0.0.1:9222'

async def connect():
    p = await async_playwright().__aenter__()
    b = await p.chromium.connect_over_cdp(CDP_URL)
    ctx = b.contexts[0] if b.contexts else await b.new_context()
    return p, b, ctx

async def search_and_get_links(product_name, exact_match=False):
    """Search for a product in JD Union and get the promotion link"""
    p, b, ctx = await connect()
    
    # Use a new page to avoid polluting existing tabs
    page = await ctx.new_page()
    
    try:
        # Go to product promotion page
        await page.goto('https://union.jd.com/proManager/index?pageNo=1', 
                        wait_until='domcontentloaded')
        await asyncio.sleep(3)
        
        # Type into search box
        input_selector = '.el-input__inner[placeholder*="商品名称"]'
        input_el = await page.wait_for_selector(input_selector, timeout=5000)
        if not input_el:
            return {'error': 'Search input not found'}
        
        # Clear and type
        await input_el.click()
        await input_el.fill('')
        await asyncio.sleep(0.5)
        await input_el.type(product_name, delay=50)
        await asyncio.sleep(0.5)
        
        # Find and click search button
        search_btn = await page.query_selector('.el-input-group__append')
        if search_btn:
            await search_btn.click()
        else:
            # Try Enter key
            await page.keyboard.press('Enter')
        
        await asyncio.sleep(3)
        
        # Wait for results to load
        await page.wait_for_load_state('networkidle', timeout=10000)
        await asyncio.sleep(2)
        
        # Extract page info
        url = page.url
        title = await page.title()
        
        # Get all product text
        page_text = await page.evaluate('() => document.body.innerText || ""')
        
        return {
            'url': url,
            'title': title,
            'page_text': page_text[:5000]
        }
    finally:
        await page.close()
        await b.close()

async def click_onekey_link(tab_id=0):
    """Click '一键领链' buttons on current page to generate links"""
    p, b, ctx = await connect()
    pages = ctx.pages
    page = pages[tab_id if tab_id < len(pages) else -1]
    
    # Find and click "一键领链" buttons
    btns = await page.query_selector_all('span:has-text("一键领链")')
    result = []
    for btn in btns:
        if await btn.is_visible():
            await btn.click()
            await asyncio.sleep(1)
            result.append('clicked')
    
    await asyncio.sleep(2)
    
    # Check for popup/dialog with the link
    dialog = await page.query_selector('.el-dialog, .el-message-box')
    if dialog and await dialog.is_visible():
        dialog_text = await dialog.inner_text()
        link_input = await dialog.query_selector('input[readonly], input[type="text"]')
        link_value = ''
        if link_input:
            link_value = await link_input.get_attribute('value') or ''
        
        # Close dialog
        close_btn = await dialog.query_selector('.el-dialog__close, .el-message-box__close, .el-button--primary')
        if close_btn:
            await close_btn.click()
        
        result.append({
            'dialog_text': dialog_text[:500],
            'link': link_value
        })
    
    return {'result': result}

async def auto_search_all():
    """Search for all earbud products one by one and record links"""
    products = [
        # Apple series
        ('AirPods Pro 2 USB-C', 'Apple AirPods Pro 2'),
        ('AirPods 4 主动降噪', 'Apple AirPods 4'),
        ('AirPods 4 标准版', 'Apple AirPods 4'),
        ('AirPods Max', 'Apple AirPods Max'),
        # Sony
        ('Sony WH-1000XM5', 'Sony WH-1000XM5'),
        # Bose
        ('Bose QC Ultra Earbuds', 'Bose QC Ultra'),
        # OPPO
        ('OPPO Enco Air 5 Pro', 'OPPO Enco Air 5 Pro'),
        # Edifier
        ('漫步者 NeoBuds Pro 2', 'Edifier NeoBuds Pro 2'),
        ('漫步者 LolliPro 3', 'Edifier LolliPro 3'),
        ('漫步者 Comfo Run', 'Edifier Comfo Run'),
        ('漫步者 X5 Pro', 'Edifier X5 Pro'),
        ('漫步者 TWS1 Air 2', 'Edifier TWS1 Air 2'),
        ('漫步者 W820NB 双金标', 'Edifier W820NB'),
        # Xiaomi
        ('小米 Buds 5 Pro', 'Xiaomi Buds 5 Pro'),
        ('小米 Buds 5', 'Xiaomi Buds 5'),
        ('Redmi Buds 6 Pro', 'Redmi Buds 6 Pro'),
        ('小米 Buds 5 半入耳版', 'Xiaomi Buds 5半入耳'),
        ('Redmi Buds 6', 'Redmi Buds 6'),
    ]
    
    results = []
    for name, label in products:
        print(f'Searching: {name}...')
        try:
            r = await search_and_get_links(name)
            results.append({'name': name, 'label': label, **r})
        except Exception as e:
            results.append({'name': name, 'label': label, 'error': str(e)})
    
    return results

async def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'help'
    
    if cmd == 'search':
        name = ' '.join(sys.argv[2:]) if len(sys.argv) > 2 else '耳机'
        result = await search_and_get_links(name)
    elif cmd == 'onekey':
        tid = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        result = await click_onekey_link(tid)
    elif cmd == 'auto':
        result = await auto_search_all()
    else:
        result = {'usage': 'python jd_link_generator.py <search|onekey|auto> [args]'}
    
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    import sys
    asyncio.run(main())
