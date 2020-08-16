#!/bin/bash

LED_PATH=/data/ledstrips/rpi-ws281x-python

# sudo PYTHONPATH=".:${LED_PATH}/library/build/lib.linux-armv7l-2.7" /usr/bin/python3 ${LED_PATH}/examples/SK6812_switch_1.py > /var/log/ledstrip.log 2>&1
sudo /usr/bin/python3 ${LED_PATH}/examples/SK6812_switch_1.py > /var/log/ledstrip.log 2>&1

