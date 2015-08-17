from . import utils


class DDPSession(object):

    def __init__(self, version, socket):
        self.version = version
        self.socket = socket
        self.id = utils.gen_id()

    NotImplemented
