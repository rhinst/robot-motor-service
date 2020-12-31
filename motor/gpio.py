import platform


if platform.platform().lower().find("armv71") > -1:
    import RPi.GPIO as GPIO
else:
    import Mock.GPIO as GPIO

__all__ = ["GPIO"]
