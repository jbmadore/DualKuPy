import threading
import time
from radar.radar import init_radar, fetch_radar_data, close_radar
from plotting.plotting import init_plot, update_plot
import matplotlib.pyplot as plt
from data_io.file_writer import record_measurement

# Global flags and settings
running = False  # Controls display running state
recording_lock = threading.Lock()

def main():
    global running

    # Define radar IPs and ports
    radar1_ip = '192.168.0.13'
    radar2_ip = '192.168.0.17'
    radar1_host_port = 4100
    radar2_host_port = 4101

    # Initialize each radar
    com1, cmd1, ok1 = init_radar(radar1_ip, host_port=radar1_host_port)
    com2, cmd2, ok2 = init_radar(radar2_ip, host_port=radar2_host_port)
    if not ok1 or not ok2:
        print("Failed to initialize one or both radars.")
        return

    # Initialize the plot
    fig, ax, lines = init_plot(("13GHz", "17GHz"), two_radar=True)

    # Start the keyboard listener in the background
    keyboard_thread = threading.Thread(target=keyboard_listener, args=(cmd1, cmd2))
    keyboard_thread.daemon = True
    keyboard_thread.start()

    # Run the display update on the main thread
    update_display(ax, lines, cmd1, cmd2)

    # Clean up
    close_radar(com1)
    close_radar(com2)

def update_display(ax, lines, cmd1, cmd2):
    global running
    while True:
        if running:
            # Fetch and process data
            data1 = fetch_radar_data(cmd1)
            data2 = fetch_radar_data(cmd2)

            if data1 is None or data2 is None:
                print("Error fetching data; stopping display.")
                break

            # Process data for each radar
            rx_values1_copol = [abs(item) for item in data1['data'][0]][0:100]
            rx_values1_crosspol = [abs(item) for item in data1['data'][1]][0:100]
            rx_values2_copol = [abs(item) for item in data2['data'][0]][0:100]
            rx_values2_crosspol = [abs(item) for item in data2['data'][1]][0:100]

            # Update plot
            update_plot(ax, lines, rx_values1_copol, rx_values1_crosspol, 
                        two_radar=True, rx_values2_copol=rx_values2_copol, 
                        rx_values2_crosspol=rx_values2_crosspol)
            plt.pause(0.05)
# Increment chirp count
        else:
            plt.pause(0.1)

def keyboard_listener(cmd1, cmd2):
    """Listen for keyboard events to control display and take measurements."""

    while True:
        key = input("\nPress Enter to toggle display, or '1', '2', 'b' to take measurements when paused: ")

        # Toggle the display running state with Enter
        if key == "":
            toggle_display()
        elif not running and not recording_lock.locked():
            if key == "1":
                take_measurement(cmd1, "Radar 13GHz")
            elif key == "2":
                take_measurement(cmd2, "Radar 17GHz")
            elif key == "b":
                take_measurement((cmd1,cmd2), "Radar 13GHz and 17GHz")
                #take_measurement(cmd2, "Radar 2")

def toggle_display():
    """Toggles the display between running and paused."""
    global running
    running = not running
    print("Display toggled:", "Running" if running else "Paused")

def gather_recording_info():
    """Prompt for measurement information once."""
    site_name = input("Enter the site name: ")
    measure_id = input("Enter the measure_id: ")
    radar_angle = input("Enter the radar angle: ")
    polarization = input("Enter the measurement polarization (vertical or horizontal): ")
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
    with recording_lock:
        recording_info = gather_recording_info()
        print(f"Starting measurement for {radar_label} at site {recording_info['site_name']} "
              f"with angle {recording_info['radar_angle']} and polarization {recording_info['polarization']}...")
        
        if isinstance(cmd, tuple) and len(cmd)==2:
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
            record_measurement(num_records=50, foldername="./", measure_number=1, options=options_1)
            record_measurement(num_records=50, foldername="./", measure_number=1, options=options_2)
            
        else :
            options = {
            "cmd": cmd,
            "site_name": '',  # Placeholder values
            "measure_id": '',
            "polarization": '',
            "additional_info": ""
            }
            options.update(recording_info)
            record_measurement(num_records=50, foldername="./", measure_number=1, options=options)      
                  
        # num_records = 50
        # measurement_data = []
        # for i in range(num_records):
        #     data = fetch_radar_data(cmd)
        #     if data is None:
        #         print(f"Error fetching data for {radar_label}; stopping measurement.")
        #         return
        #     measurement_data.append(data)
        #     print(f"{radar_label} measurement {i+1}/{num_records} recorded.")

        # Optionally, save `measurement_data` to a file or process it further
        print(f"Measurement for {radar_label} complete.")

# Run main
if __name__ == "__main__":
    main()
