import math
import statistics
import time
import pigpio
import RPi.GPIO as gpio

class Motor_control:
    # these are the fixed dimensions of the stingray
    def __init__(
        self, pi, width_robot=205, diameter_wheels=50, unitsFC=360,
        dcMin_l=27.3, dcMax_l=969.15,
        dcMin_r=27.3, dcMax_r=978.25,
        l_wheel_gpio=17, r_wheel_gpio=27,
        servo_l_gpio=23, min_pw_l=600, max_pw_l=2400, min_speed_l=-1, max_speed_l=1,
        servo_r_gpio=24, min_pw_r=600, max_pw_r=2400, min_speed_r=-1, max_speed_r=1,
        sampling_time=0.01,
        Kp_p=0.1
    ):
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
        self.l_wheel = Servo_read(pi=self.pi, gpio=l_wheel_gpio)
        self.r_wheel = Servo_read(pi=self.pi, gpio=r_wheel_gpio)
        self.servo_l = Servo_write(pi=self.pi, gpio=servo_l_gpio,
                                   min_pw=min_pw_l, max_pw=max_pw_l, min_speed=min_speed_l, max_speed=max_speed_l)
        self.servo_r = Servo_write(pi=self.pi, gpio=servo_r_gpio,
                                   min_pw=min_pw_r, max_pw=max_pw_r, min_speed=min_speed_r, max_speed=max_speed_r)
        time.sleep(1)

    def get_angle_l(self):
        angle_l = (self.unitsFC - 1) - ((self.l_wheel.read() - self.dcMin_l) * self.unitsFC) / (self.dcMax_l - self.dcMin_l + 1)
        angle_l = max(min((self.unitsFC - 1), angle_l), 0)
        return angle_l

    def get_angle_r(self):
        angle_r = (self.r_wheel.read() - self.dcMin_r) * self.unitsFC / (self.dcMax_r - self.dcMin_r + 1)
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
        if (angle < (0.25 * unitsFC)) and (prev_angle > (0.75 * unitsFC)):
            turns += 1
        # If in 1st to 4th quadrant
        elif (prev_angle < (0.25 * unitsFC)) and (angle > (0.75 * unitsFC)):
            turns -= 1

        if turns >= 0:
            total_angle = (turns * unitsFC) + angle
        else:
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

    def turn(self, degree, turning_speed=0.5):
        """
        Turn the robot by a specified number of degrees.
        Positive values turn right; negative values turn left.
        This method uses encoder feedback from the left wheel to determine when the turn is complete.

        Parameters:
        degree (float): Degrees to turn (positive for right, negative for left).
        turning_speed (float): Magnitude of turning speed (default 0.5).
        """
        if degree == 0:
            return

        # Calculate how many encoder ticks are required to achieve the desired turn.
        # arc_circle returns the arc length (in mm) the wheel must travel for the turn,
        # and tick_length returns the distance (in mm) per encoder tick.
        required_ticks = abs(self.arc_circle(degree)) / self.tick_length()

        # Get an initial encoder reading from the left wheel.
        prev_angle = self.get_angle_l()
        turns = 0
        _, initial_total = self.get_total_angle(prev_angle, self.unitsFC, prev_angle, 0)
        current_total = initial_total

        # Set wheel speeds based on the desired turning direction.
        # Note on wheel speed commands:
        #   - In this design, set_speed_l calls servo_l.set_speed(-speed).
        #   - For a right turn (degree > 0): left wheel must move forward (positive actual speed)
        #     and right wheel must move in reverse (negative actual speed).
        #   - For a left turn (degree < 0): left wheel must move in reverse (negative actual speed)
        #     and right wheel must move forward (positive actual speed).
        if degree > 0:
            # Right turn: To get left wheel forward, call set_speed_l with -turning_speed (because it inverts).
            # For right wheel, use -turning_speed to command reverse.
            self.set_speed_l(-turning_speed)
            self.set_speed_r(turning_speed)
        else:
            # Left turn: left wheel should reverse and right wheel forward.
            # Calling set_speed_l with turning_speed results in a negative actual speed (reverse) for left.
            self.set_speed_l(turning_speed)
            self.set_speed_r(-turning_speed)

        # Use a feedback loop to monitor the number of encoder ticks that have been accumulated.
        # while abs(current_total - initial_total) < required_ticks:
        #     print(f"Current total delta: {current_total - initial_total}, Required ticks: {required_ticks}")
        #     current_angle = self.get_angle_l()
        #     print(f"Current angle: {current_angle}")
        #     # Update the cumulative tick count; get_total_angle takes into account wrapping.
        #     turns, current_total = self.get_total_angle(current_angle, self.unitsFC, prev_angle, turns)
        #     print(f"Current total: {current_total}, Turns: {turns}")
        #     prev_angle = current_angle
        #     time.sleep(self.sampling_time)
        time.sleep(0.1)
        # Once the desired tick count is reached, stop both wheels.
        self.servo_l.stop()
        self.servo_r.stop()

    def straight(self, speed):
        self.set_speed_l()
        self.set_speed_r(speed)
        return None
    
class Servo_read:

    def __init__(self, pi, gpio):
        self.pi = pi
        self.gpio = gpio
        self.period = 1 / 910 * 1000000
        self.tick_high = self.compute_tick_high(tick_high=0)
        self.duty_scale = 1000
        self.pi.set_mode(gpio=self.gpio, mode=pigpio.INPUT)
        self.duty_cycle = self.compute_duty_cycle(tick_high=self.tick_high)

    def compute_tick_high(self, tick_high):
        return tick_high

    def compute_duty_cycle(self, tick_high):
        return (tick_high / self.period) * self.duty_scale

    def read(self):
        return self.duty_cycle

class Servo_write:
    # class to control the robot movements and angles
    # change the min and max pulsewidth only between (600-2400).
    def __init__(self, pi, gpio, min_pw=1280, max_pw=1720, min_speed=-1, max_speed=1, min_degree=-90, max_degree=90):
        self.pi = pi
        self.gpio = gpio
        self.min_pw = min_pw
        self.max_pw = max_pw
        self.min_speed = min_speed
        self.max_speed = max_speed
        self.min_degree = min_degree
        self.max_degree = max_degree
        
        # calculate slope for calculating the pulse width
        self.slope = (self.min_pw - ((self.min_pw + self.max_pw) / 2)) / self.max_degree
        # calculate y-offset for calculating the pulse width
        self.offset = (self.min_pw + self.max_pw) / 2

    def set_pw_speed(self, pulse_width):
        pulse_width = max(min(self.max_pw, pulse_width), self.min_pw)
        self.pi.set_servo_pulsewidth(user_gpio=self.gpio, pulsewidth=pulse_width)

    def set_pw(self, pulse_width):
        pulse_width = max(min(self.max_pw, pulse_width), self.min_degree)
        self.pi.set_servo_pulsewidth(user_gpio=self.gpio, pulsewidth=pulse_width)

    def calc_pw_speed(self, speed):
        pulse_width = self.slope * speed * 100 + self.offset
        return pulse_width

    def calc_pw(self, degree):
        pulse_width = self.slope * degree + self.offset
        return pulse_width

    def set_speed(self, speed):
        speed = max(min(self.max_speed, speed), self.min_speed)
        calculated_pw = self.calc_pw_speed(speed=speed)
        self.set_pw(pulse_width=calculated_pw)

    def stop(self):
        pulse_width = (self.min_pw + self.max_pw) / 2
        self.set_pw(pulse_width=pulse_width)

    def max_backward(self):
        self.set_pw(self.max_pw)

    def max_forward(self):
        self.set_pw(self.min_pw)

    def max_left(self):
        self.set_pw(self.max_pw)

    def max_right(self):
        self.set_pw(self.min_pw)

    def set_position(self, degree):
        degree = max(min(self.max_degree, degree), self.min_degree)
        calculated_pw = self.calc_pw(degree=degree)
        self.set_pw(pulse_width=calculated_pw)

pi = pigpio.pi()

def main():
    # Create an instance of Motor_control using the default parameters.
    motor = Motor_control(pi=pi)
    
    # Call the turn method with 90 to turn 90 degrees to the right.
    motor.turn(90)
    
    pi.stop()

if __name__ == "__main__":
    main()
