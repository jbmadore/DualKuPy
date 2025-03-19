import subprocess
import socket

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

    # Initial message
    draw.text((50, 5), "Booting...", font=font, fill=0)
    draw.text((50, 20), "Checking network...", font=font, fill=0)
    display_image(image)

    time.sleep(2)  # Allow time for network setup

    # Get the Raspberry Pi's current IP
    ip_addresses = get_ip_address()
    is_computer_connected = False
    is_radar_connected = False

    if ip_addresses:
        for ip in ip_addresses:
            if ip.startswith("192.168.0."):
                if ip in ["192.168.0.13", "192.168.0.17"]:
                    is_radar_connected = True
                else:
                    is_computer_connected = True

    draw.rectangle((50, 20, 128, 64), fill=1)  # Clear previous message

    if is_computer_connected:
        draw.text((50, 20), "Computer found!", font=font, fill=0)
        draw.text((50, 35), "Skipping routing...", font=font, fill=0)
    elif is_radar_connected:
        draw.text((50, 20), "Radar detected!", font=font, fill=0)
        draw.text((50, 35), "Applying routes...", font=font, fill=0)
        display_image(image)

        # Apply routing for radars
        subprocess.run("sudo ip route add 192.168.0.17 via 192.168.0.100 dev eth0", shell=True)
        subprocess.run("sudo ip route add 192.168.0.13 via 192.168.0.101 dev eth1", shell=True)
    else:
        draw.text((50, 20), "No network detected", font=font, fill=0)
        draw.text((50, 35), "Check connections", font=font, fill=0)

    display_image(image)
    time.sleep(2)

    # Radar connection routine
    draw.rectangle((50, 20, 128, 64), fill=1)
    draw.text((50, 20), "Testing radars...", font=font, fill=0)
    display_image(image)

    radar1_ip = "192.168.0.13"
    radar2_ip = "192.168.0.17"

    com1, cmd1, ok1 = init_radar(radar1_ip, host_port=4100)
    com2, cmd2, ok2 = init_radar(radar2_ip, host_port=4101)

    attempts = 0
    while not (ok1 or ok2) and attempts < 5:
        draw.rectangle((50, 20, 128, 64), fill=1)
        draw.text((50, 20), f"Retry {attempts+1}/5", font=font, fill=0)
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