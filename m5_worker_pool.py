import asyncio
import httpx


async def worker(name: str, queue: asyncio.Queue, client: httpx.AsyncClient) -> None:
    while True:                                  # line cook: grab tickets forever
        url = await queue.get()                  # wait for the next ticket
        try:
            response = await client.get(url)
            print(f"  [{name}] {response.status_code}  {url}")
        except httpx.RequestError:
            print(f"  [{name}] ERROR  {url}")
        finally:
            queue.task_done()                    # always mark the ticket done


async def main() -> None:
    urls = [
        "https://example.com", "https://www.python.org", "https://api.github.com",
        "https://httpbin.org/get", "https://www.wikipedia.org", "https://www.mozilla.org",
        "https://news.ycombinator.com", "https://www.djangoproject.com",
    ]

    queue: asyncio.Queue = asyncio.Queue()
    for url in urls:
        queue.put_nowait(url)                    # clip all tickets to the rail

    async with httpx.AsyncClient(timeout=5) as client:
        # start 3 line cooks
        workers = [asyncio.create_task(worker(f"cook-{i}", queue, client)) for i in range(3)]

        await queue.join()                       # wait until every ticket is task_done

        # work's finished — stop the cooks (they loop forever)
        for w in workers:
            w.cancel()
        await asyncio.gather(*workers, return_exceptions=True)   # swallow the CancelledErrors

    print("\nAll done.")


if __name__ == "__main__":
    asyncio.run(main())