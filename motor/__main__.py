import os
from itertools import cycle
from time import sleep
from typing import Dict
import json

from redis import Redis
from redis.client import PubSub

from motor.config import load_config
import motor.device

environment: str = os.getenv("ENVIRONMENT", "dev")
config: Dict = load_config(environment)
redis_client: Redis = Redis(
    host=config["redis"]["host"], port=int(config["redis"]["port"])
)
pubsub: PubSub = redis_client.pubsub(ignore_subscribe_messages=True)

commands = {
    "drive": motor.device.drive,
    "stop": motor.device.stop,
}

pubsub.subscribe("subsystem.motor.command")
motor.device.initialize(config["device"]["name"], config["device"]["options"])
while cycle([True]):
    try:
        # see if there is a command for me to execute
        if redis_message := pubsub.get_message():
            message = json.loads(redis_message)
            getattr(motor.device, commands[message["command"]])(message["arguments"])
        # TODO: send quadrature encoder measurements back
        # measurements = motor.device.get_measurements()
        # redis_client.publish("subsystem.motor.measurement", json.dumps(measurements))
        sleep(0.25)
    finally:
        pubsub.close()
        redis_client.close()
        motor.device.cleanup()
