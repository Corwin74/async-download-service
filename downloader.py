import asyncio
import aiohttp
import datetime


async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://0.0.0.0:8080/archive/rur2/') as resp:
            with open('archive.zip', 'wb') as file_descriptor:
                i = 0
                is_delay_done = False
                async for chunk in resp.content.iter_any():
                    print(len(chunk))
                    await asyncio.sleep(10)
                    if i > 255 and not is_delay_done:
                        print('Pause....')
                        print(datetime.datetime.now())
                        await asyncio.sleep(600)
                        is_delay_done = True
                    file_descriptor.write(chunk)
                    i += 1


if __name__ == '__main__':
    asyncio.run(main())
