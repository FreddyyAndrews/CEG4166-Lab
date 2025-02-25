import RPi.GPIO as gpio
import time
class HCSR04:
#Encapsulates the attributes and methods to use the HC-SR04 ultra-sound distance sensor
    trig = 0
    echo = 0
    const_cm = 17014.50
    const_in = 6698.62
    const_ft = 558.2
    def __init__(self, trig, echo):
        self.trig = trig
        self.echo = echo

        gpio.setmode(gpio.BOARD)
        gpio.setup(self.trig, gpio.OUT)
        gpio.setup(self.echo, gpio.IN)
        gpio.output(self.trig, False)
        # Sleep for 0.3 s for the sensor to settle
        time.sleep(0.3)

    def __del__(self):
        gpio.cleanup()
        print("all clean")
    
    #Measures the distance and return the distance in the desired unit
    def measure(self, samples, unit):
        count = 0
        distance = 0.0
        pulse_start = 0
        pulse_end = 0
        acc = 0
        while count < samples:

            gpio.output(self.trig, True)
            time.sleep(0.00001)
            gpio.output(self.trig, False)
            
            start = time.time()
            while gpio.input(self.echo) == 0:
                if time.time() - start > 0.05:
                    return None  # Timeout if no echo received
                pulse_start = time.time()
            while gpio.input(self.echo) == 1:
                if time.time() - start > 0.05:
                    return None
                pulse_end = time.time()
            
            pulse_duration = pulse_end - pulse_start
            if(unit == "cm"):
                distance = pulse_duration * self.const_cm
            elif(unit == "in"):
                distance = pulse_duration * self.const_in
            elif(unit == "ft"):
                distance = pulse_duration * self.const_ft
            else:
                distance = 0.0
            acc += distance
            count += 1
            
        acc = round(acc / samples, 2)
        return acc


from HCSR04 import HCSR04
samples = 5
#creation of sonar sensor
sensor = HCSR04(7, 12)
#Function for sonar sensor takes HCSR04 object and sample number for accuracy of distance
def Sonar(sensor, samples):
    while(True):
        
        distance = sensor.measure(samples, "cm")
    
        if distance is not None:
            print ("Distance:", distance, "cm")
            if distance < 10:
                print("Object detected, stopping robot and rerouting.....")
        else:
            print ("Sensor timeout or error")
        time.sleep(0.1)

sensorThread = threading.Thread(target = Sonar, args = (sensor, samples))
sensorThread.start()