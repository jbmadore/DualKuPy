"""
lcd_display.py
Handles the initialization and operation of the LCD screen.
"""

import spidev
import RPi.GPIO as GPIO
import time
from PIL import Image, ImageDraw, ImageFont
from radar.radar import init_radar # Import radar connection function
import subprocess
import socket


# === GPIO Pin Definitions for LCD ===
CS = 8       # Chip Select
RESET = 25   # Reset Pin
A0 = 24      # Data/Command Select

# === SPI Initialization ===
spi = spidev.SpiDev()


def get_ip_address():
    """
    Retrieves the Raspberry Pi's IP address on the network.
    
    Returns:
        str: The detected IP address, or None if no connection is found.
    """
    try:
        ip = subprocess.check_output("hostname -I", shell=True).decode().strip().split()
        return ip if ip else None
    except Exception as e:
        print(f"Error getting IP: {e}")
        return None


# def get_ip_addresses():
#     """Returns a list of IP addresses assigned to the Raspberry Pi."""
#     import netifaces
#     ip_list = []
#     interfaces = netifaces.interfaces()
# 
#     for interface in interfaces:
#         addrs = netifaces.ifaddresses(interface)
#         if netifaces.AF_INET in addrs:
#             for addr in addrs[netifaces.AF_INET]:
#                 ip_list.append(addr['addr'])
#     
#     return ip_list

def detect_connection():
    """
    Tries for up to 10 seconds to detect if a radar or computer is connected
    by checking the assigned IP addresses.
    """
    is_radar_connected = False
    is_computer_connected = False
    timeout = 10  # Maximum waiting time in seconds
    start_time = time.time()

    while time.time() - start_time < timeout:
        ip_addresses = get_ip_address()

        if ip_addresses:
            for ip in ip_addresses:
                if ip.startswith("192.168.0."):
                    #if ip in ["192.168.0.13", "192.168.0.17"]:
                    if "192.168.0.101" in ip:
                        is_radar_connected = True
                    else:
                        is_computer_connected = True

        if is_radar_connected or is_computer_connected:
            break  # Stop checking if an IP is found

        time.sleep(1)  # Wait 1 second before checking again

    return is_radar_connected, is_computer_connected

# === Function to Initialize the LCD Display ===
def init_display():
    """
    Initializes the LCD display by configuring the GPIO pins and sending initialization commands.
    """
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(CS, GPIO.OUT)
    GPIO.setup(RESET, GPIO.OUT)
    GPIO.setup(A0, GPIO.OUT)

    spi.open(0, 0)
    spi.max_speed_hz = 1000000  # Set SPI speed to 1 MHz

    # Reset the display and send initialization commands
    reset_display()
    send_command(0xA0)  # Segment direction
    send_command(0xA2)  # LCD Bias
    send_command(0xC8)  # COM direction
    send_command(0x2F)  # Power control
    send_command(0x26)  # Resistor ratio
    send_command(0x81)  # Contrast
    send_command(0x11)  # Contrast value
    send_command(0xAF)  # Display ON


# === Function to Reset the LCD Display ===
def reset_display():
    """
    Resets the LCD display by toggling the RESET pin.
    """
    GPIO.output(RESET, GPIO.LOW)
    time.sleep(0.1)
    GPIO.output(RESET, GPIO.HIGH)


# === Function to Send a Command to the LCD ===
def send_command(cmd):
    """
    Sends a command byte to the LCD.
    
    Args:
        cmd (int): The command byte to be sent.
    """
    GPIO.output(A0, GPIO.LOW)  # Set to command mode
    GPIO.output(CS, GPIO.LOW)
    spi.xfer([cmd])
    GPIO.output(CS, GPIO.HIGH)


# === Function to Send Data to the LCD ===
def send_data(data):
    """
    Sends a data byte to the LCD.
    
    Args:
        data (int): The data byte to be sent.
    """
    GPIO.output(A0, GPIO.HIGH)  # Set to data mode
    GPIO.output(CS, GPIO.LOW)
    spi.xfer([data])
    GPIO.output(CS, GPIO.HIGH)


def display_welcome_screen():
    """
    Displays a welcome screen while checking network status and radar connections.
    """
    try:
        logo = Image.open("logo.png").convert('1')
    except FileNotFoundError:
        print("Error: 'logo.png' file not found!")
        logo = Image.new('1', (64, 128), 1)

    image = Image.new('1', (128, 64), 1)
    image.paste(logo, (0, 0))

    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    small_font = ImageFont.truetype(font_path, 7) 

    # Initial message
    draw.text((50, 5), "Booting...", font=small_font, fill=0)
    draw.text((50, 20), "Checking network...", font=small_font, fill=0)
    display_image(image)

    time.sleep(10)  # Allow time for network setup

    # Get the Raspberry Pi's current IP
#     ip_addresses = get_ip_address()
#     is_computer_connected = False
#     is_radar_connected = False
# 
#     if ip_addresses:
#         for ip in ip_addresses:
#             if ip.startswith("192.168.0."):
#                 if ip in ["192.168.0.13", "192.168.0.17"]:
#                     is_radar_connected = True
#                 else:
#                     is_computer_connected = True

    draw.rectangle((50, 20, 128, 64), fill=1)  # Clear previous message

#     if is_computer_connected:
#         draw.text((50, 20), "Computer found!", font=small_font, fill=0)
#         draw.text((50, 35), "Skipping radar...", font=small_font, fill=0)
#         display_image(image)
#         time.sleep(2)
# 
#         radar1_ip = "192.168.0.13"
#         radar2_ip = "192.168.0.17"
# 
#         com1, cmd1, ok1 = init_radar(radar1_ip, host_port=4100)
#         com2, cmd2, ok2 = init_radar(radar2_ip, host_port=4101)
#     
#         return (com1, cmd1, ok1), (com2, cmd2, ok2)
#     elif is_radar_connected:
#         draw.text((50, 20), "Radar detected!", font=small_font, fill=0)
#         draw.text((50, 35), "Applying routes...", font=small_font, fill=0)
#         display_image(image)
# 
#         # Apply routing for radars
#         subprocess.run("sudo ip route add 192.168.0.17 via 192.168.0.100 dev eth0", shell=True)
#         subprocess.run("sudo ip route add 192.168.0.13 via 192.168.0.101 dev eth1", shell=True)
#     else:
#         draw.text((50, 20), "No network detected", font=small_font, fill=0)
#         draw.text((50, 35), "Check connections", font=small_font, fill=0)


    radar_connected, computer_connected = detect_connection()

    if radar_connected:
        draw.text((50, 20), "Radar detected!", font=small_font, fill=0)
        draw.text((50, 35), "Applying routes...", font=small_font, fill=0)
        display_image(image)

        # Apply routing for radars
        #subprocess.run("sudo ip route add 192.168.0.17 via 192.168.0.100 dev eth0", shell=True)
        #subprocess.run("sudo ip route add 192.168.0.17 via 192.168.0.100 dev eth0", shell=True)

        subprocess.run("sudo ip route add 192.168.0.17 via 192.168.0.101 dev eth1", shell=True)
        # Add routing commands
    elif computer_connected:
        draw.text((50, 20), "Computer found!", font=small_font, fill=0)
        draw.text((50, 35), "Skipping radar...", font=small_font, fill=0)
        display_image(image)
        time.sleep(2)

        radar1_ip = "192.168.0.13"
        radar2_ip = "192.168.0.17"

        com1, cmd1, ok1 = init_radar(radar1_ip, host_port=4100)
        com2, cmd2, ok2 = init_radar(radar2_ip, host_port=4101)
    
        return (com1, cmd1, ok1), (com2, cmd2, ok2)
    else:
        print("No network device detected.")


    display_image(image)
    time.sleep(2)

    # Radar connection routine
    draw.rectangle((50, 20, 128, 64), fill=1)
    draw.text((50, 20), "Testing radars...", font=small_font, fill=0)
    display_image(image)

    radar1_ip = "192.168.0.13"
    radar2_ip = "192.168.0.17"

    com1, cmd1, ok1 = init_radar(radar1_ip, host_port=4100)
    com2, cmd2, ok2 = init_radar(radar2_ip, host_port=4101)
    print(com1)
    print(cmd2)
    print(ok1)

    attempts = 0
    while not (ok1 or ok2) and attempts < 5:
        draw.rectangle((50, 20, 128, 64), fill=1)
        draw.text((50, 20), f"Retry {attempts+1}/5", font=small_font, fill=0)
        display_image(image)
        time.sleep(3)

        com1, cmd1, ok1 = init_radar(radar1_ip, host_port=4100)
        com2, cmd2, ok2 = init_radar(radar2_ip, host_port=4101)
        attempts += 1

    draw.rectangle((50, 20, 128, 64), fill=1)
    draw.text((50, 20), "Radar Status:", font=font, fill=0)

    if ok1:
        draw.text((50, 35), "13GHz: Connected", font=font, fill=0)
    else:
        draw.text((50, 35), "13GHz: Failed", font=font, fill=0)

    if ok2:
        draw.text((50, 45), "17GHz: Connected", font=font, fill=0)
    else:
        draw.text((50, 45), "17GHz: Failed", font=font, fill=0)

    if ok1 and ok2:
        draw.text((50, 55), "All connected!", font=font, fill=0)

    display_image(image)
    time.sleep(2)

    return (com1, cmd1, ok1), (com2, cmd2, ok2)

# 
# # === Function to Display the Welcome Screen ===
# def display_welcome_screen():
#     """
#     Displays a welcome screen with a logo on the left and a message on the right.
#     
#     Args:
#         message (str): The message to be displayed on the right side of the screen.
#     """
#     try:
#         # Load the logo (Ensure the image is 64x128 pixels)
#         logo = Image.open("logo.png").convert('1')
# 
#     except FileNotFoundError:
#         print("Error: 'logo.png' file not found!")
#         logo = Image.new('1', (64, 128), 1)  # Create an empty image if the logo is missing
# 
#     # Create a 128x64 image for the LCD screen
#     image = Image.new('1', (128, 64), 1)
#     image.paste(logo, (0, 0))  # Insert the logo on the left side
# 
#     # Draw the message on the right side
#     draw = ImageDraw.Draw(image)
#     font = ImageFont.load_default()
#     
#     ##### Radar routine ##########
#     # Radar IPs
#     radar1_ip = "192.168.0.13"
#     radar2_ip = "192.168.0.17"
# 
#     draw.text((50, 5), "Booting...", font=font, fill=0)
#     draw.text((50, 20), "Testing radars", font=font, fill=0)
#     display_image(image)
#     
#     # Test radar connections
#     com1, cmd1, ok1 = init_radar(radar1_ip, host_port=4100)
#     com2, cmd2, ok2 = init_radar(radar2_ip, host_port=4101)
# 
#     attempts = 0
#     while not (ok1 or ok2) and attempts < 5:  # Try 5 times max
#         draw.rectangle((50, 20, 128, 64), fill=1)  # Clear right screen
#         draw.text((50, 20), f"Retry {attempts+1}/5", font=font, fill=0)
#         display_image(image)
#         time.sleep(3)
# 
#         com1, cmd1, ok1 = init_radar(radar1_ip, host_port=4100)
#         com2, cmd2, ok2 = init_radar(radar2_ip, host_port=4101)
#         attempts += 1
# 
#     # Update display with final status
#     draw.rectangle((50, 20, 128, 64), fill=1)  # Clear previous status
#     draw.text((50, 20), "Radar Status:", font=font, fill=0)
# 
#     if ok1:
#         draw.text((50, 35), "13GHz: Connected", font=font, fill=0)
#     else:
#         draw.text((50, 35), "13GHz: Failed", font=font, fill=0)
# 
#     if ok2:
#         draw.text((50, 45), "17GHz: Connected", font=font, fill=0)
#     else:
#         draw.text((50, 45), "17GHz: Failed", font=font, fill=0)
# 
# 
# #     text_x = 70  # Offset for text placement
# #     text_y = 20  # Vertical position for message
# #     draw.text((text_x, text_y), message, font=font, fill=0)
# # 
#     # Display the welcome screen
#     display_image(image)
#     time.sleep(2)  # Pause before showing the main menu
#     return (com1, cmd1, ok1), (com2, cmd2, ok2)


# === Function to Display an Image on the LCD ===
def display_image(image):
    """
    Displays an image on the LCD screen.
    
    Args:
        image (PIL.Image): The image to be displayed.
    """
    image = image.convert('1')  # Convert to 1-bit black & white
    pixels = list(image.getdata())

    for page in range(8):  # The screen is divided into 8 pages (each page = 8 rows)
        send_command(0xB0 + page)  # Set page address
        send_command(0x10)  # Set column high nibble
        send_command(0x00)  # Set column low nibble

        for x in range(128):  # Iterate through each column
            byte = 0
            for bit in range(8):  # Pack 8 pixels into a byte
                if pixels[(page * 8 + bit) * 128 + x] == 0:
                    byte |= (1 << bit)
            send_data(byte)

