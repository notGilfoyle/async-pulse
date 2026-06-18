import asyncio
import httpx

in_flight = 0


async def check(client: httpx.AsyncClient, url: str, sem: asyncio.Semaphore) -> tuple[str, object]:
    global in_flight
    async with sem:                                  # wait for a free slot
        in_flight += 1
        print(f"  start (in flight: {in_flight})  {url}")
        try:
            response = await client.get(url)
            status: object = response.status_code
        except httpx.RequestError:
            status = "ERROR"
        in_flight -= 1
        print(f"  done  ({status})  {url}")
        return (url, status)


async def main() -> None:
    urls = [
        "https://example.com",
        "https://www.python.org",
        "https://api.github.com",
        "https://httpbin.org/get",
        "https://www.wikipedia.org",
        "https://www.mozilla.org",
        "https://news.ycombinator.com",
        "https://www.djangoproject.com",
    ]

    sem = asyncio.Semaphore(3)                        # at most 3 requests at a time

    async with httpx.AsyncClient(timeout=5) as client:
        results = await asyncio.gather(*(check(client, url, sem) for url in urls))

    print("\nFinal:", {url: status for url, status in results})


if __name__ == "__main__":
    asyncio.run(main())