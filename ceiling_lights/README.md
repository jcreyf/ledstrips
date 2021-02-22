# Ceiling Lights

## Raspberry PI project to control SK6812 RGBW led strips in the ceiling

We live in a dark A-Frame home in the woods with very little lighting.<br>
I installed LED strips in the ridge of the roof all across the length of the house to add light evenly throughout the house.<br>
There are 2 zones under the roof:<br>
- a 5 meter (16.4ft) bedroom;
- a 7.5 meter (24.6ft) loft;
Each zone has 2 continues LED strips installed in parallel to each other and both are controlled with a Raspberry PI.  The signal lines in each zone are tide together at this point and thus they work as clones at this point, but the goal is to make them individually addressable at some point when I get far enough with the software to split them up.<br>
Also, the strips are being controlled by Raspberry PIs but a couple power outages have painfully highlighted that this cannot be a permanent setup.  A few SD card corruptions and the PI's taking a couple minutes to boot before my light service becomes available on the machines are some decent points to decide to eventually move the control to some more rigid hardware like the ESP32 or similar high performant microcontroller.<br>
<br>
Until then, this Python project deals with 1 or 2 ordinary light switches to turn the LED strips on or off (white light; full brightness).  No special effects just yet.<br>
<br>
<img src="../_documentation/resources/rpi.jpg" alt="The Raspberry PI platform" width="200">
