import asyncio
import logging
import os
import argparse
from aiohttp import web
import aiofiles


logger = logging.getLogger(__file__)


async def archive(request):
    response = web.StreamResponse()
    response.enable_chunked_encoding()
    archive_hash = request.match_info.get('archive_hash')

    target_directory = request.app['working_directory'] + '/' + archive_hash
    print(target_directory)
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
            await asyncio.sleep(request.app['latency'])
            print(request.app['latency'])
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
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', type=str, default='test_photos/')
    parser.add_argument('-l', '--latency', type=float, default=1)
    parser.add_argument("-v", "--verbose", nargs='?',
                        const=True, default=False,
                        help="Activate debug mode.")
    parsed_args = parser.parse_args()
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    if parsed_args.verbose:
        logger.setLevel(logging.DEBUG)
    working_directory = os.path.dirname(os.path.abspath(__file__))
    if parsed_args.directory[0] == '/':
        working_directory = parsed_args.directory
    else:
        working_directory += '/' + parsed_args.directory
    if working_directory[-1] == '/':
        working_directory = working_directory[:-1]
    if not os.path.exists(working_directory):
        logger.error("%s not exist", working_directory)
        return
    logger.info('Working directory: %s', working_directory)
    app = web.Application()
    app['latency'] = parsed_args.latency
    app['working_directory'] = parsed_args.directory
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', archive),
    ])
    web.run_app(app)


if __name__ == '__main__':
    main()
