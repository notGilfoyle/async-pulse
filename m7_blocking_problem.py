import asyncio
import time


def blocking_work(seconds: float) -> None:
    """A synchronous blocking call — stands in for requests.get, a sync DB query, etc."""
    time.sleep(seconds)                      # NOT asyncio.sleep — this freezes the loop


async def heartbeat() -> None:
    while True:
        print("  heartbeat")
        await asyncio.sleep(0.5)


async def main() -> None:
    hb = asyncio.create_task(heartbeat())    # keep the reference (see the footgun list!)

    await asyncio.sleep(1.5)
    print(">>> calling blocking_work(3) DIRECTLY — watch the heartbeat")
    blocking_work(3)                         # loop is frozen for 3 whole seconds
    print(">>> blocking_work done")

    await asyncio.sleep(1.5)
    hb.cancel()


if __name__ == "__main__":
    asyncio.run(main())