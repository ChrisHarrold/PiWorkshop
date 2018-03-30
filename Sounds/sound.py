# Import libraries used in this program
# the RPI.GPIO library is used by Python to interface with the RPi Hardware
import RPi.GPIO as GPIO
# the OS module allows us to use the file system
import os
# time is an incedibly useful python library that gives you access to commands for time
import time
# decimal allows you to work with decimal notation for numbers - very useful for high-precision
from decimal import *
# the math library allows you to perform standard math functions
import math
# here we are setting a decimal precision to use for accuracy in our math later - 4 decimal places
# is realtively good precision for this project
getcontext().prec = 4

# Startup message - will print to the console only
print("Preparing to monitor sound levels")
print("You can gracefully exit the program by pressing ctrl-C")

# We will be outputting to a website for a real-time view of noise detection events.
# for debugging you can leave this section commented out:
print("Readying Web Output File")
# Web output file definition - this file is called by the sound.html webpage and used to
# display the status of the sound detection
web_file = "/var/www/html/table.html"

# Opens and preps the HTML file for the first time. Will remove anything it
# finds in the file and prep it with this default entry - the replaces old
# data so definitely collect that info if you want it!
with open(web_file + '.new', 'w') as f_output:
    f_output.write("")
	os.rename(web_file + '.new', web_file)

# Set our GPIO pin assignments to the right pins
sensor_in = 18
red_led = 21
green_led = 20

#various counters used for determining the thresholds for sensitivity and detection
#as well as the time of the loop and frequency for debugging
Loud_Count = 0
per_detected = 0
time_loop = 5

# loop count is used in the non-service example for controlling how long the program runs.
loop_count = 0

# Max loop is determined by the tuning exercise this program allows you to undertake
# 10000000 is a good starting point - it is the time between counter resets for doing the
# general math
max_loop = 10000000

# This value is the final threshold where the system will take action
# it is the value of the number of times loud sound was detected
# versus the number of times the sensor was polled. Unless
# you are looking for spikes amidst loud noise, this number will be
# likely be .01 or even less
a_threshold = .01

# How long between sound level checks - not required, but you 
# can slow it down if needed for debuging or just for funsies
interval = .5

# Setup GPIO commands and pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(red_led, GPIO.OUT)
GPIO.setup(green_led, GPIO.OUT)
GPIO.setup(sensor_in, GPIO.IN)

#this is our work function - if the sensor is triggered, we will do work here
def callback(sensor_in): 
	global Loud_Count, loop_count, per_detected, max_loop
	# did we detect something?
	if GPIO.input(sensor_in):
		GPIO.output(red_led, GPIO.HIGH)

		# We have NOISE! Add it to the count of Loud events
		Loud_Count = Loud_Count + 1

		# Lets see if we have actually detected a sound that meets the
		# threshold? If so, we will turn on the red light and it will stay on
		# until the sound drops under the threshold again.
		per_detected = Decimal(Loud_Count) / Decimal(loop_count)
		per_detected = round(per_detected, 4)
		print("Detect vs Threshold: " + str(per_detected) + " / " + str(a_threshold))
		print(str(loop_count) + "loops and " + str(Loud_Count) + "events")
		
		# have we hit our threshold of noises yet?		 
		with open(web_file + '.new', 'a') as f_output:
   				f_output.write("")


# Make sure the pins start off in the LOW state
GPIO.output(green_led, GPIO.LOW)
GPIO.output(red_led, GPIO.LOW)

# Then turn on the green - no noise light - and confirm system is online.
GPIO.output(green_led, GPIO.HIGH)
GPIO.output(red_led, GPIO.LOW)
print("GPIO set. Service starting. Press ctrl-c to break")

# If sound is loud enough, the GPIO PIN will switch state
GPIO.add_event_detect(sensor_in, GPIO.RISING, bouncetime=300)  # let us know when the pin is triggered
GPIO.add_event_callback(sensor_in, callback)  # assign function to GPIO PIN, Run function on change

# try block to handle the exception conditions and run the program loop
try:	
	# This syntax will lock the loop into a time window (5 seconds 
	# by default as definied by the time_loop variable)
	# This is extremely useful for debugging, and for threshold detection.

	# Now we get to the actual loop and start detecting sound
	t_end = time.time() + time_loop
	while(True): # time.time() < t_end:
		# Count the number of iterations - important for determining 
		# sustained detection versus flutter in the sensor
		loop_count = loop_count + 1

		# Lastly for the main body, we catch our loop count before it gets to max_loop
		# and reset everything to keep everything running, and our math accurate:
		if loop_count == max_loop:
			print("Reseting Counters")
			loop_count = 0
			per_detected = 0
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
	print("Total loops run: " + str(loop_count))
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
	print("System Reset on Keyboard Command or SysExit")
	print(" ")
	print("Total Noises Detected: " + str(Loud_Count))
	print(" ")
	print("Total loops run: " + str(loop_count))
	print(" ")
	print("-------------------------------------------")
	GPIO.cleanup()
