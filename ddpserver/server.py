import asyncio
import sockjs
import ejson
import json
import traceback
from .utils import logger
from aiohttp import web


class DDPServer(web.Application):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sockjs.add_endpoint(self, self.__handle_message, name="ddp_server")
        self.ddp_sessions = {}

    @asyncio.coroutine
    def __handle_message(self, msg, session):
        if msg.tp == sockjs.MSG_OPEN:
            session._ddp_session = None

        elif msg.tp == sockjs.MSG_MESSAGE:

            try:
                try:
                    mbody = ejson.loads(msg.data)
                    if type(mbody) != dict or mbody.get("msg") == None:
                        logger.debug(
                            "Discarding non-object DDP message {0}"
                            .format(msg.data),
                            )
                        session.send(ejson.dumps({
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
                    session.send(json.dumps({
                        "msg": "error",
                        "reason": "Bad request",
                        }))
                    return

                if mbody["msg"] == "connect":
                    if session._ddp_session:
                        session.send(json.dumps({
                            "msg": "error",
                            "reason": "Already connected",
                            "offendingMessage": mbody,
                            }))
                        return
                    asyncio.async(self.__handle_connect(mbody, session))
                    return

                if not session._ddp_session:
                    session.send(ejson.dumps({
                        "msg": "error",
                        "reason": "Must connect first",
                        "offendingMessage": mbody,
                        }))
                    return

                session._ddp_session.process_message(mbody)

            except Exception as err:
                logger.error(
                    "Internal exception while processing message {0}\n{1}"
                    .format(msg.data, traceback.format_exc())
                    )

    @asyncio.coroutine
    def __handle_connect(self, msg, session):
        return NotImplemented
