# Python script to show network speed on a display

import speedtest
import socket
import time
from signal import signal, SIGINT
from sys import exit
import csv
import os.path
from os import path
from datetime import datetime
import argparse


#Countdown for minutes
def countdown(t):
	while t:
		mins, secs = divmod(t, 60)
		timer = '{:02d}:{:02d}'.format(mins, secs)
		print("Time until next run: " + timer, end="\r")
		time.sleep(1)
		t -= 1
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


#Handles Ctrl+C
def handler(signal_received, frame):
	# Handle any cleanup here
	print()
	print('SIGINT or CTRL-C detected. Please wait until the service has stopped.')
	exit(0)



#Main
if __name__ == '__main__':
	# Tell Python to run the handler() function when SIGINT is recieved
	signal(SIGINT, handler)

	avg = 0
	download = 0
	upload = 0
	run = 0
	printcsv = 1

	# Check for arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("--version", "-v", help="Prints the version", action="store_true")
	parser.add_argument("--nocsv", "-nocsv", help="Disbales the csv file saving", action="store_true")

	args = parser.parse_args()
	if args.version:
		print("Version: 1.0")
		exit(0)

	if args.nocsv:
		print("Option: CSV saving disabled!")
		printcsv = 0


	#Create CSV file if it dows not exist
	if printcsv == 1:
		if path.exists("networkspeeds.csv") == False:
			try:
				with open('networkspeeds.csv', 'w', newline='') as csvfile:
					resultwriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
					resultwriter.writerow(["Download", "Upload", "Average", "DateTime"])
			except:
				print("Failed writing to csv.")


	print('Running. Press CTRL-C to exit.')
	while True:
		print("========== Run " + str(run) + " ==========")
		# First, check connection
		result = is_connected()
		if is_connected() == False:
			print("No network connection was found!")
			exit()

		print("Testing network speed, please wait... ", end="\r")
		#Download speed
		st = speedtest.Speedtest()
		download = st.download()
		download = round(download / 1000 / 1000, 2)

		if run == 0:
			avg = download
		else:
			avg = round(((avg + download) / 2), 2)

		run = run + 1

		# Upload speed
		upload = st.upload()
		upload = round(upload / 1000 / 1000, 2)
		print("                                           ", end="\r")

		print("Download:\t" + str(download) + " Mbit/s")
		print("Upload:\t\t" + str(upload) + " Mbit/s")
		print("Average:\t" + str(avg) + " Mbit/s")
		print(" ")

		# Save to CSV
		# datetime object containing current date and time
		now = datetime.now()
		# dd/mm/YY H:M:S
		dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
		if printcsv == 1:
			try:
				with open('networkspeeds.csv', 'a', newline='') as csvfile:
					resultwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
					resultwriter.writerow([download, upload, avg, dt_string])
			except:
				print("Failed writing to csv.")

		countdown(int(120))
