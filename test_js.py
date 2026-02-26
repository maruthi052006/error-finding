
import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        pg = await b.new_page()
        pg.on('console', lambda m: print('CONSOLE:', m.text))
        pg.on('pageerror', lambda e: print('PAGE_ERROR:', e))
        await pg.goto('http://127.0.0.1:8000/login/')
        await pg.fill('input[name=username]', 'testteam1')
        await pg.fill('input[name=password]', 'password')
        await pg.click('button[type=submit]')
        await pg.goto('http://127.0.0.1:8000/compiler/dashboard/')
        print('On dashboard')
        # Click enter round
        await pg.click('a.btn-primary')
        print('Clicked enter round')
        await pg.wait_for_timeout(2000)
        print('Current url:', pg.url)
        # Click nav btn
        btns = await pg.query_selector_all('.nav-btn')
        print('Found', len(btns), 'nav btns')
        if len(btns) > 1:
            await btns[1].click()
            print('Clicked Q2')
            await pg.wait_for_timeout(2000)
            print('New url:', pg.url)
        await b.close()
asyncio.run(main())
