class MeteorError(Exception):

    def __init__(self, *args):
        super().__init__(*args)
        self.reason = args[0] if len(args) >= 1 else None
        self.details = args[1] if len(args) >= 2 else None
