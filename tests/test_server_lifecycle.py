import asyncio
import meteorish
import sockjs
from unittest import mock
from aiohttp import web
from nose.tools import (assert_is_instance, assert_in,
                        assert_equal, with_setup)
from . import utils as test_utils


def setup_socket_message():
    global loop, server, message, socket, handle_message, handle_connect
    loop = asyncio.get_event_loop()
    server = meteorish.DDPServer(loop=loop)
    message = mock.Mock()
    socket = mock.Mock()
    handle_message = test_utils.run_until_complete(
        server._handle_message,
        loop=loop,
        )
    handle_connect = test_utils.run_until_complete(
        server._handle_connect,
        loop=loop,
        )


def test_server_class():
    loop = asyncio.get_event_loop()
    server = meteorish.DDPServer(loop=loop)
    assert_is_instance(server, web.Application)
    assert_in("__sockjs_managers__", server)
    assert_in("ddp_server", server["__sockjs_managers__"])


@with_setup(setup_socket_message)
def test_handle_connection_opened():
    assert_equal(server.ddp_sessions, {})
    message.tp = sockjs.MSG_OPEN
    message.data = None
    handle_message(message, socket)
    assert_equal(socket._ddp_session, None)


@mock.patch("meteorish.session.DDPSession")
@with_setup(setup_socket_message)
def test_on_connection_callback(ddpsession):
    ddpsession.return_value = mock.Mock()
    callback1 = mock.Mock()
    server.on_connection(callback1)

    @server.on_connection
    def callback2(session):
        raise Exception("Should not stop here")

    callback3 = mock.Mock()
    server.on_connection(callback3)
    handle_connect({
        "msg": "connect",
        "version": "1",
        "support": ["1", "pre2", "pre1"],
        }, socket)
    test_utils.next_tick(loop)
    callback1.assert_called_with(ddpsession.return_value)
    callback3.assert_called_with(ddpsession.return_value)
