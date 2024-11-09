'''
Created on 15.07.2022

@author: IMST GmbH
'''

# frontend codes
FE_CODE_NO_FE = 0xFE000000
FE_CODE_AWR1243 = 0xFE770001

# maximum number of rx channels
MAX_RX_CHAN = 4
MAX_RX_CHAN_MIMO = 12

# possible radar cube values (samples_chrirps_rxChannel)
RCUBE_smpl256_crp1_4rx = 0
RCUBE_smpl512_crp1_4rx = 1
RCUBE_smpl1024_crp1_4rx = 2
RCUBE_smpl2048_crp1_4rx = 3
RCUBE_smpl128_crp64_4rx = 4
RCUBE_smpl128_crp128_4rx = 5
RCUBE_smpl128_crp256_4rx = 6
RCUBE_smpl256_crp64_4rx = 7
RCUBE_smpl256_crp128_4rx = 8
RCUBE_smpl256_crp256_4rx = 9
RCUBE_smpl512_crp64_4rx = 10
RCUBE_smpl512_crp128_4rx = 11
RCUBE_smpl512_crp256_4rx = 12
RCUBE_smpl1024_crp64_4rx = 13
RCUBE_smpl1024_crp128_4rx = 14
RCUBE_smpl256_crp64_tdMimo_3tx_4rx = 15
RCUBE_smpl256_crp128_tdMimo_3tx_4rx = 16
RCUBE_smpl256_crp256_tdMimo_3tx_4rx = 17
RCUBE_smpl512_crp64_tdMimo_3tx_4rx = 18
RCUBE_smpl512_crp128_tdMimo_3tx_4rx = 19
RCUBE_smpl1024_crp64_tdMimo_3tx_4rx = 20
RCUBE_maxValue = 21

# possible processing steps
PROC_NoProcessing = 0
PROC_RangeFFT = 1
PROC_DopplerFFT = 2
PROC_Combining = 3
PROC_PeakDet = 4
PROC_CFAR = 5
PROC_Detections = 6
PROC_Tracking = 7

# possible FFT windows
FFTWIN_NoWin = 0
FFTWIN_Blackman = 1
FFTWIN_Hamming = 2
FFTWIN_Hann = 3
FFTWIN_Nuttal = 4

# possible tx signal modulations
ST_CwMinFrequency = 1
ST_CwMaxFrequency = 2
ST_FmcwUpRamp = 3
ST_FmcwDownRamp = 4
ST_FmcwUpDownRamp = 5
ST_FmcwDownUpRamp = 6

# dimension of the sector map
SECTOR_RANGE_NUM = 20
SECTOR_ANGLE_NUM = 18

# possible speed estimation options
SPEED_EST_OFF = 0
SPEED_EST_SPEED_ONLY = 1
SPEED_EST_FILTER_ALL = 2
SPEED_EST_FILTER_TRACKS = 3

# Ethernet
ENET_DEFAULT_IP = "192.168.0.2"
ENET_DEFAULT_TCP_PORTS = (1024,1025,1026,1027,1028,1029)
ENET_MAX_TCP_PORTS = 2
ENET_DEFAULT_UDP_PORTS = (4120,4121,4122,4123,4124,4125)
ENET_MAX_UDP_PORTS = 2
ENET_DEFAULT_UDP_HOST_PORT = 4100
ENET_DEFAULT_GATEWAY = "192.168.0.1"
ENET_DEFAULT_SUBNET_MASK = "255.255.0.0"
ENET_SNTP_OFF = 0
ENET_SNTP_POLL = 1
ENET_SNTP_LISTEN = 2
ENET_MAX_MULTICAST_GROUPS = 4
ENET_DEFAULT_MULTICAST_GROUPS = ["227.115.82.100", "0.115.82.101", "0.115.82.102", "0.115.82.103"]
ENET_UDP_MULTICAST_PORT = 4440
ENET_UDP_BROADCAST_PORT = 4444

MAX_NUM_TARGETS = 128
MAX_NUM_TRACKS = 30
NUM_NN_CLASSES = 8

C0 = 299792458  # [m/s]

'==========================================================================='
class InfoParameters(object):
    def __init__(self):
        self.deviceNumber = None
        self.frontendConnected = FE_CODE_NO_FE
        self.fwVersion = None
        self.fwRevision = None
        self.fwDate = None
        
    def getFwVersionString(self):
        return "%d.%d.%d"%((self.fwVersion>>16)&0xFF, (self.fwVersion>>8)&0xFF, self.fwVersion&0xFF)
    
    def getFwDateString(self):
        return "%d.%d.%d"%((self.fwDate>>24)&0xFF, (self.fwDate>>16)&0xFF, self.fwDate&0xFFFF)

'==========================================================================='
class RadarParameters(object):
    # values to indicate that current maximum values should be used
    MAX_RANGE_BIN = 0xEFCA
    MAX_DOPPLER_BIN = 0xFEAC
    NO_DOPPLER_INTERVAL = 0xD000
    
    def __init__(self):
        # Data acquisition
        self.RadarCube = RCUBE_smpl512_crp128_4rx   # data cube dimension
        self.ContinuousMeas = 0         # 0 or 1
        self.MeasInterval = 0           # timer interval [ms] (0 - 10000)
        self.Processing = PROC_RangeFFT
        self.RangeWinFunc = FFTWIN_Blackman
        self.DopplerWinFunc = FFTWIN_Blackman
        self.DopplerFftShift = 1        # shift doppler data when sending data cube (0 or 1)
        self.MinRangeBin = 0            # minimum range bin for data sending
        self.MaxRangeBin = 255          # maximum range bin for data sending
        self.MinDopplerBin = -64        # minimum doppler bin for data sending
        self.MaxDopplerBin = 63         # maximum doppler bin for data sending
        # Target detection
        self.CfarWindowSize = 10        # window size of CFAR
        self.CfarGuardInt = 2           # CFAR guard interval
        self.RangeCfarThresh = 8        # threshold for CFAR in range direction
        self.TriggerThresh = 10         # threshold for triggering pin
        self.PeakSearchThresh = 6       # threshold for initialization of threshold used by peak search
        self.SuppressStaticTargets = 0  # 0 = OFF, 1 = delete 0 doppler, 2 = delete 0 doppler and neighbours
        self.MaxTargets = 30            # maximum number of detected targets allowed
        # Target tracking
        self.MaxTracks = 10             # maximum number of tracks allowed (<= MaxTargets)
        self.MaxHorSpeed = 5            # [m/s]
        self.MaxVerSpeed = 1            # [m/s]
        self.MaxAccel = 10              # [m/s^2]
        self.MaxRangeError = 20         # range error [m/10]
        self.MinConfirm = 2             # minimum number of confirmations
        self.TargetSize = 5             # expected target size [m/10]
        self.MergeLimit = 15            # limit for track merging
        # Other
        self.SectorFiltering = 0        # if enabled, targets are filtered with saved sector configuration
        self.SpeedEstimation = SPEED_EST_OFF # enable/disable estimation of radar system speed
        self.DspDopplerProc = 0         # use DSP doppler processing for tracks
        self.RxChannels = 0xF           # bitmask which rx channels should be sent in data read commands
        self.CfarSelect = 1             # bitmasl: 0 = No CFAR; 0x1 = Range CFAR, 0x2 = Doppler CFAR
        self.DopplerCfarThresh = 10     # threshold for CFAR in doppler direction

        self.updateInternals()
        
    '-----------------------------------------------------------------------------'
    'update internally used variables'
    def updateInternals(self):
        nS, nR, nD = self.getCubeBins(self.RadarCube)
        
        self._isMIMO = self.RadarCube >= RCUBE_smpl256_crp64_tdMimo_3tx_4rx
        
        self._NumSamples = nS
        self._NumRangeBins = nR
        self._NumDopplerBins = nD
        self._ActiveRangeBins = self.MaxRangeBin - self.MinRangeBin + 1
        self._ActiveDopplerBins = self.MaxDopplerBin - self.MinDopplerBin + 1
        self._ActiveRxChannels = self.getNumActiveRxChan()
        
        # get internal used doppler indices, dependent on FFT shift here!
        self._dBinNegL = self._dBinNegH = self._dBinPosL = self._dBinPosH = self.NO_DOPPLER_INTERVAL
        if self.MinDopplerBin < 0 and self.MaxDopplerBin >= 0:
            self._dBinNegL = self._NumDopplerBins + self.MinDopplerBin
            self._dBinNegH = self._NumDopplerBins - 1
            self._dBinPosL = 0                              
            self._dBinPosH = self.MaxDopplerBin
        elif self.MinDopplerBin >= 0 and self.MaxDopplerBin > 0:
            self._dBinPosL = self.MinDopplerBin
            self._dBinPosH = self.MaxDopplerBin
        else:   # MinDopplerBin < 0 and MaxDopplerBin < 0
            self._dBinNegL = self._NumDopplerBins + self.MinDopplerBin
            self._dBinNegH = self._NumDopplerBins + self.MaxDopplerBin
        
        if self.DopplerFftShift: # correct indices for doppler shift
            nD //= 2
            if self._dBinNegL != self.NO_DOPPLER_INTERVAL:  # lower limit of negative doppler interval
                self._dBinNegL -= nD
            if self._dBinNegH != self.NO_DOPPLER_INTERVAL:  # upper limit of negative doppler interval
                self._dBinNegH -= nD
            if self._dBinPosL != self.NO_DOPPLER_INTERVAL:  # lower limit of positive doppler interval
                self._dBinPosL += nD
            if self._dBinPosH != self.NO_DOPPLER_INTERVAL:  # upper limit of positive doppler interval
                self._dBinPosH += nD
        
        if self.DopplerFftShift:
            if self._dBinNegL != self.NO_DOPPLER_INTERVAL:
                self._dBinIdxs = [d for d in range(self._dBinNegL, self._dBinNegH+1)]
            if self._dBinPosL != self.NO_DOPPLER_INTERVAL:
                self._dBinIdxs += [d for d in range(self._dBinPosL, self._dBinPosH+1)]
        else:
            if self._dBinPosL != self.NO_DOPPLER_INTERVAL:
                self._dBinIdxs = [d for d in range(self._dBinPosL, self._dBinPosH+1)]
            if self._dBinNegL != self.NO_DOPPLER_INTERVAL:
                self._dBinIdxs += [d for d in range(self._dBinNegL, self._dBinNegH+1)]
                
    '-----------------------------------------------------------------------------'
    'return number of range and doppler bins of selected cube in form (samples,range,doppler)'
    @staticmethod
    def getCubeBins(cube):
        try:
            cube = int(cube)
        except:
            raise Exception("\"cube\" must be a valid number!")
        if cube < 0 or cube > RCUBE_maxValue-1:
            raise Exception("\"cube\" value out of range!")
        if cube == RCUBE_smpl256_crp1_4rx:
            return (256,256,1)
        elif cube == RCUBE_smpl512_crp1_4rx:
            return (512,512,1)
        elif cube == RCUBE_smpl1024_crp1_4rx:
            return (1024,1024,1)
        elif cube == RCUBE_smpl2048_crp1_4rx:
            return (2048,2048,1)
        elif cube == RCUBE_smpl128_crp64_4rx:
            return (128,64,64)
        elif cube == RCUBE_smpl128_crp128_4rx:
            return (128,64,128)
        elif cube == RCUBE_smpl128_crp256_4rx:
            return (128,64,256)
        elif cube == RCUBE_smpl256_crp64_4rx:
            return (256,128,64)
        elif cube == RCUBE_smpl256_crp128_4rx:
            return (256,128,128)
        elif cube == RCUBE_smpl256_crp256_4rx:
            return (256,128,256)
        elif cube == RCUBE_smpl512_crp64_4rx:
            return (512,256,64)
        elif cube == RCUBE_smpl512_crp128_4rx:
            return (512,256,128)
        elif cube == RCUBE_smpl512_crp256_4rx:
            return (512,256,256)
        elif cube == RCUBE_smpl1024_crp64_4rx:
            return (1024,512,64)
        elif cube == RCUBE_smpl1024_crp128_4rx:
            return (1024,512,128)
        elif cube == RCUBE_smpl256_crp64_tdMimo_3tx_4rx:
            return (256,128,64)
        elif cube == RCUBE_smpl256_crp128_tdMimo_3tx_4rx:
            return (256,128,128)
        elif cube == RCUBE_smpl256_crp256_tdMimo_3tx_4rx:
            return (256,128,256)
        elif cube == RCUBE_smpl512_crp64_tdMimo_3tx_4rx:
            return (512,256,64)
        elif cube == RCUBE_smpl512_crp128_tdMimo_3tx_4rx:
            return (512,256,128)
        elif cube == RCUBE_smpl1024_crp64_tdMimo_3tx_4rx:
            return (1024,512,64)
        
    '-----------------------------------------------------------------------------'
    def getMaxNumRxChan(self):
        if self._isMIMO:
            return MAX_RX_CHAN
        else:
            return MAX_RX_CHAN_MIMO
    
    '-----------------------------------------------------------------------------'
    def getNumActiveRxChan(self):
        if self._isMIMO:
            return bin(self.RxChannels & 0xFFF).count("1")
        else:
            return bin(self.RxChannels & 0xF).count("1")

        
'==========================================================================='
class FrontendParameters(object):
    'Base class for frontend parameters. Each frontend should use it.'
    
    def __init__(self):
        self.MinFrequency = 0
        self.MaxFrequency = 1
        self.SignalType = 0
        self.RxChannelSelection = 0x0
        self.TxChannelSelection = 0x0
        self.TxPowerSetting = 0
        self.RxPowerSetting = 0
        self.RampInit = 0
        self.RampTime = 0
        self.RampReset = 0
        self.RampDelay = 0
        self.OptParam1 = 0
        self.OptParam2 = 0
        self.OptParam3 = 0
        self.OptParam4 = 0
        
    '-----------------------------------------------------------------------------'
    def checkValues(self):
        raise Exception("Method not implemented!")
    
    '-----------------------------------------------------------------------------'
    def getChirpTime(self):
        return (self.RampInit + self.RampTime + self.RampReset + self.RampDelay) * 1e-9   # [s]
    
    '-----------------------------------------------------------------------------'
    def getRangeResolution(self):
        try:
            return C0/(2.*(self.MaxFrequency-self.MinFrequency)*1e3)   # [m]
        except:
            return 1    # division by zero

    '-----------------------------------------------------------------------------'
    def getDopplerResolution(self, numChirps):
        try:
            return 1./(self.getChirpTime()*numChirps)   # [Hz]
        except:
            return 1    # division by zero
    
    '-----------------------------------------------------------------------------'
    def getSpeedResolution(self, numChirps):
        try:
            f0 = (self.MinFrequency + self.MaxFrequency)/2 * 1e3    # [Hz]
            return C0/(2.*f0*self.getChirpTime()*numChirps)  # [m/s]
        except:
            return 1    # division by zero
    
    '-----------------------------------------------------------------------------'
    def getIfResolution(self):
        try:
            return 1./self.getChirpTime()   # [Hz]
        except:
            return 1    # division by zero

'==========================================================================='
class FE_Parameters_AWR1243(FrontendParameters):
    Freq_Limits_kHz = ( (76000000,77000000), (77000000,81000000) )  # limits for supported VCO bands
    Num_Tx = 3
    Num_Rx = 4
    
    def __init__(self):
        self.MinFrequency = self.Freq_Limits_kHz[0][0]  # [kHz]
        self.MaxFrequency = self.Freq_Limits_kHz[0][1]  # [kHz]
        self.SignalType = ST_FmcwUpRamp                 # enum
        self.RxChannelSelection = 0xF                   # bitmask
        self.TxChannelSelection = 0x1                   # bitmask
        self.TxPowerSetting = 0                         # attenuation enum: 0-11
        self.RxPowerSetting = 10                        # gain enum 0-14
        self.RampInit = 0                               # [ns] (ADC start delay), readonly
        self.RampTime = 70000                           # [ns] (complete time of one chirp)
        self.RampReset = 0                              # [ns] (excess time), readonly
        self.RampDelay = 0                              # [ns] (idle time), readonly
        self.OptParam1 = 1                              # power saving ON/OFF here
        self.OptParam2 = 0                              # ADC sampling rate, enum: 0=10MHz, 1=15MHz, 2=20MHz, 3=30MHz
        self.OptParam3 = 60                             # DC peak suppression [dB] (0-200)
        self.OptParam4 = 0                              # reserve

'==========================================================================='
class EthernetParams(object):
    'Object for Ethernet settings of the radar'
    def __init__(self):        
        self.MAC = None # readonly
        self.initValues()
    
    def initValues(self):
        self.DHCP = 0
        self.AutoIP = 0
        self.IP = ENET_DEFAULT_IP
        self.TcpPorts = [ENET_DEFAULT_TCP_PORTS[n] for n in range(ENET_MAX_TCP_PORTS)]
        self.UdpPorts = [ENET_DEFAULT_UDP_PORTS[n] for n in range(ENET_MAX_UDP_PORTS)]
        self.DefaultGateway = ENET_DEFAULT_GATEWAY
        self.SubnetMask = ENET_DEFAULT_SUBNET_MASK
        self.SntpMode = ENET_SNTP_OFF
        self.NtpServer = "0.0.0.0"
        self.MulticastGroups = ENET_DEFAULT_MULTICAST_GROUPS
        self.UdpMcPort = ENET_UDP_MULTICAST_PORT
        self.UdpBcPort = ENET_UDP_BROADCAST_PORT
            
    def getIpAsList(self, ip=None):
        if not ip:
            ip = self.IP
        return [int(n) for n in ip.split(".")]
    
    def getIpAsStr(self, ip):
        return str(ip[0]) + "." + str(ip[1]) + "." + str(ip[2]) + "." + str(ip[3])
    
'==========================================================================='
'Objects for reading detection and tracking data'
class Target(object):
    idNumber = None     # target ID
    rangeBin = None     # used by detections
    dopplerBin = None   # used by detections
    tarRange = None     # result of tracking
    speed = None        # result of tracking
    aziAngle = None     # azimuth angle [deg]
    eleAngle = None     # elevation angle [deg] (only != 0 for MIMO radar cubes)
    magnitude = None    # target magnitude
    lifeTime = None     # how often target was found again (tracking)
    inferenceResult = None # results of inference when DSP with NN is available and DspDopplerProc = 1 (tracking)
    dopplerSpectra = None  # complex or magnitude values of doppler spectra of tracks
        
class RadarTargets(object):
    def __init__(self, tracks=False):
        self.time = 0
        self.sysDopplerBin = 0  # doppler bin representing estimated radar system speed
        self.sysSpeed = 0       # interpolated estimated radar system speed [m/s*100]
        self.numTargets = 0
        
        if tracks:
            self.targets = [Target() for _ in range(MAX_NUM_TRACKS)]
        else:
            self.targets = [Target() for _ in range(MAX_NUM_TARGETS)]
        

