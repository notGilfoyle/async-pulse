import asyncio
import httpx


async def check(client: httpx.AsyncClient, url: str) -> tuple[str, object]:
    try:
        response = await client.get(url)
        return (url, response.status_code)
    except httpx.RequestError:
        return (url, "ERROR")


async def as_they_finish(client, urls):
    """Async generator: yields each result the moment its check completes."""
    tasks = [asyncio.create_task(check(client, url)) for url in urls]
    for coro in asyncio.as_completed(tasks):
        yield await coro


async def main() -> None:
    urls = [
        "https://httpbin.org/delay/3",   # slowest — should print LAST
        "https://example.com",           # fast — should print first
        "https://www.python.org",
        "https://httpbin.org/delay/1",   # middle
    ]

    async with httpx.AsyncClient(timeout=10) as client:
        async for url, status in as_they_finish(client, urls):
            print(f"  {status}  {url}")   # prints live, in finishing order


if __name__ == "__main__":
    asyncio.run(main())