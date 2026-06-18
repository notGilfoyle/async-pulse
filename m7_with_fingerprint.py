import asyncio
import hashlib
import httpx


def fingerprint(data: bytes) -> str:
    """Hashing is blocking, CPU-flavored work — run it off the loop."""
    return hashlib.sha256(data).hexdigest()[:12]


async def check(client: httpx.AsyncClient, url: str) -> tuple[str, object, str]:
    try:
        response = await client.get(url)
        fp = await asyncio.to_thread(fingerprint, response.content)   # don't hash inline
        return (url, response.status_code, fp)
    except httpx.RequestError:
        return (url, "ERROR", "-")


async def main() -> None:
    urls = [
        "https://example.com",
        "https://www.python.org",
        "https://api.github.com",
        "https://www.wikipedia.org",
    ]

    async with httpx.AsyncClient(timeout=5) as client:
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(check(client, url)) for url in urls]
        results = [t.result() for t in tasks]

    print("Health report:")
    for url, status, fp in results:
        print(f"  {status}  {fp}  {url}")


if __name__ == "__main__":
    asyncio.run(main())