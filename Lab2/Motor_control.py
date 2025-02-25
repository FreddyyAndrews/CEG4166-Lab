#Parallax Servo 360 Python test code to control angular rotations and speeds of the motors
#SEG 4145
#Lab2

import math
import statistics
import time
import pigpio
import RPi.GPIO as gpio

class Motor_control:
    
    
    # these are the fixed dimensions of the stingray
    def __init__(
        self, pi, width_robot = 205, diameter_wheels = 50 , unitsFC = 360,
        dcMin_l = 27.3, dcMax_l = 969.15,
        dcMin_r = 27.3, dcMax_r = 978.25,
        l_wheel_gpio = 16, r_wheel_gpio = 20,
        servo_l_gpio = 17, min_pw_l = 1280, max_pw_l = 1720, min_speed_l = -1, max_speed_l = 1,
        servo_r_gpio = 27, min_pw_r = 1280, max_pw_r = 1720, min_speed_r = -1, max_speed_r = 1,
        sampling_time = 0.01,
        Kp_p = 0.1):
        self.pi = pi
        self.width_robot = width_robot
        self.diameter_wheels = diameter_wheels
        self.unitsFC = unitsFC
        self.dcMin_l = dcMin_l
        self.dcMax_l = dcMax_l
        self.dcMin_r = dcMin_r
        self.dcMax_r = dcMax_r
        self.sampling_time = sampling_time
        self.Kp_p = Kp_p
        self.l_wheel = Servo_read(pi = self.pi, gpio = l_wheel_gpio)
        self.r_wheel = Servo_read(pi = self.pi, gpio = r_wheel_gpio)
        self.servo_l = Servo_write(pi = self.pi, gpio = servo_l_gpio,min_pw =
        min_pw_l, max_pw = max_pw_l, min_speed = min_speed_l, max_speed = max_speed_l)
        self.servo_r = Servo_write(pi = self.pi, gpio = servo_r_gpio,min_pw =
        min_pw_r, max_pw = max_pw_r, min_speed = min_speed_r, max_speed = max_speed_r)
        time.sleep(1)
    def get_angle_l(self):
        angle_l = (self.unitsFC - 1) - ((self.l_wheel.read() -
                                         self.dcMin_l) * self.unitsFC) / (self.dcMax_l - self.dcMin_l + 1)
        angle_l = max(min((self.unitsFC - 1), angle_l), 0)
        return angle_l

    # angular position in units full circle
    def get_angle_r(self):
        angle_r = ((self.r_wheel.read() - self.dcMin_r) * self.unitsFC /
                   (self.dcMax_r - self.dcMin_r + 1))
        angle_r = max(min((self.unitsFC - 1), angle_r), 0)
        return angle_r

    def set_speed_l(self, speed):
        self.servo_l.set_speed(-speed)
        return None

    def set_speed_r(self, speed):
        self.servo_r.set_speed(speed)
        return None

    def get_total_angle(self, angle, unitsFC, prev_angle, turns):

        # If 4th to 1st quadrant
        if ((angle < (0.25 * unitsFC)) and (prev_angle > (0.75 * unitsFC))):
            turns += 1
        # If in 1st to 4th quadrant
        elif ((prev_angle < (0.25 * unitsFC)) and (angle >
                                               (0.75 * unitsFC))):
            turns -= 1
        if (turns >= 0):
            total_angle = (turns * unitsFC) + angle
        elif (turns < 0):
            total_angle = ((turns + 1) * unitsFC) - (unitsFC - angle)
        return turns, total_angle


    def get_target_angle(self, number_ticks, angle):
        target_angle = angle + number_ticks
        return target_angle

    def tick_length(self):
        tick_length_mm = math.pi * self.diameter_wheels / self.unitsFC
        return tick_length_mm

    def arc_circle(self, degree):
        arc_circle_mm = degree * math.pi * self.width_robot / 360.0
        return arc_circle_mm

    def turn(self, degree):
        number_ticks = self.arc_circle(degree) / self.tick_length()
        return None

    def straight(self, distance_in_mm):
        number_ticks = distance_in_mm / self.tick_length()
        return None


class Servo_read:
    def __init__(self, pi, gpio):
        self.pi = pi
        self.gpio = gpio
        self.period = 1 / 910 * 1000000
        self.tick_high = None
        self.duty_cycle = None
        self.duty_scale = 1000
        self.pi.set_mode(gpio=self.gpio, mode=pigpio.INPUT)

    def read(self):
        return self.duty_cycle


class Servo_write:

    # class to control the robot movements and angles
    # change the min and max pulsewidth only between (600-2400).
    def __init__(self, pi, gpio, min_pw=1280, max_pw=
    1720, min_speed=-1, max_speed=1, min_degree=-90, max_degree=90):
        self.pi = pi
        self.gpio = gpio
        self.min_pw = min_pw
        self.max_pw = max_pw
        self.min_speed = min_speed
        self.max_speed = max_speed
        self.min_degree = min_degree
        self.max_degree = max_degree
        # calculate slope for calculating the pulse width
        self.slope = ((self.min_pw - ((self.min_pw + self.max_pw) / 2))
                      / self.max_degree)
        # calculate y-offset for calculating the pulse width
        self.offset = (self.min_pw + self.max_pw) / 2

    def set_pw_speed(self, pulse_width):  # sets the speed of the
        pulse_width = max(min(self.max_pw, pulse_width), self.min_pw)
        self.pi.set_servo_pulsewidth(user_gpio=self.gpio, pulsewidth =pulse_width)

    def set_pw(self, pulse_width):
        pulse_width = max(min(self.max_pw, pulse_width), self.min_degree)
        self.pi.set_servo_pulsewidth(user_gpio=self.gpio, pulsewidth=pulse_width)

    def calc_pw_speed(self, speed):  # calculates the pulsewidth with respect to the speed
        pulse_width = self.slope * speed + self.offset
        return pulse_width

    def calc_pw(self, degree):  # calculates the pulsewidth with respect to the angle given
        pulse_width = self.slope * degree + self.offset
        return pulse_width

    def set_speed(self, speed):  # sets the motor rotation speed
        speed = max(min(self.max_speed, speed), self.min_speed)
        calculated_pw = self.calc_pw(speed=speed)
        self.set_pw(pulse_width=calculated_pw)

    def stop(self):  # stops the motor
        pulse_width = (self.min_pw + self.max_pw) / 2
        self.set_pw(pulse_width=pulse_width)

    def max_backward(self):  # moves the motor backward
        self.set_pw(self.max_pw)

    def max_forward(self):  # forward motion of the motor
        self.set_pw(self.min_pw)

    def max_left(self):  # max left turn for the motor (90 degrees)
        self.set_pw(self.max_pulsewidth)

    def max_right(self):  # max right turn for the motor (90 degrees)
        self.set_pw(self.min_pulsewidth)

    def set_position(self, degree):
        degree = max(min(self.max_degree, degree), self.min_degree)
        calculated_pw = self.calc_pw(degree=degree)
        self.set_pw(pulse_width=calculated_pw)

pi = pigpio.pi()

def main():
    left_servo = Servo_write(pi=pi, gpio=23)
    left_servo.set_position(-60)
    time.sleep(1)
    left_servo.stop()
    pi.stop()

if __name__ == "__main__":
    main()
