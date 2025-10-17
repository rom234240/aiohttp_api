from aiohttp import web
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
import re
from app.models import get_db_session, User
from app.auth import hash_password, check_password, validate_password, create_jwt_token

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

async def register_user(request):
    data = request.json_data
    if not data or not all(key in data for key in ['username', 'email', 'password']):
        return web.json_response(
            {'error': 'Missing required fields: username, email, password'},
            status=400
        )
    
    if not validate_email(data['email']):
        return web.json_response(
            {'error': 'Invalid email format'},
            status=400
        )
    
    if not validate_password(data['password']):
        return web.json_response(
            {'error': 'Password must be at least 8 chacters long'}, 
            status=400
        )
    
    async for session in get_db_session():
        try:
            password_hash = hash_password(data['password'])
            new_user = User(
                username=data['username'],
                email = data['email'],
                password_hash = password_hash
            )
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)

            token = create_jwt_token(new_user.id)
            return web.json_response({
                'user': new_user.to_dict(),
                'token': token
            }, status=201)
        except IntegrityError:
            return web.json_response(
                {'error': 'Username or email already exists'},
                status=400
            )
        
async def login_user(request):
    data = request.json_data
    if not data or not all(key in data for key in ['email', 'password']):
        return web.json_response(
            {'error': 'Missing email or password'},
            status=400
        )
    async for session in get_db_session():
        result = await session.execute(select(User).where(User.email == data['email']))
        user = result.scalar_one_or_none()

        if not user or not check_password(data['password'], user.password_hash):
            return web.json_response(
                {'error': 'Invalid email or password'},
                status=401
            )
        
        token = create_jwt_token(user.id)
        return web.json_response({
            'user': user.to_dict(),
            'token': token
        })
    