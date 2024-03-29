
```
sudo mkdir /data
sudo chown jcreyf /data
sudo chgrp users /data
chmod 770 /data

mkdir /data/ledstrips
```
in `/etc/sudoers.d/50_jcreyf`:
```
  Defaults env_keep += "PYTHONPATH"
  jcreyf  ALL=(ALL)       ALL
  jcreyf  ALL=(ALL)       NOPASSWD: /sbin/reboot, /sbin/shutdown -h now
  jcreyf  ALL=(ALL)       NOPASSWD: /usr/bin/python3,/usr/bin/python
```

```
sudo apt-get install python3-gpiozero
```

---

## Led driver:
(https://github.com/jgarff/rpi_ws281x)
```
sudo apt-get install git scons
```

- https://github.com/jgarff/rpi_ws281x
- Python binding: https://github.com/rpi-ws281x/rpi-ws281x-python

```
cd /data
git clone https://github.com/jcreyf/ledstrips.git
cd /data/ledstrips/rpi_ws281x
scons
  > scons: Reading SConscript files ...
  > scons: done reading SConscript files.
  > scons: Building targets ...
  > Version version.h
  > CC      main.o
  > CC      mailbox.o
  > CC      ws2811.o
  > CC      pwm.o
  > CC      pcm.o
  > CC      dma.o
  > CC      rpihw.o
  > AR      libws2811.a
  > RANLIB  libws2811.a
  > LINK    test
  > scons: done building targets.
```

This should generate file `libws2811.a`  
Copy that file and header-files to a GCC include path:
```
  sudo cp *.a /usr/local/bin/
  sudo cp *.h /usr/local/include/
```

```
sudo ./test --strip rgbw --width 1 --height 100 --gpio 18 --clear
```

Works fine on RPi4 device  
Failed to create mailbox device on older RPi:  
-> https://github.com/jgarff/rpi_ws281x/blob/31f668cc637cd96e132b611db82cbe9de9838366/mailbox.c#L276  
-> it tries to create file `/tmp/mailbox-<pid>` and fails;  
-> need to run as root;

---

## Python binding:
(https://github.com/rpi-ws281x/rpi-ws281x-python)

```
sudo apt-get install git scons python3-pip python3-setuptools python3-dev
```

```
cd /data/ledstrips/rpi_ws281x-python/library
cp /data/ledstrips/rpi_ws281x/*.h lib/
cp /data/ledstrips/rpi_ws281x/*.c lib/
sudo python3 setup.py build
> running build
> Compiling ws281x library...
> creating build/lib.linux-armv7l-3.7
> creating build/lib.linux-armv7l-3.7/rpi_ws281x
> copying rpi_ws281x/__init__.py -> build/lib.linux-armv7l-3.7/rpi_ws281x
> copying rpi_ws281x/rpi_ws281x.py -> build/lib.linux-armv7l-3.7/rpi_ws281x
> running build_ext
> building '_rpi_ws281x' extension
> creating build/temp.linux-armv7l-3.7
> creating build/temp.linux-armv7l-3.7/lib
>...
> arm-linux-gnueabihf-gcc -pthread -shared -Wl,-O1 -Wl,-Bsymbolic-functions -Wl,-z,relro -Wl,-z,relro -g -fstack-protector-strong -Wformat -Werror=format-security -Wdate-time -D_FORTIFY_SOURCE=2 build/temp.linux-armv7l-3.7/rpi_ws281x_wrap.o build/temp.linux-armv7l-3.7/lib/dma.o build/temp.linux-armv7l-3.7/lib/mailbox.o build/temp.linux-armv7l-3.7/lib/main.o build/temp.linux-armv7l-3.7/lib/pcm.o build/temp.linux-armv7l-3.7/lib/pwm.o build/temp.linux-armv7l-3.7/lib/rpihw.o build/temp.linux-armv7l-3.7/lib/ws2811.o -o build/lib.linux-armv7l-3.7/_rpi_ws281x.cpython-37m-arm-linux-gnueabihf.so
```

This creates a "build" directory:  
```
> la -R build/
>   build/:
>     drwxr-xr-x 3 root   root   4096 Oct 12 22:00 lib.linux-armv7l-3.7
>     drwxr-xr-x 3 root   root   4096 Oct 12 22:00 temp.linux-armv7l-3.7
on the old RPi for old python:
#>     drwxr-xr-x 3 jcreyf jcreyf 4096 Jul 16 21:27 lib.linux-armv7l-2.7
#>     drwxr-xr-x 3 jcreyf jcreyf 4096 Jul 16 21:27 temp.linux-armv7l-2.7
#>   
#>   build/lib.linux-armv7l-2.7:
#>     -rwxr-xr-x 1 root   root   257200 Jul 16 21:27 _rpi_ws281x.so
#>   
#>   build/lib.linux-armv7l-2.7/rpi_ws281x:
#>     -rw-r--r-- 1 jcreyf jcreyf  170 Jul 15 20:56 __init__.py
#>     -rw-r--r-- 1 jcreyf jcreyf 7134 Jul 15 20:56 rpi_ws281x.py
#>   
#>   build/temp.linux-armv7l-2.7:
#>     -rw-r--r-- 1 root   root   217188 Jul 16 21:27 rpi_ws281x_wrap.o
#>   
#>   build/temp.linux-armv7l-2.7/lib:
#>     -rw-r--r-- 1 root   root    4996 Jul 16 21:27 dma.o
#>     -rw-r--r-- 1 root   root   19740 Jul 16 21:27 mailbox.o
#>     -rw-r--r-- 1 root   root   26220 Jul 16 21:27 main.o
#>     -rw-r--r-- 1 root   root    4156 Jul 16 21:27 pcm.o
#>     -rw-r--r-- 1 root   root    4268 Jul 16 21:27 pwm.o
#>     -rw-r--r-- 1 root   root    9424 Jul 16 21:27 rpihw.o
#>     -rw-r--r-- 1 root   root   47484 Jul 16 21:27 ws2811.o
```

```
cd /data/ledstrips/rpi_ws281x-python/examples
```

Make sure to have this in your sudoers.d/50_jcreyf file:
```
Defaults env_keep += "PYTHONPATH"
```

```
sudo PYTHONPATH=".:/data/ledstrips/rpi_ws281x-python/library/build/lib.linux-armv7l-3.7" python3 SK6812_white_test.py
```

### If built for old python:
```
sudo PYTHONPATH=".:/data/ledstrips/rpi_ws281x-python/library/build/lib.linux-armv7l-2.7" python SK6812_white_test.py
```

### To add support for the newer GPIO library: `gpizero`
```
sudo apt-get install python3-gpiozero
```

### You can run the `pinout` command in the linux shell to see the available I/O pinout on your Pi
(https://gpiozero.readthedocs.io/en/stable/cli_tools.html)


---

## Go binding:
(https://github.com/rpi-ws281x/rpi-ws281x-go)

```
sudo apt-get install golang
```
```
cd /data/ledstrips/rpi_ws281x-go/
sudo cp /data/ledstrips/rpi_ws281x/libws2811.a /usr/lib/
```

### Build the Go-wrapper:
```
go get -v -u github.com/rpi-ws281x/rpi-ws281x-go
```

If this error:
```
#   > /usr/bin/ld: cannot find -lws2811
#   > collect2: error: ld returned 1 exit status
#   -> https://stackoverflow.com/questions/28380448/cant-install-rpi-ws281x-error-command-gcc-failed-with-exit-status-1
#   > or: export LD_LIBRARY_PATH=/data/ledstrips/rpi_ws281x/lws2811.a
```

### Build a sample app and run:
```
cd /data/ledstrips/rpi_ws281x-go/examples/color_wipe
go build color_wipe.go
```
This builds a binary, executable file: `color_wipe`
```
sudo ./color_wipe
```

---

## Creating an autostart config:
(https://learn.sparkfun.com/tutorials/how-to-run-a-raspberry-pi-program-on-startup#method-3-systemd)


### Create unit-file (as root) for the app to start at boot:
```
/lib/systemd/system/ledstrip.service

  # Systemd config-file to auto-start the Ledstrip app at boot:
  [Unit]
  Description=Ledstrip control
  After=multi-user.target
  ConditionPathExists=/data/ledstrips/rpi_ws281x-python/examples
  
  [Service]
  ExecStart=/data/ledstrips/rpi_ws281x-python/examples/SK6812_switch_1.sh
  
  [Install]
  WantedBy=multi-user.target
  Alias=ledstrip.service
```

### The script file:
```
  #!/bin/bash
  LED_PATH=/data/ledstrips/rpi_ws281x-python
  sudo PYTHONPATH=".:${LED_PATH}/library/build/lib.linux-armv7l-3.7" /usr/bin/python3 ${LED_PATH}/examples/SK6812_switch_1.py
```

### Then run this to activate and enable (execute each time the config-file is changed):
```
  sudo systemctl daemon-reload
  sudo systemctl enable ledstrip.service
  sudo systemctl start ledstrip.service
```

### If you want to disable it again at some point from auto-start:
```
  sudo systemctl disable ledstrip.service
```

### Check to see if it's running:
```
  sudo systemctl status ledstrip.service
```

### See systemd logs for this new service:
```
  sudo journalctl -u ledstrip.log
```

---

## ceiling_lights

This project uses yaml to configure the led strips and their switches.  
It also uses the Flask web server to expose an API on the network.  
### Install:
```
sudo apt-get install python3-flask python3-yaml
```
Add these 2 lines to your sudoers config:
```
Defaults env_keep += "PYTHONPATH"
Defaults env_keep += "DEBUG"
```
Update the `lights.yaml` file to reflect your setup.  

Put in the new `lights.service` config in `/lib/systemd/system/`  
Go through the same steps lined out above to enable and start the service (first remove the `ledstrip.service` if you had that installed to avoid hardware conflicts).  

---

## Android app
