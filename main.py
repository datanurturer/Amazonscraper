from apify import Actor
from crawlee import PlaywrightCrawler, Request
from playwright.async_api import Page

async def extract_product_data(page: Page, request: Request):
    await page.wait_for_selector("#productTitle", timeout=10000)
    title = await page.locator("#productTitle").inner_text()
    try:
        price = await page.locator(".a-price .a-offscreen").first.inner_text()
    except:
        price = "N/A"
    try:
        rating = await page.locator(".a-icon-alt").first.inner_text()
    except:
        rating = "N/A"

    return {
        "url": request.url,
        "title": title.strip(),
        "price": price.strip(),
        "rating": rating.strip()
    }

async def main():
    async with Actor:
        input_data = await Actor.get_input() or {}
        urls = input_data.get("urls", [])

        if not urls:
            raise ValueError("Input must include a list of 'urls'.")

        results = []

        async def handle_page(context):
            result = await extract_product_data(context.page, context.request)
            results.append(result)

        crawler = PlaywrightCrawler(
            request_handler=handle_page,
            headless=True,
        )

        for url in urls:
            await crawler.add_requests([Request(url=url)])

        await crawler.run()
        await Actor.push_data(results)