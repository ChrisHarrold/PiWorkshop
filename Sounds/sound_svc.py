# Import libraries used in this program
import RPi.GPIO as GPIO
import os, sys
import time
from decimal import *
import math
getcontext().prec = 4

# Startup message
print "Preparing to monitor sound levels"
	
# Set our pin assignments
sensor_in = 18
red_led = 21
green_led = 20

#Simple string for printing an output on detection - can be removed for quiet running
Is_Loud = "No"

# Web output settings:
web_file = "/var/www/html/level.js"

# Various counters used for determining the thresholds for sensitivity and detection
# as well as the time of the loop and frequency for debugging
Loud_Count = 0
per_detected = 0
events_detected = 0
time_loop = 15

# Max loop is determined by the tuning exercise and will depend heavily on your sensor
# for the sensor I originally used, the max loop was 30000 to get consistent readings
loop_count = 0
max_loop = 30000

# This value is the final threshold where the system will take action
# it is the value of the number of times loud sound was detected
# versus the number of times the sensor was polled. Unless
# you are looking for spikes amidst loud noise, this number will
# likely be .01 or even significantly smaller
a_threshold = .01

# How long between sound level checks - not required, but you 
# can slow it down if needed for debuging or just for funsies
interval = .5

# Setup GPIO commands and pins and cleanup pins in case of errors
GPIO.setmode(GPIO.BCM)
GPIO.setup(red_led, GPIO.OUT)
GPIO.setup(green_led, GPIO.OUT)
GPIO.setup(sensor_in, GPIO.IN)

# Make sure the pins start off in the LOW state
GPIO.output(green_led, GPIO.LOW)
GPIO.output(red_led, GPIO.LOW)

# Then turn on the green - no noise light - and confirm system is online.
GPIO.output(green_led, GPIO.HIGH)
GPIO.output(red_led, GPIO.LOW)

print "Readying Web Output File"
# Opens and preps the HTML file for the first time. Will remove anything it
# finds in the file and prep it with this default:
with open(web_file + '.new', 'w') as f_output:
    f_output.write("var int_level = 0")

os.rename(web_file + '.new', web_file)

print "GPIO set. Service starting. Press ctrl-c to break"

# Main try block to handle the exception conditions
try:	

    # Primary monitor is a "while" loop that will keep the monitor running 
	# indefinitely as a soft service.
	#
	# This first syntax will lock the loop into a time window, 5 seconds 
	# by default as definied by the time_loop variable.
	# This is extremely useful for debugging, and for threshold detection.
	#
	# The microphone sensor is notoriously hard to tune for threshold
	# and having this will allow you to figure out the number of events
	# in a fixed window of time. This means you can divide by the number
	# of events versus the number of times the monitor looked for an event,
	# to define the sensitivity in software and not rely solely on the
	# sensor itself.
	#	
	# You can remove this version once the sensitivity is reliable:

	# t_end = time.time() + time_loop
	# while time.time() < t_end:
	
	# This version simply loops for eternity unless ctrl-c is pressed
	# and should be your "production" version of the loop based on your
	# tuning results and the length of the loop that matches your sensitivity needs
	# my happy default is 30k loops or about 5 seconds:
	
	while loop_count < max_loop:

	# Now we get to the actual loop and start detecting sound
		
		# Count the number of iterations - important for determining 
		# sustained detection versus flutter in the sensor
		loop_count = loop_count + 1
		
		# If sound is loud enough, the GPIO PIN will switch state to HIGH
		# record the occurance and add it to the count for computation
		if GPIO.input(sensor_in) == GPIO.HIGH:
			Is_Loud = "Loudness Detected"
			Loud_Count = Loud_Count + 1

		
		# have we hit our threshold yet?		 
		per_detected = Decimal(Loud_Count) / Decimal(loop_count)
		# You can un-remark the line to print the detected and threshold value each loop
		# which is useful for the debugging, but takes cycles away from computation
		
		#print "Detect vs Threshold: " + str(per_detected) + " / " + str(a_threshold)
		
		# write it to the .js file for web display if per_detected is high enough to trigger
		# the output otherwise, just leave it alone (saves CPU but causes a minor 'bleed'
		# where the last per_detected could be displayed for a long time
		if per_detected > 0:
			with open(web_file + '.new', 'w') as f_output:
   				f_output.write("var int_level = " + str(per_detected))
				os.rename(web_file + '.new', web_file)
		
		# Lets see if we have actually detected a sound that meets the
		# threshold? If so, we will turn on the red light and it will stay on
		# until the sound drops under the threshold again.
		if per_detected > a_threshold:
			GPIO.output(red_led, GPIO.HIGH)

		else:
			GPIO.output(red_led, GPIO.LOW)

		# Lastly for the main body, we catch our loop count before it gets to max_loop
		# and reset everything to keep everything running, and our math accurate:
		if loop_count == max_loop:
			print "System is listening"
			loop_count = 0
			per_detected = 0
			Loud_Count = 0
			with open(web_file + '.new', 'w') as f_output:
    				f_output.write("var int_level = 0 ")
    				os.rename(web_file + '.new', web_file)
			

except (KeyboardInterrupt, SystemExit):
	
	# If the system is interrupted (ctrl-c) this will print the final values
	# so that you have at least some idea of what happened
	print "-------------------------------------------"
	print " "
	print "System Reset on Keyboard Command or SysExit"
	print " "
	print "Final Detection was " + str(Is_Loud)
	print " "
	print "Total Noises Detected: " + str(Loud_Count)
	print " "
	print "Total loops run: " + str(loop_count)
	print " "
	print "-------------------------------------------"
	GPIO.cleanup()

else:
	
	GPIO.cleanup()

        # You can remove this entire block once you go to "production" mode
		# but these values are critical for the initial tuning phase.
        print "-------------------------------------------"
        print " "
        print "System Reset on Keyboard Command or SysExit"
        print " "
        print "Final Detection was " + str(Is_Loud)
        print " "
        print "Total Noises Detected: " + str(Loud_Count)
        print " "
        print "Total loops run: " + str(loop_count)
        print " "
        print "-------------------------------------------"
