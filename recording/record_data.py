import threading


recording_lock = threading.Lock()

def gather_recording_info():
    """Prompt the user once and return recording info as a dictionary."""
    site_name = input("Enter the site name: ")
    radar_angle = input("Enter the radar angle: ")
    polarization = input("Enter the measurement polarization (vertical or horizontal): ")
    return {
        "site_name": site_name,
        "radar_angle": radar_angle,
        "polarization": polarization
    }

def start_recording(radar_option, recording_info):
    """Records data using pre-defined recording info."""
    with recording_lock:
        # Use the passed-in recording info for each measurement
        radar_option["site_name"] = recording_info["site_name"]
        radar_option["radar_angle"] = recording_info["radar_angle"]
        radar_option["polarization"] = recording_info["polarization"]

        print(f"Recording data for radar {radar_option['measure_id']} at site {radar_option['site_name']} "
              f"with angle {radar_option['radar_angle']} and polarization {radar_option['polarization']}...")
        
        # Call record_measurement (or replace with actual recording function)
        record_measurement(num_records=50, foldername="./", measure_number=1, options=radar_option)
        print("Recording complete.")
