"""Check if we can now access the course content"""
import asyncio, json
from playwright.async_api import async_playwright

async def main():
    p = await async_playwright().__aenter__()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    ctx = b.contexts[0]
    page = ctx.pages[0]
    
    # Reload the page
    await page.reload()
    await page.wait_for_load_state('networkidle')
    await asyncio.sleep(3)
    
    url = page.url
    title = await page.title()
    text = await page.evaluate('document.body.innerText')
    
    has_purchase = "购买后" in text
    has_buy_now = "立即购买" in text
    has_course_content = "试学" in text or "目录" in text or "第1课" in text
    
    print(f"URL: {url}")
    print(f"Title: {title}")
    print(f"Body length: {len(text)}")
    print(f"Still shows '购买后': {has_purchase}")
    print(f"Still shows '立即购买': {has_buy_now}")
    print(f"Has course content: {has_course_content}")
    
    await b.close()

asyncio.run(main())
