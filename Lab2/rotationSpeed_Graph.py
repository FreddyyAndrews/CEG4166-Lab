#Import Libraries
import threading
import time
from matplotlib.pylab import *
#from mpl_toolkits.axes_grid1 import host_subplot
import matplotlib.animation as animation
import pigpio
import RPi.GPIO as GPIO
from wheel import WheelController
from PlotDataRobot import multiplePlots
import matplotlib.pyplot as plt

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
        
servos = [23,24]
raspi= pigpio.pi()

samples = 5

#creation of two encoders using WheelController class
leftEncoderCount = WheelController(raspi, 17, 32, 5.65/2)
rightEncoderCount = WheelController(raspi, 27, 32, 5.65/2)

xmax = 5
plotData = multiplePlots(leftEncoderCount, rightEncoderCount,
    samples, xmax)

#Defing Constants for the Motor Controller
LEFT_STOP = 0
LEFT_FORWARD = 2500
LEFT_REVERSE = 500
RIGHT_STOP = 0
RIGHT_FORWARD = 500
RIGHT_REVERSE = 2500



#Returning values to plot the data
def loopData(self):
    plotData.updateData()
    return plotData.p011, plotData.p012, plotData.p021, plotData.p022
	
def Left_forward(n):
    raspi.set_servo_pulsewidth(servos[0], n)
    
def Left_reverse():
    raspi.set_servo_pulsewidth(servos[0], LEFT_REVERSE)
	
def Left_stop():
    raspi.set_servo_pulsewidth(servos[0], LEFT_STOP)

#Value for servo speed forward now an argument that must be passed    
def Right_forward(n):
    raspi.set_servo_pulsewidth(servos[1], n)
    
def Right_reverse():
    raspi.set_servo_pulsewidth(servos[1], RIGHT_REVERSE)
    
def Right_stop():
    raspi.set_servo_pulsewidth(servos[1], RIGHT_STOP)

#robot forward function takes two arguments for each motors servo speed
def Robot_forward(n, m):
    Left_forward(n)
    Right_forward(m)
    time.sleep(.1)
    
def Robot_reverse():
    Left_reverse()
    Right_reverse()
    time.sleep(.1)
    
def Robot_stop():
    Left_stop()
    Right_stop()
    time.sleep(.1)
        
def Robot_right():
    Left_forward(LEFT_FORWARD)
    Right_reverse()

def Robot_left():
    Right_forward(RIGHT_FORWARD)
    Left_reverse()

#Function to stop all motors    
def motorStop():
    for s in servos:
        raspi.set_servo_pulsewidth(s,0)  

# Function to display messages on the screen
def display_message(top, bottom):
    print(f"Displaying on screen:\n{top.center(20)}\n{bottom.center(20)}")
     
#Function for encoder output takes WheelController object and a name for the encoder as #arguments
def Encoders(WheelController, name):
    while(True):
        dist = WheelController.getCurrentDistance()
        totDist = WheelController.getTotalDistance()
        # print("\n{} Distance: {}cm".format(name, dist))
        # print("\n{} Ticks: {}".format(name, WheelController.getTicks()))
        # print("\n{} Total Distance: {}cm".format(name, totDist))
        # print("\n{} Total Ticks: {}".format(name, WheelController.getTotalTicks()))
        time.sleep(0.01)


#create a function to move the robot, with 2 arguments
#remember to add the functions that you need from the previous codes,
#as Robot_forward() and Robot_stop()

#Define the function to move the robot
def move_sequence():
    display_message("Path", "1")
    time.sleep(5)  # Display "Path 1" before movement
    Robot_forward(LEFT_FORWARD, RIGHT_FORWARD)
    time.sleep(5)
    Robot_right()
    time.sleep(1.2)
    Robot_forward(LEFT_FORWARD, RIGHT_FORWARD)
    time.sleep(5)
    Robot_stop()

def move_sequence2():
    display_message("Path", "2")
    time.sleep(5)  # Display "Path 2" before movement
    Robot_forward(LEFT_FORWARD, RIGHT_FORWARD)
    time.sleep(5)
    Robot_left()
    time.sleep(1.2)
    Robot_forward(LEFT_FORWARD, RIGHT_FORWARD)
    time.sleep(5)
    Robot_stop()


def moves(any, any2):
    #wait for the graph to appear on the screen
    time.sleep(5)
    
    Robot_forward(2500,500)
    time.sleep(5)
    Robot_right()
    time.sleep(1.2)
    Robot_forward(2500,500)
    time.sleep(5)
    Robot_stop()


#create a thread to call this function
movementThread = threading.Thread(target = move_sequence)
movementThread2 = threading.Thread(target = move_sequence2)
#movementThread3 = threading.Thread(target = moves, args = ('anything','anything2'))


#start the thread
movementThread.start()
movementThread2.start()
#movementThread3.start()

#Create an animation to plot the data, during 1 minute
simulation = animation.FuncAnimation(fig=plotData.f0, func=loopData,
                    blit=False, frames=200, interval=20, repeat=False)

#plotting
plt.show()
print('terminou')
plt.close()

#stop the raspberry pi
raspi.stop()
