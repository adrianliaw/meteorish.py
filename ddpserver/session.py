from .utils import gen_id


class DDPSession(object):

    def __init__(self, version, socket):
        self.version = version
        self.socket = socket
        self.id = gen_id()

    NotImplemented
