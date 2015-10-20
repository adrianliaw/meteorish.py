import meteorish
import asyncio
import sockjs
from . import utils as test_utils
from unittest import mock
from .utils import assert_socket_sent_json
from nose.tools import (assert_true, assert_equal, with_setup,
                        nottest)


def setup_socket_message():
    global loop, server, message, socket, handle_message, handle_connect
    loop = asyncio.get_event_loop()
    server = meteorish.DDPServer(loop=loop)
    message = mock.Mock()
    message.tp = sockjs.MSG_MESSAGE
    socket = mock.Mock()
    handle_message = test_utils.run_until_complete(
        server._handle_message,
        loop=loop,
        )
    handle_connect = test_utils.run_until_complete(
        server._handle_connect,
        loop=loop,
        )


@with_setup(setup_socket_message)
def test_handle_invalid_json():
    message.data = "{invalid: json,}"
    handle_message(message, socket)
    assert_socket_sent_json(socket, {
        "msg": "error",
        "reason": "Bad request",
        })


@with_setup(setup_socket_message)
def test_handle_null():
    message.data = "null"
    handle_message(message, socket)
    assert_socket_sent_json(socket, {
        "msg": "error",
        "reason": "Bad request",
        "offendingMessage": None,
        })


@with_setup(setup_socket_message)
def test_handle_array():
    message.data = '[{"msg": "connect", "version": "1"}]'
    handle_message(message, socket)
    assert_socket_sent_json(socket, {
        "msg": "error",
        "reason": "Bad request",
        "offendingMessage": [{
            "msg": "connect",
            "version": "1",
            }],
        })


@with_setup(setup_socket_message)
def test_handle_invalid_ddp():
    message.data = '{"lorem": "ipsum"}'
    handle_message(message, socket)
    assert_socket_sent_json(socket, {
        "msg": "error",
        "reason": "Bad request",
        "offendingMessage": {"lorem": "ipsum"}
        })


@with_setup(setup_socket_message)
def test_handle_connect_message():
    message.data = '{"msg": "connect"}'
    socket._ddp_session = None
    server._handle_connect = handle_connect = mock.Mock()
    handle_message(message, socket)
    test_utils.next_tick(loop)
    handle_connect.assert_called_with({"msg": "connect"}, socket)


@with_setup(setup_socket_message)
def test_handle_no_session():
    message.data = '{"msg": "ping"}'
    socket._ddp_session = None
    handle_message(message, socket)
    assert_socket_sent_json(socket, {
        "msg": "error",
        "reason": "Must connect first",
        "offendingMessage": {"msg": "ping"},
        })


@with_setup(setup_socket_message)
def test_handle_valid_ddp():
    message.data = '{"msg": "ping"}'
    socket._ddp_session = mock.Mock()
    handle_message(message, socket)
    socket._ddp_session.process_message.assert_called_with({
        "msg": "ping"
        })


@with_setup(setup_socket_message)
def test_handle_connect_should_fail():
    messages = [
        {"msg": "connect"},
        {"msg": "connect", "version": 1},
        {"msg": "connect", "version": "1"},
        {"msg": "connect", "version": "1", "support": 1},
        {"msg": "connect", "version": "1", "support": [1]},
        {"msg": "connect", "version": "1", "support": ["pre2", "pre1"]},
        {"msg": "connect", "version": "pre1", "support": ["pre1"]},
        ]
    for message in messages:
        yield handle_connect_should_fail_tester, message, mock.Mock()


@nottest
def handle_connect_should_fail_tester(msg, ses):
    handle_connect(msg, ses)
    assert_socket_sent_json(ses, {"msg": "failed", "version": "1"})
    assert_true(ses.close.called)


@mock.patch("meteorish.session.DDPSession")
@with_setup(setup_socket_message)
def test_handle_connect_create_ddp_session(ddpsession):
    ddpsession.return_value = mock.Mock(id="TeStSeSsIoNiD")
    message = {
        "msg": "connect",
        "version": "1",
        "support": ["1", "pre2", "pre1"],
        }
    handle_connect(message, socket)
    ddpsession.assert_called_with(server, "1", socket, loop)
    assert_equal(socket._ddp_session, ddpsession())
    assert_equal(server.ddp_sessions, {"TeStSeSsIoNiD": ddpsession()})
