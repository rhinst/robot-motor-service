import os
from itertools import cycle
from time import sleep
from typing import Dict
import json

from redis import Redis
from redis.client import PubSub

from motor.config import load_config
import motor.device
from motor.logging import logger, initialize_logger
from motor.enum import (
    MotorPosition,
    MotorDirection,
    MotorState,
    DriveDirection,
    TurnDirection
)


def handle_drive(**kwargs):
    required = ['direction', 'speed']
    for arg in required:
        if arg not in kwargs:
            raise ValueError(f"Missing argument: {arg}")
    direction = kwargs['direction'].upper()
    speed = kwargs['speed']
    if direction not in DriveDirection.__members__.keys():
        raise ValueError(f"Unknown direction: {direction}")
    direction = DriveDirection.__members__[direction]
    if speed < 0.0:
        raise ValueError("Minimum speed is 0.0")
    if speed > 1.0:
        raise ValueError("Maximum speed is 1.0")
    motor.device.drive(direction, speed)


def handle_turn(**kwargs):
    required = ['direction', 'speed']
    for arg in required:
        if arg not in kwargs:
            raise ValueError(f"Missing argument: {arg}")
    if kwargs['direction'] not in TurnDirection.__members__.keys():
        raise ValueError(f"Unknown direction: {kwargs['direction']}")
    if kwargs['speed'] < 0.0:
        raise ValueError("Minimum speed is 0.0")
    if kwargs['speed'] > 1.0:
        raise ValueError("Maximum speed is 1.0")
    direction = TurnDirection.__members__[kwargs['direction'].upper()]
    speed = kwargs['speed']
    motor.device.turn(direction, speed)


def handle_turn_left(**kwargs):
    pass


def handle_turn_right(**kwargs):
    pass


def handle_stop(**_):
    motor.device.stop()


def main():
    environment: str = os.getenv("ENVIRONMENT", "dev")
    config: Dict = load_config(environment)
    initialize_logger(level=config['logging']['level'], filename=config['logging']['filename'])
    redis_host = config['redis']['host']
    redis_port = config['redis']['port']
    logger.debug(f"Connecting to redis at {redis_host}:{redis_port}")
    redis_client: Redis = Redis(
        host=redis_host, port=redis_port, db=0
    )
    pubsub: PubSub = redis_client.pubsub(ignore_subscribe_messages=True)

    pubsub.subscribe("subsystem.motor.command")
    motor.device.initialize(config["device"]["name"], config["device"]["options"])
    handlers = {
        "drive": handle_drive,
        "stop": handle_stop,
        "turn": handle_turn,
        "turn_left": handle_turn_left,
        "turn_right": handle_turn_right,
    }
    try:
        while cycle([True]):
            # see if there is a command for me to execute
            redis_message = pubsub.get_message()
            if redis_message is not None:
                logger.debug(f"Received a '{redis_message['command']}' message")
                message = json.loads(redis_message['data'])
                handlers[message["command"]](**message)
            # TODO: send quadrature encoder measurements back
            # measurements = motor.device.get_measurements()
            # redis_client.publish("subsystem.motor.measurement", json.dumps(measurements))
            sleep(0.25)
    except Exception:
        logger.exception("Something bad happened")
    finally:
        pubsub.close()
        redis_client.close()
        motor.device.cleanup()


if __name__ == '__main__':
    main()
