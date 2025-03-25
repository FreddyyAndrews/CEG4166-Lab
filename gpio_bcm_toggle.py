import RPi.GPIO as GPIO
import time
import sys
import select
import termios
import tty

# Set the GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# List of GPIO pins to control
all_pins = [2, 3, 4, 17, 27, 22, 10, 9, 11, 5, 6, 13, 19, 26, 14, 15, 18, 23, 24, 25, 8, 7, 12, 16, 20, 21]
available_pins = []

# Function to check if a key has been pressed
def is_key_pressed():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

# Function to get the pressed key
def get_key():
    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())
        if is_key_pressed():
            return sys.stdin.read(1)
        else:
            return None
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

# Function to turn off all pins
def turn_off_all_pins():
    for pin in available_pins:
        GPIO.output(pin, GPIO.LOW)
    print("\nAll pins have been turned OFF")

try:
    # Set terminal to raw mode to capture keypresses without Enter
    old_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())
    
    # Set up pins one by one
    for pin in all_pins:
        try:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
            print(f"Pin {pin} set up successfully")
            available_pins.append(pin)  # Add to available pins list
        except Exception as e:
            print(f"Failed to set up pin {pin}: {e}")
    
    print(f"\nTotal available pins: {len(available_pins)}")
    print(f"Available pins: {available_pins}")
    print("Press 'S' at any time to shut down all pins\n")
    
    # Iterate through each available pin
    for pin in available_pins:
        # Turn on the current pin
        GPIO.output(pin, GPIO.HIGH)
        
        # Print the current pin
        print(f"Current pin: {pin} is ON")
        
        # Wait for a short period, checking for keypress
        start_time = time.time()
        while time.time() - start_time < 1:
            key = get_key()
            if key and key.upper() == 'S':
                turn_off_all_pins()
                print("Program terminated by user")
                GPIO.cleanup()
                sys.exit(0)
            time.sleep(0.1)
        
        # Turn off the current pin
        GPIO.output(pin, GPIO.LOW)
        print(f"Pin {pin} turned OFF")
        
        # Small delay between pins, still checking for keypress
        start_time = time.time()
        while time.time() - start_time < 0.3:
            key = get_key()
            if key and key.upper() == 'S':
                turn_off_all_pins()
                print("Program terminated by user")
                GPIO.cleanup()
                sys.exit(0)
            time.sleep(0.1)

finally:
    # Restore terminal settings
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    # Clean up GPIO settings
    GPIO.cleanup() 