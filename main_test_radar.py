import Parameters as Pars
from Communication import Commands, EthernetInterfaces
import pickle

# Create an Ethernet configuration object and configure needed settings
#cfg = EthernetInterfaces.EnetConfig('192.168.0.2',  # radar IP address (default)
#                                    4120,           # radar UDP port (default)
#                                    4100)           # host port, needed by UDP
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
    radarParams.RangeWinFunc = 0
    
    # Set compatible bin limits (maximum possible for this cube here)
    #radarParams.MinRangeBin = 0
    #radarParams.MaxRangeBin = 1024
    #radarParams.MinDopplerBin = -64
    #radarParams.MaxDopplerBin = 63
    # Enable sending of all possible rx channels of this radar cube
    
    # Set to command triggered mode here, which means that the command specifies the data processing.
    # If set to 1, the parameter "Processing" specifies the processing step and must be set to the type of data
    # which is intended to be read.
    
    # Set target detection parameters so, that the radar is very sensitive to have some detections.
    #radarParams.PeakSearchThresh = 6
    #radarParams.SuppressStaticTargets = 0
    #radarParams.MaxTargets = 30
    #radarParams.CfarSelect = 3
    #radarParams.CfarWindowSize = 10
    #radarParams.CfarGuardInt = 2
    #radarParams.RangeCfarThresh = 8
    #radarParams.DopplerCfarThresh = 10
    
    # Send changed parameters and don't save them to EEPROM here.
    # The parameter object may be given as parameter to the function call but we are
    # already using a reference of command's parameter object.
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
        pickle.dump(data, file)
        
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
        
        

# if ok:
#     # Request a measurement and read range FFT results of one chirp
#     chirpNo = 0 # number of chirp to be read (if 0xFFFF, data for all chirps would be sent which is not implemented here!)
#     dict_data = {}
#     n=0
#     while True:
        
#         try:
#             data = cmd.executeCmd(Commands.CMD_READ_RANGE_DATA, chirpNo)
#             dict_data[n] = data
#             # Measurement results are in the returned dictionary
#             print('\nRead Range FFT Data')
#             print('Measurement time [ms]:', data['time'])
#             print('Some values of enabled rx channels:')
#             file = open('./fft_data_exemple.p', 'wb')
            
#             # for rx, values in data['data'].items():
#             #     s = 'Rx Channel %d: '%rx
#             #     for r in range(10):
#             #         s += '%s, '%str(values[r])
#             #     s += '...'
#             #     print(s)
#             n +=1
#         except KeyboardInterrupt:
#             print("Program interrupted by User.")
#             comVal.value = COMVAL_ABORT
#             break
#         except Exception as E:
#             print('Error in command %s: %s'%(Commands.CMD_READ_RANGE_DATA, str(E)))
#             ok = False    
            
            
import matplotlib.pyplot as plt
import time
import signal
import sys
import threading
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

# Global variable to control the inner loop
running = False

# Function to toggle the running state on Enter key press
def listen_for_enter():
    global running
    while True:
        input("Press Enter to toggle start/stop...")
        running = not running  # Toggle running state

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
                plt.pause(0.1)

                # Increment counter
                n += 1
                if n == 100:  # Condition to break out of the inner loop if needed
                    break
            except Exception as E:
                print('Error in command %s: %s' % (Commands.CMD_READ_RANGE_DATA, str(E)))
                break
        else:
            # Wait briefly if not running to prevent high CPU usage
            plt.pause(0.1)
    except KeyboardInterrupt:
        print("\nExiting program...")
        break  # Exit the main loop on Ctrl+C
        
        
# while True:
#     try:
#         # Execute command to read data
#         #data = cmd.executeCmd(Commands.CMD_READ_RAW_DATA)
#         data = cmd.executeCmd(Commands.CMD_READ_RANGE_DATA, chirpNo)
        
#         # Store data in dictionary
#         dict_data[n] = data

#         # Append the new data to lists for plotting
#         # time_ms = data['time']  # Extract time from the returned data
#         #rx_values = list(data['data'].values())[0][:10]  # Adjust if data structure differs
#         print(data['data'].values())
#         rx_values = [abs(item) for item in data['data'][0]][0:100]  # Adjust if data structure differs

#         # # Update plot with new data
#         line.set_xdata(range(len(rx_values)))
#         line.set_ydata(rx_values)
#         ax.relim()  # Adjust axis limits to fit new data
    
#         ax.autoscale_view()  # Auto-scale axis view

#         # # Pause to update the plot
#         plt.pause(0.1)
        
#         # Print data to the console
#         # print('\nRead Range FFT Data')
#         # print('Measurement time [ms]:', time_ms)
#         # print('Some values of enabled rx channels:', rx_values)
        
#         # Save data periodically (optional)

        
#         # Increment counter
#         n += 1
#         if n==100:
#             break
#     except Exception as E:
#         print('Error in command %s: %s' % (Commands.CMD_READ_RANGE_DATA, str(E)))
#         break
print(time.time() - start)
# with open('./raw_data_example3_13GHz.p', 'wb') as file:
#     pickle.dump(dict_data, file)
com.Close()
print('\n>============ End ============<')
input("Press any Key to exit.")