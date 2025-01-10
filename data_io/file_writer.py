import datetime
from Communication import Commands
from radar import radar

def write_header(file, radar_frequency, site_name, radar_angle, measure_id, polarization, infoParams, frontendParams, radarParams, sensor_temp, additional_info=None):
    """
    Writes a detailed header for a measurement session to the file, including radar configuration and parameters.
    
    Parameters:
        file (file object): Open file object to write the header to.
        radar_frequency (float): Frequency of the radar in GHz.
        site_name (str) : Name of the measurement site
        radar_angle (int) : Angle at which the measurement are made
        measure_id (int): Unique ID for the measurement session.
        polarization (str): Polarization type of the measurement ("Vertical" or "Horizontal").
        infoParams (InfoParameters): Instance containing general information about the radar module (e.g., device number, firmware version).
        frontendParams (FrontendParameters): Instance containing frontend-specific parameters (e.g., frequency range, signal type, channel selection).
        radarParams (RadarParameters): Instance containing radar measurement and processing parameters (e.g., measurement procedure, radar cube settings).
        additional_info (dict, optional): Dictionary with any additional information (e.g., location, gain, notes).
    
    """
    
    # Get radar informations

    
    timestamp = datetime.datetime.now().isoformat()
    file.write("# === Measurement Header ===\n")
    file.write(f"# Radar Frequency: {radar_frequency}\n")
    file.write(f"# Site Name: {site_name}\n")
    file.write(f"# Radar Angle: {radar_angle}\n")
    file.write(f"# Measurement ID: {measure_id}\n")
    file.write(f"# Polarization: {polarization}\n")
    file.write(f"# Timestamp: {timestamp}\n")
    
    # Device and firmware parameters
    file.write(f"# Device Number: {infoParams.deviceNumber}\n")
    file.write(f"# Frontend Connected: {infoParams.frontendConnected}\n")
    file.write(f"# Firmware Version: {infoParams.fwVersion}\n")
    file.write(f"# Firmware Revision: {infoParams.fwRevision}\n")
    file.write(f"# Firmware Date: {infoParams.fwDate}\n")
    
    # Frontend parameters
    file.write(f"# Min Frequency: {frontendParams.MinFrequency}\n")
    file.write(f"# Max Frequency: {frontendParams.MaxFrequency}\n")
    file.write(f"# Signal Type: {frontendParams.SignalType}\n")
    file.write(f"# TX Channel Selection: {frontendParams.TxChannelSelection}\n")
    file.write(f"# RX Channel Selection: {frontendParams.RxChannelSelection}\n")
    file.write(f"# TX Power Setting: {frontendParams.TxPowerSetting}\n")
    file.write(f"# RX Power Setting: {frontendParams.RxPowerSetting}\n")
    file.write(f"# Ramp Init: {frontendParams.RampInit}\n")
    file.write(f"# Ramp Time: {frontendParams.RampTime}\n")
    file.write(f"# Ramp Reset: {frontendParams.RampReset}\n")
    file.write(f"# Ramp Delay: {frontendParams.RampDelay}\n")
    file.write(f"# Sensor temperature: {sensor_temp}\n")
    
    # Radar parameters
    file.write(f"# Radar Cube: {radarParams.RadarCube}\n")
    file.write(f"# Processing: {radarParams.Processing}\n")
    file.write(f"# Range Window Function: {radarParams.RangeWinFunc}\n")
    file.write(f"# Min Range Bin: {radarParams.MinRangeBin}\n")
    file.write(f"# Max Range Bin: {radarParams.MaxRangeBin}\n")
    file.write(f"# Trigger Threshold: {radarParams.TriggerThresh}\n")
    file.write(f"# RX Channels: {radarParams.RxChannels}\n")

    file.write("# ==========================\n\n")
    file.write(f"# Comments: {additional_info}\n")
    # Write additional information if provided
    # if additional_info:
    #     for key, value in additional_info.items():
    #         file.write(f"# {key}: {value}\n")
    
    file.write("# ==========================\n\n")


def write_chirp_to_file(file, chirp_number, timestamp, data):
    """
    Writes a single chirp's data to the file.
    
    Parameters:
        file (file object): Open file object to write to.
        chirp_number (int): Chirp number within the measurement.
        timestamp (str): Timestamp for the chirp.
        data (list of lists): 4x1024 matrix data for the chirp.
    """
    file.write(f"# Chirp Number: {chirp_number}\n")
    file.write(f"# Timestamp: {timestamp}\n")
    for row in zip(data['data'][0], data['data'][1], data['data'][2], data['data'][3]):
        file.write(', '.join(map(str, row)) + "\n")
    file.write("# --- End of Chirp ---\n\n")


def record_measurement(num_records=50, foldername="./data/", measure_number=1, options=None, fullname=None):
    """
    Records a measurement consisting of `num_records` chirps, writing both header and chirp data.
    
    Parameters:
        num_records (int): Number of chirps to record in one measurement.
        radar (int): Radar ID or configuration (0 to record both radars).
        filename (str): File to write the data to.
        measure_number (int): Measurement session number.
        options (dict, optional): Dictionary of additional parameters, including:
            - cmd (Commands): Instance of the Commands class for radar 1 communication.
            - radar_frequency: Frequency of the radar in GHz.
            - infoParams (InfoParameters): General radar information.
            - frontendParams (FrontendParameters): Frontend-specific parameters.
            - radarParams (RadarParameters): Radar measurement and processing parameters.
            - polarization (str): Polarization type for the measurement (e.g., "Vertical" or "Horizontal").
            - additional_info (dict): Any extra metadata for the header.
    """
    # Set options to an empty dictionary if None is provided
    if options is None:
        options = {}

    # Extract parameters from options with defaults if they aren't provided
    cmd = options.get("cmd")
    
    #sensor_temp = cmd.executeCmd(Commands.CMD_GET_FE_SENSORS)
    
    site_name = options.get("site_name")
    measure_id = options.get("measure_id")
    radar_angle = options.get("radar_angle")
    # radar_frequency = options.get("radar_frequency")
    # infoParams = options.get("infoParams")
    # frontendParams = options.get("frontendParams")
    # radarParams = options.get("radarParams")
    polarization = options.get("polarization", "Vertical")  # Default to "Vertical" if not provided
    additional_info = options.get("additional_info")
    
    infoParams, frontendParams, radarParams = radar.fetch_radar_info(cmd)
    
    if frontendParams.MinFrequency == 12500000:
        radar_frequency = '13GHz'
        
    elif frontendParams.MinFrequency == 16500000:
        radar_frequency = '17GHz'
        
    filename = radar_frequency + '_' + site_name + '_' + str(measure_id) + '_' + polarization + '_' + radar_angle + 'deg.txt'
    if fullname == None:
        fullname = foldername + filename
    with open(fullname, 'w') as file:
        # Write the header for this measurement
        write_header(
            file, radar_frequency=radar_frequency, site_name=site_name,
            radar_angle=radar_angle, measure_id=measure_number, 
            polarization=polarization, infoParams=infoParams, 
            frontendParams=frontendParams, radarParams=radarParams, sensor_temp='Nan',
            additional_info=additional_info
        )
        
        # Record and write each chirp
        for chirp_number in range(1, num_records + 1):
            
            timestamp = datetime.datetime.now().isoformat()
            
            data = cmd.executeCmd(Commands.CMD_READ_RAW_DATA)
            write_chirp_to_file(file,chirp_number=chirp_number, timestamp=timestamp, data=data)
            

    print(f"Measurement {measure_number} recorded to {filename}")

