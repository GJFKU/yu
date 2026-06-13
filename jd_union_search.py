"""
京东联盟商品推广链接获取
"""
import asyncio, sys, json
from playwright.async_api import async_playwright

CDP_URL = 'http://127.0.0.1:9222'

async def connect():
    p = await async_playwright().__aenter__()
    b = await p.chromium.connect_over_cdp(CDP_URL)
    ctx = b.contexts[0] if b.contexts else await b.new_context()
    return p, b, ctx

async def search_product(product_name, tab_id=0):
    """Search for a product and get its promotion link"""
    p, b, ctx = await connect()
    pages = ctx.pages
    if not pages or tab_id >= len(pages):
        await b.close()
        return {'error': f'Tab {tab_id} not available'}
    
    page = pages[tab_id]
    
    # Navigate to product promotion page
    await page.goto('https://union.jd.com/proManager/index?pageNo=1', wait_until='domcontentloaded')
    await asyncio.sleep(3)
    
    # Type into search box
    result = await page.evaluate(f"""
        () => {{
            const input = document.querySelector('.el-input__inner[placeholder*="商品名称"]');
            if (!input) return 'search input not found';
            
            // Trigger Vue reactivity
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                window.HTMLInputElement.prototype, 'value'
            ).set;
            nativeInputValueSetter.call(input, '{product_name}');
            input.dispatchEvent(new Event('input', {{ bubbles: true, cancelable: true }}));
            
            // Find and click search button
            const searchBtn = document.querySelector('.el-input-group__append, .el-button--primary, button:has(i.el-icon-search)');
            if (searchBtn) {{
                searchBtn.click();
                return 'searched: ' + '{product_name}';
            }}
            
            // Try pressing Enter
            input.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', keyCode: 13, bubbles: true }}));
            return 'pressed Enter';
        }}
    """)
    
    await asyncio.sleep(3)
    
    url = page.url
    title = await page.title()
    text = await page.evaluate('() => document.body?.innerText || ""')
    
    await b.close()
    return {
        'search_result': result,
        'title': title[:100],
        'url': url[:200],
        'page_text': text[:3000]
    }

async def get_products_on_page(tab_id=0):
    """Get all products currently visible on the page"""
    p, b, ctx = await connect()
    pages = ctx.pages
    if not pages or tab_id >= len(pages):
        await b.close()
        return {'error': 'Tab not available'}
    
    page = pages[tab_id]
    
    products = await page.evaluate("""
        () => {
            const items = document.querySelectorAll('.el-table__body-wrapper tbody tr, [class*="goods-list"] [class*="item"], .pro-item');
            return Array.from(items).map(item => ({
                text: item.textContent.trim().substring(0, 200)
            }));
        }
    """)
    
    # Also try to find all products with their links
    link_info = await page.evaluate("""
        () => {
            const buttons = document.querySelectorAll('button, a, span');
            const linkBtns = [];
            for (const btn of buttons) {
                if (btn.textContent.trim().includes('一键领链') || 
                    btn.textContent.trim().includes('我要推广')) {
                    linkBtns.push(btn.textContent.trim());
                }
            }
            return linkBtns;
        }
    """)
    
    title = await page.title()
    url = page.url
    text = await page.evaluate('() => document.body?.innerText || ""')
    
    await b.close()
    return {
        'title': title[:100],
        'url': url[:200],
        'products_count': len(products) if isinstance(products, list) else 0,
        'link_buttons': link_info[:10],
        'page_text': text[:3000]
    }

async def get_promotion_links(tab_id=0):
    """Get promotion links for all visible products by clicking '一键领链'"""
    p, b, ctx = await connect()
    pages = ctx.pages
    if not pages or tab_id >= len(pages):
        await b.close()
        return {'error': 'Tab not available'}
    
    page = pages[tab_id]
    
    # Click all '一键领链' buttons to generate links
    result = await page.evaluate("""
        () => {
            const btns = document.querySelectorAll('span, a, button');
            const clicked = [];
            for (const btn of btns) {
                if (btn.textContent.trim() === '一键领链') {
                    btn.click();
                    clicked.push('clicked 一键领链');
                }
            }
            return clicked;
        }
    """)
    
    await asyncio.sleep(2)
    
    # Check for modal/dialog
    dialog_text = await page.evaluate("""
        () => {
            const dialogs = document.querySelectorAll('.el-dialog, .el-message-box, [class*="modal"], [class*="dialog"]');
            return Array.from(dialogs).map(d => ({
                visible: d.style.display !== 'none',
                text: d.textContent.trim().substring(0, 500)
            }));
        }
    """)
    
    title = await page.title()
    url = page.url
    
    await b.close()
    return {
        'result': result[:10],
        'dialog_text': dialog_text,
        'title': title[:100],
        'url': url[:200]
    }

async def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'help'
    
    if cmd == 'search':
        name = sys.argv[2] if len(sys.argv) > 2 else '耳机'
        tid = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        result = await search_product(name, tid)
    elif cmd == 'products':
        tid = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        result = await get_products_on_page(tid)
    elif cmd == 'getlinks':
        tid = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        result = await get_promotion_links(tid)
    else:
        result = {'error': 'Usage: jd_union_search.py <search|products|getlinks> [args]'}
    
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    asyncio.run(main())
