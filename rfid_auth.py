#!/usr/bin/env python
# -*- coding: utf8 -*-

import RPi.GPIO as GPIO
import MFRC522
import signal
import time
import threading
from multiprocessing import Process

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print "Ctrl+C captured, ending read."
    continue_reading = False
    GPIO.cleanup()


continue_reading = True
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11,GPIO.OUT)
GPIO.setup(13,GPIO.OUT)
GPIO.setup(15,GPIO.OUT)


# LED Pulsate function
def pulsate():
    red = GPIO.PWM(11, 100)
    red.start(0)

    pause_time = 0.011

    try:
        while True:
            print "running"
            for i in range(100, -1, -1):
                red.ChangeDutyCycle(100 -  i)
                time.sleep(pause_time)
            for i in range(0, 101):
                red.ChangeDutyCycle(100 -  i)
                time.sleep(pause_time)

    except Exception as e:
       print str(e)


# Create object for pulsate_led process
def startPulsate():
    pulsate_led = Process(target=pulsate)
    pulsate_led.daemon = True
    pulsate_led.start()
    return pulsate_led

# Call pulsate process into a variable
p = startPulsate()

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)


# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while continue_reading:

    # Scan for cards
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # Get the UID of the card
    (status,uid) = MIFAREReader.MFRC522_Anticoll()

    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:
        # Join UID array into friendly string
        uid_str = ":".join([str(x) for x in uid])

        # Define authorized card
        authorized_uid = "201:133:20:43:115"

        # Kill pulsating LED process
        p.terminate()

        # Check if UID is Authorized
        if uid_str == authorized_uid:

            # Green Light
            GPIO.output(13, GPIO.HIGH)
        else:
            # Red Light - DENIED
            GPIO.output(15, GPIO.HIGH)
            print("DENIED!")

        # Wait 5 seconds then turn all the lights off
        time.sleep(5)
        GPIO.output(13, GPIO.LOW)
        GPIO.output(15, GPIO.LOW)

        # Restart pulsating process
        p = startPulsate()
