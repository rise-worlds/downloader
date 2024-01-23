import asyncio
import os
import urllib.parse
from playwright.async_api import async_playwright, Response
import requests


bash_path = '.'
path={}

def on_response(rep:Response):
    global path
    # print(rep.text)
    url = urllib.parse.urlparse(rep.url)
    print(url.path)
    if path.get(url.path) is None:
        response = requests.get(url.geturl())
        if response.status_code == 200 :
            dir_name = f'{bash_path}{os.path.dirname(url.path)}'
            os.makedirs(dir_name, exist_ok=True)
            # filename = os.path.basename(url.path)
            file_path = f'{bash_path}{url.path}'
            with open(file_path, 'wb') as f:
                f.write(response.content)
            path[url.path] = 1
    pass


async def main():
    default_timeout = 600 * 1000
    # 打开浏览器
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False, timeout=default_timeout, devtools=False)  #, proxy={"server": "http://127.0.0.1:8787"}
        context = await browser.new_context(permissions=[])
        context.set_default_timeout(default_timeout)
        context.set_default_navigation_timeout(default_timeout)
        hold_page = await context.new_page()

        try:
            # 打开游戏页面
            page = await context.new_page()

            page.on('response', on_response)
            page.on('load', lambda exc: print(f"page load: {exc.url}"))
            await page.goto("https://incubator-static.easygame2021.com/move-block-game/web-mobile/index.html")
            # 等待页面加载完成
            await page.wait_for_load_state(timeout=default_timeout)

            while not page.is_closed():
                await asyncio.sleep(0.1)
                continue
        finally:
            # 关闭浏览器
            await hold_page.close()
            await context.close()
            await browser.close()

    print(f'get {len(path)} assets.')
    # for key in path.keys():
    #     print(key)

if __name__ == '__main__':
    asyncio.run(main())
