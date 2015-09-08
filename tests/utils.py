import asyncio
import json
import nose.tools
from unittest import mock


def run_until_complete(func, loop=asyncio.get_event_loop()):
    def wrapper(*args, **kwargs):
        return loop.run_until_complete(func(*args, **kwargs))
    return wrapper


def next_tick(loop):
    loop.run_until_complete(asyncio.coroutine(lambda: None)())


def assert_json_equal(first, second):
    if isinstance(first, str):
        first = json.loads(first)
    if isinstance(second, str):
        second = json.loads(second)
    nose.tools.assert_dict_equal(first, second)


def assert_socket_sent(socket_session, message):
    nose.tools.assert_is_instance(
        socket_session.send,
        mock.Mock,
        "send method is not a Mock object, not testable",
        )
    nose.tools.assert_is_instance(
        message, str,
        "message should be a string, got {0}".format(type(message)),
        )
    nose.tools.assert_true(
        socket_session.send.called, "socket didn't send anything"
        )
    args, kwargs = socket_session.send.call_args
    if "msg" in kwargs:
        out_msg = kwargs["out_msg"]
    else:
        out_msg = args[0]
    nose.tools.assert_equal(out_msg, message)


def assert_socket_sent_json(socket_session, message):
    nose.tools.assert_is_instance(
        socket_session.send,
        mock.Mock,
        "send method is not a Mock object, not testable",
        )
    if isinstance(message, str):
        message = json.loads(message)
    args, kwargs = socket_session.send.call_args
    if "msg" in kwargs:
        out_msg = json.loads(kwargs["out_msg"])
    else:
        out_msg = json.loads(args[0])
    nose.tools.assert_dict_equal(out_msg, message)
