import asyncio
import datetime
import argparse
import aiohttp


async def main(parsed_args):
    async with aiohttp.ClientSession() as session:
        async with session.get(parsed_args.url) as resp:
            with open(parsed_args.filename, 'wb') as file_descriptor:
                i = 0
                async for chunk in resp.content.iter_any():
                    print(len(chunk))
                    await asyncio.sleep(parsed_args.latency)
                    if i == parsed_args.pause_at and parsed_args.delay:
                        print('Pause....')
                        print(datetime.datetime.now())
                        await asyncio.sleep(parsed_args.delay)
                    file_descriptor.write(chunk)
                    i += 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Downloader')
    parser.add_argument('url')
    parser.add_argument(
        '-f', '--filename',
        default='archive.zip',
        required=False
    )
    parser.add_argument('-d', '--delay', type=int)
    parser.add_argument('-p', '--pause_at', type=int, default=3)
    parser.add_argument('-l', '--latency', type=float, default=0)
    parsed_args = parser.parse_args()
    print(parsed_args)
    asyncio.run(main(parsed_args))
