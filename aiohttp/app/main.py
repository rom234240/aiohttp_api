import asyncio
import logging
from aiohttp import web
from app.config import Config
from app.models import create_tables
from app.middleware import json_middleware, auth_middleware
from app.routes import (
    handle_root, register_user, login_user,
    create_advertisement, get_advertisement, delete_advertisement
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_app():
    try:
        Config.validate()
        logger.info("Configuration validated successfully")

        from app.models import create_tables

        app = web.Application(middlewares=[json_middleware, auth_middleware])

        logger.info("Creating database tables")
        await create_tables()
        logger.info("Database tables created successfully")


        app.router.add_get('/', handle_root)
        app.router.add_post('/register', register_user)
        app.router.add_post('/login', login_user)
        app.router.add_post('/advertisements', create_advertisement)
        app.router.add_get(r'/advertisements/{ad_id:\d+}', get_advertisement)
        app.router.add_delete(r'/advertisements/{ad_id:\d+}', delete_advertisement)

        logger.info("Application initialized successfuly")
        return app
    
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise

if __name__ == '__main__':
    logger.info("Starting AioHTTP application")
    web.run_app(init_app(), host='0.0.0.0', port=5000)