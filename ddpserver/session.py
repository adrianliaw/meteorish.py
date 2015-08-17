from . import utils
import json
import ejson


class DDPSession(object):

    def __init__(self, server, version, socket):
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
