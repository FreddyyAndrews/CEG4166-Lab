import time, sys, tty, termios, select
import pigpio
from motor_control import Motor_control

# Table 1: Keyboard Keys and Stingray Commands
# W - Move forward one tile
# D - Rotate 90 degrees clockwise
# A - Rotate 90 degrees counter clockwise
# Q - Exit program

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        rlist, _, _ = select.select([sys.stdin], [], [], 0)
        if rlist:
            return sys.stdin.read(1).lower()
        return None
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
# Initialize motor controller
pi = pigpio.pi()
mc = Motor_control(pi=pi)

try:
    while True:
        char = getch()
        if char == 'w':
            mc.straight(200)  # Move forward one tile (200mm)
        elif char == 'd':
            mc.turn(90)  # Rotate 90 degrees clockwise
        elif char == 'a':
            mc.turn(-90)  # Rotate 90 degrees counter-clockwise
        elif char == 'q':
            print("Exiting...")
            break

        time.sleep(0.01)
finally:
    mc.servo_l.stop()
    mc.servo_r.stop()
    pi.stop()

