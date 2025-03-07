import sys, tty, termios, select
import pigpio
import RPi.GPIO as gpio
from motor_control import Motor_control
from sonar_sensor import *


def set_terminal_raw(fd):
    old_settings = termios.tcgetattr(fd)
    new_settings = termios.tcgetattr(fd)
    # Disable canonical mode and echo.
    new_settings[3] &= ~(termios.ECHO | termios.ICANON)
    termios.tcsetattr(fd, termios.TCSADRAIN, new_settings)
    return old_settings


def restore_terminal(fd, settings):
    termios.tcsetattr(fd, termios.TCSADRAIN, settings)


def getch(timeout=0.1):
    fd = sys.stdin.fileno()
    rlist, _, _ = select.select([sys.stdin], [], [], timeout)
    if rlist:
        return sys.stdin.read(1).lower()
    return None


# Initialize motor controller
pi = pigpio.pi()
mc = Motor_control(pi=pi)

if __name__ == "__main__":
    fd = sys.stdin.fileno()
    old_settings = set_terminal_raw(fd)
    try:
        while True:
            char = getch()
            if char:
                if char == "w":
                    print("Moving forward...")
                    mc.straight(500)
                    # Call your movement function here.
                elif char == "d":
                    print("Turning right...")
                    mc.turn_right()
                elif char == "a":
                    print("Turning left...")
                    mc.turn_left()
                elif char == "s":
                    print("Moving backward...")
                    mc.straight(-500)
                elif char == "x":
                    print("Stopping Wheels...")
                    mc.straight(0)
                elif char == "k":
                    print("Moving sonar to center...")
                    MoveCenter()
                elif char == "l":
                    print("Moving sonar to right...")
                    MoveRight()
                elif char == "j":
                    print("Moving sonar to left...")
                    MoveLeft()
                elif char == "m":
                    print("Sweepping sonar...")
                    Sonar(sensor, samples)
                    MoveLeft()
                elif char == "p":
                    samples = 5
                    # creation of sonar sensor
                    sensor = HCSR04(7, 12)
                    mc.straight(0)
                    print("Exiting...")
                    break
            # Your loop delay
    finally:
        mc.servo_l.stop()
        mc.servo_r.stop()
        pi.stop()
        restore_terminal(fd, old_settings)
