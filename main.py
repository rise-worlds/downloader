# -*- coding: utf-8 -*-
""" use playwright & requests download h5 resources """
import argparse
import asyncio
import os
import urllib.parse
from playwright.async_api import async_playwright, Response
import requests


BASE_PATH = '.'
CACHED_PATH = {}
DEFAULT_TIMEOUT = 600 * 1000


def on_response(rep:Response):
    """ page request callback """
    # print(rep.text)
    url = urllib.parse.urlparse(rep.url)
    print(url.path)
    if CACHED_PATH.get(url.path) is None:
        response = requests.get(url.geturl(), timeout=DEFAULT_TIMEOUT)
        if response.status_code == 200 :
            dir_name = f'{BASE_PATH}{os.path.dirname(url.path)}'
            os.makedirs(dir_name, exist_ok=True)
            # filename = os.path.basename(url.path)
            file_path = f'{BASE_PATH}{url.path}'
            with open(file_path, 'wb') as f:
                f.write(response.content)
            CACHED_PATH[url.path] = 1


async def main():
    """ main """
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="need download be h5 url address")
    args = parser.parse_args()

    if len(args.url) == 0 :
        parser.print_help()
        return

    # 打开浏览器
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False, timeout=DEFAULT_TIMEOUT, devtools=False)
            #, proxy={"server": "http://127.0.0.1:8787"}
        context = await browser.new_context(permissions=[])
        context.set_default_timeout(DEFAULT_TIMEOUT)
        context.set_default_navigation_timeout(DEFAULT_TIMEOUT)
        hold_page = await context.new_page()

        try:
            # 打开游戏页面
            page = await context.new_page()

            page.on('response', on_response)
            page.on('load', lambda exc: print(f"page load: {exc.url}"))
            await page.goto(args.url)
            # 等待页面加载完成
            await page.wait_for_load_state(timeout=DEFAULT_TIMEOUT)

            while not page.is_closed():
                await asyncio.sleep(0.1)
                continue
        finally:
            # 关闭浏览器
            await hold_page.close()
            await context.close()
            await browser.close()

    print(f'get {len(CACHED_PATH)} assets.')
    # for key in CACHED_PATH.keys():
    #     print(key)

if __name__ == '__main__':
    asyncio.run(main())
