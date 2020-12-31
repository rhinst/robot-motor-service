from dataclasses import dataclass
from typing import Union

from motor.gpio import GPIO
from motor.enum import MotorDirection, MotorState


@dataclass
class Motor:
    direction: MotorDirection
    speed: float
    direction_pin: int
    speed_pin: int
    pwm: Union[GPIO.PWM, None]
    state: MotorState
