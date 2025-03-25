import time
import RPi.GPIO as GPIO
import pigpio
from hcsr04 import HCSR04
from motor_control import Motor_control
import threading
from maze_visualization import start_visualization
from sonar_sensor import MoveRight, MoveCenter, MoveLeft, sensor, samples

# Initialize GPIO mode
GPIO.setwarnings(False)

# Define obstacle detection threshold (in cm)
OBSTACLE_THRESHOLD = 15
MIN_SAFE_DISTANCE = 20

# Define movement speeds (0-255)
FORWARD_SPEED = 20
TURN_SPEED = 40
TURN_DURATION = 0.6  # Increased from 0.35 to ensure full 90-degree rotation

# Initialize motor controller
pi = pigpio.pi()
mc = Motor_control(pi=pi)

# Visualization object (will be initialized later)
viz = None
root = None

def measure_distance():
    """Measure distance using the sonar sensor"""
    # Take multiple readings for stability
    readings = []
    for _ in range(3):
        reading = sensor.measure(samples, "cm")
        readings.append(reading)
        time.sleep(0.05)
    
    # Filter out extreme values
    readings.sort()
    if len(readings) >= 3:
        # Use median value
        distance = readings[len(readings)//2]
    else:
        # Use the average if we don't have enough readings
        distance = sum(readings) / len(readings)
    
    print(f"Distance: {distance} cm")
    
    # Update visualization if available
    if viz:
        viz.add_update('distance', distance)
    
    return distance


def move_forward():
    """Move the robot forward"""
    print("Moving forward...")
    mc.straight(FORWARD_SPEED)
    
    # Update visualization if available
    if viz:
        viz.add_update('status', 'Moving forward')
        viz.add_update('move', 'forward')

def stop():
    """Stop the robot"""
    print("Stopping...")
    mc.straight(0)
    
    # Update visualization if available
    if viz:
        viz.add_update('status', 'Stopped')

def rotate_right():
    """Rotate the robot to the right"""
    print("Obstacle detected! Rotating right...")
    
    # Update visualization if available
    if viz:
        viz.add_update('status', 'Turning right')
        viz.add_update('move', 'right')
    
    mc.turn_right(TURN_SPEED)
    time.sleep(TURN_DURATION)  # Using defined duration for 90 degrees
    stop()

def rotate_left():
    """Rotate the robot to the left"""
    print("Obstacle still detected! Rotating left...")
    
    # Update visualization if available
    if viz:
        viz.add_update('status', 'Turning left')
        viz.add_update('move', 'left')
    
    mc.turn_left(TURN_SPEED)
    time.sleep(TURN_DURATION)  # Using defined duration for 90 degrees
    stop()

def autonomous_drive():
    """Main function for autonomous driving with maze-solving capabilities"""
    try:
        print("Starting autonomous driving mode...")
        # Update visualization if available
        if viz:
            viz.add_update('status', 'Starting autonomous driving')
        
        time.sleep(0.5)  # Initial stabilization time
        
        while True:
            # Check forward distance first to see if path is clear
            forward_distance = measure_distance()
            
            # If we can move forward safely without scanning
            if forward_distance > MIN_SAFE_DISTANCE:
                move_forward()
                # Move for a short time, then check again
                time.sleep(0.5)  # Increased from 0.3 to slow down overall movement
                # Briefly stop to get more accurate readings
                stop()
                time.sleep(0.1)
            else:
                # Need to scan and decide
                stop()
                time.sleep(0.2)  # Ensure we've fully stopped
                
                # If we detected an obstacle, mark it in the visualization
                if forward_distance <= OBSTACLE_THRESHOLD and viz:
                    viz.add_update('obstacle', None)
                    
                    # First turn right
                    rotate_right()
                    time.sleep(0.3)  # Wait for rotation to complete
                    
                    # Check if there's an obstacle after turning right
                    right_distance = measure_distance()
                    if right_distance <= OBSTACLE_THRESHOLD:
                        # If obstacle detected after right turn, do 180-degree turn to the left
                        print("Obstacle detected after right turn, turning 180 degrees left...")
                        if viz:
                            viz.add_update('status', 'Turning 180 degrees left')
                        mc.turn_left(TURN_SPEED)
                        time.sleep(TURN_DURATION * 2)  # Double duration for 180 degrees
                        stop()
                        time.sleep(0.3)  # Wait for rotation to complete
                    else:
                        # If no obstacle after right turn, continue in that direction
                        move_forward()
                        time.sleep(0.3)
                        stop()
                
            time.sleep(0.2)  # Small delay for stability
            
    except KeyboardInterrupt:
        # Clean shutdown on keyboard interrupt
        print("Autonomous driving stopped by user")
    finally:
        # Clean up
        stop()
        mc.servo_l.stop()
        mc.servo_r.stop()
        pi.stop()
        
        # Stop visualization if it's running
        if viz:
            viz.stop()
        
        GPIO.cleanup()
        print("Resources cleaned up")

def start_gui_thread():
    """Start the GUI in a separate thread"""
    global viz, root
    viz, root = start_visualization()
    
    # Start the Tkinter main loop
    # We must use after() here to check for exit condition
    # since mainloop() will block this thread
    def check_exit():
        if not getattr(threading.current_thread(), "running", True):
            root.quit()
        else:
            root.after(100, check_exit)
    
    root.after(100, check_exit)
    root.mainloop()

if __name__ == "__main__":
    print("Autonomous driving program starting...")
    print(f"Obstacle detection threshold: {OBSTACLE_THRESHOLD} cm")
    
    # Create and start GUI thread with proper daemon status
    gui_thread = threading.Thread(target=start_gui_thread)
    gui_thread.daemon = True
    setattr(gui_thread, "running", True)
    gui_thread.start()
    
    # Give the GUI time to initialize
    time.sleep(2)
    
    try:
        # Start autonomous driving
        autonomous_drive()
    except Exception as e:
        print(f"Error in autonomous driving: {e}")
    finally:
        # Make sure to clean up even if autonomous_drive doesn't
        if gui_thread.is_alive():
            setattr(gui_thread, "running", False)
            time.sleep(0.5)  # Give thread time to exit 