"""
Enhanced Edge Browser Control via Playwright CDP
"""
import asyncio, sys, json
from playwright.async_api import async_playwright

CDP_URL = 'http://127.0.0.1:9222'
_browser = None
_context = None

async def connect():
    global _browser, _context
    p = await async_playwright().__aenter__()
    _browser = await p.chromium.connect_over_cdp(CDP_URL)
    _context = _browser.contexts[0] if _browser.contexts else await _browser.new_context()
    return _browser, _context

async def cmd_tabs():
    b, c = await connect()
    pages = c.pages
    result = []
    for i, p in enumerate(pages):
        try:
            result.append({'tabId': i, 'title': await p.title(), 'url': p.url[:120]})
        except:
            result.append({'tabId': i, 'title': 'N/A', 'url': 'N/A'})
    await b.close()
    return result

async def cmd_open(url):
    b, c = await connect()
    page = await c.new_page()
    await page.goto(url, wait_until='domcontentloaded')
    result = {'tabId': len(c.pages) - 1, 'url': url}
    await b.close()
    return result

async def cmd_snapshot(tab_id=None):
    b, c = await connect()
    pages = c.pages
    if not pages:
        await b.close()
        return {'error': 'No tabs open'}
    if tab_id is not None and tab_id < len(pages):
        page = pages[tab_id]
    else:
        page = pages[-1]
    title = await page.title()
    url = page.url
    text = await page.evaluate('() => document.body?.innerText?.substring(0, 5000) || ""')
    await b.close()
    return {'title': title, 'url': url, 'tabId': tab_id if tab_id else len(pages)-1, 'text': text[:3000]}

async def cmd_navigate(url, tab_id=None):
    b, c = await connect()
    pages = c.pages
    if tab_id is not None and tab_id < len(pages):
        page = pages[tab_id]
    elif pages:
        page = pages[-1]
    else:
        await b.close()
        return {'error': 'No tabs'}
    await page.goto(url, wait_until='domcontentloaded')
    result = {'url': url, 'tabId': tab_id if tab_id else len(pages)-1}
    await b.close()
    return result

async def cmd_screenshot(tab_id=None):
    b, c = await connect()
    pages = c.pages
    if not pages:
        await b.close()
        return {'error': 'No tabs'}
    if tab_id is not None and tab_id < len(pages):
        page = pages[tab_id]
    else:
        page = pages[-1]
    await page.screenshot(path='C:\\Users\\yu\\Desktop\\earbuds-review\\screenshot.png', full_page=True)
    await b.close()
    return {'screenshot': 'C:\\Users\\yu\\Desktop\\earbuds-review\\screenshot.png'}

async def cmd_close(tab_id):
    b, c = await connect()
    pages = c.pages
    if tab_id < len(pages):
        await pages[tab_id].close()
    await b.close()
    return {'closed': tab_id}

async def cmd_evaluate(js, tab_id=None):
    b, c = await connect()
    pages = c.pages
    if tab_id is not None and tab_id < len(pages):
        page = pages[tab_id]
    else:
        page = pages[-1]
    result = await page.evaluate(js)
    await b.close()
    return {'result': str(result)[:3000]}

async def main():
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'Usage: edge_browser_enhanced.py <command> [args]'}, ensure_ascii=False))
        return
    cmd = sys.argv[1]
    args = sys.argv[2:]
    try:
        if cmd == 'tabs':
            result = await cmd_tabs()
        elif cmd == 'open':
            result = await cmd_open(args[0]) if args else {'error': 'URL required'}
        elif cmd == 'snapshot':
            tid = int(args[0]) if args else None
            result = await cmd_snapshot(tid)
        elif cmd == 'navigate':
            result = await cmd_navigate(args[0], int(args[1]) if len(args) > 1 else None)
        elif cmd == 'screenshot':
            tid = int(args[0]) if args else None
            result = await cmd_screenshot(tid)
        elif cmd == 'close':
            result = await cmd_close(int(args[0])) if args else {'error': 'tabId required'}
        elif cmd == 'eval':
            tid = int(args[1]) if len(args) > 1 else None
            result = await cmd_evaluate(args[0], tid)
        else:
            result = {'error': f'Unknown command: {cmd}'}
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({'error': str(e)}, ensure_ascii=False))

asyncio.run(main())
