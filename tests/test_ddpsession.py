import asyncio
import ddpserver
import json
from nose.tools import assert_equal, with_setup
from unittest import mock


def setup_socket_message():
    global loop, server, socket
    loop = asyncio.get_event_loop()
    server = ddpserver.DDPServer(loop=loop)
    socket = mock.Mock()


@mock.patch("ddpserver.utils.gen_id")
@with_setup(setup_socket_message)
def test_create_ddp_session(gen_id):
    gen_id.return_value = "TeStSeSsIoNiD"
    session = ddpserver.DDPSession(server, "1", socket)
    (out_msg, ), _ = socket.send.call_args
    out_msg = json.loads(out_msg)
    assert_equal(out_msg, {
        "msg": "connected",
        "session": "TeStSeSsIoNiD",
        })
