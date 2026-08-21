class InvalidMoveException(BaseException):
    def __init__(self, txt):
        super().__init__(txt)

class NotImplementedError(BaseException):
    def __init__(self):
        super().__init__("Haven't implemented yet")
