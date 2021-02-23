#!/bin/bash
LED_PATH=/data/ledstrips
sudo PYTHONPATH=".:${LED_PATH}/rpi_ws281x-python/library/build/lib.linux-armv7l-3.7" /usr/bin/python3 ${LED_PATH}/ceiling_lights/lights.py
