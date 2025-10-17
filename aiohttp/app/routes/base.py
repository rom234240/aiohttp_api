from aiohttp import web
from app.config import Config

def json_dumps(data):
    import json
    return json.dumps(data, ensure_ascii=False, indent=2)

async def handle_root(request):
    return web.json_response({
        'message': 'Aiohttp API with authentication is running',
        'endpoints': {
            'POST /register': 'Register new user',
            'POST /login': 'User login',
            'POST /advertisements': 'Create advertisement (requires auth)',
            'GET /advertisements/{id}': 'Get advertisement',
            'DELETE /advertisements/{id}': 'Delete advertisement (requires auth)'
        }
    }, dumps=json_dumps)