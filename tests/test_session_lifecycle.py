import asyncio
import meteorish
import datetime
from . import utils as test_utils
from nose.tools import (assert_raises, assert_true, assert_not_in,
                        assert_is_none, assert_false, with_setup)
from .utils import assert_socket_sent_json
from unittest import mock


def setup_socket_message():
    global loop, server, socket, session
    loop = asyncio.get_event_loop()
    server = meteorish.DDPServer(loop=loop)
    socket = mock.Mock()
    session = meteorish.DDPSession(server, "1", socket, loop)


@with_setup(setup_socket_message)
def test_session_send():
    session.send({
        "msg": "connected",
        "session": "TeStSeSsIoNiD",
        })
    assert_socket_sent_json(
        socket, {"msg": "connected", "session": "TeStSeSsIoNiD"}
        )
    session.send({
        "msg": "result",
        "id": "1",
        "result": datetime.datetime(2015, 8, 17, 19, 43, 56, 289379),
        })
    assert_socket_sent_json(socket, {
        "msg": "result",
        "id": "1",
        "result": {"$date": 1439840636000}
        })
    assert_raises(ValueError, session.send, {
        "msg": "result",
        "id": 4,
        "result": "foo",
        })


@mock.patch("meteorish.utils.gen_id")
@with_setup(setup_socket_message)
def test_create_ddp_session(gen_id):
    gen_id.return_value = "TeStSeSsIoNiD"
    session = meteorish.DDPSession(server, "1", socket, loop)
    assert_socket_sent_json(socket, {
        "msg": "connected",
        "session": "TeStSeSsIoNiD",
        })


@mock.patch("meteorish.utils.gen_id")
@with_setup(setup_socket_message)
def test_close_session(gen_id):
    gen_id.return_value = "TeStSeSsIoNiD"
    session = meteorish.DDPSession(server, "1", socket, loop)
    server.ddp_sessions["TeStSeSsIoNiD"] = session
    session.close()
    socket.close.assert_called_with(3000, "Normal closure")
    assert_is_none(socket._ddp_session)
    assert_not_in("TeStSeSsIoNiD", server.ddp_sessions)


@with_setup(setup_socket_message)
def test_session_on_close_callbacks_deferring():
    callbacks = [mock.Mock() for i in range(100)]
    for callback in callbacks:
        session.on_close(callback)
    session.close()
    for callback in callbacks:
        assert_false(callback.called)
    test_utils.next_tick(loop)
    for callback in callbacks:
        assert_true(callback.called)


@with_setup(setup_socket_message)
def test_session_on_close_callback_with_error():
    callback1 = mock.Mock()
    session.on_close(callback1)
    callback2 = mock.Mock(side_effect=ValueError)
    session.on_close(callback2)
    callback3 = mock.Mock()
    session.on_close(callback3)
    session.close()
    test_utils.next_tick(loop)
    assert_true(callback1.called)
    assert_true(callback2.called)
    assert_true(callback3.called)
