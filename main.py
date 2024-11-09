import threading
import time
from radar.radar import init_radar, fetch_radar_data, close_radar
from plotting.plotting import init_plot, update_plot
#from listener.listener import listen_for_enter
from Communication import Commands
from Communication.EthernetInterfaces import EnetUdpInterface, EnetConfig
import signal
from matplotlib import pyplot as plt
#from utils.utils import some_utility_function  # If there are utility functions


# Flags to control the thread and running state
stop_thread = False
running = False
def listen_for_enter(stop_thread, running_flag):
    global running
    while not stop_thread():
        input("Press Enter to toggle start/stop display\n")
        # Toggle the global `running` variable
        running = not running  # Update the global `running` flag

            
def main():
    global running, stop_thread

    # Initialize both radars
    radar1_ip = '192.168.0.13'
    radar2_ip = '192.168.0.17'
    
    # Define unique host ports for each radar
    radar1_ip = '192.168.0.13'
    radar2_ip = '192.168.0.17'
    radar1_host_port = 4100
    radar2_host_port = 4101

    # Initialize each radar with a unique host port
    com1, cmd1, ok1 = init_radar(radar1_ip, host_port=radar1_host_port)
    com2, cmd2, ok2 = init_radar(radar2_ip, host_port=radar2_host_port)

    # com1, cmd1, ok1 = init_radar(radar1_ip)
    # com2, cmd2, ok2 = init_radar(radar2_ip)

    if not ok1 or not ok2:
        print("Failed to initialize one or both radars.")
        return
    
    
    
    try:
        
        infoParams = cmd2.executeCmd(Commands.CMD_INFO)

        for attr, value in vars(infoParams).items():
            print(f"{attr}: {value}")
        #print([radarParams._NumDopplerBins])
        #print('radarParams._NumDopplerBins :', infoParams._NumDopplerBins)
    except Exception as E:
        print('Error in command %s: %s'%('infoParams', str(E)))
        ok = False

    # Initialize the plot with two subplots for two radars and specify radar wavelengths
    fig, ax, lines = init_plot(("13GHz", "17GHz"), two_radar=True)

    # Start the listener thread
    thread = threading.Thread(target=listen_for_enter, args=(lambda: stop_thread, lambda: running), daemon=True)
    thread.start()

    start_time = time.time()
    dict_data1 = {}
    dict_data2 = {}
    n = 0
    print_flag=0
    try:
        while True:
            if running:
                # Fetch data from both radars
                if print_flag==1:
                    print("Radar measurement being displayed\n")
                data1 = fetch_radar_data(cmd1)
                data2 = fetch_radar_data(cmd2)
                
                if data1 is None or data2 is None:
                    print("Error fetching data; exiting loop.")
                    break

                # Store data in respective dictionaries
                #dict_data1[n] = data1
                #dict_data2[n] = data2

                # Process data for radar 1 (co-pol and cross-pol)
                rx_values1_copol = [abs(item) for item in data1['data'][0]][0:100]
                rx_values1_crosspol = [abs(item) for item in data1['data'][1]][0:100]

                # Process data for radar 2 (co-pol and cross-pol)
                rx_values2_copol = [abs(item) for item in data2['data'][0]][0:100]
                rx_values2_crosspol = [abs(item) for item in data2['data'][1]][0:100]

                # Update plots for both radars
                update_plot(
                    ax, 
                    lines, 
                    rx_values1_copol, 
                    rx_values1_crosspol, 
                    two_radar=True, 
                    rx_values2_copol=rx_values2_copol, 
                    rx_values2_crosspol=rx_values2_crosspol
                )

                # Pause to update the plot
                plt.pause(0.05)

                # Increment counter for dictionary storage
                n += 1
                print_flag = 0
            else:
                # Brief pause when not running to avoid high CPU usage
                if print_flag == 0:
                    print("Press:\n1:13GHz measurement\n2:17GHz measurement\nb: Both Frenquency measuremnt\nEnter Display FFT data\n")
                print_flag=1
                plt.pause(0.1)

    except KeyboardInterrupt:
        print("\nExiting program...")

    # Signal thread to stop and close radars
    stop_thread = True
    thread.join()
    close_radar(com1)
    close_radar(com2)
    print("Program finished. Duration:", time.time() - start_time)




    # fig, ax, line_coPol, line_crossPol = init_plot()
    # # Start the listener thread
    # thread = threading.Thread(target=listen_for_enter, args=(lambda: stop_thread, lambda: running), daemon=True)
    # thread.start()

    # chirpNo = 0
    # start_time = time.time()
    # dict_data1 = {}
    # dict_data2 = {}
    # n = 0

    # try:
    #     while True:
           
    #         if running:

    #             # Fetch data from both radars
    #             data1 = fetch_radar_data(cmd1, chirpNo)
    #             data2 = fetch_radar_data(cmd2, chirpNo)
    #             if data1 is None or data2 is None:
    #                 break  # Exit if there's an error fetching data

    #             # Store data in respective dictionaries
    #             dict_data1[n] = data1
    #             dict_data2[n] = data2

    #             # Process and plot data for radar 1
    #             rx_values_coPol = [abs(item) for item in data1['data'][0]][0:100]
    #             rx_values_crossPol = [abs(item) for item in data1['data'][1]][0:100]
    #             update_plot(ax, line_coPol, line_crossPol, rx_values_coPol, rx_values_crossPol)
    #             plt.pause(0.05)

    #             # You could also add a separate plot for radar 2 if desired,
    #             # or display radar 2 data alongside radar 1
    #             # Process and plot data for radar 2 (if adding a second plot)
    #             # rx_values2 = [abs(item) for item in data2['data'][0]][0:100]
    #             # update_plot(ax, line2, rx_values2)

    #         else:
    #             plt.pause(0.1)

    # except KeyboardInterrupt:
    #     print("\nExiting program...")

    # stop_thread = True
    # thread.join()
    # close_radar(com1)
    # close_radar(com2)
    # print("Program finished. Duration:", time.time() - start_time)

if __name__ == "__main__":
    main()
