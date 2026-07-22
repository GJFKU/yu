"""Check course page structure - what elements are clickable"""
import asyncio, json
from playwright.async_api import async_playwright

async def main():
    p = await async_playwright().__aenter__()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    ctx = b.contexts[0]
    page = ctx.pages[0]
    
    # Basic info
    has_purchase = await page.evaluate('document.body.innerText.includes("购买后")')
    has_buy_now = await page.evaluate('document.body.innerText.includes("立即购买")')
    page_title = await page.title()
    body_len = await page.evaluate('document.body.innerText.length')
    print(f"Title: {page_title}")
    print(f"Body length: {body_len}")
    print(f"Shows '购买后': {has_purchase}")
    print(f"Shows '立即购买': {has_buy_now}")
    
    # Try to find course chapter/lesson elements by common selectors
    for selector in [
        "[class*=chapter]", "[class*=lesson]", "[class*=section]",
        "[class*=course-item]", "[class*=curriculum]", "[class*=catalog]",
        ".el-tree", ".el-tree-node", "[class*=menu-item]",
        "[class*=list-item]", "[class*=content-item]"
    ]:
        count = await page.evaluate(f'document.querySelectorAll("{selector}").length')
        if count > 0:
            first_few = await page.evaluate(f'''() => {{
                const els = document.querySelectorAll("{selector}");
                return Array.from(els).slice(0,5).map((e,i) => ({{
                    idx: i,
                    tag: e.tagName,
                    cls: (e.className || "").substring(0,80),
                    txt: (e.innerText || "").substring(0,60),
                    visible: !!e.offsetParent
                }}));
            }}''')
            print(f"\nSelector '{selector}': {count} found")
            print(json.dumps(first_few, ensure_ascii=False, indent=2))
            break
    
    # Also check all anchor tags with text
    anchors = await page.evaluate('''() => {
        const items = document.querySelectorAll("a");
        return Array.from(items).slice(0,30).map(a => ({
            text: (a.innerText || "").substring(0,50),
            href: (a.href || "").substring(0,100),
            visible: !!a.offsetParent
        }));
    }''')
    print(f"\nAnchor tags ({len([a for a in anchors if a['visible']])} visible):")
    for a in anchors:
        if a['visible']:
            print(f"  {a['text'][:40]:40s} {a['href'][:60]}")
    
    # Get full HTML body for analysis (first 3000 chars)
    html_start = await page.evaluate('document.body.innerHTML.substring(0, 3000)')
    
    await b.close()

asyncio.run(main())
