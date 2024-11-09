import Parameters as Pars
from Communication import Commands, EthernetInterfaces

def init_radar(ip_address, udp_port=4120, host_port=4100):
    """
    Initializes the radar connection and configures radar parameters.
    
    Parameters:
        ip_address (str): The IP address of the radar.
        udp_port (int): The radar's UDP port. Default is 4120.
        host_port (int): The host's UDP port for receiving radar data. Default is 4100.
    
    Returns:
        tuple: A tuple containing:
            - com (EnetUdpInterface): The UDP interface for radar communication.
            - cmd (Commands): The Commands instance used for radar commands.
            - bool: True if initialization and configuration succeed, False otherwise.
    """
    
    # Configure Ethernet settings for radar communication
    cfg = EthernetInterfaces.EnetConfig(ip_address, udp_port, host_port)
    # Create an Ethernet UDP interface based on the configuration
    com = EthernetInterfaces.EnetUdpInterface(cfg)
    # Attempt to open the UDP connection to the radar
    ok = com.Open()
    # Create a Commands instance for sending radar commands
    cmd = Commands.Commands(interface=com)

    # Check if the connection was successful
    if not ok:
        print(f'Error opening interface for radar {ip_address}:', com.getErrorString())
        # Return early with a failure status if unable to connect
        return com, cmd, False

    try:
        # Retrieve current radar parameters
        radarParams = cmd.executeCmd(Commands.CMD_GET_RADAR_PARAMS)
        
        # Set specific radar parameters
        radarParams.RadarCube = Pars.RCUBE_smpl1024_crp1_4rx  # Radar data format (e.g., 4 RX channels, 1024 samples)
        radarParams.RxChannels = 0xF                          # Enable all receiver channels
        radarParams.ContinuousMeas = 0                        # Set to single measurement mode (no continuous measurements)
        radarParams.RangeWinFunc = 2                          # Set range window function (e.g., Hamming or rectangular)
        
        # Apply the modified radar parameters
        cmd.executeCmd(Commands.CMD_SET_RADAR_PARAMS_NO_EEP)
        print(f'Radar parameters set for {ip_address}.')
    except Exception as e:
        # Handle any errors in parameter retrieval or configuration
        print(f"Error setting radar parameters for {ip_address}: {e}")
        return com, cmd, False

    # Return the communication interface, command instance, and success status
    return com, cmd, True


def fetch_radar_info(cmd):
    """
    Fetches radar information parameters, frontend parameters, and radar parameters.
    
    Parameters:
        cmd (Commands): An instance of the Commands class used to communicate with the radar.
    
    Returns:
        tuple: A tuple containing (infoParams, frontendParams, radarParams), or (None, None, None) if an error occurs.
    """
    try:
        infoParams = cmd.executeCmd(Commands.CMD_INFO)
        frontendParams = cmd.executeCmd(Commands.CMD_GET_FRONTEND_PARAMS)
        radarParams = cmd.executeCmd(Commands.CMD_GET_RADAR_PARAMS)
        return infoParams, frontendParams, radarParams
    except Exception as e:
        print(f"Error getting radar parameters with error: {e}")
        return None, None, None  # Fallback return in case of error
    
    
def fetch_radar_data(cmd):
    """
    Fetches radar range data for a specific chirp (radar pulse).
    
    Parameters:
        cmd (Commands): An instance of the Commands class used to communicate with the radar.
        chirpNo (int): The chirp number for which to fetch the radar data.
    
    Returns:
        dict or None: The radar data for the specified chirp if successful, or None if an error occurs.
    """
    try:
        # Execute the radar command to read range data for the given chirp number
        data = cmd.executeCmd(Commands.CMD_READ_RANGE_DATA, 0)
        # Return the retrieved radar data
        return data
    
    except Exception as e:
        # Handle any errors that occur during data retrieval and print an error message
        print(f"Error reading radar data: {e}")
        # Return None if there was an error, indicating failure to fetch data
        return None


def close_radar(com):
    com.Close()
    print("Radar interface closed.")
