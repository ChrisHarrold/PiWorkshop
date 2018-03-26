import RPi.GPIO as GPIO
import time
from decimal import *
import math
getcontext().prec = 4
sensor_in = 18
red_led = 21
green_led = 20
Loud_Count = 0
per_detected = 0
time_loop = 5
loop_count = 0
max_loop = 30000
a_threshold = .01
interval = .5
GPIO.setup(red_led, GPIO.OUT)
GPIO.setup(green_led, GPIO.OUT)
GPIO.setup(sensor_in, GPIO.IN)
GPIO.output(red_led, GPIO.LOW)
GPIO.output(red_led, GPIO.LOW)
try:
    t_end = time.time() + time_loop
    while time.time() < t_end:
		loop_count = loop_count + 1
		if GPIO.input(sensor_in) == GPIO.HIGH:
			Loud_Count = Loud_Count + 1	 
		per_detected = Decimal(Loud_Count) / Decimal(loop_count)
		print("Detect vs Threshold: " + str(per_detected) + " / " + str(a_threshold))
		if per_detected > a_threshold:
			print("LOUD LOUD LOUD")
			GPIO.output(red_led, GPIO.HIGH)
		else:
			GPIO.output(red_led, GPIO.LOW)
		if loop_count == max_loop:
			loop_count = 0
			per_detected = 0
			Loud_Count = 0
except (KeyboardInterrupt, SystemExit):
	GPIO.cleanup()
else:	
	GPIO.cleanup()
