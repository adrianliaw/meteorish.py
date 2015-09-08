import asyncio
import ddpserver
from nose.tools import with_setup
from unittest import mock


def setup_socket_message():
    global loop, server, socket, session
    loop = asyncio.get_event_loop()
    server = ddpserver.DDPServer(loop=loop)
    socket = mock.Mock()
    session = ddpserver.DDPSession(server, "1", socket, loop)


@with_setup(setup_socket_message)
def test_process_ping():
    session.send = mock.Mock()
    session.process_message({"msg": "ping"})
    session.send.assert_called_with({"msg": "pong"})
    session.process_message({"msg": "ping", "id": "4"})
    session.send.assert_called_with({"msg": "pong", "id": "4"})
