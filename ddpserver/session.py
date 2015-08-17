from . import utils
import json


class DDPSession(object):

    def __init__(self, server, version, socket):
        self.server = server
        self.version = version
        self.socket = socket
        self.id = utils.gen_id()

        socket.send(json.dumps({
            "msg": "connected",
            "session": self.id,
            }))
