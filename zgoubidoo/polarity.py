class MetaPolarity(type):
    """Metaclass to construct polarity types. Supports conversion to float and int."""
    def __float__(cls):
        return int(cls)

    def __int__(cls):
        return cls.P


class Polarity(metaclass=MetaPolarity):
    """Base class to build polarity."""
    P = 0


class PositivePolarity(Polarity):
    """Positive polarity."""
    P = 1


class NegativePolarity(Polarity):
    """Negative polarity."""
    P = -1
