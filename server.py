import asyncio
import os
from aiohttp import web
import aiofiles


async def archive(request):
    response = web.StreamResponse()
    archive_hash = request.match_info.get('archive_hash')

    response.headers['Content-Type'] = 'application/octet-stream'
    response.headers['Content-Disposition'] = \
        'attachment; filename="photo_archive.zip"'

    # Отправляет клиенту HTTP заголовки
    await response.prepare(request)

    proc = await asyncio.create_subprocess_exec(
        'zip',
        '-r',
        '-',
        '.',
        stdout=asyncio.subprocess.PIPE,
        cwd=f'{working_directory}/test_photos/{archive_hash}/'
    )

    while True:
        if proc.stdout.at_eof():
            break
        data = await proc.stdout.read(1024*400)
        await response.write(data)

    await response.write_eof()
    await proc.wait()
    return response


async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


if __name__ == '__main__':
    working_directory = os.path.dirname(os.path.abspath(__file__))
    print(f'Working directory: {working_directory}')
    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', archive),
    ])
    web.run_app(app)
