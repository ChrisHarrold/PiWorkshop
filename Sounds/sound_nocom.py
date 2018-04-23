
import RPi.GPIO as GPIO
import os
import time
from decimal import Decimal
import math

print("Preparing to monitor sound levels")
print("You can gracefully exit the program by pressing ctrl-C")
print("Readying Web Output File")
web_file = "/var/www/html/table.shtml"
with open(web_file + '.new', 'w') as f_output:
	f_output.write("")
	os.rename(web_file + '.new', web_file)
Loud_Count = 0 # Count of trigger events from the sensor total since the program started running
louds_per = 0 # Count of trigger events from the sensor in this time interval
per_detected = 0 # The percent of loops where sound is detected versus not detected (math performed on this value later)
time_loop = 5 # The numeric value is how many seconds you want the timestamps to be spaced by
stime = time.time() # The time right now (in UNIX Datetime format - that is to say a really long string of seconds)
etime = stime + time_loop #etime is the end time of our loop - the difference between right now and the time_loop value
ptime = time.ctime() #the "pretty" version of the current time - suitable for charts and graphs!
Loops_Tot = 0
loop_count = 0
max_loop = 10000000
a_threshold = .00000001
sensor_in = 18
red_led = 21
green_led = 20
GPIO.setmode(GPIO.BCM)
GPIO.setup(red_led, GPIO.OUT)
GPIO.setup(green_led, GPIO.OUT)
GPIO.setup(sensor_in, GPIO.IN)
GPIO.output(green_led, GPIO.LOW)
GPIO.output(red_led, GPIO.LOW)
GPIO.output(green_led, GPIO.HIGH)
print("GPIO set. Service ready. Initiating Detection Protocol.")
GPIO.add_event_detect(sensor_in, GPIO.RISING, bouncetime=300)

def dowork(sensor_in): 
	global Loud_Count, loop_count, per_detected, max_loop, louds_per
	if GPIO.input(sensor_in):
		GPIO.output(red_led, GPIO.HIGH)
		Loud_Count = Loud_Count + 1
		louds_per = louds_per + 1
		per_detected = Decimal(louds_per) / Decimal(loop_count)
		per_detected = round(per_detected, 10)
		if per_detected > a_threshold:
			print("REALLY PRETTY LOUD! Detect vs Threshold: " + str(per_detected) + " / " + str(a_threshold))
			print(str(loop_count) + "loops vs " + str(louds_per) + " events")
		else:
			print("Meh. Some noise. Detect vs Threshold: " + str(per_detected) + " / " + str(a_threshold))
			print(str(loop_count) + "loops vs " + str(louds_per) + " events")

try:	
	etime = time.time() + time_loop #etime is the end time of our loop - the difference between right now and the time_loop value
	while(True): #time.time() < etime:
		loop_count = loop_count + 1
		Loops_Tot = Loops_Tot + 1
		if GPIO.event_detected(sensor_in):
			dowork(sensor_in)

			GPIO.remove_event_detect(sensor_in)
			time.sleep(0.25)
			GPIO.add_event_detect(sensor_in, GPIO.RISING, bouncetime=300)  # lets us know when the pin is triggered
		if time.time() > etime:
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
			GPIO.output(red_led, GPIO.LOW)
			

except (KeyboardInterrupt, SystemExit):
	print("-------------------------------------------")
	print(" ")
	print("System Reset on Keyboard Command or SysExit")
	print(" ")
	print("Total Noises Detected: " + str(Loud_Count))
	print(" ")
	print("Total loops run: " + str(Loops_Tot))
	print(" ")
	print("-------------------------------------------")
	GPIO.cleanup()

else:
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
