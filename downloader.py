import asyncio
import logging
import argparse
import aiohttp


logger = logging.getLogger(__file__)


async def download(url, filename, pause_at=None, latency=0, delay=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                with open(filename, 'wb') as file_descriptor:
                    logger.info('Start downloading...')
                    iteration_counter = 0
                    async for chunk in resp.content.iter_any():
                        logger.debug('Iteration #%s', iteration_counter)
                        logger.debug(
                            'Receive chunk %s bytes length',
                            len(chunk)
                        )
                        await asyncio.sleep(latency)
                        if iteration_counter == pause_at and delay:
                            logger.info('Pause for %s seconds', delay)
                            await asyncio.sleep(delay)
                        file_descriptor.write(chunk)
                        iteration_counter += 1
                logger.info('Download save to %s', filename)
            else:
                logger.error(await resp.text())


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    parser = argparse.ArgumentParser()
    parser.add_argument('url')
    parser.add_argument(
        '-f', '--filename',
        default='archive.zip',
        required=False
    )
    parser.add_argument('-d', '--delay', type=int)
    parser.add_argument('-p', '--pause_at', type=int, default=3)
    parser.add_argument('-l', '--latency', type=float, default=0.5)
    parser.add_argument("-v", "--verbose", nargs='?',
                        const=True, default=False,
                        help="Activate debug mode.")
    parsed_args = parser.parse_args()
    if parsed_args.verbose:
        logger.setLevel(logging.DEBUG)
    asyncio.run(download(
        parsed_args.url,
        parsed_args.filename,
        parsed_args.pause_at,
        parsed_args.latency,
        parsed_args.delay,
    ))


if __name__ == '__main__':
    main()
