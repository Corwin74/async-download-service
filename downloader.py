import asyncio
import datetime
import argparse
import aiohttp


async def main(parsed_args):
    async with aiohttp.ClientSession() as session:
        async with session.get(parsed_args.url) as resp:
            with open(parsed_args.filename, 'wb') as file_descriptor:
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
    parser = argparse.ArgumentParser(description='Downloader')
    parser.add_argument('url', default=None)
    parser.add_argument('--filename', default='archive.zip', required=False)
    parsed_args = parser.parse_args()
    print(parsed_args.url)
    asyncio.run(main(parsed_args))
