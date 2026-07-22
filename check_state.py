"""Check browser state after login"""
import asyncio, json
from playwright.async_api import async_playwright

async def main():
    p = await async_playwright().__aenter__()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    ctx = b.contexts[0]
    page = ctx.pages[0]
    
    # Check all tabs
    tabs_info = []
    for i, pg in enumerate(ctx.pages):
        tabs_info.append({
            'id': i,
            'title': await pg.title(),
            'url': pg.url[:120]
        })
    print("Current tabs:", json.dumps(tabs_info, ensure_ascii=False))
    
    # Check if there are any cookies for xet.pomoho.com
    cookies = await ctx.cookies()
    xet_cookies = [c for c in cookies if 'xet' in c.get('domain', '') or 'pomoho' in c.get('domain', '')]
    print(f"\nXET/Pomoho cookies: {len(xet_cookies)}")
    for c in xet_cookies[:10]:
        print(f"  {c['name']}: {c['value'][:30]}... domain={c['domain']}")
    
    await b.close()

asyncio.run(main())
