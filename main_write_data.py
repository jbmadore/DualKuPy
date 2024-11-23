import threading
import time
from radar.radar import init_radar, fetch_radar_data, close_radar
from plotting.plotting import init_plot, update_plot, update_record_plot
import matplotlib.pyplot as plt
from data_io.file_writer import record_measurement
from queue import Queue
from datetime import datetime

# Set the metadata for the measurement here
num_record_=150
site_name = ''
radar_angle = ''
polarization = ''
measure_id = ''
additional_info = ''
foldername = '' # put the / at the end!
    
    
def main():

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
        
    data1 = fetch_radar_data(cmd1)
    data2 = fetch_radar_data(cmd2)

    recoring_info  =      {
        "site_name": site_name,
        "radar_angle": radar_angle,
        "polarization": polarization,
        "measure_id": measure_id,
        "additional_info": additional_info
    }
    options_1 = {
    "cmd": cmd1,
    "site_name": '',  # Placeholder values
    "measure_id": '',
    "polarization": '',
    "additional_info": ""
    }
    options_2 = {
        "cmd": cmd2,
        "site_name": '',  # Placeholder values
        "measure_id": '',
        "polarization": '',
        "additional_info": ""
    }
    options_1.update(recording_info)
    options_2.update(recording_info)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename_13GHz = f"{site_name}_13GHz_{timestamp}.txt"
    filename_17GHz = f"{site_name}_17GHz_{timestamp}.txt"

    record_measurement(num_records=num_record_, fullname=foldername + filename_13GHz, measure_number=1, options=options_1)
    record_measurement(num_records=num_record_, fullname=foldername + filename_17GHz, measure_number=1, options=options_2)

# Run main
if __name__ == "__main__":
    main()
