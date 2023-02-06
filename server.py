import asyncio
import logging
import os
from aiohttp import web
import aiofiles
import aiohttp_debugtoolbar


logger = logging.getLogger(__file__)
working_directory = os.path.dirname(os.path.abspath(__file__))


async def archive(request):
    response = web.StreamResponse()
    response.enable_chunked_encoding()
    archive_hash = request.match_info.get('archive_hash')

    target_directory = f'{working_directory}/test_photos/{archive_hash}/'
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
    request.app['run_procs'][proc.pid] = True
    i = 0
    j = []
    try:
        while True:
            print(proc.stdout.at_eof())
            print(proc.returncode)
            if proc.stdout.at_eof() and proc.returncode == 0:
                await response.write_eof()
                print('All Zip! Send eof')
                break
            if proc.stdout.at_eof():
                logging.info('Eof bad')
                raise ConnectionResetError
            if i == 2:
                #0/0
                j[3] = 3
                #raise ZeroDivisionError('Караул!')
            data = await proc.stdout.read(1024*400)
            logger.info('Sending archive chunk %s bytes to length', len(data))
            await response.write(data)
            await asyncio.sleep(1)
            #i += 1
    except ConnectionResetError:
        logger.info('Download was interrupted')
    except asyncio.CancelledError:
        logger.info('Cancelled error exception')
    except SystemExit:
        logger.error('System Exit exception')
    else:
        logging.info('Archive has been sent')
        request.app['run_procs'].pop(proc.pid, None)
        return response
    finally:
        print(f"Proc: {request.app['run_procs']}")
        if proc.returncode is None:
            proc.terminate()
            logging.info('Terminating...')
            await proc.communicate()
            logging.info('Zip process has been terminated')
            raise web.HTTPBadRequest(text='Drop connection')


async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


async def on_shutdown(app):
    print('Shutdown Aaaaaaaaaaaaa')
    print(app['run_procs'])


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logger.setLevel(logging.INFO)
    logger.info('Working directory: %s', working_directory)
    # add stuff to the loop, e.g. using asyncio.create_task()
    # ...
    app = web.Application()
    app['run_procs'] = {}
    aiohttp_debugtoolbar.setup(app)
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', archive),
    ])
    app.on_shutdown.append(on_shutdown)
    web.run_app(app)


if __name__ == '__main__':
    main()
