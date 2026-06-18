import asyncio
import time


async def fake_check(url: str, latency: float) -> None:
    """Pretend to check a URL. asyncio.sleep stands in for a real network call."""
    print(f"  -> checking {url}")
    await asyncio.sleep(latency)          # simulated network wait
    print(f"  <- {url} responded after {latency}s")


async def main() -> None:
    start = time.perf_counter()

    # For now, run them ONE AT A TIME with sequential awaits.
    await fake_check("api.alpha.dev", 2.0)
    await fake_check("api.bravo.dev", 1.0)
    await fake_check("api.charlie.dev", 1.5)

    elapsed = time.perf_counter() - start
    print(f"\nTotal time: {elapsed:.2f}s")


if __name__ == "__main__":
    asyncio.run(main())