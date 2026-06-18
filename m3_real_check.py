import asyncio
import time
import httpx


async def check(client: httpx.AsyncClient, url: str) -> tuple[str, object, float]:
    start = time.perf_counter()
    try:
        response = await client.get(url)
        status = response.status_code
    except httpx.RequestError:
        status = "ERROR"          # a seatbelt so one dead URL doesn't crash the batch
    elapsed = time.perf_counter() - start
    return (url, status, elapsed)


async def main() -> None:
    urls = [
        "https://example.com",
        "https://httpbin.org/delay/2",   # this one deliberately takes ~2s to reply
        "https://www.python.org",
        "https://api.github.com",
    ]

    overall_start = time.perf_counter()

    async with httpx.AsyncClient(timeout=10) as client:
        results = await asyncio.gather(*(check(client, url) for url in urls))

    print("\nHealth report:")
    for url, status, elapsed in results:
        print(f"  {status!s:>6}  {elapsed:5.2f}s  {url}")

    total = time.perf_counter() - overall_start
    print(f"\nChecked {len(urls)} sites in {total:.2f}s")


if __name__ == "__main__":
    asyncio.run(main())