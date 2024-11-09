import Parameters as Pars
from Communication import Commands, EthernetInterfaces
import matplotlib.pyplot as plt
import time
import signal
import sys
import threading



cfg = EthernetInterfaces.EnetConfig('192.168.0.13',  # radar IP address (default)
                                    4120,           # radar UDP port (default)
                                    4100)           # host port, needed by UDP
# Create an UDP interface object
com = EthernetInterfaces.EnetUdpInterface(cfg)
ok = True

ok = com.Open()
cmd = Commands.Commands(interface=com)

if not ok:
    print('Error when opening interface:', com.getErrorString())
    
if ok:
    # Read radar processing parameters
    try:
        radarParams = cmd.executeCmd(Commands.CMD_GET_RADAR_PARAMS)
        #print('test get parameters')
        for attr, value in vars(radarParams).items():
            print(f"{attr}: {value}")
        #print([radarParams._NumDopplerBins])
        print('radarParams._NumDopplerBins :', radarParams._NumDopplerBins)
    except Exception as E:
        print('Error in command %s: %s'%(Commands.CMD_GET_RADAR_PARAMS, str(E)))
        ok = False
        


if ok:
    # Read radar processing parameters
    try:
        frontendParams = cmd.executeCmd(Commands.CMD_GET_FRONTEND_PARAMS)
        #print('test get parameters')
        for attr, value in vars(frontendParams).items():
            print(f"{attr}: {value}")
        #print([radarParams._NumDopplerBins])

    except Exception as E:
        print('Error in command %s: %s'%(Commands.CMD_GET_FRONTEND_PARAMS, str(E)))
        ok = False

if ok:
    # Set some specific radar parameters
    #### A valider ce que c'est. ça fait planter le setting de parameter
    radarParams.RadarCube = Pars.RCUBE_smpl1024_crp1_4rx   # 256 range bins, 128 doppler bins, 4 rx channels
    radarParams.RxChannels = 0xF
    radarParams.ContinuousMeas = 0
    radarParams.RangeWinFunc = 2
    try:
        cmd.executeCmd(Commands.CMD_SET_RADAR_PARAMS_NO_EEP)
        print('Sent radar parameters.')
    except Exception as E:
        print('Error in command %s: %s'%(Commands.CMD_SET_RADAR_PARAMS_NO_EEP, str(E)))
        ok = False    


if ok:
    # Read radar processing parameters
    try:
        radarParams = cmd.executeCmd(Commands.CMD_GET_RADAR_PARAMS)
        #print('test get parameters')
        for attr, value in vars(radarParams).items():
            print(f"{attr}: {value}")
        #print([radarParams._NumDopplerBins])
        print('radarParams._NumDopplerBins :', radarParams._NumDopplerBins)
    except Exception as E:
        print('Error in command %s: %s'%(Commands.CMD_GET_RADAR_PARAMS, str(E)))
        ok = False

if ok:
    # Read radar processing parameters
    try:
        frontendParams = cmd.executeCmd(Commands.CMD_GET_FRONTEND_PARAMS)
        #print('test get parameters')
        for attr, value in vars(frontendParams).items():
            print(f"{attr}: {value}")
        #print([radarParams._NumDopplerBins])

    except Exception as E:
        print('Error in command %s: %s'%(Commands.CMD_GET_FRONTEND_PARAMS, str(E)))
        ok = False

if ok:
    try:
        data = cmd.executeCmd(Commands.CMD_READ_RAW_DATA)
        file = open('./raw_data_exemple.p', 'wb')
        #pickle.dump(data, file)
        
        #print(data)
        print('Measurement time [ms]:', data['time'])
        # print('Some values of enabled rx channels:')
        # for rx, values in data['data'].items():
        #     s = 'Rx Channel %d: '%rx
        #     for r in range(10):
        #         s += '%s, '%str(values[r])
        #     s += '...'
        #     print(s)
        
    except Exception as E:
        print('Error in command %s: %s'%(Commands.CMD_READ_RAW_DATA, str(E)))
        ok = False  
        
chirpNo = 0  # Number of chirp to be read
dict_data = {}
n = 0

# def signal_handler(sig, frame):
#     print("\nExiting program...")
#     sys.exit(0)
    
# signal.signal(signal.SIGINT, signal_handler)


# Initialize the plot
plt.ion()  # Turn on interactive mode
fig, ax = plt.subplots()
line, = ax.plot([], [], 'r-')  # Initialize an empty line plot
start = time.time()
ax.set_ylim((0,20000))
ax.set_xlim((0,100))

# # Global variable to control the inner loop
# running = False

# # Function to toggle the running state on Enter key press
# def listen_for_enter():
#     global running
#     while True:
#         input("Press Enter to toggle start/stop...")
#         running = not running  # Toggle running state


# Flags to control the thread and running state
stop_thread = False
running = False

def listen_for_enter():
    global running
    while not stop_thread:
        input("Press Enter to toggle start/stop...")
        running = not running  # Toggle runni

# Start the Enter listener in a separate thread
thread = threading.Thread(target=listen_for_enter, daemon=True)
thread.start()


# Main loop
while True:
    try:
        if running:
            try:
                # Execute command to read data
                # data = cmd.executeCmd(Commands.CMD_READ_RAW_DATA)
                data = cmd.executeCmd(Commands.CMD_READ_RANGE_DATA, chirpNo)
                
                # Store data in dictionary
                dict_data[n] = data

                # Process data for plotting
                rx_values = [abs(item) for item in data['data'][0]][0:100]

                # Update plot with new data
                line.set_xdata(range(len(rx_values)))
                line.set_ydata(rx_values)
                ax.relim()  # Adjust axis limits to fit new data
                ax.autoscale_view()  # Auto-scale axis view

                # Pause to update the plot
                plt.pause(0.05)

            except Exception as E:
                print('Error in command %s: %s' % (Commands.CMD_READ_RANGE_DATA, str(E)))
                break
        else:
            # Wait briefly if not running to prevent high CPU usage
            plt.pause(0.1)
    except KeyboardInterrupt:
        print("\nExiting program...")
        break  # Exit the main loop on Ctrl+C
stop_thread = True  # Signal the thread to stop

# Optionally join the thread to ensure it stops cleanly
thread.join() 

print(time.time() - start)
# with open('./raw_data_example3_13GHz.p', 'wb') as file:
#     pickle.dump(dict_data, file)
com.Close()
print('\n>============ End ============<')
input("Press any Key to exit.")