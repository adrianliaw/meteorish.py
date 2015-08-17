import ddpserver
import asyncio
import sockjs
import json
from aiohttp import web
from unittest import mock
from nose.tools import (assert_is_instance, assert_in,
                        assert_equal, assert_raises,
                        assert_is, with_setup, nottest)


def setup_socket_message():
    global loop, server, message, socket, handle_message, handle_connect
    loop = asyncio.get_event_loop()
    server = ddpserver.DDPServer(loop=loop)
    message = mock.Mock()
    socket = mock.Mock()
    handle_message = run_until_complete(
        server._DDPServer__handle_message,
        loop=loop,
        )
    handle_connect = run_until_complete(
        server._DDPServer__handle_connect,
        loop=loop,
        )


def run_until_complete(func, loop=asyncio.get_event_loop()):
    def wrapper(*args, **kwargs):
        return loop.run_until_complete(func(*args, **kwargs))
    return wrapper


def test_server_class():
    loop = asyncio.get_event_loop()
    server = ddpserver.DDPServer(loop=loop)
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


@with_setup(setup_socket_message)
def test_handle_invalid_json():
    message.tp = sockjs.MSG_MESSAGE
    message.data = "{invalid: json,}"
    handle_message(message, socket)
    (out_msg, ), _ = socket.send.call_args
    out_msg = json.loads(out_msg)
    assert_equal(out_msg, {
        "msg": "error",
        "reason": "Bad request",
        })


@with_setup(setup_socket_message)
def test_handle_null():
    message.tp = sockjs.MSG_MESSAGE
    message.data = "null"
    handle_message(message, socket)
    (out_msg, ), _ = socket.send.call_args
    out_msg = json.loads(out_msg)
    assert_equal(out_msg, {
        "msg": "error",
        "reason": "Bad request",
        "offendingMessage": None,
        })


@with_setup(setup_socket_message)
def test_handle_array():
    message.tp = sockjs.MSG_MESSAGE
    message.data = '[{"msg": "connect", "version": "1"}]'
    handle_message(message, socket)
    (out_msg, ), _ = socket.send.call_args
    out_msg = json.loads(out_msg)
    assert_equal(out_msg, {
        "msg": "error",
        "reason": "Bad request",
        "offendingMessage": [{
            "msg": "connect",
            "version": "1",
            }],
        })


@with_setup(setup_socket_message)
def test_handle_invalid_ddp():
    message.tp = sockjs.MSG_MESSAGE
    message.data = '{"lorem": "ipsum"}'
    handle_message(message, socket)
    (out_msg, ), _ = socket.send.call_args
    out_msg = json.loads(out_msg)
    assert_equal(out_msg, {
        "msg": "error",
        "reason": "Bad request",
        "offendingMessage": {"lorem": "ipsum"}
        })


@mock.patch("asyncio.async")
@with_setup(setup_socket_message)
def test_handle_connect_message(async_call):
    message.tp = sockjs.MSG_MESSAGE
    message.data = '{"msg": "connect"}'
    socket._ddp_session = None
    server._DDPServer__handle_connect = handle_connect = mock.Mock()
    handle_message(message, socket)
    handle_connect.assert_called_with({"msg": "connect"}, socket)


@with_setup(setup_socket_message)
def test_handle_no_session():
    message.tp = sockjs.MSG_MESSAGE
    message.data = '{"msg": "ping"}'
    socket._ddp_session = None
    handle_message(message, socket)
    (out_msg, ), _ = socket.send.call_args
    out_msg = json.loads(out_msg)
    assert_equal(out_msg, {
        "msg": "error",
        "reason": "Must connect first",
        "offendingMessage": {"msg": "ping"},
        })


@with_setup(setup_socket_message)
def test_handle_valid_ddp():
    message.tp = sockjs.MSG_MESSAGE
    message.data = '{"msg": "ping"}'
    socket._ddp_session = mock.Mock()
    handle_message(message, socket)
    socket._ddp_session.process_message.assert_called_with({
        "msg": "ping"
        })


@with_setup(setup_socket_message)
def test_handle_connect_should_fail():
    tester = handle_connect_should_fail_tester
    message = {"msg": "connect"}
    yield tester, message, mock.Mock()
    message = {"msg": "connect", "version": 1}
    yield tester, message, mock.Mock()
    message = {"msg": "connect", "version": "1"}
    yield tester, message, mock.Mock()
    message = {"msg": "connect", "version": "1", "support": 1}
    yield tester, message, mock.Mock()
    message = {"msg": "connect", "version": "1", "support": [1]}
    yield tester, message, mock.Mock()
    message = {"msg": "connect", "version": "1", "support": ["pre2", "pre1"]}
    yield tester, message, mock.Mock()
    message = {"msg": "connect", "version": "pre1", "support": ["pre1"]}
    yield tester, message, mock.Mock()


@nottest
def handle_connect_should_fail_tester(msg, ses):
    ses.send = mock.Mock()
    ses.close = mock.Mock()
    handle_connect(msg, ses)
    (out_msg, ), _ = ses.send.call_args
    out_msg = json.loads(out_msg)
    assert_equal(out_msg, {"msg": "failed", "version": "1"})
    ses.close.assert_called_with()


@mock.patch("ddpserver.session.DDPSession")
@with_setup(setup_socket_message)
def test_handle_connect_create_ddp_session(ddpsession):
    ddpsession.return_value = mock.Mock(id="TeStSeSsIoNiD")
    message = {
        "msg": "connect",
        "version": "1",
        "support": ["1", "pre2", "pre1"],
        }
    handle_connect(message, socket)
    assert_equal(socket._ddp_session, ddpsession())
    assert_equal(server.ddp_sessions, {"TeStSeSsIoNiD": ddpsession()})


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
