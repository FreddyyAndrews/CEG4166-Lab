import pigpio
import time
from math import pi

class WheelController():
    """
        More information in Parallax Feedback 360 Servo Datasheet
        PWM_FREQ: Measured in Hertz
        DUTY_CYCLE_MIN: Measured in percent
        DUTY_CYCLE_MAX: Measured in percent
    """

    PWM_FREQ = 910
    DUTY_CYCLE_MIN = 2.9
    DUTY_CYCLE_MAX = 97.1

    def __init__(self, raspi, inputPin, ticksPerTurn, radius) -> None:
        self.raspi = raspi
        self.inputPin = inputPin
        self.ticksPerTurn = ticksPerTurn 
        self.radius = radius
        self.numTurns = 0
        self.distPerDegree = ( 2 * pi * radius ) / 360
        self.pulseWidth = 0
        self.startTime = time.time()
        # Setup inputPin and Callback function
        self.raspi.set_mode(inputPin, pigpio.INPUT)
        self.raspi.callback(inputPin, pigpio.EITHER_EDGE, self.__gpio_callback)
    
    def __gpio_callback(self, GPIO, level, tick):
        if level:
            # Rising edge
            self.startTime = tick
        else:
            # Falling edge
            self.lastPulseWidth = self.pulseWidth
            self.pulseWidth = tick - self.startTime
            self.lastAngle = (100*(self.lastPulseWidth*self.PWM_FREQ/1000000)-self.DUTY_CYCLE_MIN)*360/(self.DUTY_CYCLE_MAX-self.DUTY_CYCLE_MIN)
            self.angle = (100*(self.pulseWidth*self.PWM_FREQ/1000000)-self.DUTY_CYCLE_MIN)*360/(self.DUTY_CYCLE_MAX-self.DUTY_CYCLE_MIN)
            if self.angle - self.lastAngle < -180:
                # One complete turn going forward
                self.numTurns+=1
            elif self.angle - self.lastAngle > 180:
                # One complete turn going backwards
                self.numTurns-=1

    def getCurrentDistance(self):
        if self.inputPin == 17:
            # Left motor
            return -(self.numTurns*360 + self.angle) * self.distPerDegree
        elif self.inputPin == 27:
            return (self.numTurns*360 + self.angle) * self.distPerDegree

    def getTotalDistance(self):
        if self.inputPin == 17:
            # Left motor
            return -(self.numTurns*360 + self.angle) * self.distPerDegree
        elif self.inputPin == 27:
            # Right motor
            return (self.numTurns*360 + self.angle) * self.distPerDegree
        