"""
Enhanced Edge Browser Control v2 - with wait support
"""
import asyncio, sys, json
from playwright.async_api import async_playwright

CDP_URL = 'http://127.0.0.1:9222'

async def connect():
    p = await async_playwright().__aenter__()
    b = await p.chromium.connect_over_cdp(CDP_URL)
    ctx = b.contexts[0] if b.contexts else await b.new_context()
    return p, b, ctx

async def cmd_fullpage(tab_id=None):
    p, b, ctx = await connect()
    pages = ctx.pages
    if not pages:
        await b.close()
        return {'error': 'No tabs'}
    page = pages[tab_id if tab_id is not None and tab_id < len(pages) else -1]
    await page.wait_for_load_state('networkidle', timeout=10000)
    html = await page.content()
    title = await page.title()
    url = page.url
    text = await page.evaluate('() => document.body?.innerText || ""')
    await b.close()
    return {'title': title, 'url': url, 'text': text[:5000], 'html_len': len(html)}

async def cmd_wait_and_snapshot(tab_id=None, wait_ms=3000):
    p, b, ctx = await connect()
    pages = ctx.pages
    if not pages:
        await b.close()
        return {'error': 'No tabs'}
    page = pages[tab_id if tab_id is not None and tab_id < len(pages) else -1]
    await asyncio.sleep(wait_ms / 1000)
    title = await page.title()
    url = page.url
    text = await page.evaluate('() => document.body?.innerText || ""')
    visible_text = text[:5000]
    await b.close()
    return {'title': title, 'url': url, 'text': visible_text}

async def cmd_navigate_and_wait(url, tab_id=None):
    p, b, ctx = await connect()
    pages = ctx.pages
    if not pages:
        await b.close()
        return {'error': 'No tabs'}
    page = pages[tab_id if tab_id is not None and tab_id < len(pages) else -1]
    await page.goto(url, wait_until='domcontentloaded')
    await asyncio.sleep(3)
    text = await page.evaluate('() => document.body?.innerText || ""')
    title = await page.title()
    await b.close()
    return {'title': title, 'url': url, 'text': text[:5000]}

async def cmd_screenshot(tab_id=None):
    p, b, ctx = await connect()
    pages = ctx.pages
    if not pages:
        await b.close()
        return {'error': 'No tabs'}
    page = pages[tab_id if tab_id is not None and tab_id < len(pages) else -1]
    await page.wait_for_load_state('networkidle', timeout=10000)
    await page.screenshot(path='C:\\Users\\yu\\Desktop\\earbuds-review\\screenshot.png', full_page=True)
    await b.close()
    return {'screenshot': 'C:\\Users\\yu\\Desktop\\earbuds-review\\screenshot.png'}

async def cmd_eval(js, tab_id=None):
    p, b, ctx = await connect()
    pages = ctx.pages
    if not pages:
        await b.close()
        return {'error': 'No tabs'}
    page = pages[tab_id if tab_id is not None and tab_id < len(pages) else -1]
    result = await page.evaluate(js)
    await b.close()
    return {'result': str(result)[:5000]}

async def cmd_click_text(link_text, tab_id=None):
    """Click an element by its visible text content"""
    p, b, ctx = await connect()
    pages = ctx.pages
    if not pages:
        await b.close()
        return {'error': 'No tabs'}
    page = pages[tab_id if tab_id is not None and tab_id < len(pages) else -1]
    # Try different approaches
    results = []
    
    # Method 1: Try span/div with text
    r1 = await page.evaluate(f'''() => {{
        const all = document.querySelectorAll('*');
        for (const el of all) {{
            if (el.children.length === 0 && el.textContent.trim() === '{link_text}') {{
                el.click();
                return 'clicked via text: ' + el.tagName + ' - ' + el.textContent.trim();
            }}
        }}
        return 'not found via direct text';
    }}''')
    results.append(r1)
    await asyncio.sleep(1)
    
    if 'clicked' not in str(r1):
        # Method 2: Try finding elements that contain the text
        r2 = await page.evaluate(f'''() => {{
            const all = document.querySelectorAll('a, button, span, div, li, i, em');
            for (const el of all) {{
                if (el.textContent.trim().includes('{link_text}') && !el.querySelector('*')) {{
                    el.click();
                    return 'clicked via contains: ' + el.tagName;
                }}
            }}
            // Try parent elements
            for (const el of all) {{
                if (el.textContent.trim().includes('{link_text}')) {{
                    el.click();
                    return 'clicked via parent contains: ' + el.tagName + ' text=' + el.textContent.trim().substring(0, 50);
                }}
            }}
            return 'not found';
        }}''')
        results.append(r2)
        await asyncio.sleep(2)
    
    # Check what happened
    url = page.url
    title = await page.title()
    text = await page.evaluate('() => document.body?.innerText?.substring(0, 5000) || ""')
    await b.close()
    return {'title': title, 'url': url, 'results': results, 'text': text}

async def cmd_send_keys(selector, value, tab_id=None):
    """Type into an input field"""
    p, b, ctx = await connect()
    pages = ctx.pages
    if not pages:
        await b.close()
        return {'error': 'No tabs'}
    page = pages[tab_id if tab_id is not None and tab_id < len(pages) else -1]
    result = await page.evaluate(f'''() => {{
        const input = document.querySelector('{selector}');
        if (!input) return 'selector not found: {selector}';
        input.value = '{value}';
        input.dispatchEvent(new Event('input', {{ bubbles: true }}));
        return 'typed into: ' + input.tagName + (input.placeholder || '');
    }}''')
    await asyncio.sleep(1)
    title = await page.title()
    url = page.url
    text = await page.evaluate('() => document.body?.innerText?.substring(0, 3000) || ""')
    await b.close()
    return {'title': title, 'url': url, 'result': result, 'text': text}

async def cmd_find_by_xpath(xpath, tab_id=None):
    """Find elements by XPath"""
    p, b, ctx = await connect()
    pages = ctx.pages
    if not pages:
        await b.close()
        return {'error': 'No tabs'}
    page = pages[tab_id if tab_id is not None and tab_id < len(pages) else -1]
    result = await page.evaluate(f'''() => {{
        const iterator = document.evaluate('{xpath}', document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
        const items = [];
        for (let i = 0; i < iterator.snapshotLength; i++) {{
            const node = iterator.snapshotItem(i);
            items.push(node.tagName + ': ' + (node.textContent || '').trim().substring(0, 100));
        }}
        return items;
    }}''')
    await b.close()
    return {'result': result}

async def main():
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'Usage: edge_browser_enhanced2.py <command> [args]'}, ensure_ascii=False))
        return
    cmd = sys.argv[1]
    args = sys.argv[2:]
    try:
        if cmd == 'fullpage':
            tid = int(args[0]) if args else None
            result = await cmd_fullpage(tid)
        elif cmd == 'snapshot':
            tid = int(args[0]) if args else None
            result = await cmd_wait_and_snapshot(tid)
        elif cmd == 'navigate':
            tid = int(args[1]) if len(args) > 1 else None
            result = await cmd_navigate_and_wait(args[0], tid)
        elif cmd == 'screenshot':
            tid = int(args[0]) if args else None
            result = await cmd_screenshot(tid)
        elif cmd == 'eval':
            tid = int(args[1]) if len(args) > 1 else None
            result = await cmd_eval(args[0], tid)
        elif cmd == 'click':
            tid = int(args[1]) if len(args) > 1 else None
            result = await cmd_click_text(args[0], tid)
        elif cmd == 'sendkeys':
            tid = int(args[2]) if len(args) > 2 else None
            result = await cmd_send_keys(args[0], args[1], tid)
        elif cmd == 'xpath':
            tid = int(args[1]) if len(args) > 1 else None
            result = await cmd_find_by_xpath(args[0], tid)
        else:
            result = {'error': f'Unknown command: {cmd}'}
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({'error': str(e)}, ensure_ascii=False))

asyncio.run(main())
