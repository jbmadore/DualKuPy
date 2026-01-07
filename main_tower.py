from radar.radar import init_radar, close_radar
from data_io.file_writer import record_measurement

num_record_ = 150


def main():
    # ToDo: Add timing control for measurements
    # Read measurement configuration from file, not user input

    # Run measurement
    run_measurement()


def run_measurement():
    '''Connects the radar, and perfoms a measurment for each polarization,
    at the given set of angles'''
    # Connect the radars
    # Define radar IPs and ports
    radar1_ip = '192.168.0.13'
    radar2_ip = '192.168.0.17'
    radar1_host_port = 4100
    radar2_host_port = 4101

    # Initialize each radar
    com1, cmd1, ok1 = init_radar(radar1_ip, host_port=radar1_host_port)
    com2, cmd2, ok2 = init_radar(radar2_ip, host_port=radar2_host_port)

    # Check each radar's connection status and print the IP of connected radars
    try:
        radar_connection_sanity_check(ok1, ok2, radar1_ip, radar2_ip)
    except Exception as e:
        print(e)
        return

    # Take measurements for both radars
    take_measurement((cmd1, cmd2), "Radar 13GHz and 17GHz")

    # Close radar connections
    close_radar(com1)
    close_radar(com2)


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


def gather_recording_info():
    """Prompt for measurement information once."""
    site_name = input("Enter the site name: ")
    measure_id = input("Enter the measure_id: ")
    radar_angle = input("Enter the radar angle: ")
    polarization = input(
        "Enter the measurement polarization (vertical or horizontal): ")
    additional_info = input("Enter comments: ")
    return {
        "site_name": site_name,
        "radar_angle": radar_angle,
        "polarization": polarization,
        "measure_id": measure_id,
        "additional_info": additional_info
    }


def take_measurement(cmd, radar_label):
    """Takes a measurement for the specified radar when paused."""
    recording_info = gather_recording_info()
    print(f"Starting measurement for {radar_label}")

    options_1 = {
        "cmd": cmd[0],
        "site_name": '',  # Placeholder values
        "measure_id": '',
        "polarization": '',
        "additional_info": ""
    }
    options_2 = {
        "cmd": cmd[1],
        "site_name": '',  # Placeholder values
        "measure_id": '',
        "polarization": '',
        "additional_info": ""
    }
    options_1.update(recording_info)
    options_2.update(recording_info)
    record_measurement(
        num_records=num_record_, foldername="./data/",
        measure_number=1, options=options_1)
    record_measurement(
        num_records=num_record_, foldername="./data/",
        measure_number=1, options=options_2)


# Run main
if __name__ == "__main__":
    main()
