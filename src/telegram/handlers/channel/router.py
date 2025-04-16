from .deactivate import deactivate_router
from .channel import channel_router
from .editor import editor_router
from .share import share_router

channel_router.include_router(deactivate_router)
channel_router.include_router(editor_router)
channel_router.include_router(share_router)