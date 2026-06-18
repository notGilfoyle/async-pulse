import asyncio
import time


def blocking_work(seconds: float) -> None:
    time.sleep(seconds)


async def heartbeat() -> None:
    while True:
        print("  heartbeat")
        await asyncio.sleep(0.5)


async def main() -> None:
    hb = asyncio.create_task(heartbeat())

    await asyncio.sleep(1.5)
    print(">>> calling blocking_work(3) via asyncio.to_thread — heartbeat should keep ticking")
    await asyncio.to_thread(blocking_work, 3)   # off to a helper thread; loop stays free
    print(">>> blocking_work done")

    await asyncio.sleep(1.5)
    hb.cancel()


if __name__ == "__main__":
    asyncio.run(main())