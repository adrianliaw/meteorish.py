import asyncio
import ddpserver
import json
import datetime
from nose.tools import assert_equal, assert_raises, with_setup
from unittest import mock


def setup_socket_message():
    global loop, server, socket
    loop = asyncio.get_event_loop()
    server = ddpserver.DDPServer(loop=loop)
    socket = mock.Mock()


@with_setup(setup_socket_message)
def test_session_send():
    session = ddpserver.DDPSession(server, "1", socket)
    session.send({
        "msg": "connected",
        "session": "TeStSeSsIoNiD",
        })
    (out_msg, ), _ = socket.send.call_args
    out_msg = json.loads(out_msg)
    assert_equal(out_msg, {"msg": "connected", "session": "TeStSeSsIoNiD"})
    session.send({
        "msg": "result",
        "id": "1",
        "result": datetime.datetime(2015, 8, 17, 19, 43, 56, 289379),
        })
    (out_msg, ), _ = socket.send.call_args
    out_msg = json.loads(out_msg)
    assert_equal(out_msg, {
        "msg": "result",
        "id": "1",
        "result": {"$date": 1439840636000}
        })
    assert_raises(ValueError, session.send, {
        "msg": "result",
        "id": 4,
        "result": "foo",
        })


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
