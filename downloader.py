import asyncio
import aiohttp


async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://0.0.0.0:8080/archive/7knsa/') as resp:
            with open('archive.zip', 'wb') as file_descriptor:
                i = 0
                async for chunk in resp.content.iter_any():
                    print(len(chunk))
                    await asyncio.sleep(1)
                    if i > 2:
                        print('Pause....')
                        await asyncio.sleep(600)
                    file_descriptor.write(chunk)
                    i += 1


if __name__ == '__main__':
    asyncio.run(main())
