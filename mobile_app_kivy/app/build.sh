#!/bin/bash

# Copy the .py file from project folder:
cp ../ledstrips.py main.py

# Add comment to app:
sed -i '1 i\#' main.py
sed -i '1 i\# THIS FILE IS REQUIRED FOR BUILDOZER TO GENERATE THE ANDROID APP' main.py
sed -i '1 i\# THIS FILE IS AN EXACT COPY OF ledstrips.py!!!!' main.py
sed -i '1 i\#' main.py

# Todo: add a flag to "clean" (delete .buildozer and venv and bin directories before starting

buildozer android debug deploy run
if [ $? -eq 0 ] ; then
  echo "Build successful"
  ls -la ./bin/
  scp ./bin/ledstrips*.apk 192.168.5.7:/tmp/
fi
