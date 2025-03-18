import RPi.GPIO as GPIO
import time

# Set the GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# List of GPIO pins to control
pins = [2, 3, 4, 17, 27, 22, 10, 9, 11, 5, 6, 13, 19, 26, 14, 15, 18, 23, 24, 25, 8, 7, 12, 16, 20, 21]

try:
    # Set all pins as output
    GPIO.setup(pins, GPIO.OUT)
    
    # Iterate through each pin
    for pin in pins:
        # Turn off all pins
        GPIO.output(pins, GPIO.LOW)
        
        # Turn on the current pin
        GPIO.output(pin, GPIO.HIGH)
        
        # Print the current pin
        print(f"Current pin: {pin}")
        
        # Wait for a short period
        time.sleep(1)
        
        # Turn off the current pin
        GPIO.output(pin, GPIO.LOW)

finally:
    # Clean up GPIO settings
    GPIO.cleanup() 