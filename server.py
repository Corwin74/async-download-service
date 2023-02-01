import asyncio
import logging
import os
from aiohttp import web
import aiofiles
import aiohttp_debugtoolbar

logger = logging.getLogger(__file__)
working_directory = os.path.dirname(os.path.abspath(__file__))


async def archive(request):
    print(await request.text())
    response = web.StreamResponse()
    response.enable_chunked_encoding()
    archive_hash = request.match_info.get('archive_hash')

    target_directory = f'{working_directory}/test_photos/{archive_hash}/'
    if not os.path.exists(target_directory):
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
    i = 0
    try:
        while True:
            if proc.stdout.at_eof():
                break
            if i == 2:
                raise ZeroDivisionError('Караул!')
            data = await proc.stdout.read(1024*400)
            logger.info('Sending archive chunk %s bytes to lenght', len(data))
            await response.write(data)
            await asyncio.sleep(5)
    except ConnectionResetError:        
        logger.info('Download was interrupted')
    except asyncio.CancelledError:
        logger.info('cancelled error exception')
    except (SystemExit, ZeroDivisionError):
        logger.error('Download was interrupted')
    finally:
        proc.terminate()
    await response.write_eof()
    await proc.wait()
    return response


async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logger.setLevel(logging.INFO)
    logger.info('Working directory: %s', working_directory)
    app = web.Application()
    aiohttp_debugtoolbar.setup(app)
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', archive),
    ])
    web.run_app(app)


if __name__ == '__main__':
    main()
