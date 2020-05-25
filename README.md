# speedtest-display
An open source python script to display network speed in command line and write it to an external I2C 16x2 display.

The script will check your internet connection every 120 seconds and print the up and download speed into the console. In addition, it will save the result into a csv file.
This script is still under development!

## Installation
To install clone this repository and run 'sudo ./install.sh'. The device will reboot after completed. 

## Run
To run the script, execute 'python3 run-speedtest-display.py'.

## Options
To print all available options, use 'python3 run-speedtest-display.py --help'.

## Credits
Credits go to https://github.com/the-raspberry-pi-guy/ on teaching how to communicate with i2c
