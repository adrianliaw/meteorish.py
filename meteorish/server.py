import asyncio
import sockjs
import ejson
import json
import traceback
from aiohttp import web
from . import session


class DDPServer(web.Application):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sockjs.add_endpoint(self, self._handle_message, name="ddp_server")
        self.ddp_sessions = {}
        self._on_connection_callbacks = []

    def __repr__(self):
        return "<DDPServer>"

    @asyncio.coroutine
    def _handle_message(self, msg, socket):
        if msg.tp == sockjs.MSG_OPEN:
            socket._ddp_session = None

        elif msg.tp == sockjs.MSG_MESSAGE:

            try:
                try:
                    mbody = ejson.loads(msg.data)
                    if type(mbody) != dict or mbody.get("msg") == None:
                        self.logger.debug(
                            "Discarding non-object DDP message {msg}"
                            .format(msg=msg.data),
                            )
                        socket.send(ejson.dumps({
                            "msg": "error",
                            "reason": "Bad request",
                            "offendingMessage": mbody,
                            }))
                        return
                except ValueError:
                    self.logger.debug(
                        "Discarding message with invalid JSON {msg}"
                        .format(msg=msg.data),
                        )
                    socket.send(json.dumps({
                        "msg": "error",
                        "reason": "Bad request",
                        }))
                    return

                if mbody["msg"] == "connect":
                    if socket._ddp_session:
                        socket.send(json.dumps({
                            "msg": "error",
                            "reason": "Already connected",
                            "offendingMessage": mbody,
                            }))
                        return
                    asyncio.async(self._handle_connect(mbody, socket),
                                  loop=self.loop)
                    return

                if not socket._ddp_session:
                    socket.send(ejson.dumps({
                        "msg": "error",
                        "reason": "Must connect first",
                        "offendingMessage": mbody,
                        }))
                    return

                socket._ddp_session.process_message(mbody)

            except Exception:
                self.logger.error(
                    "Internal exception while processing message {msg}\n{err}"
                    .format(msg=msg.data, err=traceback.format_exc())
                    )

    @asyncio.coroutine
    def _handle_connect(self, msg, socket):
        if not (type(msg.get("version")) == str and
                type(msg.get("support")) == list and
                all(map(lambda x: type(x) == str, msg["support"])) and
                msg["version"] in msg["support"] and
                msg["version"] == "1"):
            # Only support version 1 currently
            socket.send(json.dumps({"msg": "failed", "version": "1"}))
            socket.close()
            return
        socket._ddp_session = session.DDPSession(self, msg["version"],
                                                 socket, self.loop)
        self.ddp_sessions[socket._ddp_session.id] = socket._ddp_session
        for callback in self._on_connection_callbacks:
            try:
                yield from callback(socket._ddp_session)
            except Exception:
                self.logger.error(
                    "Exception in on_connection callback by {func}:\n{err}"
                    .format(func=callback, err=traceback.format_exc())
                    )

    def on_connection(self, callback):
        if not asyncio.iscoroutinefunction(callback):
            callback = asyncio.coroutine(callback)
        self._on_connection_callbacks.append(callback)
        return callback
