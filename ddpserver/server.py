import asyncio
import sockjs
from aiohttp import web


class DDPServer(web.Application):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sockjs.add_endpoint(self, self._handle_message, name="ddp_server")

    def _handle_message(self, msg, session):
        pass
