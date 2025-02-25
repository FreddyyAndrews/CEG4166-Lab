import time, sys, tty, termios
from rotationSpeed_Graph import *
#Function to capture keyboard input

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

while True:
    #capture keyboard input
    char = getch()

    if char == "w":
        print("Char W pressed")
        #Move Forward
        Robot_forward(LEFT_FORWARD, RIGHT_FORWARD)
        Right_stop()
    
    elif char == "s":
        print("Char S pressed")
        #Move Backward
        Robot_reverse()
        time.sleep(.1)
        Robot_stop()
    
    elif char == "a":
        print("Char A pressed")
        #Move Left
        Robot_left()
        time.sleep(.1)
        Robot_stop()
    
    elif char == "d":
        print("Char D pressed")
        #Move Right
        Robot_right()
        time.sleep(.1)
        Robot_stop()        
    #Exits Program
    elif char == " ":
        exit()