import threading
import time
import csv
import keyboard  # Library for detecting key presses; install with `pip install keyboard`
from radar.radar import init_radar, fetch_radar_data, close_radar
from Communication import Commands
from Communication.EthernetInterfaces import EnetUdpInterface, EnetConfig
from matplotlib import pyplot as plt
from datetime import datetime
# from utils.radar_data_writer import write_header, write_pulse_to_file, record_measurement
from data_io.file_writer import record_measurement

# Flags and data containers
stop_thread = False
running = False
recording_data = False  # Flag to indicate if data is being recorded
data_records = []  # List to hold recorded data temporarily

# Initialize both radars
radar1_ip = '192.168.0.13'
radar2_ip = '192.168.0.17'
radar1_host_port = 4100
radar2_host_port = 4101

# Start both radars
com1, cmd1, ok1 = init_radar(radar1_ip, host_port=radar1_host_port)
com2, cmd2, ok2 = init_radar(radar2_ip, host_port=radar2_host_port)

if not ok1 or not ok2:
    print("Failed to initialize one or both radars.")
    exit()

# # Function to write data to CSV
# def write_data_to_csv(data_records, radar_id):
#     """
#     Writes data records to a CSV file. Each file is named with a timestamp and radar ID.
#     """
#     timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
#     filename = f"radar_{radar_id}_data_{timestamp}.csv"
    
#     # Define CSV headers, modify based on data structure
#     headers = ['timestamp', 'radar_id', 'raw_data']
    
#     with open(filename, mode='w', newline='') as file:
#         writer = csv.DictWriter(file, fieldnames=headers)
#         writer.writeheader()
        
#         # Write each data record to the CSV
#         for record in data_records:
#             writer.writerow({
#                 'timestamp': record['timestamp'],
#                 'radar_id': record['radar'],
#                 'raw_data': record['data']
#             })
    
#     print(f"Data written to {filename}")

# # Function to record raw data from one or both radars
# def record_data(num_records=50, radar=0):
#     """
#     Records `num_records` samples of raw data from the specified radar(s).
#     radar: 0 (both), 1 (radar 1), 2 (radar 2)
#     """
#     global data_records
#     data_records = []  # Reset data records for new batch
    
#     for i in range(num_records):
#         timestamp = datetime.now().isoformat()  # Record the timestamp for each sample
        
#         if radar in [0, 1]:  # Record data from radar 1 if `radar` is 0 or 1
#             data1 = cmd1.executeCmd(Commands.CMD_READ_RAW_DATA)
#             data_records.append({'timestamp': timestamp, 'radar': 1, 'data': data1})
        
#         if radar in [0, 2]:  # Record data from radar 2 if `radar` is 0 or 2
#             data2 = cmd2.executeCmd(Commands.CMD_READ_RAW_DATA)
#             data_records.append({'timestamp': timestamp, 'radar': 2, 'data': data2})

#         time.sleep(0.1)  # Small delay to prevent overloading

#     # Write the data to a CSV file
#     if radar == 0:
#         write_data_to_csv([record for record in data_records if record['radar'] == 1], radar_id=1)
#         write_data_to_csv([record for record in data_records if record['radar'] == 2], radar_id=2)
#     else:
#         write_data_to_csv(data_records, radar_id=radar)


import keyboard
import threading
import time

# Define a lock to prevent simultaneous recording sessions
recording_lock = threading.Lock()

def start_recording(radar_option):
    """Function to start recording based on radar options."""
    with recording_lock:  # Only one recording can happen at a time
        site_name = input("Enter the site name: ")
        measure_id = input("Enter the measure_id: ")
        radar_angle = input("Enter the radar angle: ")
        polarization = input("Enter the measurement polarization (vertical or horizontal): ")

        # Update radar options with user inputs
        radar_option["site_name"] = site_name
        radar_option["measure_id"] = measure_id
        radar_option["radar_angle"] = radar_angle
        radar_option["polarization"] = polarization

        print(f"Recording data from radar {radar_option['measure_id']} at site {site_name} with angle {radar_angle} and polarization {polarization}...")
        record_measurement(num_records=50, foldername="./", measure_number=1, options=radar_option)
        print("Recording complete.")

def handle_key_press(event):
    # Define options for both radars
    options_1 = {
        "cmd": cmd1,
        "site_name": 'test',  # Placeholder values
        "measure_id": '1',
        "polarization": 'Horizontal',
        "additional_info": ""
    }
    options_2 = {
        "cmd": cmd2,
        "site_name": 'test',  # Placeholder values
        "measure_id": 'test_1',
        "polarization": 'Horizontal',
        "additional_info": ""
    }

    if event.name == 'b' and not recording_lock.locked():
        # Start recording from both radars in separate threads
        threading.Thread(target=start_recording, args=(options_1,)).start()
        threading.Thread(target=start_recording, args=(options_2,)).start()

    elif event.name == '1' and not recording_lock.locked():
        # Start recording from radar 1
        threading.Thread(target=start_recording, args=(options_1,)).start()

    elif event.name == '2' and not recording_lock.locked():
        # Start recording from radar 2
        threading.Thread(target=start_recording, args=(options_2,)).start()

# Set up the key press listener
keyboard.on_press(handle_key_press)

# Main loop
try:
    while True:
        # Main processing or idle loop
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nExiting program...")



# # Key press handler to initiate recording
# def handle_key_press(event):
#     global recording_data
    
#     if recording_data:
#         return  # Exit function if already recording to prevent re-triggering



#     options_1 = {"cmd":cmd1,
#                        "site_name": 'test',
#                        "measure_id": '1',
#                         "polarization": 'Horizontal',
#                         "additional_info":""}

#     options_2 = {"cmd":cmd2,
#                         "site_name": 'test',
#                         "measure_id": 'test_1',
#                         "polarization": 'Horizontal',
#                         "additional_info":""}
            
#     # if not recording_data:
#     if event.name == 'b':  # Press 'b' to record data from both radars
#         recording_data = True
#         site_name = input("Enter the site name: ")
#         radar_angle = input("Enter the radar angle: ")
#         polarization = input("Enter the measurement polarization (vertical or horizontal): ")
        
#     # Update options with user input
#         options_1.update({"site_name": site_name, "radar_angle": radar_angle, "polarization": polarization})
#         options_2.update({"site_name": site_name, "radar_angle": radar_angle, "polarization": polarization})
        
        
#         print("Recording data from both radars...")
#         record_measurement(num_records=50, foldername="./", measure_number=1, options=options_1)
#         record_measurement(num_records=50, foldername="./", measure_number=1, options=options_2)
#         recording_data = False

#     elif event.name == '1':  # Press '1' to record data from radar 1
#         recording_data = True

#         options_1['site_name'] = input("Enter the site name: ")
#         options_1['radar_angle'] = input("Enter the radar angle: ")
#         options_1['polarization'] = input("Enter the measurement polarization (vertical or horizontal): ")
        
#         print("Recording data from radar 1...")
#         record_measurement(num_records=50, foldername="./", measure_number=1, options=options_1)
#         recording_data = False

#     elif event.name == '2':  # Press '2' to record data from radar 2
#         recording_data = True

#         options_2['site_name'] = input("Enter the site name: ")
#         options_2['radar_angle'] = input("Enter the radar angle: ")
#         options_2['polarization'] = input("Enter the measurement polarization (vertical or horizontal): ")
        
#         print("Recording data from radar 2 at site" + options_2['site_name'] + " with angle " + radar_angle)

#         record_measurement(num_records=50, foldername="./", measure_number=1, options=options_2)
#         recording_data = False

# # Listen for key presses
# keyboard.on_press(handle_key_press)

# Main loop
try:
    while True:
        # Main processing loop can go here
        # Wait briefly to reduce CPU usage
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nExiting program...")

# Cleanup
stop_thread = True
keyboard.unhook_all()  # Remove all keyboard hooks
close_radar(com1)
close_radar(com2)
print("Program finished.")
