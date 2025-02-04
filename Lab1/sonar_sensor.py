import time
import threading
from HCSR04 import HCSR04

# Number of samples for averaging distance measurements
samples = 5

# Creation of sonar sensor instance with trigger pin 7 and echo pin 12
sensor = HCSR04(7, 12)

def Sonar(sensor, samples):
    """
    Function to continuously measure and print distance using the sonar sensor.
    :param sensor: HCSR04 sensor object
    :param samples: Number of samples for accuracy
    """
    while True:
        s = time.time()  # Start time
        distance = sensor.measure(samples, "cm")  # Measure distance
        e = time.time()  # End time
        
        print("Distance:", distance, "cm")
        print("Used time:", (e - s), "seconds")
        
        time.sleep(0.01)  # Small delay to prevent excessive CPU usage

# Create and start a separate thread for the sonar function
sensorThread = threading.Thread(target=Sonar, args=(sensor, samples))
sensorThread.start()
