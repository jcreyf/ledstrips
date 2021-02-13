#!/bin/bash
LED_PATH=/data/ledstrips/rpi_ws281x-python

sudo PYTHONPATH=".:${LED_PATH}/library/build/lib.linux-armv7l-3.7" /usr/bin/python3 ${LED_PATH}/examples/SK6812_switch_1_double.py
