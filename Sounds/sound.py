# ------------------------------------------------------------------------------------------
# Introduction
# ------------------------------------------------------------------------------------------
# Welcome to my sound sensor project! This program will do 3 basic things:
# 1) configure your RPi to use a sound sensor (based on the DAOKI sound sensor from Amazon)
# 2) Monitor the sensor for a change in state
# 3) Output both a visual alert (Red LED) and update a webpage with detection information
#
# You can grab this project from github with the following command:
# git clone https://github.com/ChrisHarrold/PiWorkshop.git
# this project is in the Sounds folder
# Happy Pi-ing

# ------------------------------------------------------------------------------------------
# Libs, Variables, and Program Header
# ------------------------------------------------------------------------------------------

# Import libraries used in this program
# the RPI.GPIO library is used by Python to interface with the RPi Hardware
import RPi.GPIO as GPIO
# the OS module allows us to use the file system
import os
# time is an incedibly useful python library that gives you access to commands for time
import time
# decimal allows you to work with decimal notation for numbers - very useful for high-precision
from decimal import Decimal
# the math library allows you to perform standard math functions
import math

# Startup message - will print to the console only
print("Preparing to monitor sound levels")
print("You can gracefully exit the program by pressing ctrl-C")

# We will be outputting to a website for a real-time view of noise detection events.
# for debugging you can leave this section commented out:
print("Readying Web Output File")
# Web output file definition - this file is called by the sound.html webpage and used to
# display the status of the sound detection
web_file = "/var/www/html/table.shtml"

# Opens and preps the HTML file for the first time. Will remove anything it
# finds in the file and prep it with this default entry - the replaces old
# data so definitely collect that info somewhere else if you want to keep it!
with open(web_file + '.new', 'w') as f_output:
	f_output.write("")
	os.rename(web_file + '.new', web_file)


# various counters used for determining the thresholds for sensitivity and detection
# as well as the time of the loop and frequency for debugging
Loud_Count = 0 # Count of trigger events from the sensor total since the program started running
louds_per = 0 # Count of trigger events from the sensor in this time interval
per_detected = 0 # The percent of loops where sound is detected versus not detected (math performed on this value later)
time_loop = 5 # The numeric value is how many seconds you want the timestamps to be spaced by
stime = time.time() # The time right now (in UNIX Datetime format - that is to say a really long string of seconds)
etime = stime + time_loop #etime is the end time of our loop - the difference between right now and the time_loop value
ptime = time.ctime() #the "pretty" version of the current time - suitable for charts and graphs!

# loop count and max_loop are used for math on the number of detection loops within the time threshold
Loops_Tot = 0
loop_count = 0
max_loop = 10000000

# This value is the number of times loud sound was detected
# versus the number of times the loop ran. this number will likely be
# very small - something on the order of .00000001
# You determine this number by running the program a few times and seeing the
# ratio of detections to loops (It is printed out later in the program)
a_threshold = .00000001


# ------------------------------------------------------------------------------------------
# Setup Area
# ------------------------------------------------------------------------------------------

# Set our GPIO pin assignments to the right pins
sensor_in = 18
red_led = 21
green_led = 20
# Setup GPIO commands and pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(red_led, GPIO.OUT)
GPIO.setup(green_led, GPIO.OUT)
GPIO.setup(sensor_in, GPIO.IN)

# Make sure the pins start off in the LOW state
GPIO.output(green_led, GPIO.LOW)
GPIO.output(red_led, GPIO.LOW)

# Then turn on the green - no noise light - and confirm system is online.
GPIO.output(green_led, GPIO.HIGH)
print("GPIO set. Service ready. Initiating Detection Protocol.")

# Add an event detection setting to the sensor pin - when it changes state it will trigger an alert condition
GPIO.add_event_detect(sensor_in, GPIO.RISING, bouncetime=300)


# ------------------------------------------------------------------------------------------
# Functions Area
# ------------------------------------------------------------------------------------------

#this is our main work function - if the sensor is triggered, we will do work here
def dowork(sensor_in): 
	# because Python implements loose variables - we have to make sure it knows we are not redefining these
	# but reusing the global versions. This is not strictly "good code", but there is not a good alternative
	global Loud_Count, loop_count, per_detected, max_loop, louds_per
	
	# did we detect something?
	if GPIO.input(sensor_in):
		# YUP! Turn on that red light!
		GPIO.output(red_led, GPIO.HIGH)

		# We have NOISE! Add it to the count of Loud events
		Loud_Count = Loud_Count + 1
		louds_per = louds_per + 1

		# Now we can see if we are detecting a lot of events or not?
		# By getting the ratio of events to the number of times we looked for one, we can see if it was
		# a spike or actually a really noisy time. This is why the "max_loop" variable matters
		# so you can set the a_threshold value and see if you have consistent noise or just spikes
		per_detected = Decimal(louds_per) / Decimal(loop_count)
		per_detected = round(per_detected, 10)
		
		# compare the percent of detection loops to the overall threshold for loudness - that is the ratio
		# of non-detection loops to detection events - and then respond accordingly:
		if per_detected > a_threshold:
			print("REALLY PRETTY LOUD! Detect vs Threshold: " + str(per_detected) + " / " + str(a_threshold))
			print(str(loop_count) + "loops vs " + str(louds_per) + " events")
		else:
			print("Meh. Some noise. Detect vs Threshold: " + str(per_detected) + " / " + str(a_threshold))
			print(str(loop_count) + "loops vs " + str(louds_per) + " events")


# ------------------------------------------------------------------------------------------
# Main Program Area
# ------------------------------------------------------------------------------------------

# try block to handle exception conditions and run the program loop
try:	
	# This syntax will lock the loop into a time window (5 seconds 
	# by default as definied by the time_loop variable)
	# This is extremely useful for debugging, and for setting the max_loops value
	etime = time.time() + time_loop #etime is the end time of our loop - the difference between right now and the time_loop value
	while(True): #time.time() < etime:

		# Count the number of iterations
		loop_count = loop_count + 1
		Loops_Tot = Loops_Tot + 1
		if GPIO.event_detected(sensor_in):

			# Now we also need to go do our work to update our hardware and software:
			dowork(sensor_in)
			
			# Because we detected sounds, we need to turn on and off our event collector to avoid
			# "duplicate assignment" errors
			GPIO.remove_event_detect(sensor_in)
			# an extra pause of sleep cycle to make sure everything is cleared out before re-enabling our event detection
			# if you want to slow down to overall sound detection event, you can raise this number (in seconds)
			time.sleep(0.25)
			# Turn back on the detection and start "listening" to our pin again
			GPIO.add_event_detect(sensor_in, GPIO.RISING, bouncetime=300)  # lets us know when the pin is triggered

		# Lastly for the main body, we catch our loop count when it exceeds the end time
		# and reset everything to keep everything running, and our display and math accurate:
		if time.time() > etime:
			# first we update our output to the web for display:
			with open(web_file, 'a') as f_output:
				if louds_per > 5:
					if louds_per > 10:
						f_output.write("<tr><td align=center bgcolor=red><font color=white>On " + str(ptime) + ", it was Loud!!</td><td align=center bgcolor=red><font color=white>" + str(louds_per) + "</font></td></tr>")
					else:
						f_output.write("<tr><td align=center bgcolor=orange><font color=white>On " + str(ptime) + ", it was a little loud.</td><td align=center bgcolor=orange><font color=white>" + str(louds_per) + "</font></td></tr>")
				else:
					f_output.write("<tr><td align=center bgcolor=green><font color=white>On " + str(ptime) + ", it was pretty quiet.</td><td align=center bgcolor=green><font color=white>" + str(louds_per) + "</font></td></tr>")
				
			print("Reseting Counters")
			loop_count = 0
			louds_per = 0
			etime = time.time() + time_loop # etime is the end time of our loop - the difference between right now and the time_loop value
			ptime = time.ctime(etime) # the "pretty" version of the current time block - suitable for charts and graphs!
			# turn off the RED LED since we are starting a new detection loop - maximum time it would stay on is 5 seconds by default
			GPIO.output(red_led, GPIO.LOW)
			

except (KeyboardInterrupt, SystemExit):
	
	#If the system is interrupted (ctrl-c) this will print the final values
	#so that you have at least some idea of what happened
	print("-------------------------------------------")
	print(" ")
	print("System Reset on Keyboard Command or SysExit")
	print(" ")
	print("Total Noises Detected: " + str(Loud_Count))
	print(" ")
	print("Total loops run: " + str(Loops_Tot))
	print(" ")
	print("-------------------------------------------")

	# Having this command is a best practice for all Raspberry Pi programs!
	# It ensures that the GPIO pins are all reset to defaults (off) state
	# when the program exits. Important so that you don't have errors on the
	# next program run!
	GPIO.cleanup()

else:
	

	# You can remove this entire block once you go to "production" mode
	# but these values are critical for the initial tuning phase.
	print("-------------------------------------------")
	print(" ")
	print("System Reset for some reason")
	print(" ")
	print("Total Noises Detected: " + str(Loud_Count))
	print(" ")
	print("Total loops run: " + str(Loops_Tot))
	print(" ")
	print("-------------------------------------------")
	GPIO.cleanup()
