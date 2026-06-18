import asyncio
import httpx


async def check(client: httpx.AsyncClient, url: str) -> tuple[str, object]:
    try:
        response = await client.get(url)
        return (url, response.status_code)
    except httpx.RequestError:
        return (url, "ERROR")


async def main() -> None:
    urls = [
        "https://example.com",
        "https://www.python.org",
        "https://api.github.com",
        "https://httpbin.org/delay/1",
        "https://www.wikipedia.org",
    ]

    async with httpx.AsyncClient(timeout=5) as client:
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(check(client, url)) for url in urls]
        # reached only after EVERY task in the group has finished
        results = [t.result() for t in tasks]

    print("Results:")
    for url, status in results:
        print(f"  {status}  {url}")


if __name__ == "__main__":
    asyncio.run(main())