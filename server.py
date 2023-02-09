import asyncio
import logging
import os
import argparse
from aiohttp import web
import aiofiles


logger = logging.getLogger(__file__)
working_directory = os.path.dirname(os.path.abspath(__file__))
latency = 1
photo_directory = '/test_photos/'


async def archive(request):
    response = web.StreamResponse()
    response.enable_chunked_encoding()
    archive_hash = request.match_info.get('archive_hash')

    target_directory = working_directory + photo_directory + archive_hash
    print(f'{target_directory= }')
    if not os.path.exists(target_directory):
        logging.error(
            "Cannot access '%s': No such directory",
            target_directory
        )
        raise web.HTTPNotFound(text='Архив не существует или был удален')

    response.headers['Content-Type'] = 'application/octet-stream'
    response.headers['Content-Disposition'] = \
        'attachment; filename="photo_archive.zip"'

    await response.prepare(request)

    proc = await asyncio.create_subprocess_exec(
        'zip',
        '-rq',
        '-',
        '.',
        stdout=asyncio.subprocess.PIPE,
        cwd=target_directory,
    )
    try:
        while True:
            if proc.stdout.at_eof() and proc.returncode == 0:
                await response.write_eof()
                logger.debug('Zip process exit status is OK')
                break
            if proc.stdout.at_eof():
                logger.debug(
                    'Receive eof, but zip process returncode: %s',
                    proc.returncode
                )
                raise ConnectionResetError
            data = await proc.stdout.read(1024*400)
            logger.debug('Sending archive chunk %s bytes to length', len(data))
            await response.write(data)
            await asyncio.sleep(latency)
    except ConnectionResetError:
        logger.info('Download was interrupted')
    except SystemExit:
        logger.error('System Exit exception')
    else:
        logger.info('Archive has been sent')
        return response
    finally:
        if proc.returncode is None:
            proc.terminate()
            logger.debug('Terminating zip process...')
            await proc.communicate()
            logging.debug('Zip process has been terminated')
            raise web.HTTPBadRequest(text='Drop connection')


async def handle_index_page(_):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


def main():
    global latency, photo_directory
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', type=str)
    parser.add_argument('-l', '--latency', type=float, default=0)
    parser.add_argument("-v", "--verbose", nargs='?',
                        const=True, default=False,
                        help="Activate debug mode.")
    parsed_args = parser.parse_args()
    latency = parsed_args.latency
    if parsed_args.directory:
        photo_directory = parsed_args.directory
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    if parsed_args.verbose:
        logger.setLevel(logging.DEBUG)
    logger.info('Working directory: %s', working_directory)
    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', archive),
    ])
    web.run_app(app)


if __name__ == '__main__':
    main()
