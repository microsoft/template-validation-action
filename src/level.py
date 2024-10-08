class Level(object):
    LOW = 1
    MODERATE = 2
    HIGH = 3

    @staticmethod
    def validate(level):
        if level == Level.MODERATE:
            return Level.MODERATE
        elif level == Level.HIGH:
            return Level.HIGH
        elif level == Level.LOW:
            return Level.LOW
        else:
            return Level.MODERATE

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented

    def isBlocker(self):
        return self >= Level.HIGH
