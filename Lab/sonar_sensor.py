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

    if pulse_width >= 2495:
        print("Got here")
        direction = False
    if pulse_width <= 705:
        print("got there")
        direction = True

    # Convert pulse width to duty cycle
    duty_cycle = pulse_width / 20000 * 100  # Assuming 20ms period for 50Hz
    pwm.ChangeDutyCycle(duty_cycle)
    return pulse_width, direction

def MoveCenter():
    pwm.ChangeDutyCycle(8)  # Adjust duty cycle for center position
    read()
    return None

def MoveRight():
    pwm.ChangeDutyCycle(3.5)  # Adjust duty cycle for right position
    read()
    return None

def MoveLeft():
    pwm.ChangeDutyCycle(12.5)  # Adjust duty cycle for left position
    read()
    return None

def read():
    time.sleep(1)  # Adjust delay as needed
    distance = sensor.measure(samples, "cm")
    print(f"Distance: {distance} cm")

