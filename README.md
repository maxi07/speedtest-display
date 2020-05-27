# speedtest-display
An open source python script to display network speed in command line and write it to an external I2C 16x2 display.

The script will check your internet connection every 120 seconds and print the up and download speed into the console. In addition, it will save the result into a csv file.

## Installation
To install clone this repository and run
```bash
sudo ./install.sh
```
The device will reboot after completed. 

## Wiring / LCD Display
The script was developed for a 16x2 I2C display, which can be found for cheap on Amazon.com.
For wiring setup, please check the [wiki.](https://github.com/maxi07/speedtest-display/wiki/Connect-LCD-display)

## Run
To run the script, execute
```bash
python3 run-speedtest-display.py
```

## Options
To print all available options, use 
```bash
python3 run-speedtest-display.py --help
```

## Credits
Credits go to https://github.com/the-raspberry-pi-guy/ on teaching how to communicate with i2c
