from aiohttp import web

@web.middleware
async def json_middleware(request, handler):
    if request.method in ['POST', 'PUT'] and request.content_type == 'application/json':
        try:
            request.json_data = await request.json()
        except:
            request.json_data = None
    else:
        request.json_data = None
    return await handler(request)