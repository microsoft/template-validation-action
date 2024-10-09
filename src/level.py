class Level(object):
    LOW = 1
    MODERATE = 2
    HIGH = 3

    def validate(level):
        if isinstance(level, str):
            level = level.strip().lower()
            if level == "low":
                return Level.LOW
            elif level == "moderate":
                return Level.MODERATE
            elif level == "high":
                return Level.HIGH
            else:
                return Level.MODERATE
        if level == Level.MODERATE or level == Level.LOW or level == Level.HIGH:
            return level
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
