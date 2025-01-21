import time
from time import sleep
import pigpio
import RPi.GPIO as GPIO

# Use def to define functions
# Initialization of servos and libraries
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

servos = [23, 24]
raspi = pigpio.pi()

# Left and right motor movement, each motor behaves differently based on
# pulse width values; thus determine the values your robot motors use
# Play around with the values to find max values for the Stingray motors
def Left_forward():
    raspi.set_servo_pulsewidth(servos[0], 2500)

def Left_reverse():
    raspi.set_servo_pulsewidth(servos[0], 500)

def Left_stop():
    raspi.set_servo_pulsewidth(servos[0], 0)

def Right_forward():
    raspi.set_servo_pulsewidth(servos[1], 500)

def Right_reverse():
    raspi.set_servo_pulsewidth(servos[1], 2500)

def Right_stop():
    raspi.set_servo_pulsewidth(servos[1], 0)

# Robot movement clockwise or counterclockwise by calling on functions
# motor movement
def Robot_right():
    Left_forward()
    Right_reverse()
    time.sleep(0.1)

def Robot_left():
    Right_forward()
    Left_reverse()
    time.sleep(0.1)

try:
    # Python code starts execution from here
    while True:
        Robot_right()
except KeyboardInterrupt:
    print("Keyboard Press")
finally:
    for s in servos:
        raspi.set_servo_pulsewidth(s, 0)
