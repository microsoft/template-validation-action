class Severity(object):
    LOW = 1
    MODERATE = 2
    HIGH = 3

    def validate(severity):
        if isinstance(severity, str):
            severity = severity.strip().lower()
            if severity == "low":
                return Severity.LOW
            elif severity == "moderate":
                return Severity.MODERATE
            elif severity == "high":
                return Severity.HIGH
            else:
                return Severity.MODERATE
        if (
            severity == Severity.MODERATE
            or severity == Severity.LOW
            or severity == Severity.HIGH
        ):
            return severity
        else:
            return Severity.MODERATE

    def to_string(severity):
        if severity == Severity.LOW:
            return "Low"
        elif severity == Severity.MODERATE:
            return "Moderate"
        elif severity == Severity.HIGH:
            return "High"
        else:
            return "Moderate"

    def isBlocker(self):
        return self >= Severity.HIGH
