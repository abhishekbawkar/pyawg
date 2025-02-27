from enum import Enum


class AmplitudeUnit(Enum):
    VPP = "VPP"
    VRMS = "VRMS"
    DBM = "DBM"


class FrequencyUnit(Enum):
    HZ = "HZ"
    KHZ = "KHZ"
    MHZ = "MHZ"


class Polarity(Enum):
    NORMAL = "NORM"
    INVERTED = "INVT"


class BurstModeRigol(Enum):
    TRIGGERED = "TRIG"
    INFINITY = "INF"
    GATED = "GAT"


class BurstModeSiglent(Enum):
    NCYC = "NCYC"
    GATE = "GATE"


class BurstTriggerSource(Enum):
    INTERNAL = "INT"
    EXTERNAL = "EXT"
    MANUAL = "MAN"


class WaveformType(Enum):
    SINE = "SIN"
    SQUARE = "SQU"
    RAMP = "RAMP"
    PULSE = "PULS"
    NOISE = "NOIS"
    DC = "DC"
    ARB = "ARB"  # Arbitrary
