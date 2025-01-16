import argparse
import json
import time
from datetime import datetime, timedelta
from radar.radar import init_radar, fetch_radar_data, close_radar
from data_io.file_writer import record_measurement


def load_config(config_file):
    """Load recording configuration from a JSON file."""
    try:
        with open(config_file, 'r') as file:
            config = json.load(file)
        return config
    except Exception as e:
        print(f"Error loading config file: {e}")
        exit(1)


def parse_time(time_str, label):
    """Parse start or stop time from a string."""
    try:
        return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S") if time_str else None
    except ValueError:
        print(f"Invalid date format for {label}. Use 'YYYY-MM-DD HH:MM:SS'.")
        exit(1)


def wait_until_start_time(start_time):
    """Wait until the start time."""
    if start_time:
        now = datetime.now()
        if now < start_time:
            wait_seconds = (start_time - now).total_seconds()
            print(f"Waiting {wait_seconds:.2f} seconds until the start time: {start_time}.")
            time.sleep(wait_seconds)


def wait_until_next_interval(interval_minutes):
    """Wait until the next interval."""
    now = datetime.now()
    next_minute = (now.minute // interval_minutes + 1) * interval_minutes
    if next_minute >= 60:
        # Move to the next hour
        next_minute %= 60
        now = now + timedelta(hours=1)

    target_time = now.replace(minute=next_minute, second=0, microsecond=0)
    time_to_wait = (target_time - datetime.now()).total_seconds()
    print(f"Waiting for {time_to_wait:.2f} seconds until the next interval at {target_time.strftime('%H:%M:%S')}.")
    time.sleep(max(0, time_to_wait))


def main(config_file):
    """Main function to execute the radar recording script."""
    # Load recording information from the provided config file
    config = load_config(config_file)

    # Extract metadata from the config file
    num_record_ = config.get("num_records", 150)
    site_name = config.get("site_name", "default_site")
    radar_angle = config.get("radar_angle", "default_angle")
    polarization = config.get("polarization", "default_polarization")
    measure_id = config.get("measure_id", "default_measure_id")
    additional_info = config.get("additional_info", "default_info")
    foldername = config.get("foldername", "./")  # Ensure it ends with a '/'
    interval_minutes = config.get("interval_minutes", 15)
    start_time = parse_time(config.get("start_time"), "start_time")
    stop_time = parse_time(config.get("stop_time"), "stop_time")

    # Wait until the start time
    wait_until_start_time(start_time)

    # Define radar IPs and ports
    radar1_ip = '192.168.0.13'
    radar2_ip = '192.168.0.17'
    radar1_host_port = 4100
    radar2_host_port = 4101

    # Initialize each radar
    com1, cmd1, ok1 = init_radar(radar1_ip, host_port=radar1_host_port)
    com2, cmd2, ok2 = init_radar(radar2_ip, host_port=radar2_host_port)

    # Check each radar's connection status and print the IP of connected radars
    if ok1 and ok2:
        print(f"Radar 13GHz connected at IP address {radar1_ip}")
        print(f"Radar 17GHz connected at IP address {radar2_ip}")

    recording_info = {
        "site_name": site_name,
        "radar_angle": radar_angle,
        "polarization": polarization,
        "measure_id": measure_id,
        "additional_info": additional_info
    }
    options_1 = {"cmd": cmd1}
    options_2 = {"cmd": cmd2}
    options_1.update(recording_info)
    options_2.update(recording_info)


    # Fetch data
    data1 = fetch_radar_data(cmd1)
    data2 = fetch_radar_data(cmd2)

    # Generate filenames with timestamps
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename_13GHz = f"{site_name}_13GHz_{timestamp}.txt"
    filename_17GHz = f"{site_name}_17GHz_{timestamp}.txt"

    # Record data
    record_measurement(num_records=num_record_, fullname=foldername + filename_13GHz, measure_number=1, options=options_1)
    record_measurement(num_records=num_record_, fullname=foldername + filename_17GHz, measure_number=1, options=options_2)




if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Radar Recording Script with Configurable Parameters")
    parser.add_argument(
        "config_file",
        type=str,
        help="Path to the configuration JSON file containing recording info."
    )
    args = parser.parse_args()

    # Run the main function with the provided config file
    main(args.config_file)
