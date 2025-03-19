"""
buttons.py
Handles button inputs for menu navigation.
"""

import RPi.GPIO as GPIO
import time

# === Button Pin Definitions ===
BTN_UP = 17
BTN_DOWN = 27
BTN_OK = 22
BTN_CANCEL = 23


# === Function to Initialize Buttons ===
def init_buttons():
    """
    Configures the buttons as inputs with pull-up resistors.
    """
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BTN_UP, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BTN_DOWN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BTN_OK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BTN_CANCEL, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# === Function to Wait for a Button Press ===
def wait_for_button(timeout=None):
    """Waits for a button press with an optional timeout.

    Args:
        timeout (float, optional): Time in seconds to wait before returning None.

    Returns:
        str: "UP", "DOWN", "OK", "CANCEL", or None if timed out.
    """
    start_time = time.time()
    
    while True:
        if GPIO.input(BTN_UP) == GPIO.LOW:
            time.sleep(0.1)  # Debounce
            while GPIO.input(BTN_UP) == GPIO.LOW:
                pass  # Wait until button is released
            return "UP"

        if GPIO.input(BTN_DOWN) == GPIO.LOW:
            time.sleep(0.1)
            while GPIO.input(BTN_DOWN) == GPIO.LOW:
                pass
            return "DOWN"

        if GPIO.input(BTN_OK) == GPIO.LOW:
            time.sleep(0.1)
            while GPIO.input(BTN_OK) == GPIO.LOW:
                pass
            return "OK"

        if GPIO.input(BTN_CANCEL) == GPIO.LOW:
            time.sleep(0.1)
            while GPIO.input(BTN_CANCEL) == GPIO.LOW:
                pass
            return "CANCEL"
        
        if timeout and (time.time() - start_time) >= timeout:
            return None  # Timeout reached, no button was pressed

        time.sleep(0.1)  # Prevent excessive CPU usage
