from typing import Dict, Union

from motor.enum import (
    MotorPosition,
    MotorDirection,
    MotorState,
    DriveDirection,
    TurnDirection
)
from motor.motor import Motor
from motor.gpio import GPIO
from motor.logging import logger

PWM_FREQUENCY = 500

motors: Dict[MotorPosition, Motor]


def initialize(options: Dict):
    global motors
    motors = {}
    for pos_name, pos_index in MotorPosition.__members__.items():
        direction_pin = options["motors"][pos_name.lower()]["direction_pin"]
        speed_pin = options["motors"][pos_name.lower()]["speed_pin"]
        reverse_polarity = options["motors"][pos_name.lower()]["reverse"]
        motors[pos_index] = Motor(
            direction=MotorDirection.FORWARD,
            speed=0.0,
            direction_pin=direction_pin,
            speed_pin=speed_pin,
            reverse_polarity=reverse_polarity,
            pwm=None,
            state=MotorState.IDLE
        )
    GPIO.setmode(GPIO.BCM)
    for position, motor in motors.items():
        logger.debug(f"Using pin {motor.direction_pin} for direction on motor {position}")
        GPIO.setup(motor.direction_pin, GPIO.OUT)
        logger.debug(f"Using pin {motor.speed_pin} for speed on motor {position}")
        GPIO.setup(motor.speed_pin, GPIO.OUT)
        motor.pwm = GPIO.PWM(motor.speed_pin, PWM_FREQUENCY)
        motor.pwm.start(0.0)


def get_measurements():
    #TODO: implement me
    pass


def drive(direction: DriveDirection, speed: float):
    logger.debug("Driving!")
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
    logger.debug(f"Driving motor at position {position} {direction} at {speed*100}% speed")
    motor = motors[position]
    if motor.reverse_polarity:
        direction = MotorDirection.BACKWARD if direction == MotorDirection.FORWARD else MotorDirection.FORWARD
    GPIO.output(motor.direction_pin, GPIO.LOW if direction == MotorDirection.BACKWARD else GPIO.HIGH)
    motor.direction = direction
    motor.pwm.ChangeDutyCycle(speed * 100)
    motor.speed = speed
    motor.state = MotorState.RUNNING


def stop():
    logger.debug("Stopping!")
    for motor in motors.values():
        motor.speed = 0.0
        motor.pwm.stop()


def cleanup():
    try:
        stop()
    finally:
        GPIO.cleanup()
