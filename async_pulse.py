import asyncio
import signal
import time
from datetime import datetime

import httpx

CONCURRENCY = 5        # max requests in flight at once
INTERVAL = 10          # seconds between rounds
TIMEOUT = 5            # give up on one request after this many seconds
RETRIES = 1            # extra attempts on failure

URLS = [
    "https://example.com",
    "https://www.python.org",
    "https://api.github.com",
    "https://www.wikipedia.org",
    "https://www.djangoproject.com",
]


async def check(client: httpx.AsyncClient, url: str, sem: asyncio.Semaphore):
    async with sem:                                  # M5: respect the concurrency cap
        start = time.perf_counter()
        status: object = "ERROR"
        for attempt in range(RETRIES + 1):           # M4: retry with backoff
            try:
                response = await client.get(url)
                return (url, response.status_code, time.perf_counter() - start)
            except httpx.TimeoutException:
                status = "TIMEOUT"
            except httpx.ConnectError:
                status = "NO CONNECT"
            except httpx.RequestError:
                status = "ERROR"
            if attempt < RETRIES:
                await asyncio.sleep(attempt + 1)
        return (url, status, time.perf_counter() - start)


async def run_round(client: httpx.AsyncClient, sem: asyncio.Semaphore) -> None:
    async with asyncio.TaskGroup() as tg:            # M6: structured concurrency
        tasks = [tg.create_task(check(client, url, sem)) for url in URLS]
    results = [t.result() for t in tasks]

    stamp = datetime.now().strftime("%H:%M:%S")
    up = sum(1 for _, status, _ in results if status == 200)
    print(f"\n[{stamp}]  {up}/{len(results)} up")
    for url, status, elapsed in results:
        mark = "OK" if status == 200 else "!!"
        print(f"  {mark}  {status!s:>10}  {elapsed:5.2f}s  {url}")


async def monitor(stop_event: asyncio.Event, client: httpx.AsyncClient, sem: asyncio.Semaphore) -> None:
    while True:
        await run_round(client, sem)
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=INTERVAL)
            break                                    # stop requested → leave the loop
        except asyncio.TimeoutError:
            pass                                     # interval passed → another round


async def main() -> None:
    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):      # flip the flag on Ctrl+C / kill
        loop.add_signal_handler(sig, stop_event.set)

    sem = asyncio.Semaphore(CONCURRENCY)
    print(f"async-pulse: monitoring {len(URLS)} sites every {INTERVAL}s. Press Ctrl+C to stop.")

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        await monitor(stop_event, client, sem)       # client auto-closes when this returns

    print("\nStopped cleanly. Goodbye.")


if __name__ == "__main__":
    asyncio.run(main())