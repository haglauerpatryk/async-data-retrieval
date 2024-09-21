import asyncio
import aiohttp

async def fetch_data(session, url):
    results = []

    while url:
        async with session.get(url) as response:
            data = await response.json()
            results.extend(data['results'])
            url = data['next']

    return results

async def main():
    url = 'https://swapi.dev/api/people/?page=1'  # Replace with your initial URL
    async with aiohttp.ClientSession() as session:
        data = await fetch_data(session, url)
        print(data)

asyncio.run(main())