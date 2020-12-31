from importlib import import_module
from typing import Dict

modules = {"4wd": "4wd"}

active_device = None
_active_module = None

get_measurements: callable
cleanup: callable
drive: callable
turn: callable
turn_left: callable
turn_right: callable
stop: callable


def initialize(device_name: str, device_options: Dict):
    global _active_module
    methods = ["get_meaurements", "cleanup", "drive", "turn", "turn_left", "turn_right", "stop"]
    module_name = modules[device_name]
    _active_module = import_module(f"motor.device.{module_name}")
    getattr(_active_module, "initialize")(device_options)
    for method_name in methods:
        globals()[method_name] = getattr(_active_module, method_name)
