"""Deep check the page state after login"""
import asyncio, json
from playwright.async_api import async_playwright

async def main():
    p = await async_playwright().__aenter__()
    b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    ctx = b.contexts[0]
    page = ctx.pages[0]
    
    # Check if there's any user/login info visible
    login_texts = await page.evaluate('''() => {
        const body = document.body.innerText;
        const lines = body.split('\\n').filter(l => l.trim().length > 0);
        // Find lines that might show login state or user info
        const userLines = lines.filter(l => 
            l.includes('我的') || l.includes('您好') || l.includes('欢迎') || 
            l.includes('退出') || l.includes('登录') || l.includes('用户') ||
            l.includes('个人中心') || l.includes('学习')
        );
        return userLines.slice(0,20);
    }''')
    print("User-related text lines:")
    for l in login_texts:
        print(f"  {l}")
    
    # Check if the URL needs to change - try navigating to the original course player URL
    course_url = "https://appmywwtfwy6965.h5.xet.pomoho.com/p/course/ecourse/course_2rL24flJeU0H24sq6ODXDrAagq8"
    print(f"\nCurrent URL: {page.url}")
    print(f"Original course URL: {course_url}")
    
    # Look for any visible clickable elements that look like lessons
    clickable = await page.evaluate('''() => {
        const all = document.querySelectorAll('div[class*="item"], div[class*="list"], span[class*="text"]');
        return Array.from(all).filter(el => el.offsetParent !== null && el.innerText.trim().length > 0)
            .slice(0,30).map(el => ({
                tag: el.tagName,
                cls: (el.className||'').substring(0,60),
                txt: el.innerText.trim().substring(0,60)
            }));
    }''')
    print(f"\nClickable elements ({len(clickable)}):")
    for el in clickable:
        print(f"  [{el['tag']}] {el['txt'][:50]}")
    
    await b.close()

asyncio.run(main())
