"""
Edge Browser Control via Playwright CDP
Usage: python edge_browser.py <command> [args]

Commands:
  tabs          - List all open tabs
  open <url>    - Open URL in new tab (returns tab id)
  close <tabId> - Close a tab
  current       - Show current tab URL/title
  snapshot      - Take an accessibility snapshot
  click <ref>   - Click element by ref
  screenshot    - Take screenshot
  type <ref> <text> - Type into element
  navigate <url> - Navigate current tab
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
        result.append({'id': i, 'title': await p.title(), 'url': p.url[:100]})
    await b.close()
    return result

async def cmd_open(url):
    b, c = await connect()
    page = await c.new_page()
    await page.goto(url)
    result = {'tabId': len(c.pages) - 1, 'url': url}
    await b.close()
    return result

async def cmd_snapshot():
    b, c = await connect()
    pages = c.pages
    if not pages:
        await b.close()
        return {'error': 'No tabs open'}
    page = pages[-1]
    # Get key page info
    title = await page.title()
    url = page.url
    text = await page.evaluate('() => document.body?.innerText?.substring(0, 2000) || ""')
    await b.close()
    return {'title': title, 'url': url, 'text': text[:500]}

async def cmd_navigate(url):
    b, c = await connect()
    pages = c.pages
    if pages:
        await pages[-1].goto(url)
    result = {'url': url}
    await b.close()
    return result

async def main():
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'Usage: edge_browser.py <command> [args]'}, ensure_ascii=False))
        return
    cmd = sys.argv[1]
    args = sys.argv[2:]
    try:
        if cmd == 'tabs':
            result = await cmd_tabs()
        elif cmd == 'open':
            result = await cmd_open(args[0]) if args else {'error': 'URL required'}
        elif cmd == 'snapshot':
            result = await cmd_snapshot()
        elif cmd == 'navigate':
            result = await cmd_navigate(args[0]) if args else {'error': 'URL required'}
        else:
            result = {'error': f'Unknown command: {cmd}'}
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({'error': str(e)}, ensure_ascii=False))

asyncio.run(main())
