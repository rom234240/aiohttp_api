from aiohttp import web
from sqlalchemy import select
from app.models import get_db_session, Advertisement, User
import logging

logger = logging.getLogger(__name__)

async def create_advertisement(request):
    try:
        if not hasattr(request, 'user_id'):
            return web.json_response(
                {'error': 'Authentication required'},
                status=401
            )
        
        data = request.json_data
        if not data or not all(key in data for key in ['title', 'description']):
            return web.json_response(
                {'error': 'Missing title or description'},
                status=400
            )
        
        async for session in get_db_session():
            new_ad = Advertisement(
                title=data['title'],
                description=data['description'],
                user_id=request.user_id
            )
            session.add(new_ad)
            await session.commit()
            await session.refresh(new_ad)
            
            user_result = await session.execute(select(User).where(User.id == request.user_id))
            user = user_result.scalar_one()
            
            response_data = {
                'id': new_ad.id,
                'title': new_ad.title,
                'description': new_ad.description,
                'created_at': new_ad.created_at.isoformat(),
                'user_id': new_ad.user_id,
                'owner': user.username
            }
            
            return web.json_response(response_data, status=201)
            
    except Exception as e:
        logger.error(f"Error in create_advertisement: {str(e)}", exc_info=True)
        return web.json_response(
            {'error': 'Internal server error'},
            status=500
        )

async def get_advertisement(request):
    try:
        ad_id = int(request.match_info['ad_id'])
        async for session in get_db_session():
            result = await session.execute(
                select(Advertisement).where(Advertisement.id == ad_id)
            )
            ad = result.scalar_one_or_none()

            if not ad:
                return web.json_response(
                    {'error': 'Advertisement not found'},
                    status=404
                )
            
            user_result = await session.execute(select(User).where(User.id == ad.user_id))
            user = user_result.scalar_one_or_none()
            
            response_data = {
                'id': ad.id,
                'title': ad.title,
                'description': ad.description,
                'created_at': ad.created_at.isoformat(),
                'user_id': ad.user_id,
                'owner': user.username if user else 'Unknown'
            }
            
            return web.json_response(response_data)
            
    except ValueError:
        return web.json_response(
            {'error': 'Invalid advertisement ID'},
            status=400
        )
    except Exception as e:
        logger.error(f"Error in get_advertisement: {str(e)}", exc_info=True)
        return web.json_response(
            {'error': 'Internal server error'},
            status=500
        )

async def delete_advertisement(request):
    try:
        if not hasattr(request, 'user_id'):
            return web.json_response(
                {'error': 'Authentication required'},
                status=401
            )
        
        ad_id = int(request.match_info['ad_id'])
        async for session in get_db_session():
            result = await session.execute(
                select(Advertisement).where(Advertisement.id == ad_id)
            )
            ad = result.scalar_one_or_none()
            
            if not ad:
                return web.json_response(
                    {'error': 'Advertisement not found'}, 
                    status=404
                )
            
            if ad.user_id != request.user_id:
                return web.json_response(
                    {'error': 'Access denied'}, 
                    status=403
                )
            
            await session.delete(ad)
            await session.commit()
            return web.Response(status=204)
            
    except ValueError:
        return web.json_response(
            {'error': 'Invalid advertisement ID'},
            status=400
        )
    except Exception as e:
        logger.error(f"Error in delete_advertisement: {str(e)}", exc_info=True)
        return web.json_response(
            {'error': 'Internal server error'},
            status=500
        )