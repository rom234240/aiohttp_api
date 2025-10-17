from aiohttp import web
from app.auth.jwt import verify_jwt_token

@web.middleware
async def auth_middleware(request, handler):
    public_routes = ['/', '/register', '/login']
    if (request.path in public_routes or
        (request.method == 'GET' and request.path.startswith('/advertisements/'))):
            return await handler(request)
    
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer'):
        return web.json_response(
            {'error': 'Missing or invalid authorization token'},
            status=401
        )
    
    token = auth_header.split(' ')[1]
    user_id = verify_jwt_token(token)
    if not user_id:
        return web.json_response(
            {'error': 'Invalid or expired token'}, 
            status=401
        )
    
    request.user_id = user_id
    return await handler(request)