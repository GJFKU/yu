"""Try navigating to the learning URL"""
import asyncio, json
from playwright.async_api import async_playwright

async def main():
    p = await async_playwright().__aenter__()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    ctx = b.contexts[0]
    page = ctx.pages[0]
    
    # Try navigating to the original course learning URL
    course_url = "https://appmywwtfwy6965.h5.xet.pomoho.com/p/course/ecourse/course_2rL24flJeU0H24sq6ODXDrAagq8"
    await page.goto(course_url)
    await page.wait_for_load_state('networkidle')
    await asyncio.sleep(3)
    
    text = await page.evaluate('document.body.innerText')
    url = page.url
    title = await page.title()
    
    print(f"Final URL: {url}")
    print(f"Title: {title}")
    
    # Look for the purchase prompt or lesson content
    has_purchase = "购买后" in text or "立即购买" in text or "前往购买" in text
    print(f"Still purchase page: {has_purchase}")
    
    # Check for "我的课程" or "学习" 
    my_courses = "我的课程" in text
    print(f"Has '我的课程': {my_courses}")
    
    # Check what's around the top of the page
    lines = text.split('\n')
    first_50 = [l for l in lines if l.strip()][:30]
    print("\nFirst 30 non-empty lines:")
    for l in first_50:
        print(f"  {l}")
    
    await b.close()

asyncio.run(main())
