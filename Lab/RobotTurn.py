# Import Libraries
import threading
import time
from matplotlib.pylab import *
from mpl_toolkits.axes_grid1 import host_subplot
import matplotlib.animation as animation
import pigpio
import RPi.GPIO as GPIO
from WheelEncoders import WheelEncoder
from PlotData import multiplePlots
import matplotlib.pyplot as plt

# GPIO setup
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# Servo pins
servos = [23, 24]

# Initialize pigpio
raspi = pigpio.pi()

# Number of samples and encoder setup
samples = 5
leftEncoderCount = WheelEncoder(11, 32, 5.65 / 2)
rightEncoderCount = WheelEncoder(13, 32, 5.65 / 2)
xmax = 5
plotData = multiplePlots(leftEncoderCount, rightEncoderCount, samples, xmax)

# Returning values to plot the data
def loopData(self):
    plotData.updateData()
    return plotData.p011, plotData.p012, plotData.p021, plotData.p022

# Servo motor control functions
def Left_forward(n):
    raspi.set_servo_pulsewidth(servos[0], n)

def Left_reverse():
    raspi.set_servo_pulsewidth(servos[0], 500)

def Left_stop():
    raspi.set_servo_pulsewidth(servos[0], 0)

def Right_forward(n):
    raspi.set_servo_pulsewidth(servos[1], n)

def Right_reverse():
    raspi.set_servo_pulsewidth(servos[1], 2500)

def Right_stop():
    raspi.set_servo_pulsewidth(servos[1], 0)

# Robot motion functions
def Robot_forward(n, m):
    Left_forward(n)
    Right_forward(m)
    time.sleep(0.1)

def Robot_reverse():
    Left_reverse()
    Right_reverse()
    time.sleep(0.1)

def Robot_stop():
    Left_stop()
    Right_stop()
    time.sleep(0.1)

def Robot_right():
    Left_forward(2500)
    Right_reverse()

def Robot_left():
    Right_forward(500)
    Left_reverse()

# Function to stop all motors
def motorStop():
    for s in servos:
        raspi.set_servo_pulsewidth(s, 0)

# Function for encoder output
def Encoders(wheelEncoder, name):
    while True:
        dist = wheelEncoder.getCurrentDistance()
        totDist = wheelEncoder.getTotalDistance()
        # Uncomment below for debugging encoder values
        # print("\n{} Distance: {}cm".format(name, dist))
        # print("\n{} Ticks: {}".format(name, wheelEncoder.getTicks()))
        # print("\n{} Total Distance: {}cm".format(name, totDist))
        # print("\n{} Total Ticks: {}".format(name, wheelEncoder.getTotalTicks()))
        time.sleep(0.01)

# Function to move the robot
def moves(any, any2):
    # Wait for the graph to appear on the screen
    time.sleep(5)

    Robot_forward(1280, 1280)
    time.sleep(5)
    Robot_right()
    time.sleep(1.2)
    Robot_forward(1280, 1280)
    time.sleep(5)
    Robot_stop()

# Create a thread to call the movement function
movementThread = threading.Thread(target=moves, args=('anything', 'anything2'))
movementThread.start()

# Create an animation to plot the data
simulation = animation.FuncAnimation(
    fig=plotData.f0, func=loopData, blit=False, frames=200, interval=20, repeat=False
)

# Plotting
plt.show()

print('terminou')
plt.close()

# Stop the Raspberry Pi
# raspi.stop()
