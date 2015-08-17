import asyncio
import sockjs
import ejson
import json
import traceback
from aiohttp import web
from .utils import logger
from . import session


class DDPServer(web.Application):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sockjs.add_endpoint(self, self.__handle_message, name="ddp_server")
        self.ddp_sessions = {}

    @asyncio.coroutine
    def __handle_message(self, msg, socket):
        if msg.tp == sockjs.MSG_OPEN:
            socket._ddp_session = None

        elif msg.tp == sockjs.MSG_MESSAGE:

            try:
                try:
                    mbody = ejson.loads(msg.data)
                    if type(mbody) != dict or mbody.get("msg") == None:
                        logger.debug(
                            "Discarding non-object DDP message {0}"
                            .format(msg.data),
                            )
                        socket.send(ejson.dumps({
                            "msg": "error",
                            "reason": "Bad request",
                            "offendingMessage": mbody,
                            }))
                        return
                except ValueError:
                    logger.debug(
                        "Discarding message with invalid JSON {0}"
                        .format(msg.data),
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
                    asyncio.async(self.__handle_connect(mbody, socket))
                    return

                if not socket._ddp_session:
                    socket.send(ejson.dumps({
                        "msg": "error",
                        "reason": "Must connect first",
                        "offendingMessage": mbody,
                        }))
                    return

                socket._ddp_session.process_message(mbody)

            except Exception as err:
                logger.error(
                    "Internal exception while processing message {0}\n{1}"
                    .format(msg.data, traceback.format_exc())
                    )

    @asyncio.coroutine
    def __handle_connect(self, msg, socket):
        if not (type(msg.get("version")) == str and
                type(msg.get("support")) == list and
                all(map(lambda x: type(x) == str, msg["support"])) and
                msg["version"] in msg["support"] and
                msg["version"] == "1"):
            # Only support version 1 currently
            socket.send(json.dumps({"msg": "failed", "version": "1"}))
            socket.close()
            return
        socket._ddp_session = session.DDPSession(msg["version"], socket)
        self.ddp_sessions[socket._ddp_session.id] = socket._ddp_session
