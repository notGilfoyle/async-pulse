import asyncio
import time


async def fake_check(url: str, latency: float) -> tuple[str, int]:
    print(f"  -> checking {url}")
    await asyncio.sleep(latency)           # simulated network wait
    print(f"  <- {url} responded")
    return (url, 200)                      # pretend it returned HTTP 200


async def main() -> None:
    start = time.perf_counter()

    results = await asyncio.gather(
        fake_check("api.alpha.dev", 2.0),
        fake_check("api.bravo.dev", 1.0),
        fake_check("api.charlie.dev", 1.5),
    )

    print("\nResults:")
    for url, status in results:
        print(f"  {url} -> {status}")

    elapsed = time.perf_counter() - start
    print(f"\nTotal time: {elapsed:.2f}s")


if __name__ == "__main__":
    asyncio.run(main())