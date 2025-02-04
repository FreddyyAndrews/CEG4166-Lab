from hcsr04 import HCSR04
import pigpio
import RPi.GPIO as GPIO
import threading
import time

samples = 5
#creation of sonar sensor
sensor = HCSR04(7, 12)

raspi = pigpio.pi()

# Function for sonar sensor takes HCSR04 object and sample number for accuracy of distance
def Sonar(sensor, samples):
    current_pulse_width: int = 2500
    direction: bool = False

    while True:
        s = time.time()
        distance = sensor.measure(samples, "cm")
        e = time.time()
        current_pulse_width, direction = Sweep(current_pulse_width, direction)
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

    raspi.set_servo_pulsewidth(25, pulse_width)
    return pulse_width, direction

if __name__ == "__main__":
    sensorThread = threading.Thread(target=Sonar, args=(sensor, samples))
    sensorThread.start()

