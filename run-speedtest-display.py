# Python script to show network speed on a display
# Author: Maximilian Krause
# Date 27.05.2020

# #############
# Define Var
version = 1.3
printcsv = 1
errormsg = "Null"
sleep = 30 # In seconds
avglist = []
# #############


# Define Error Logging
def printerror(ex):
	print('\033[31m' + str(ex) + '\033[0m')

def printwarning(warn):
	print('\033[33m' + str(warn) + '\033[0m')

print("Loading modules...")
try:
	import speedtest
	import socket
	import time
	from signal import signal, SIGINT
	from sys import exit
	import csv
	import os.path
	from os import path
	from datetime import datetime
	import requests
	import argparse
	import lcddriver
	import socket
except ModuleNotFoundError:
	printerror("The app could not be started.")
	printerror("Please run 'sudo ./install.sh' first.")
	exit(2)
except:
	printerror("An unknown error occured while loading modules.")
	exit(2)

# Check for arguments
parser = argparse.ArgumentParser()
parser.add_argument("--version", "-v", help="Prints the version", action="store_true")
parser.add_argument("--csvoff", "-c", help="Disbales the csv file saving", action="store_true")
parser.add_argument("--sleep", "-s", help="Sets the countdown time between each run", type=int)
parser.add_argument("--backlightoff", "-b", help="Turns off the backlight of the lcd", action="store_true")
parser.add_argument("--update", "-u", help="Checks for new update", action="store_true")

args = parser.parse_args()
if args.version:
	print(str(version))
	exit(0)

if args.csvoff:
	printwarning("Option: CSV saving disabled!")
	printcsv = 0

if args.sleep:
	if args.sleep < 1:
		printerror("Value must be greater than 1.")
		exit(2)
	sleep = args.sleep
	printwarning("Option: Sleep set to " + str(args.sleep))


# Load driver for LCD display
try:
	display = lcddriver.lcd()

	#Check backlight option
	if args.backlightoff:
		printwarning("Option: Backlight turned off!")
		display.backlight(0)
	else:
		display.backlight(1)

	display.lcd_display_string("Load speedtest", 1)
	display.lcd_display_string("V " + str(version), 2)
	time.sleep(1.5)
except IOError:
	printerror("The connection to the display failed.")
	printerror("Please check your connection for all pins.")
	printerror("From bash you can run i2cdetect -y 1")

	printerror("Would you like to proceed anyway (More errors might occur)? [y/n]")
	yes = {'yes', 'y'}
	no = {'no', 'n'}
	choice = input().lower()
	if choice in yes:
		print("Will continue...")
	elif choice in no:
		print("Shutting down... Bye!")
		exit(1)
	else:
		print("Please choose yes or no")
except Exception as e:
	printerror("An unknown error occured while connecting to the lcd.")
	printerror(e)

# Define custom LCD characters
# Char generator can be found at https://omerk.github.io/lcdchargen/
fontdata1 = [
	#char(0) - Up Arrow
	[0b00100, 0b01110, 0b10101, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100],

	#char(1) - Down Arrow
	[0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b10101, 0b01110, 0b00100],

	#char(2) - Avg Symbol
	[0b00000, 0b00001, 0b01110, 0b01010, 0b01010, 0b01110, 0b10000, 0b0000],

	#char(3) - Progressbar-Symbol
	[0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111]
]

display.lcd_load_custom_chars(fontdata1)

#Countdown for minutes
def countdown(t):
	total = t
	progvalue = 0
	display.lcd_display_string("      ..........", 2)
	while t:
		mins, secs = divmod(t, 60)
		timer = '{:02d}:{:02d}'.format(mins, secs)
		print("Time until next run: " + timer, end="\r")
		time.sleep(1)
		t -= 1
		progvalue += 1
		progress = progvalue / total * 10
		progress = round(progress, 0)
		pbar = ""
		while progress > 0:
			pbar = pbar + chr(3)
			progress = progress - 1
		display.lcd_display_string(timer + " " + str(pbar), 2)
	print(" ", end="\r")


#Check or internet connection
def is_connected():
    try:
        # connect to the host -- tells us if the host is actually
        # reachable
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        pass
    return False


# Read IP Adress
def get_ip():
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("8.8.8.8", 80))
		ip_address = s.getsockname()[0]
		s.close()
		return str(ip_address)
	except:
		return str("0.0.0.0")
		printerror("Unable to get IP")


#Handles Ctrl+C
def handler(signal_received, frame):
	# Handle any cleanup here
	print()
	printwarning('SIGINT or CTRL-C detected. Please wait until the service has stopped.')
	if errormsg == "Null":
		display.lcd_clear()
		display.lcd_display_string("Manual cancel.", 1)
		display.lcd_display_string("Exiting app.", 2)
	else:
		display.lcd_clear()
		display.lcd_display_string(str(errormsg), 1)
		display.lcd_display_string("Exiting app.", 2)
	exit(0)

# Save to CSV
def SaveToCSV(down, up, average):
	# datetime object containing current date and time
	now = datetime.now()
	# dd/mm/YY H:M:S
	dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
	if printcsv == 1:
		try:
			with open('networkspeeds.csv', 'a', newline='') as csvfile:
				resultwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
				resultwriter.writerow([down, up, average, dt_string])
		except Exception as e:
			printerror("Failed writing to csv.")
			printerror(e)

# Checks for updates
def checkUpdate():
	updateUrl = "https://raw.githubusercontent.com/maxi07/speedtest-display/master/doc/version"
	try:
		f = requests.get(updateUrl)
		latestVersion = float(f.text)
		if latestVersion > version:
			printwarning("There is an update available.")
			printwarning("Head over to https://github.com/maxi07/speedtest-display to get the hottest features.")
		else:
			print("Application is running latest version.")
	except Exception as e:
		printerror("An error occured while searching for updates.")
		printerror(e)


#Main
if __name__ == '__main__':
	# Tell Python to run the handler() function when SIGINT is recieved
	signal(SIGINT, handler)

	avg = 0
	download = 0
	upload = 0
	run = 0

	# Check if --update tag was used for only retrieving version
	if args.update:
		checkUpdate()
		display.lcd_clear()
		exit(0)


	#Create CSV file if it dows not exist
	if printcsv == 1:
		if path.exists("networkspeeds.csv") == False:
			try:
				with open('networkspeeds.csv', 'w', newline='') as csvfile:
					resultwriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
					resultwriter.writerow(["Download", "Upload", "Average", "DateTime"])
			except Exception as e:
				printerror("Failed writing to csv.")
				printerror(e)


	#Print IP to display
	display.lcd_display_string(get_ip(), 2)
	time.sleep(1.5)
	checkUpdate()
	print('Running. Press CTRL-C to exit.')
	while True:
		print("========== Run " + str(run) + " ==========")
		run = run + 1
		# First, check connection
		result = is_connected()
		if is_connected() == False:
			printerror("No network connection was found!")
			display.lcd_clear()
			display.lcd_display_string("No Network!", 1)
			SaveToCSV(0,0,0)
			countdown(int(sleep))
			continue

		print("Testing network speed, please wait... ", end="\r")

		#Download speed
		display.lcd_display_string("Download Test...", 2)
		st = speedtest.Speedtest()
		download = st.download()
		download = round(download / 1000 / 1000, 2)


		# Upload speed
		display.lcd_display_string("Upload Test...  ", 2)
		upload = st.upload()
		upload = round(upload / 1000 / 1000, 2)
		print("                                           ", end="\r")


		#Calculate Average
		if len(avglist) >= 10:
			del avglist[0]
		avglist.append(download)
		avg_temp = 0
		for x in avglist:
			avg_temp += x
		avg = round(avg_temp / len(avglist), 2)

		print("Download:\t" + str(download) + " Mbit/s")
		print("Upload:\t\t" + str(upload) + " Mbit/s")
		print("Average:\t" + str(avg) + " Mbit/s")
		print(" ")

		# Print to display
		upload_s = round(upload, 0)
		download_s = round(download, 0)
		avg_s = round(avg, 0)

		# Do formatting for display
		pad2 = " " * 2
		pad3 = " " * 3

		if upload_s > 99:
			padding1 = pad2
		else:
			padding1 = pad3

		if download_s > 99:
			padding2 = pad2
		else:
			padding2 = pad3


		display.lcd_clear()
		display.lcd_display_string(chr(1) + str(int(download_s)) + padding1 + chr(0) + str(int(upload_s)) + padding2 + chr(2) + str(int(avg_s)), 1)

		SaveToCSV(download, upload, avg)
		done_download = False
		done_upload = False

		countdown(int(sleep))
