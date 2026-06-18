import asyncio
import time
import httpx


async def check(client: httpx.AsyncClient, url: str, retries: int = 1) -> tuple[str, object, float]:
    start = time.perf_counter()
    status: object = "ERROR"

    for attempt in range(retries + 1):
        try:
            response = await client.get(url)
            elapsed = time.perf_counter() - start
            return (url, response.status_code, elapsed)      # success — return immediately
        except httpx.TimeoutException:
            status = "TIMEOUT"
        except httpx.ConnectError:
            status = "NO CONNECT"
        except httpx.RequestError:
            status = "ERROR"

        if attempt < retries:                                # failed, but we have tries left
            await asyncio.sleep(attempt + 1)                 # backoff: 1s, then 2s, ...

    elapsed = time.perf_counter() - start
    return (url, status, elapsed)


async def main() -> None:
    urls = [
        "https://example.com",
        "https://httpbin.org/delay/2",
        "https://www.python.org",
        "https://api.github.com",
        "https://this-domain-does-not-exist-9999.dev",   # to see NO CONNECT
    ]

    overall_start = time.perf_counter()

    async with httpx.AsyncClient(timeout=3) as client:      # give up on any one request after 3s
        results = await asyncio.gather(*(check(client, url) for url in urls))

    print("\nHealth report:")
    for url, status, elapsed in results:
        print(f"  {status!s:>10}  {elapsed:5.2f}s  {url}")

    total = time.perf_counter() - overall_start
    print(f"\nChecked {len(urls)} sites in {total:.2f}s")


if __name__ == "__main__":
    asyncio.run(main())