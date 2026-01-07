import os
import time
import RPi.GPIO as GPIO
from datetime import datetime

from radar.radar import init_radar, close_radar
from data_io.file_writer import record_measurement

# Number of records per measurement
N_RECORD = 150
# Solid State Relay pin for radar power control
SSR_PIN = 17  # GPIO17 = pin physique 11
# Data storage paths
USB_DATA_PATH = "/mnt/dualku-usb"
LOCAL_DATA_PATH = "/home/grimp/data/dualku_tower/"


def main():
    """Main daemon loop - runs a measurement sequence every hour."""
    print(f"[{datetime.now()}] Starting measurement daemon...")

    while True:
        try:
            run_measurement_routine()
            now = datetime.now()
            seconds_to_next_hour = (
                3600 - now.minute * 60 - now.second
            )
            print(
                f"[{datetime.now()}] Sleeping for "
                f"{seconds_to_next_hour} s..."
            )
            time.sleep(seconds_to_next_hour)
        except KeyboardInterrupt:
            print(f"\n[{datetime.now()}] Daemon stopped by user.")
            break
        except Exception as e:
            print(f"[{datetime.now()}] Error during measurement: {e}")
            now = datetime.now()
            seconds_to_next_hour = (
                3600 - now.minute * 60 - now.second
            )
            print(
                f"[{datetime.now()}] Sleeping for "
                f"{seconds_to_next_hour} s..."
            )
            time.sleep(seconds_to_next_hour)


def ssr_setup():
    '''
    Initiate Solid State Relay (SSR) to control radar power.
    Set to OFF by default.
    '''
    GPIO.setmode(GPIO.BCM)
    # SSR OFF par défaut au démarrage
    GPIO.setup(SSR_PIN, GPIO.OUT, initial=GPIO.LOW)


def swith_ssr_on():
    '''
    Switches the SSR to ON and sleeps for 10 seconds to allow radars to
    power up.
    '''
    GPIO.output(SSR_PIN, GPIO.HIGH)
    time.sleep(10)


def switch_ssr_off():
    GPIO.output(SSR_PIN, GPIO.LOW)
    GPIO.cleanup()


def run_measurement_routine():
    '''Connects the radar, and perfoms a measurment for each polarization,
    at the given set of angles'''
    # Power up the radars
    ssr_setup()
    swith_ssr_on()

    # Define radar IPs and ports
    radar1_ip = '192.168.0.13'
    radar2_ip = '192.168.0.17'
    radar1_host_port = 4100
    radar2_host_port = 4101

    # Connect and initialize each radar
    com1, cmd1, ok1 = init_radar(radar1_ip, host_port=radar1_host_port)
    com2, cmd2, ok2 = init_radar(radar2_ip, host_port=radar2_host_port)

    # Check each radar's connection status and print the IP of connected radars
    try:
        radar_connection_sanity_check(ok1, ok2, radar1_ip, radar2_ip)
    except Exception as e:
        print(e)
        switch_ssr_off()
        return

    # Get experiment parameters and launch measurement sequence
    print("Acquiring experiment parameters...")
    exp_params = get_experiment_parameters()
    print("Experiment parameters acquired. \nStarting measurement sequence...")
    perform_measurement_sequence(exp_params, [cmd1, cmd2])
    print("Measurement sequence completed. \nClosing radars...")
    # Close both radar connections
    for com in [com1, com2]:
        close_radar(com)
    print("Radars closed. \nSwitching off SSR...")
    switch_ssr_off()


def radar_connection_sanity_check(ok1, ok2, radar1_ip, radar2_ip):
    '''Checks if the radars are connected properly'''
    if ok1 and ok2:
        print(f"Radar 13GHz connected at IP address {radar1_ip}")
        print(f"Radar 17GHz connected at IP address {radar2_ip}")

    elif ok1 and not ok2:
        print(f"Radar 13GHz connected at IP address {radar1_ip}")
        print(f"Failed 17GHz to connect radar at IP address {radar2_ip}")

    elif ok2 and not ok1:
        print(f"Radar 17GHz connected at IP address {radar2_ip}")
        print(f"Failed 13GHz to connect radar at IP address {radar1_ip}")
    else:
        raise Exception("Failed to initialize both radars. Exiting...")


def get_experiment_parameters(exp_params_file="experiment_params.env"):
    """Get recording metadata from the experiment parameters file."""
    with open(exp_params_file, 'r') as f:
        lines = f.readlines()

    params = {}
    for line in lines:
        key, value = line.strip().split('=')
        params[key] = value

    return params


def perform_measurement_sequence(exp_params, commands):
    """
    Perform a measurement sequence for the given set of radars.
    Args:
        exp_params (dict): Experiment parameters including site name, radar
                           angle, polarization, etc.
        commands (list): List of radar command objects.
    """
    for cmd in commands:
        measurement_params = {
            "site_name": exp_params['SITE_NAME'],
            "radar_angle": exp_params['RADAR_ANGLE'],
            "polarization": exp_params['POLARIZATION'],
            "cmd": cmd
        }

        # Check if USB key is mounted, otherwise use local storage
        if os.path.exists(USB_DATA_PATH):
            data_path = USB_DATA_PATH
            print(f"Using USB storage: {data_path}")
        else:
            data_path = LOCAL_DATA_PATH
            print(f"USB not found, using local storage: {data_path}")

        print(f"Starting measurement: {cmd}")
        record_measurement(
            num_records=N_RECORD, foldername=data_path,
            measure_number=1, options=measurement_params
        )
        print(f"Completed measurement: {cmd}")


# Run main
if __name__ == "__main__":
    main()
