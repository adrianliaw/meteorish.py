from . import utils
import asyncio
import json
import ejson


class DDPSession(object):

    def __init__(self, server, version, socket, loop=asyncio.get_event_loop()):
        self.server = server
        self.version = version
        self.socket = socket
        self.id = utils.gen_id()

        self.send({
            "msg": "connected",
            "session": self.id,
            })

    def send(self, message):
        if type(message.get("id", "")) != str:
            raise ValueError("Message id is not a string")
        self.socket.send(ejson.dumps(message))

    def process_message(self, message):
        if message["msg"] == "ping":
            out_msg = {"msg": "pong"}
            if "id" in message:
                out_msg["id"] = message["id"]
            self.send(out_msg)
