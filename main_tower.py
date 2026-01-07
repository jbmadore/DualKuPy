import time
from datetime import datetime

from radar.radar import init_radar, close_radar
from data_io.file_writer import record_measurement

N_RECORD = 150
MEASUREMENT_INTERVAL_SECONDS = 3600


def main():
    """Main daemon loop - runs a measurement sequence every hour."""
    print(f"[{datetime.now()}] Starting measurement daemon...")

    while True:
        try:
            run_measurement_routine()
            print(
                f"[{datetime.now()}] Sleeping for "
                f"{MEASUREMENT_INTERVAL_SECONDS} s..."
            )
            time.sleep(MEASUREMENT_INTERVAL_SECONDS)
        except KeyboardInterrupt:
            print(f"\n[{datetime.now()}] Daemon stopped by user.")
            break
        except Exception as e:
            print(f"[{datetime.now()}] Error during measurement: {e}")
            time.sleep(MEASUREMENT_INTERVAL_SECONDS)


def run_measurement_routine():
    '''Connects the radar, and perfoms a measurment for each polarization,
    at the given set of angles'''
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
        return

    # Get experiment parameters and launch measurement sequence
    print("Acquiring experiment parameters...")
    exp_params = get_experiment_parameters()
    print("Experiment parameters acquired. Starting measurement sequence...")
    perform_measurement_sequence(exp_params, [cmd1, cmd2])
    print("Measurement sequence completed. Closing radars...")
    # Close both radar connections
    for com in [com1, com2]:
        close_radar(com)
    print("Radars closed. Going to sleep for 1 hour...")


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
        if value.startswith('['):
            params[key] = value.strip("[]").split(',')
        else:
            params[key] = value

    return params


def perform_measurement_sequence(exp_params, commands):
    """
    Perform a measurement sequence for the given set of polarizations and
    radars.
    Args:
        exp_params (dict): Experiment parameters including site name, radar
                           angle, polarization, etc.
        commands (list): List of radar command objects.
    """

    for pol in exp_params['POLARIZATION']:
        # Take measurements for both radars
        for cmd in commands:
            measurement_params = {
                "site_name": exp_params['SITE_NAME'],
                "radar_angle": exp_params['RADAR_ANGLE'],
                "polarization": pol,
                "cmd": cmd
            }
            print(f"Starting measurement: {cmd} at polarization {pol}")
            record_measurement(
                num_records=N_RECORD, foldername="./data/",
                measure_number=1, options=measurement_params
            )
            print(f"Completed measurement: {cmd} at polarization {pol}")


# Run main
if __name__ == "__main__":
    main()
