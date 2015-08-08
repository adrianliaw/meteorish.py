import ddpserver
import asyncio
from aiohttp import web
from nose.tools import assert_is_instance, assert_in


def test_server_class():
    loop = asyncio.get_event_loop()
    server = ddpserver.DDPServer(loop=loop)
    assert_is_instance(server, web.Application)
    assert_in("__sockjs_managers__", server)
    assert_in("ddp_server", server["__sockjs_managers__"])
