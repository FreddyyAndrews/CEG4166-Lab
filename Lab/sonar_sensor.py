from hcsr04 import HCSR04
import time
import threading
import RPi.GPIO as GPIO

samples = 5
# creation of sonar sensor
sensor = HCSR04(7, 12)

# Setup for servo
servo_pin = 22  # Change as needed for your setup
GPIO.setup(servo_pin, GPIO.OUT)
pwm = GPIO.PWM(servo_pin, 50)  # 50Hz frequency
pwm.start(7.5)  # Start at center position
pulse_width = 1600  # Initial pulse width
direction = True  # Initial direction

# Define positions
POSITION_CENTER = 7.0
POSITION_RIGHT = 0.5
POSITION_LEFT = 12.5
current_position = POSITION_CENTER  # Track current position

# Function for sonar sensor takes HCSR04 object and sample number for accuracy of distance
def Sonar(sensor, samples):
    while(True):
        s = time.time()
        distance = sensor.measure(samples, "cm")
        e = time.time()
        print("Distance:", distance, "cm")
        print("Used time:", (e - s), "seconds")
        time.sleep(0.01)

def Sweep(pulse_width: int, direction: bool):
    if direction:
        pulse_width += 5
    else:
        pulse_width -= 5

    print(pulse_width)

    if pulse_width >= 2395:
        print("Got here")
        direction = False
    if pulse_width <= 605:
        print("got there")
        direction = True

    # Convert pulse width to duty cycle
    duty_cycle = pulse_width / 20000 * 100  # Assuming 20ms period for 50Hz
    pwm.ChangeDutyCycle(duty_cycle)
    return pulse_width, direction

def MoveCenter():
    global current_position
    if current_position != POSITION_CENTER:
        pwm.ChangeDutyCycle(POSITION_CENTER)
        current_position = POSITION_CENTER
        time.sleep(0.5)  # Allow servo to settle
    read()
    return None

def MoveRight():
    global current_position
    if current_position != POSITION_RIGHT:
        pwm.ChangeDutyCycle(POSITION_RIGHT)
        current_position = POSITION_RIGHT
        time.sleep(0.5)  # Allow servo to settle
    read()
    return None

def MoveLeft():
    global current_position
    if current_position != POSITION_LEFT:
        pwm.ChangeDutyCycle(POSITION_LEFT)
        current_position = POSITION_LEFT
        time.sleep(0.5)  # Allow servo to settle
    read()
    return None

def read():
    time.sleep(1)  # Adjust delay as needed
    distance = sensor.measure(samples, "cm")
    print(f"Distance: {distance} cm")

