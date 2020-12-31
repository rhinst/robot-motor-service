from typing import Dict, Union
from enum import Enum
from dataclasses import dataclass

from motor.gpio import GPIO

PWM_FREQUENCY = 500


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


@dataclass
class Motor:
    direction: MotorDirection
    speed: float
    direction_pin: int
    speed_pin: int
    pwm: Union[GPIO.PWM, None]
    state: MotorState


motors: Dict[MotorPosition, Motor]


def initialize(options: Dict):
    global motors
    for pos_name, pos_index in MotorPosition.__members__:
        direction_pin = options["direction_pins"][pos_name.lower()]
        speed_pin = options["speed_pins"][pos_name.lower()]
        motors[pos_index] = Motor(
            direction=MotorDirection.FORWARD,
            speed=0.0,
            direction_pin=direction_pin,
            speed_pin=speed_pin,
            pwm=None,
            state=MotorState.IDLE
        )
    GPIO.setmode(GPIO.BCM)
    GPIO.setup([motor.direction_pin for motor in motors.values()], GPIO.OUT)
    GPIO.setup([motor.speed_pin for motor in motors.values()], GPIO.OUT)
    for motor in motors.values():
        motor.pwm = GPIO.PWM(motor.speed_pin, PWM_FREQUENCY),


def get_measurements():
    #TODO: implement me
    pass


def drive(direction: DriveDirection, speed: float):
    if direction not in list(DriveDirection):
        raise ValueError("Unrecognized drive direction")
    if speed < 0:
        raise ValueError("Minimum speed is 0.0")
    if speed > 1:
        raise ValueError("Maximum speed is 1.0")
    motor_dir = {
        DriveDirection.FORWARD: MotorDirection.FORWARD,
        DriveDirection.BACKWARD: MotorDirection.BACKWARD,
    }
    for pos, motor in motors.items():
        _drive_motor(pos, motor_dir[direction], speed)


def turn(direction: TurnDirection, speed: float):
    if direction not in list(TurnDirection):
        raise ValueError("Unrecognized turn direction")
    if speed < 0:
        raise ValueError("Minimum speed is 0.0")
    if speed > 1:
        raise ValueError("Maximum speed is 1.0")
    methods = {
        TurnDirection.LEFT: turn_left,
        TurnDirection.RIGHT: turn_right
    }
    methods[direction](speed)


def turn_left(speed: float):
    _drive_motor(MotorPosition.FRONT_LEFT, MotorDirection.BACKWARD, speed)
    _drive_motor(MotorPosition.REAR_LEFT, MotorDirection.BACKWARD, speed)
    _drive_motor(MotorPosition.FRONT_RIGHT, MotorDirection.FORWARD, speed)
    _drive_motor(MotorPosition.REAR_RIGHT, MotorDirection.FORWARD, speed)


def turn_right(speed: float):
    _drive_motor(MotorPosition.FRONT_RIGHT, MotorDirection.BACKWARD, speed)
    _drive_motor(MotorPosition.REAR_RIGHT, MotorDirection.BACKWARD, speed)
    _drive_motor(MotorPosition.FRONT_LEFT, MotorDirection.FORWARD, speed)
    _drive_motor(MotorPosition.REAR_LEFT, MotorDirection.FORWARD, speed)


def _drive_motor(position: MotorPosition, direction: MotorDirection, speed: float):
    if speed < 0:
        raise ValueError("Minimum speed is 0.0")
    if speed > 1:
        raise ValueError("Maximum speed is 1.0")
    motor = motors[position]
    GPIO.output(motor.direction, GPIO.LOW if direction == MotorDirection.BACKWARD else GPIO.HIGH)
    motor.direction = direction
    if motor.state == MotorState.IDLE:
        motor.pwm.start(speed * 100)
    else:
        motor.pwm.ChangeDutyCycle(speed * 100)
    motor.speed = speed
    motor.state = MotorState.RUNNING


def stop():
    for motor in motors.values():
        motor.speed = 0.0
        motor.pwm.stop()


def cleanup():
    try:
        stop()
    finally:
        GPIO.cleanup()
