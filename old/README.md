# ledstrips

Raspberry PI project to control SK6812 RGBW led strips.

--------
https://tutorials-raspberrypi.com/connect-control-raspberry-pi-ws2812-rgb-led-strips/
--------

/> sudo usermod -a -G users jcreyf

drwxrwsr-x  4 root staff 4096 Feb 13 07:57 python2.7
drwxrwsr-x  3 root staff 4096 Feb 13 07:56 python3.7

/> sudo chgrp -R users /usr/local/lib/python*
/> sudo chmod -R g+w /usr/lib/python*
drwxrwsr-x  4 root users 4096 Feb 13 07:57 python2.7
drwxrwsr-x  3 root users 4096 Feb 13 07:56 python3.7

/> apt-get install pip
/> apt install python3-pip
/> pip3 install rpi-ws281x

./ledstrips/rpi_ws281x/python> python3 ./setup.py build
  /usr/bin/ld: cannot find -lws2811
