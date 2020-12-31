from enum import Enum


class MotorPosition(Enum):
    FRONT_LEFT = 1
    FRONT_RIGHT = 2
    REAR_LEFT = 3
    REAR_RIGHT = 4


class MotorDirection(Enum):
    FORWARD = 1
    BACKWARD = 2


class MotorState(Enum):
    IDLE = 1
    RUNNING = 2


class DriveDirection(Enum):
    FORWARD = 1
    BACKWARD = 2


class TurnDirection(Enum):
    LEFT = 1
    RIGHT = 2
