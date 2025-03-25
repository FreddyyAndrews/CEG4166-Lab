import RPi.GPIO as GPIO

# Set the GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# List of all possible BCM GPIO pins on Raspberry Pi 4
all_pins = [2, 3, 4, 17, 27, 22, 10, 9, 11, 5, 6, 13, 19, 26, 14, 15, 18, 23, 24, 25, 8, 7, 12, 16, 20, 21]

try:
    # Initialize available pins list
    available_pins = []
    
    # Set up pins one by one
    for pin in all_pins:
        try:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
            available_pins.append(pin)
            print(f"Pin {pin} set to LOW")
        except Exception as e:
            print(f"Could not set pin {pin}: {e}")
    
    print(f"\nAll available pins ({len(available_pins)}) have been turned OFF")
    print(f"Available pins: {available_pins}")

finally:
    # Clean up GPIO settings
    GPIO.cleanup()
    print("GPIO cleanup complete") 