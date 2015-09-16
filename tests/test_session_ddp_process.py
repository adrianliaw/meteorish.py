import asyncio
import meteorish
from nose.tools import with_setup
from unittest import mock
from .utils import assert_socket_sent_json


def setup_socket_message():
    global loop, server, socket, session
    loop = asyncio.get_event_loop()
    server = meteorish.DDPServer(loop=loop)
    socket = mock.Mock()
    session = meteorish.DDPSession(server, "1", socket, loop)
    server.ddp_sessions[session.id] = session


@with_setup(setup_socket_message)
def test_process_ping():
    session.process_message({"msg": "ping"})
    assert_socket_sent_json(socket, {"msg": "pong"})
    session.process_message({"msg": "ping", "id": "4"})
    assert_socket_sent_json(socket, {"msg": "pong", "id": "4"})
