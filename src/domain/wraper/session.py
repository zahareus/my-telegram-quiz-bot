from functools import wraps

from src.database import sessionmanager
from typing import Callable


def session_wrap(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with sessionmanager.session() as session:
            kwargs['session'] = session
            result = await func(*args, **kwargs)
            await session.commit()
            return result
    return wrapper
