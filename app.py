import os
import json
from datetime import datetime
from aiohttp import web
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime, select
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment variables")

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

class Advertisement(Base):
    __tablename__ = 'advertisement'

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    owner =Column(String(50), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'owner': self.owner
        }
    
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

async def create_ad(request):
    data = request.json_data
    if not data or not all(key in data for key in ['title', 'description', 'owner']):
        return web.json_response(
            {'error': 'Missing data'},
            status=400,
            dumps=json.dumps
        )
    
    async with AsyncSessionLocal() as session:
        new_ad = Advertisement(
            title=data['title'],
            description=data['description'],
            owner=data['owner']
        )
        session.add(new_ad)
        await session.commit()
        await session.refresh(new_ad)
        return web.json_response(
            new_ad.to_dict(),
            status=201,
            dumps=json.dumps
        )
    
async def get_ad(request):
    ad_id = int(request.match_info['ad_id'])
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Advertisement).where(Advertisement.id == ad_id))
        ad = result.scalar_one_or_none()

        if not ad:
            return web.json_response(
                {'error': 'Advertisement not found'},
                status=404,
                dumps=json.dumps
            )
        return web.json_response(
            ad.to_dict(),
            dumps=json.dumps
        )
    
async def delete_ad(request):
    ad_id = int(request.match_info['ad_id'])
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Advertisement).where(Advertisement.id == ad_id))
        ad = result.scalar_one_or_none()
        
        if not ad:
            return web.json_response(
                {'error': 'Advertisement not found'}, 
                status=404,
                dumps=json.dumps
            )
        
        await session.delete(ad)
        await session.commit()
        return web.Response(status=204)
    
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def handle_root(request):
    return web.json_response({
        'message': 'Aiohttp API is running',
        'endpoints': {
            'POST /aiohttp': 'Created advertisement',
            'GET /aiohttp/{id}': 'Get advertisement',
            'DELETE /aiohttp/{id}': 'Delete advertisement'
        }
    })
    
async def init_app():
    app = web.Application(middlewares=[json_middleware])

    await create_tables()

    app.router.add_get('/', handle_root)
    app.router.add_post('/aiohttp', create_ad)
    app.router.add_get(r'/aiohttp/{ad_id:\d+}', get_ad)
    app.router.add_delete(r'/aiohttp/{ad_id:\d+}', delete_ad)

    return app

if __name__ == '__main__':
    web.run_app(init_app(), host='0.0.0.0', port=5000)