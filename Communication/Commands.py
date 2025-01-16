# -*- coding: utf-8 -*-
'''
Created on 06.01.2022

@author: IMST GmbH
'''

from Communication.CRC import CRC16
from time import sleep, time
import Parameters as Par


CMD_GET_ERRORS                  = "CMD_GET_ERRORS"
CMD_GET_ERROR_LOGS              = "CMD_GET_ERROR_LOGS"
CMD_RESET_ERROR_LOGS            = "CMD_RESET_ERROR_LOGS"
CMD_GET_ERROR_LOG_TABLE         = "CMD_GET_ERROR_LOG_TABLE"
CMD_RESET_ERROR_LOG_TABLE       = "CMD_RESET_ERROR_LOG_TABLE"
CMD_INFO                        = "CMD_INFO"
CMD_GET_SYS_TIME                = "CMD_GET_SYS_TIME"
CMD_SET_SYS_TIME                = "CMD_SET_SYS_TIME"
CMD_GET_RADAR_PARAMS            = "CMD_GET_RADAR_PARAMS"
CMD_SET_RADAR_PARAMS            = "CMD_SET_RADAR_PARAMS"
CMD_SET_RADAR_PARAMS_NO_EEP     = "CMD_SET_RADAR_PARAMS_NO_EEP"
CMD_RESET_RADAR_PARAMS          = "CMD_RESET_RADAR_PARAMS"
CMD_GET_RADAR_RESOLUTION        = "CMD_GET_RADAR_RESOLUTION"
CMD_GET_FRONTEND_PARAMS         = "CMD_GET_FRONTEND_PARAMS"
CMD_SET_FRONTEND_PARAMS         = "CMD_SET_FRONTEND_PARAMS"
CMD_SET_FRONTEND_PARAMS_NO_EEP  = "CMD_SET_FRONTEND_PARAMS_NO_EEP"
CMD_GET_FE_SENSORS              = "CMD_GET_FE_SENSORS"    # added to get the sensor temperature Nov 22nd 2022
CMD_RESET_FRONTEND_PARAMS       = "CMD_RESET_FRONTEND_PARAMS"
CMD_RESET_FRONTEND              = "CMD_RESET_FRONTEND"
CMD_GET_ETHERNET_CONFIG         = "CMD_GET_ETHERNET_CONFIG"
CMD_SET_ETHERNET_CONFIG         = "CMD_SET_ETHERNET_CONFIG"
CMD_SET_ETHERNET_CONFIG_NO_EEP  = "CMD_SET_ETHERNET_CONFIG_NO_EEP"
CMD_RESET_ETHERNET_CONFIG       = "CMD_RESET_ETHERNET_CONFIG"
CMD_GET_STREAM                  = "CMD_GET_STREAM"
CMD_START_ETHERNET_STREAM       = "CMD_START_ETHERNET_STREAM"
CMD_STOP_ETHERNET_STREAM        = "CMD_STOP_ETHERNET_STREAM"
CMD_STOP_USB_STREAM             = "CMD_STOP_USB_STREAM"
CMD_GET_MULTI_DATA_STREAM       = "CMD_GET_MULTI_DATA_STREAM"
CMD_CONFIGURE_STREAM            = "CMD_CONFIGURE_STREAM"
CMD_TRIGGER_STREAM              = "CMD_TRIGGER_STREAM"
CMD_TRIG_MEAS                   = "CMD_TRIG_MEAS"
CMD_READ_DATA                   = "CMD_READ_DATA"
CMD_READ_RAW_DATA               = "CMD_READ_RAW_DATA"
CMD_READ_RANGE_DATA             = "CMD_READ_RANGE_DATA"
CMD_READ_DOPPLER_DATA           = "CMD_READ_DOPPLER_DATA"
CMD_READ_RANGE_DOPPLER_MAP      = "CMD_READ_RANGE_DOPPLER_MAP"
CMD_READ_PEAK_MAP               = "CMD_READ_PEAK_MAP"
CMD_READ_CFAR_MAP               = "CMD_READ_CFAR_MAP"
CMD_READ_ALL_MAPS               = "CMD_READ_ALL_MAPS"
CMD_READ_DETECTIONS             = "CMD_READ_DETECTIONS"
CMD_READ_TRACKS                 = "CMD_READ_TRACKS"
CMD_READ_TRACKED_DOPPLER_SPECTRA= "CMD_READ_TRACKED_DOPPLER_SPECTRA"

CMD_CONFIG_SECTOR_MAP           = "CMD_CONFIG_SECTOR_MAP"
CMD_GET_SECTOR_MAP              = "CMD_GET_SECTOR_MAP"
CMD_SET_SECTOR_MAP              = "CMD_SET_SECTOR_MAP"

CMD_FW_UPD_START                = "CMD_FW_UPD_START"
CMD_FW_UPD_ABORT                = "CMD_FW_UPD_ABORT"
CMD_FW_UPD_DATA32               = "CMD_FW_UDP_DATA32"
CMD_FW_UPD_DATA64               = "CMD_FW_UDP_DATA64"
CMD_FW_UPD_DATA128              = "CMD_FW_UDP_DATA128"
CMD_FW_UPD_DATA256              = "CMD_FW_UDP_DATA256"
CMD_FW_UPD_DATA512              = "CMD_FW_UDP_DATA512"
CMD_FW_UPD_DATA1024             = "CMD_FW_UDP_DATA1024"
CMD_FW_UPD_FLASH_START          = "CMD_FW_UPD_FLASH_START"

# Command Return States
CMD_STATE_OK                    = 0x0000
CMD_STATE_CRC_ERROR             = 0x0001
CMD_STATE_WRONG_RX_DATA         = 0x0002        # received data was not ok
CMD_STATE_MEAS_TIMEOUT          = 0x0004        # measurement took too long or wasn't performed by radar core
CMD_STATE_FE_ERROR              = 0x0008        # problem with frontend (e.g. SPI communication)
CMD_STATE_FE_TEMP_ERROR         = 0x0010        # frontend temperature error, so it was shutdown and no measurement was performed
CMD_STATE_ACUTE_GLOBAL_ERROR    = 0x0100        # there is a global acute error pending
CMD_STATE_GLOBAL_ERROR_LOGGED   = 0x0200        # a global error has been logged
CMD_STATE_FW_UPD_ERROR          = 0x1000        # error during uploading firmware update

UNKOWN_CMD_ID                   = 0xE0F0
ACK_SIZE = 4
CRC_SIZE = 2

RADAR_MAX_BUF_SIZE = 40*1024  # [bytes]

class Commands(object):
    
    def __init__(self, infoParams=None, radarParams=None, frontendParams=None, enetParams=None, interface=None, useCrc=True):
        
        self.infoParams = infoParams
        if self.infoParams is None:
            self.infoParams = Par.InfoParameters()
        
        self.radarParams = radarParams
        if self.radarParams is None:
            self.radarParams = Par.RadarParameters()
            
        self.frontendParams = frontendParams
        if self.frontendParams is None:
            self.frontendParams = Par.FrontendParameters()
            
        self.enetParams = enetParams
        if self.enetParams is None:
            self.enetParams = Par.EthernetParams()
        
        self.detections = Par.RadarTargets()
        self.tracks = Par.RadarTargets(tracks=True)
        
        self.myInterface = interface
        
        self.useCrc = useCrc    # if True, CRC16 is used for data transmission, else not
        self.crc16 = CRC16()
        
        self.cmd_list = {}
        self.cmd_list[CMD_GET_ERRORS]               = (0xE000, self.cmd_getErrors)
        self.cmd_list[CMD_GET_ERROR_LOGS]           = (0xE001, self.cmd_getErrorLogs)
        self.cmd_list[CMD_RESET_ERROR_LOGS]         = (0xE002, self.cmd_resetErrorLogs)
        self.cmd_list[CMD_GET_ERROR_LOG_TABLE]      = (0xE003, self.cmd_getErrorLogTable)
        self.cmd_list[CMD_RESET_ERROR_LOG_TABLE]    = (0xE004, self.cmd_resetErrorLogTable)
        
        self.cmd_list[CMD_INFO]                     = (0x0001, self.cmd_getInfo)
        self.cmd_list[CMD_GET_SYS_TIME]             = (0x0003, self.cmd_getSysTime)
        self.cmd_list[CMD_SET_SYS_TIME]             = (0x0004, self.cmd_setSysTime)
        
        self.cmd_list[CMD_GET_RADAR_PARAMS]         = (0x000A, self.cmd_getRadarParams)
        self.cmd_list[CMD_SET_RADAR_PARAMS]         = (0x000B, self.cmd_setRadarParams)
        self.cmd_list[CMD_SET_RADAR_PARAMS_NO_EEP]  = (0x800B, self.cmd_setRadarParams)
        self.cmd_list[CMD_RESET_RADAR_PARAMS]       = (0x000C, self.cmd_resetRadarParams)
        self.cmd_list[CMD_GET_RADAR_RESOLUTION]     = (0x000D, self.cmd_getRadarResolution)
        
        self.cmd_list[CMD_GET_FRONTEND_PARAMS]      = (0x0010, self.cmd_getFrontendParams)
        self.cmd_list[CMD_SET_FRONTEND_PARAMS]      = (0x0011, self.cmd_setFrontendParams)
        self.cmd_list[CMD_SET_FRONTEND_PARAMS_NO_EEP] = (0x8011, self.cmd_setFrontendParams)
        self.cmd_list[CMD_RESET_FRONTEND_PARAMS]    = (0x0012, self.cmd_resetFrontendParams)
        self.cmd_list[CMD_RESET_FRONTEND]           = (0x0013, self.cmd_resetFrontend)
        self.cmd_list[CMD_GET_FE_SENSORS]           = (0xFE01, self.cmd_getFeSensors)   # added to get the sensor temperature Nov 22nd 2022
    
        
        self.cmd_list[CMD_GET_ETHERNET_CONFIG]      = (0x0020, self.cmd_getEthernetConfig)
        self.cmd_list[CMD_SET_ETHERNET_CONFIG]      = (0x0021, self.cmd_setEthernetConfig)
        self.cmd_list[CMD_SET_ETHERNET_CONFIG_NO_EEP] = (0x8021, self.cmd_setEthernetConfig)
        self.cmd_list[CMD_RESET_ETHERNET_CONFIG]    = (0x0022, self.cmd_resetEthernetConfig)
        self.cmd_list[CMD_GET_STREAM]               = (0x0023, self.cmd_getStream)
        self.cmd_list[CMD_START_ETHERNET_STREAM]    = (0x0024, self.cmd_startEthernetStream)
        self.cmd_list[CMD_STOP_ETHERNET_STREAM]     = (0x0025, self.cmd_stopEthernetStream)
        self.cmd_list[CMD_STOP_USB_STREAM]          = (0x0026, self.cmd_stopUsbStream)
        self.cmd_list[CMD_GET_MULTI_DATA_STREAM]    = (0x0027, self.cmd_getMultiDataStream)
        self.cmd_list[CMD_CONFIGURE_STREAM]         = (0x0028, self.cmd_configureStream)
        self.cmd_list[CMD_TRIGGER_STREAM]           = (0x0029, self.cmd_triggerStream)

        self.cmd_list[CMD_READ_DATA]                = (0x0030, self.cmd_readData)
        self.cmd_list[CMD_READ_RAW_DATA]            = (0x0031, self.cmd_readRawData)
        self.cmd_list[CMD_READ_RANGE_DATA]          = (0x0032, self.cmd_readRangeData)
        self.cmd_list[CMD_READ_DOPPLER_DATA]        = (0x0033, self.cmd_readDopplerData)
        self.cmd_list[CMD_READ_RANGE_DOPPLER_MAP]   = (0x0034, self.cmd_readRangeDopplerMap)
        self.cmd_list[CMD_READ_PEAK_MAP]            = (0x0035, self.cmd_readPeakMap)
        self.cmd_list[CMD_READ_CFAR_MAP]            = (0x0036, self.cmd_readCfarMap)
        self.cmd_list[CMD_READ_ALL_MAPS]            = (0x0037, self.cmd_readAllMaps)
        self.cmd_list[CMD_READ_DETECTIONS]          = (0x0038, self.cmd_readDetections)
        self.cmd_list[CMD_READ_TRACKS]              = (0x0039, self.cmd_readTracks)
        self.cmd_list[CMD_READ_TRACKED_DOPPLER_SPECTRA] = (0x003A, self.cmd_readTrackedDopplerSpectra)

        self.cmd_list[CMD_CONFIG_SECTOR_MAP]        = (0x0040, self.cmd_configSectorMap)
        self.cmd_list[CMD_GET_SECTOR_MAP]           = (0x0041, self.cmd_getSectorMap)
        self.cmd_list[CMD_SET_SECTOR_MAP]           = (0x0042, self.cmd_setSectorMap)
        
        self.cmd_list[CMD_FW_UPD_START]             = (0xFDA0, self.cmd_fwUpdStart)
        self.cmd_list[CMD_FW_UPD_ABORT]             = (0xFDA1, self.cmd_fwUpdAbort)
        self.cmd_list[CMD_FW_UPD_DATA32]            = (0xFDA2, self.cmd_fwUpdData)
        self.cmd_list[CMD_FW_UPD_DATA64]            = (0xFDA3, self.cmd_fwUpdData)
        self.cmd_list[CMD_FW_UPD_DATA128]           = (0xFDA4, self.cmd_fwUpdData)
        self.cmd_list[CMD_FW_UPD_DATA256]           = (0xFDA5, self.cmd_fwUpdData)
        self.cmd_list[CMD_FW_UPD_DATA512]           = (0xFDA6, self.cmd_fwUpdData)
        self.cmd_list[CMD_FW_UPD_DATA1024]          = (0xFDA7, self.cmd_fwUpdData)
        self.cmd_list[CMD_FW_UPD_FLASH_START]       = (0xFDA8, self.cmd_fwUpdFlashStart)
        # ...
        
        self.curCmdCode = None  # to save current used command code for comparison
        self.stateRcvd = 0      # to save current received radar state for later

    '-----------------------------------------------------------------------------'
    def paramsAccepted(self):
        return self.stateRcvd & CMD_STATE_WRONG_RX_DATA == 0
    
    '-----------------------------------------------------------------------------'
    def hasRadarError(self):
        return self.stateRcvd & (CMD_STATE_ACUTE_GLOBAL_ERROR | CMD_STATE_GLOBAL_ERROR_LOGGED)

    '-----------------------------------------------------------------------------'
    def setInterface(self, interface):
        self.myInterface = interface
        
    '-----------------------------------------------------------------------------'
    def getInterface(self):
        return self.myInterface
    
    '-----------------------------------------------------------------------------'
    def executeCmd(self, cmdID, *opt):
        if self.myInterface is None:
            raise CommandError("No interface defined")
        # get cmd ID string if int was entered
        if type(cmdID) == int:
            for cmd in self.cmd_list.keys():
                if self.cmd_list[cmd][0] == cmdID:
                    cmdID = cmd                            
        if not cmdID in self.cmd_list:
            raise CommandError("Invalid command ID: {}".format(cmdID))
        # Get command code and function
        code, func = self.cmd_list[cmdID]
        # save code for comparison
        self.curCmdCode = code
        # reset state
        self.stateRcvd = 0
        # Clear TX and RX buffer
        self.myInterface.clearBuffer()
        # Add command code to TX buffer
        self.myInterface.TxU16(code)
        # Perform command
        ret = func(*opt)
        # check returned state
        self.onRadarState()
        return ret

    '-----------------------------------------------------------------------------'
    def onRadarState(self):
        if self.stateRcvd & CMD_STATE_CRC_ERROR:
            raise CommandError("CRC error returned by Command 0x%X"%self.curCmdCode)
        elif self.stateRcvd & CMD_STATE_MEAS_TIMEOUT:
            raise CommandError("Measurement Timeout in Command 0x%X"%self.curCmdCode)
        elif self.stateRcvd & CMD_STATE_FW_UPD_ERROR:
            raise CommandError("Firmware Update Error in Command 0x%X"%self.curCmdCode)
                
    '-----------------------------------------------------------------------------'
    def Transmit(self):
        'Wrapper for interface transmit function'
        if self.useCrc: # calculate CRC if enabled
            self.crc16.reset()
            self.crc16.process_buf(self.myInterface.getTxBuf(), self.myInterface.getTxCount())
            # insert CRC value at the end, no further Tx function should be called because counter wasn't increased            
            crc_bytes = self.crc16.get_crc_value_as_byte_list()
            self.myInterface.TxU8(crc_bytes[0])
            self.myInterface.TxU8(crc_bytes[1])            
        self.myInterface.Transmit(False) # TODO: always reopen interface?
    
    '-----------------------------------------------------------------------------'
    def Receive(self, rxLen, withAck=True, withCRC=True, checkCRC=True, lessOk=False):
        'Wrapper for interface receive function which always reads ACK and state'
        'rxLen : number of bytes expected'
        'withAck : if True an acknowledge is expected. In case CRC is used, it will'
        'be reset and expected. If False it can be useful for multiple calls of Receive in commands.'
        'withCRC : if CRC is enabled this flag determines if a CRC should be expected'
        'at the end or not.'        
        'checkCRC : only used if CRC is enabled, if False it will not be checked'
        'lessOk: if True, less than requested bytes are Ok also (Ethernet)'
        nRx = rxLen
        nAdd = 0
        if withAck:
            nAdd += ACK_SIZE
        if self.useCrc and withCRC:
            nAdd += CRC_SIZE
        rL = self.myInterface.Receive(nRx+nAdd, closeInterface=False, lessOk=lessOk)
        
        if not lessOk and rL < nRx:
            if rL == nAdd:
                # maybe measurement timeout
                cmdId = self.myInterface.RxU16()
                self.stateRcvd = self.myInterface.RxU16()
                self.onRadarState()
            raise Exception(self.myInterface.getErrorString())
        
        'calculate and check CRC value if enabled'
        if self.useCrc:
            if withAck:   # only reset on start of command
                self.crc16.reset()

            if checkCRC:    # enable checking if it is the only or last call of Receive
                self.crc16.process_buf(self.myInterface.getRxBuf(), self.myInterface.getNumReceived())
                if self.crc16.get_crc_value() != 0:
                    raise CommandError("CRC Error")
        
        'read acknowledge and state word if enabled'
        if withAck:
            cmdId = self.myInterface.RxU16()
            self.stateRcvd = self.myInterface.RxU16()
            rL -= ACK_SIZE
            if cmdId != self.curCmdCode:
                if cmdId == UNKOWN_CMD_ID:
                    raise CommandError("Radar does not know command: {}".format(hex(self.curCmdCode)))
                else:
                    raise CommandError("Command returned wrong ID! Sent: {}, Received: {}".format(hex(self.curCmdCode), hex(cmdId)))
        
        if withCRC:
            rL -= CRC_SIZE
        
        'not received desired number of bytes, check for state here which could raise exception'
        if rxLen > 0 and not lessOk and rL < rxLen:
            self.onRadarState()
            'no state error? raise another exception'
            raise Exception("Wrong data length.")
        return rL
        
    '-----------------------------------------------------------------------------'
    def Transceive(self, rxLen=0, delaySeconds=0.0, rxLessOk=False):
        self.Transmit()
        if delaySeconds > 0:
            sleep(delaySeconds)
        return self.Receive(rxLen, lessOk=rxLessOk)
        
    '-----------------------------------------------------------------------------'
    def cmd_getErrors(self):
        self.Transceive(34)    # (1+16)*2
        
        gMask = self.myInterface.RxU16()
        masks = []
        for _ in range(16):
            masks.append(self.myInterface.RxU16())
        return (gMask, masks)

    '-----------------------------------------------------------------------------'
    def cmd_getErrorLogs(self):
        self.Transceive(34)    # (1+16)*2
        
        gMask = self.myInterface.RxU16()
        masks = []
        for _ in range(16):
            masks.append(self.myInterface.RxU16())
        return (gMask, masks)

    '-----------------------------------------------------------------------------'
    def cmd_resetErrorLogs(self, resetMask=0xFFFF):
        self.myInterface.TxU16(resetMask)
        self.Transceive()

    '-----------------------------------------------------------------------------'
    def cmd_getErrorLogTable(self):
        nMin = 2
        if self.myInterface._interfaceType == "Ethernet":
            rl = self.Transceive(100*(8+2)+2, lessOk=True)  # just try read whole table
            if rl < nMin:
                raise CommandError("Expected at least %d bytes!"%nMin)
            nErr = self.myInterface.RxU16()
        else:   # USB
            self.Transmit()
            rl = self.Receive(nMin, withCRC=False, checkCRC=False)
            
            if rl >= nMin:
                nErr = self.myInterface.RxU16()
                # receive rest
                rest = 10 * nErr - (rl - nMin)
                self.Receive(rest, withAck=False, withCRC=True, checkCRC=True)
        
        errLog = []
        for _ in range(nErr):
            errLog.append((self.myInterface.RxU64(), self.myInterface.RxU16()))     # time [ms], error
            
        return errLog

    '-----------------------------------------------------------------------------'
    def cmd_resetErrorLogTable(self):
        self.Transceive()

    '-----------------------------------------------------------------------------'
    def cmd_getInfo(self):
        self.Transceive(5*4)
        self.infoParams.deviceNumber       = self.myInterface.RxU32()
        self.infoParams.frontendConnected  = self.myInterface.RxU32()
        self.infoParams.fwVersion          = self.myInterface.RxU32()
        self.infoParams.fwRevision         = self.myInterface.RxU32()
        self.infoParams.fwDate             = self.myInterface.RxU32()
                    
        return self.infoParams

    '-----------------------------------------------------------------------------'
    
    def cmd_getFeSensors(self):

 

        self.Transceive(4*4)  # Expecting 16 bytes

        response = {}

        response["FeSensor_1"] = self.myInterface.RxI32()

        response["FeSensor_2"] = self.myInterface.RxI32()

        response["FeSensor_3"] = self.myInterface.RxI32()

        response["FeSensor_4"] = self.myInterface.RxI32()

        return response
    
    def cmd_getSysTime(self):
        self.Transceive(8)        
        return self.myInterface.RxU64()
        
    '-----------------------------------------------------------------------------'
    def cmd_setSysTime(self, t=None):
        if t is None:
            t = int(time()*1000)
        self.myInterface.TxU64(t)
        self.Transceive()
        return t

    '-----------------------------------------------------------------------------'
    def cmd_getRadarParams(self):
        rp = self.radarParams
        self.Transceive(60)
        rp.RadarCube            = self.myInterface.RxU16()
        rp.ContinuousMeas       = self.myInterface.RxU8()
        rp.MeasInterval         = self.myInterface.RxU16()
        rp.Processing           = self.myInterface.RxU16()
        rp.RangeWinFunc         = self.myInterface.RxU16()
        rp.DopplerWinFunc       = self.myInterface.RxU16()
        rp.DopplerFftShift      = self.myInterface.RxU8()
        rp.MinRangeBin          = self.myInterface.RxU16()
        rp.MaxRangeBin          = self.myInterface.RxU16()
        rp.MinDopplerBin        = self.myInterface.RxI16()
        rp.MaxDopplerBin        = self.myInterface.RxI16()
        rp.CfarWindowSize       = self.myInterface.RxU16()
        rp.CfarGuardInt         = self.myInterface.RxU16()
        rp.RangeCfarThresh      = self.myInterface.RxU16()
        rp.TriggerThresh        = self.myInterface.RxI16()  # !
        rp.PeakSearchThresh     = self.myInterface.RxU16()
        rp.SuppressStaticTargets= self.myInterface.RxU16()
        rp.MaxTargets           = self.myInterface.RxU16()
        rp.MaxTracks            = self.myInterface.RxU16()
        rp.MaxHorSpeed          = self.myInterface.RxU16()
        rp.MaxVerSpeed          = self.myInterface.RxU16()
        rp.MaxAccel             = self.myInterface.RxU16()
        rp.MaxRangeError        = self.myInterface.RxU16()
        rp.MinConfirm           = self.myInterface.RxU16()
        rp.TargetSize           = self.myInterface.RxU16()
        rp.MergeLimit           = self.myInterface.RxU16()
        rp.SectorFiltering      = self.myInterface.RxU8()
        rp.SpeedEstimation      = self.myInterface.RxU16()
        rp.DspDopplerProc       = self.myInterface.RxU8()
        rp.RxChannels           = self.myInterface.RxU16()
        rp.CfarSelect           = self.myInterface.RxU16()
        rp.DopplerCfarThresh    = self.myInterface.RxU16()
        rp.updateInternals()
        return rp

    '-----------------------------------------------------------------------------'
    def cmd_setRadarParams(self, rp=None):
        update = True
        if rp is None:
            update = False
            rp = self.radarParams
        
        self.myInterface.TxU16(rp.RadarCube)
        self.myInterface.TxU8(rp.ContinuousMeas)
        self.myInterface.TxU16(rp.MeasInterval)
        self.myInterface.TxU16(rp.Processing)
        self.myInterface.TxU16(rp.RangeWinFunc)
        self.myInterface.TxU16(rp.DopplerWinFunc)
        self.myInterface.TxU8(rp.DopplerFftShift)
        self.myInterface.TxU16(rp.MinRangeBin)
        self.myInterface.TxU16(rp.MaxRangeBin)
        self.myInterface.TxI16(rp.MinDopplerBin)
        self.myInterface.TxI16(rp.MaxDopplerBin)
        self.myInterface.TxU16(rp.CfarWindowSize)
        self.myInterface.TxU16(rp.CfarGuardInt)
        self.myInterface.TxU16(rp.RangeCfarThresh)
        self.myInterface.TxI16(rp.TriggerThresh)  # !
        self.myInterface.TxU16(rp.PeakSearchThresh)
        self.myInterface.TxU16(rp.SuppressStaticTargets)
        self.myInterface.TxU16(rp.MaxTargets)
        self.myInterface.TxU16(rp.MaxTracks)
        self.myInterface.TxU16(rp.MaxHorSpeed)
        self.myInterface.TxU16(rp.MaxVerSpeed)
        self.myInterface.TxU16(rp.MaxAccel)
        self.myInterface.TxU16(rp.MaxRangeError)
        self.myInterface.TxU16(rp.MinConfirm)
        self.myInterface.TxU16(rp.TargetSize)
        self.myInterface.TxU16(rp.MergeLimit)
        self.myInterface.TxU8(rp.SectorFiltering)
        self.myInterface.TxU16(rp.SpeedEstimation)
        self.myInterface.TxU8(rp.DspDopplerProc)
        self.myInterface.TxU16(rp.RxChannels)
        self.myInterface.TxU16(rp.CfarSelect)
        self.myInterface.TxU16(rp.DopplerCfarThresh)
        self.Transceive()
        
        if update:
            self.radarParams.__dict__.update(rp.__dict__)

    '-----------------------------------------------------------------------------'
    def cmd_resetRadarParams(self):
        self.Transceive()

    '-----------------------------------------------------------------------------'
    def cmd_getRadarResolution(self):
        self.Transceive(4*4)
        res = {}
        res["If"]       = self.myInterface.RxFloat()
        res["Range"]    = self.myInterface.RxFloat()
        res["Doppler"]  = self.myInterface.RxFloat()
        res["Speed"]    = self.myInterface.RxFloat()
        return res

    '-----------------------------------------------------------------------------'
    def cmd_getFrontendParams(self):
        fp = self.frontendParams
        self.Transceive(42)
        fp.MinFrequency         = self.myInterface.RxU32()
        fp.MaxFrequency         = self.myInterface.RxU32()
        fp.SignalType           = self.myInterface.RxU16()
        fp.TxChannelSelection   = self.myInterface.RxU16()
        fp.RxChannelSelection   = self.myInterface.RxU16()
        fp.TxPowerSetting       = self.myInterface.RxI16()
        fp.RxPowerSetting       = self.myInterface.RxI16()
        fp.RampInit             = self.myInterface.RxU32()
        fp.RampTime             = self.myInterface.RxU32()
        fp.RampReset            = self.myInterface.RxU32()
        fp.RampDelay            = self.myInterface.RxU32()
        fp.OptParam1            = self.myInterface.RxI16()
        fp.OptParam2            = self.myInterface.RxI16()
        fp.OptParam3            = self.myInterface.RxI16()
        fp.OptParam4            = self.myInterface.RxI16()
        return fp

  
    def calculate_crc(self, data):
        """
        Calculate the CRC checksum for a given data.
        This implementation assumes a simple sum-based CRC.
        Replace with the actual CRC algorithm used by the radar.
        """
        if isinstance(data, int):
            data = data.to_bytes(2, byteorder="big")
        crc = sum(data) & 0xFFFF  # Sum and mask to 16 bits
        return crc

            
    '-----------------------------------------------------------------------------'
    def cmd_setFrontendParams(self, fp=None):
        update = True
        if fp is None:
            fp = self.frontendParams
            update = False
        
        self.myInterface.TxU32(fp.MinFrequency)
        self.myInterface.TxU32(fp.MaxFrequency)
        self.myInterface.TxU16(fp.SignalType)
        self.myInterface.TxU16(fp.TxChannelSelection)
        self.myInterface.TxU16(fp.RxChannelSelection)
        self.myInterface.TxI16(fp.TxPowerSetting)
        self.myInterface.TxI16(fp.RxPowerSetting)
        self.myInterface.TxU32(fp.RampInit)
        self.myInterface.TxU32(fp.RampTime)
        self.myInterface.TxU32(fp.RampReset)
        self.myInterface.TxU32(fp.RampDelay)
        self.myInterface.TxI16(fp.OptParam1)
        self.myInterface.TxI16(fp.OptParam2)
        self.myInterface.TxI16(fp.OptParam3)
        self.myInterface.TxI16(fp.OptParam4)
        self.Transceive()
            
        if update:
            self.frontendParams.__dict__.update(fp.__dict__)

    '-----------------------------------------------------------------------------'
    def cmd_resetFrontendParams(self):
        self.Transceive()
    
    '-----------------------------------------------------------------------------'
    def cmd_resetFrontend(self):
        self.Transceive()

    '-----------------------------------------------------------------------------'
    def cmd_getEthernetConfig(self):
        self.Transceive(29 + Par.ENET_MAX_TCP_PORTS*2 + Par.ENET_MAX_UDP_PORTS*2 + Par.ENET_MAX_MULTICAST_GROUPS*4)
        ep = self.enetParams
        ep.DHCP = self.myInterface.RxU8()
        ep.AutoIP = self.myInterface.RxU8()
        ep.IP = ep.getIpAsStr( [self.myInterface.RxU8() for _ in range(4)] )
        for n in range(Par.ENET_MAX_TCP_PORTS):
            ep.TcpPorts[n] = self.myInterface.RxU16()
        for n in range(Par.ENET_MAX_UDP_PORTS):
            ep.UdpPorts[n] = self.myInterface.RxU16()
        ep.SubnetMask = ep.getIpAsStr( [self.myInterface.RxU8() for _ in range(4)] )
        ep.DefaultGateway = ep.getIpAsStr( [self.myInterface.RxU8() for _ in range(4)] )
        for m in range(Par.ENET_MAX_MULTICAST_GROUPS):
            ep.MulticastGroups[m] = ep.getIpAsStr( [self.myInterface.RxU8() for _ in range(4)] )
        ep.SntpMode = self.myInterface.RxU8()
        ep.NtpServer = ep.getIpAsStr( [self.myInterface.RxU8() for _ in range(4)] )
        
        ep.UdpMcPort = self.myInterface.RxU16()
        ep.UdpBcPort = self.myInterface.RxU16()
        ep.MAC = [self.myInterface.RxU8() for _ in range(6)]
        return ep

    '-----------------------------------------------------------------------------'
    def cmd_setEthernetConfig(self, ep=None):
        update = True
        if ep is None:
            ep = self.enetParams
            update = False
        
        self.myInterface.TxU8(ep.DHCP)
        self.myInterface.TxU8(ep.AutoIP)
        for ip in ep.getIpAsList():
            self.myInterface.TxU8(ip)
        for n in range(Par.ENET_MAX_TCP_PORTS):
            self.myInterface.TxU16(ep.TcpPorts[n])
        for n in range(Par.ENET_MAX_UDP_PORTS):
            self.myInterface.TxU16(ep.UdpPorts[n])
        for m in ep.getIpAsList(ep.SubnetMask):
            self.myInterface.TxU8(m)
        for dg in ep.getIpAsList(ep.DefaultGateway):
            self.myInterface.TxU8(dg)
        for mc in ep.MulticastGroups:
            for g in ep.getIpAsList(mc):
                self.myInterface.TxU8(g)
        self.myInterface.TxU8(ep.SntpMode)
        for i in ep.getIpAsList(ep.NtpServer):
            self.myInterface.TxU8(i)
        
        if update:
            self.enetParams.__dict__.update(ep.__dict__)

    '-----------------------------------------------------------------------------'
    def cmd_resetEthernetConfig(self):
        self.Transceive()

    '-----------------------------------------------------------------------------'
    def cmd_getStream(self, mask=0, opt=0):
        self.myInterface.TxU16(mask)
        self.myInterface.TxU16(opt)
        self.Transceive()

    '-----------------------------------------------------------------------------'
    def cmd_getMultiDataStream(self, mask, dataMask, chirp, rangeBin, dopplerFormat):
        self.myInterface.TxU16(mask)
        self.myInterface.TxU16(dataMask)
        self.myInterface.TxU16(chirp)
        self.myInterface.TxU16(rangeBin)
        self.myInterface.TxU16(dopplerFormat)
        self.Transceive()

    '-----------------------------------------------------------------------------'
    def cmd_startEthernetStream(self, streamCfg):
        opt = 0
        if self.radarParams.Processing == Par.PROC_NoProcessing:
            opt = streamCfg.ChirpRaw
        elif self.radarParams.Processing == Par.PROC_RangeFFT:
            opt = streamCfg.ChirpRange
        elif self.radarParams.Processing == Par.PROC_DopplerFFT:
            opt = streamCfg.RangeBin
        elif self.radarParams.Processing == Par.PROC_Tracking:
            opt = streamCfg.DopplerFormat

        self.myInterface.TxU16(streamCfg.Mask)
        self.myInterface.TxU16(opt)
        self.myInterface.TxU16(streamCfg.EnetType)
        self.myInterface.TxU16(streamCfg.Port)
        for val in streamCfg.getIpAsList():
            self.myInterface.TxU8(val)
        self.myInterface.TxU16(streamCfg.OwnPort)
        self.Transceive()
    
    '-----------------------------------------------------------------------------'
    def cmd_configureStream(self, streamCfg):
        self.myInterface.TxU16(streamCfg.DataMode)
        self.myInterface.TxU16(streamCfg.MeasMode)
        for d in streamCfg.Delays:
            self.myInterface.TxU32(d)
        self.myInterface.TxU16(streamCfg.Mask)
        self.myInterface.TxU16(streamCfg.DataMask)
        self.myInterface.TxU16(streamCfg.ChirpRange)
        self.myInterface.TxU16(streamCfg.RangeBin)
        self.myInterface.TxU16(streamCfg.DopplerFormat)
        self.Transceive()
    
    '-----------------------------------------------------------------------------'
    def cmd_triggerStream(self, newTime=None, timeMode=0, delayIndex=0):
        if newTime is None:
            newTime = int(time() * 1000)
        else:
            newTime = int(newTime)
        
        self.myInterface.TxU64(newTime)
        self.myInterface.TxU16(timeMode)
        self.myInterface.TxU16(delayIndex)
        self.Transceive()
    
    '-----------------------------------------------------------------------------'
    def cmd_stopEthernetStream(self, portType=3, port=0):
        self.myInterface.TxU16(portType)
        self.myInterface.TxU16(port)
        self.Transceive()
    
    '-----------------------------------------------------------------------------'
    def cmd_stopUsbStream(self):
        self.Transceive()
        
    '-----------------------------------------------------------------------------'
    def cmd_readData(self, dataMask, chirpNum=0, rangeBin=0, dopplerFormat=0):
        rp = self.radarParams
        
        self.myInterface.TxU16(dataMask)
        self.myInterface.TxU16(chirpNum)
        self.myInterface.TxU16(rangeBin)
        self.myInterface.TxU16(dopplerFormat)
        self.Transmit()
        
        # receive data dependent on interface
        if self.myInterface._interfaceType == "Ethernet":
            # receive first packet
            rcvd = self.Receive(RADAR_MAX_BUF_SIZE, withAck=True, withCRC=False, checkCRC=False, lessOk=True)
            # read till size of data in packet
            tMeas = self.myInterface.RxU64()
            dataSize = self.myInterface.RxU32() + 12 # consider time and size
            rest = dataSize + 2 - rcvd # +CRC
            while rest > 0:
                rest -= self.Receive(RADAR_MAX_BUF_SIZE, withAck=False, withCRC=False, checkCRC=False, lessOk=True)

        else: # USB
            # read till size of data in packet
            rcvd = self.Receive(12, withAck=True, withCRC=False, checkCRC=False, lessOk=False)
            tMeas = self.myInterface.RxU64()
            dataSize = self.myInterface.RxU32()
            rest = dataSize + 2 # +CRC
            self.Receive(rest, withAck=False, withCRC=False, checkCRC=False, lessOk=False)
                            
        # read into buffers according to enabled mask bits
        # for better performance, permanent buffers should be allocated before
        dataOut = {"Mask": dataMask}
        dataOut["Time"] = tMeas
            
        #********** raw data **********
        if dataMask == 0:
            nc = 1
            if chirpNum == 0xFFFF:  # read all chirps
                nc = rp._NumDopplerBins
            dataOut["Raw"] = []
            for _d in range(nc):
                chirp = {}
                for c in range(rp.getMaxNumRxChan()):
                    if ((1<<c) & rp.RxChannels > 0):
                        chirp[c] = []
                        for _s in range(rp._NumSamples):
                            chirp[c].append(self.myInterface.RxI16())
                dataOut["Raw"].append(chirp)
                            
        else:
            #********** range FFT ********** 
            if dataMask & 0x1:
                if rp.RadarCube <= Par.RCUBE_smpl2048_crp1_4rx:
                    # one chirp kernels
                    chan = bin(rp.RxChannels & 0x3).count("1")  # complex channels
                    nBytes = chan * rp._ActiveRangeBins * 4
                    chan = bin(rp.RxChannels & 0xC).count("1")  # magnitude channels
                    nBytes += chan * rp._ActiveRangeBins * 2
                    nBytes += 6
                    
                    dataOut["RFFT"] = {}
                    for c in range(4):
                        if ((1<<c) & rp.RxChannels) > 0:
                            dataOut["RFFT"][c] = []
                            if c < 2:
                                for _ in range(rp.MinRangeBin, rp.MaxRangeBin+1):
                                    dataOut["RFFT"][c].append(complex(self.myInterface.RxI16(), self.myInterface.RxI16()))
                            else:
                                for _ in range(rp.MinRangeBin, rp.MaxRangeBin+1):
                                    dataOut["RFFT"][c].append(self.myInterface.RxU16())
                    
                    dataOut["RFFT"]["chan"] = self.myInterface.RxU16()
                    dataOut["RFFT"]["rbin"] = self.myInterface.RxU16()
                    dataOut["RFFT"]["value"] = self.myInterface.RxU16()
                else:
                    nc = 1
                    if chirpNum == 0xFFFF:  # read all chirps
                        nc = rp._NumDopplerBins
                    dataOut["RFFT"] = []
                    for _d in range(nc):
                        chirp = {}
                        for c in range(rp.getMaxNumRxChan()):
                            if ((1<<c) & rp.RxChannels) > 0:
                                chirp[c] = []
                                for _r in range(rp.MinRangeBin, rp.MaxRangeBin+1):
                                    chirp[c].append(complex(self.myInterface.RxI16(), self.myInterface.RxI16()))
                        dataOut["RFFT"].append(chirp)
            
            #********** doppler FFT **********
            if dataMask & 0x2:
                dataOut["DFFT"] = []
                nr = 1
                if rangeBin == 0xFFFF:  # read data for each range bin
                    nr = rp._ActiveRangeBins
                for _ in range(nr):
                    spec = {}
                    for c in range(rp.getMaxNumRxChan()):
                        if ((1<<c) & rp.RxChannels) > 0:
                            spec[c] = []
                            for _ in rp._dBinIdxs:
                                spec.append(complex(self.myInterface.RxI16(), self.myInterface.RxI16()))
                    dataOut["DFFT"].append(spec)
                
            #********** magnitude map **********
            if dataMask & 0x4:
                dataOut["MagMap"] = []
                for _d in rp._dBinIdxs:
                    dataOut["MagMap"].append([])
                    for _r in range(rp.MinRangeBin, rp.MaxRangeBin+1):
                        dataOut["MagMap"][-1].append(self.myInterface.RxU16())
    
            #********** peak map **********
            if dataMask & 0x8:
                dataOut["PeakMap"] = []
                for _d in range(0, rp._NumDopplerBins):
                    dataOut["PeakMap"].append([])
                    for _r in range(int(rp._NumRangeBins>>5)):  # sent as longs
                        dataOut["PeakMap"][-1].append(self.myInterface.RxU32())
            
            #********** CFAR map **********
            if dataMask & 0x10:
                dataOut["CfarMap"] = []
                for _d in range(rp._NumDopplerBins):
                    dataOut["CfarMap"].append([])
                    for _r in range(int(rp._NumRangeBins>>5)):  # sent as longs
                        dataOut["CfarMap"][-1].append(self.myInterface.RxU32())
                        
            #********** detection data **********
            if dataMask & 0x20:
                self.detections.time = tMeas
                if self.radarParams.SpeedEstimation:
                    self.detections.sysDopplerBin = self.myInterface.RxI16()
                    self.detections.sysSpeed = self.myInterface.RxI16()
                self.detections.numTargets = self.myInterface.RxU16()
                # read list
                for n in range(self.detections.numTargets):
                    self.detections.targets[n].rangeBin = self.myInterface.RxU16()
                    self.detections.targets[n].dopplerBin = self.myInterface.RxI16()
                    self.detections.targets[n].magnitude = self.myInterface.RxU16()
                    self.detections.targets[n].aziAngle = self.myInterface.RxI16()
                    self.detections.targets[n].eleAngle = self.myInterface.RxI16()
                dataOut["Detections"] = self.detections
            
            #********** tracking data **********
            if dataMask & 0x40:
                self.tracks.time = tMeas
                self.tracks.dopplerFormat = dopplerFormat
                if self.radarParams.SpeedEstimation:
                    self.tracks.sysDopplerBin = self.myInterface.RxI16()
                    self.tracks.sysSpeed = self.myInterface.RxI16()
                self.tracks.numTargets = self.myInterface.RxU16()
                
                # read list
                self.tracks.dopplerSpectra = [None]*Par.MAX_NUM_TRACKS
                for n in range(self.tracks.numTargets):
                    self.tracks.targets[n].idNumber = self.myInterface.RxU16()
                    self.tracks.targets[n].tarRange = self.myInterface.RxFloat()
                    self.tracks.targets[n].speed = self.myInterface.RxFloat()
                    self.tracks.targets[n].magnitude = self.myInterface.RxU16()
                    self.tracks.targets[n].aziAngle = self.myInterface.RxFloat()
                    self.tracks.targets[n].eleAngle = self.myInterface.RxFloat()
                    self.tracks.targets[n].lifeTime = self.myInterface.RxU32()
                    if self.paramObj.radarParams.DspDopplerProc:
                        res = []
                        for _ in range(Par.NUM_NN_CLASSES):
                            res.append(self.myInterface.RxU16())
                        self.tracks.inferenceResult[n] = res
                        
                    if dopplerFormat == 1:
                        # read complex spectra for each enabled rx channel
                        self.tracks.dopplerSpectra[n] = [None]*rp.getMaxNumRxChan()
                        
                        for c in range(rp.getMaxNumRxChan()):
                            if ((1<<c) & rp.RxChannels) > 0:
                                self.tracks.dopplerSpectra[n][c] = []
                                for _ in range(rp._ActiveDopplerBins):
                                    self.tracks.dopplerSpectra[n][c].append(complex(self.myInterface.RxI16(), self.myInterface.RxI16()))
                            
                    elif dopplerFormat >= 2:
                        # read magnitude doppler spectrum
                        self.tracks.dopplerSpectra[n] = []
                        for _ in range(rp._ActiveDopplerBins):
                            self.tracks.dopplerSpectra[n].append(self.myInterface.RxU16())
                            
                dataOut["Tracks"] = self.tracks
        
        return dataOut
    
    '-----------------------------------------------------------------------------'
    def cmd_readRawData(self, chirpNum=0):
        if chirpNum > self.radarParams._NumDopplerBins-1:
            raise CommandError("Value not supported!")  # here only one chirp is read
        
        self.myInterface.TxU16(chirpNum)
          
        samples = self.radarParams._NumSamples
          
        self.Transceive(2*self.radarParams.getNumActiveRxChan()*samples+8)
        
        data = {}
        data["time"] = self.myInterface.RxU64()
        data["data"] = {}
        
        for c in range(self.radarParams.getMaxNumRxChan()):
            if ((1<<c) & self.radarParams.RxChannels > 0):
                data["data"][c] = []
                for _ in range(samples):
                    data["data"][c].append(self.myInterface.RxI16())
        
        return data
    
    '-----------------------------------------------------------------------------'
    def cmd_readRangeData(self, chirpNum=0):
        if chirpNum > self.radarParams._NumDopplerBins-1:
            raise CommandError("Value not supported!")  # here only one chirp is read

        self.myInterface.TxU16(chirpNum)
        
        data = {}
        
        if self.radarParams.RadarCube <= Par.RCUBE_smpl2048_crp1_4rx:
            # one chirp kernels
            chan = bin(self.radarParams.RxChannels & 0x3).count("1")  # complex channels
            nBytes = chan*self.radarParams._ActiveRangeBins*4
            chan = bin(self.radarParams.RxChannels & 0xC).count("1")  # magnitude channels
            nBytes += chan*self.radarParams._ActiveRangeBins*2
            nBytes += 14

            self.Transceive(nBytes)
            
            data["time"] = self.myInterface.RxU64()
            data["data"] = {}
            for c in range(4):
                if ((1<<c) & self.radarParams.RxChannels) > 0:
                    data["data"][c] = []
                    if c < 2:
                        for _ in range(self.radarParams._ActiveRangeBins):
                            data["data"][c].append(complex(self.myInterface.RxI16(), self.myInterface.RxI16()))
                    else:
                        for _ in range(self.radarParams._ActiveRangeBins):
                            data["data"][c].append(self.myInterface.RxU16())
            
            data["channel"] = self.myInterface.RxU16()
            data["rangeBin"] = self.myInterface.RxU16()
            data["mag"] = self.myInterface.RxU16()
            
        else:            
            self.Transceive(4*self.radarParams.getNumActiveRxChan()*self.radarParams._ActiveRangeBins+8)
            
            data["time"] = self.myInterface.RxU64()
            data["data"] = {}
            for c in range(self.radarParams.getMaxNumRxChan()):
                if ((1<<c) & self.radarParams.RxChannels) > 0:
                    data["data"][c] = []
                    for _ in range(self.radarParams._ActiveRangeBins):
                        data["data"][c].append(complex(self.myInterface.RxI16(), self.myInterface.RxI16()))
                            
        return data
        
    '-----------------------------------------------------------------------------'
    def cmd_readDopplerData(self, rangeBin=0):
        if rangeBin > self.radarParams._NumRangeBins-1:
            raise CommandError("Value not supported!")  # here only one spectrum is read
        
        self.myInterface.TxU16(rangeBin)
                 
        self.Transceive(4*self.radarParams.getNumActiveRxChan()*self.radarParams._ActiveDopplerBins+8)
        
        data = {}
        data["time"] = self.myInterface.RxU64()
        data["data"] = {}
         
        for c in range(self.radarParams.getMaxNumRxChan()):
            if ((1<<c) & self.radarParams.RxChannels) > 0:
                data["data"][c] = []
                for _ in range(self.radarParams._ActiveDopplerBins):
                    data["data"][c].append(complex(self.myInterface.RxI16(), self.myInterface.RxI16()))
        
        return data
    
    '-----------------------------------------------------------------------------'
    def cmd_readRangeDopplerMap(self):
        self.Transceive(self.radarParams._ActiveRangeBins*self.radarParams._ActiveDopplerBins*2 + 8)
        data = {}
        data["time"] = self.myInterface.RxU64()
        data["data"] = []
        for _d in range(self.radarParams._ActiveDopplerBins):
            data["data"].append([])
            for _r in range(self.radarParams._ActiveRangeBins):
                data["data"][-1].append(self.myInterface.RxU16())
                        
        return data
        
    '-----------------------------------------------------------------------------'
    def cmd_readPeakMap(self):
        nR = self.radarParams._NumRangeBins >> 3  # 1 bit for each bin
        
        self.Transceive(nR*self.radarParams._NumDopplerBins+8)
        data = {}
        data["time"] = self.myInterface.RxU64()
        data["data"] = []
        for _d in range(0, self.radarParams._NumDopplerBins):
            data["data"].append([])
            for _r in range(int(nR>>2)):  # sent as longs
                data["data"][-1].append(self.myInterface.RxU32())
        
        return data
    
    '-----------------------------------------------------------------------------'
    def cmd_readCfarMap(self):
        nR = self.radarParams._NumRangeBins >> 3    # 1 bit for each bin
        
        self.Transceive(nR*self.radarParams._NumDopplerBins+8)
        data = {}
        data["time"] = self.myInterface.RxU64()
        data["data"] = []    
        for _d in range(self.radarParams._NumDopplerBins):
            data["data"].append([])
            for _r in range(int(nR/4)):  # sent as longs
                data["data"][-1].append(self.myInterface.RxU32())
        
        return data
    
    '-----------------------------------------------------------------------------'
    def cmd_readAllMaps(self):
        nR = self.radarParams._NumRangeBins >> 3
        
        self.Transceive(8 + self.radarParams._ActiveRangeBins*self.radarParams._ActiveDopplerBins*2 + nR*self.radarParams._NumDopplerBins*2)
        data = {}
        data["time"] = self.myInterface.RxU64()
        
        # RD Map Data
        data["rdm_data"] = []
        for _d in range(self.radarParams._ActiveDopplerBins):
            data["rdm_data"].append([])
            for _r in range(self.radarParams._ActiveRangeBins):
                data["rdm_data"][-1].append(self.myInterface.RxU16())
        
        # Peak Map Data
        data["peak_data"] = []
        for _d in range(self.radarParams._NumDopplerBins):
            data["peak_data"].append([])
            for _r in range(int(nR/4)):
                data["peak_data"][-1].append(self.myInterface.RxU32())
                
        # CFAR Map Data
        data["cfar_data"] = []
        for _d in range(self.radarParams._NumDopplerBins):
            data["cfar_data"].append([])
            for _r in range(int(nR/4)):
                data["cfar_data"][-1].append(self.myInterface.RxU32())
        
        return data
    
    '-----------------------------------------------------------------------------'
    MAX_BYTES_DETECTIONS = ACK_SIZE + 10 + Par.MAX_NUM_TARGETS * 14 + CRC_SIZE
    def cmd_readDetections(self):
        ok = False

        minBytes = 10    # num detections + time
        if self.radarParams.SpeedEstimation:
            minBytes += 4
        
        if self.myInterface._interfaceType == "Ethernet":
            # just try to read maximum number of bytes
            rl = self.Transceive(self.MAX_BYTES_DETECTIONS, rxLessOk=True)
            if rl >= minBytes:
                self.detections.time = self.myInterface.RxU64()
                if self.radarParams.SpeedEstimation:
                    self.detections.sysDopplerBin = self.myInterface.RxI16()
                    self.detections.sysSpeed = self.myInterface.RxI16()
                self.detections.numTargets = self.myInterface.RxU16()
                ok = True
        else:
            # USB: read number of targets first
            self.Transmit()
            rl = self.Receive(minBytes, withCRC=False, checkCRC=False)
            
            if rl >= minBytes:
                self.detections.time = self.myInterface.RxU64()
                if self.radarParams.SpeedEstimation:
                    self.detections.sysDopplerBin = self.myInterface.RxI16()
                    self.detections.sysSpeed = self.myInterface.RxI16()
                self.detections.numTargets = self.myInterface.RxU16()
                
                # receive rest
                rest = self.detections.numTargets * 10 - (rl - minBytes)
                rl = self.Receive(rest, withAck=False, withCRC=True, checkCRC=True)
                if rl >= rest:
                    ok = True
        
        if ok:
            # read list
            for n in range(self.detections.numTargets):
                self.detections.targets[n].rangeBin = self.myInterface.RxU16()
                self.detections.targets[n].dopplerBin = self.myInterface.RxI16()
                self.detections.targets[n].magnitude = self.myInterface.RxU16()
                self.detections.targets[n].aziAngle = self.myInterface.RxI16()
                self.detections.targets[n].eleAngle = self.myInterface.RxI16()
        else:
            self.detections.numTargets = 0
        
        return self.detections
    
    '-----------------------------------------------------------------------------'
    MAX_BYTES_TRACKS = ACK_SIZE + 10 + Par.MAX_NUM_TRACKS * 40 + CRC_SIZE
    def cmd_readTracks(self):
        ok = False
        minBytes = 10    # num targets + time
        if self.radarParams.SpeedEstimation > 0:
            minBytes += 4

        if self.myInterface._interfaceType == "Ethernet":
            # just try to read maximum number of tracks
            rl = self.Transceive(self.MAX_BYTES_TRACKS, rxLessOk=True)
            if rl >= minBytes:
                self.tracks.time = self.myInterface.RxU64()
                self.tracks.numTargets = self.myInterface.RxU16()
                ok = True
        else:
            # USB: read number of targets first
            self.Transmit()
            rl = self.Receive(minBytes, withCRC=False, checkCRC=False)
            
            if rl >= minBytes:
                self.tracks.time = self.myInterface.RxU64()
                self.tracks.numTargets = self.myInterface.RxU16()
                
                # receive rest
                rest = self.tracks.numTargets * 24 - (rl - minBytes)
                if self.radarParams.DspDopplerProc:
                    rest += self.tracks.numTargets * 16
                rl = self.Receive(rest, withAck=False, withCRC=True, checkCRC=True)
                if rl >= rest:
                    ok = True
                    
        if ok:
            # read list
            if self.radarParams.SpeedEstimation > 0:
                self.tracks.sysDopplerBin = self.myInterface.RxI16()
                self.tracks.sysSpeed = self.myInterface.RxI16()
            for n in range(self.tracks.numTargets):
                self.tracks.targets[n].idNumber = self.myInterface.RxU16()
                self.tracks.targets[n].tarRange = self.myInterface.RxFloat()
                self.tracks.targets[n].speed = self.myInterface.RxFloat()
                self.tracks.targets[n].magnitude = self.myInterface.RxU16()
                self.tracks.targets[n].aziAngle = self.myInterface.RxFloat()
                self.tracks.targets[n].eleAngle = self.myInterface.RxFloat()
                self.tracks.targets[n].lifeTime = self.myInterface.RxU32()
                if self.radarParams.DspDopplerProc:
                    res = []
                    for _ in range(Par.NUM_NN_CLASSES):
                        res.append(self.myInterface.RxU16())
                    self.tracks.targets[n].inferenceResult = res
        else:
            self.tracks.numTargets = 0
            
        return self.tracks
    
    '-----------------------------------------------------------------------------'
    def cmd_readTrackedDopplerSpectra(self, spectra_format=2):
        ok = False
        
        tarBytes = 24
        if self.radarParams.DspDopplerProc:
            tarBytes += 16
        if spectra_format == 1: # complex
            tarBytes += self.radarParams._ActiveDopplerBins * self.radarParams.getNumActiveRxChan() * 4
        elif spectra_format == 2: # magnitudes
            tarBytes += self.radarParams._ActiveDopplerBins * 2
        
        minBytes = 10   # num target + time
        if self.radarParams.SpeedEstimation > 0:
            minBytes += 4
        maxBytes = minBytes + tarBytes * Par.MAX_NUM_TRACKS
        if self.useCrc:
            maxBytes += CRC_SIZE
        
        self.myInterface.TxU16(spectra_format)
        
        self.Transmit()
        
        if self.myInterface._interfaceType == "Ethernet":
            rl = self.Receive(maxBytes, withAck=True, withCRC=False, checkCRC=False, lessOk=True)
        else:
            rl = self.Receive(minBytes, withAck=True, withCRC=False, checkCRC=False, lessOk=False)
            
        if rl >= minBytes:
            self.tracks.time = self.myInterface.RxU64()
            if self.radarParams.SpeedEstimation > 0:
                self.tracks.sysDopplerBin = self.myInterface.RxI16()
                self.tracks.sysSpeed = self.myInterface.RxI16()
            self.tracks.numTargets = self.myInterface.RxU16()
            
            rest = tarBytes * self.tracks.numTargets - (rl - minBytes)
            
            while rest > 0:
                try:
                    rest -= self.Receive(rest, withAck=False, withCRC=False, checkCRC=False, lessOk=True)
                except Exception as E:
                    raise CommandError(E)
            
            if self.useCrc:
                self.crc16.process_buf(self.myInterface.getRxBuf(), self.myInterface.getNumReceived())
                if self.crc16.get_crc_value() != 0:
                    raise CommandError("CRC Error")
            
            ok = True
        
        if ok:
            # read list
            for n in range(self.tracks.numTargets):
                self.tracks.targets[n].idNumber = self.myInterface.RxU16()
                self.tracks.targets[n].tarRange = self.myInterface.RxFloat()
                self.tracks.targets[n].speed = self.myInterface.RxFloat()
                self.tracks.targets[n].magnitude = self.myInterface.RxU16()
                self.tracks.targets[n].aziAngle = self.myInterface.RxFloat()
                self.tracks.targets[n].eleAngle = self.myInterface.RxFloat()
                self.tracks.targets[n].lifeTime = self.myInterface.RxU32()
                if self.radarParams.DspDopplerProc:
                    res = []
                    for _ in range(Par.NUM_NN_CLASSES):
                        res.append(self.myInterface.RxU16())
                    self.tracks.targets[n].inferenceResult = res
                    
                if spectra_format == 1:
                    # read complex spectra for each enabled rx channel
                    self.tracks.targets[n].dopplerSpectra = {}
                    
                    for c in range(self.radarParams.getMaxNumRxChan()):
                        if ((1<<c) & self.radarParams.RxChannels) > 0:
                            self.tracks.targets[n].dopplerSpectra[c] = []
                            for _ in range(self.radarParams._ActiveDopplerBins):
                                self.tracks.targets[n].dopplerSpectra[c].append(complex(self.myInterface.RxI16(), self.myInterface.RxI16()))
                        
                elif spectra_format == 2:
                    # read one magnitude doppler spectrum
                    self.tracks.targets[n].dopplerSpectra = []
                    for _ in range(self.radarParams._ActiveDopplerBins):
                        self.tracks.targets[n].dopplerSpectra.append(self.myInterface.RxU16())
                    
        else:
            self.tracks.numTargets = 0
            
        return self.tracks
    
    '-----------------------------------------------------------------------------'
    def cmd_configSectorMap(self, cmd):
        self.myInterface.TxU16(cmd)
        self.Transceive()
        
    '-----------------------------------------------------------------------------'
    def cmd_getSectorMap(self):
        self.Transceive(Par.SECTOR_RANGE_NUM*Par.SECTOR_ANGLE_NUM)
        
        sectors = []
        for _r in range(Par.SECTOR_RANGE_NUM):
            tmp = []
            for _a in range(Par.SECTOR_ANGLE_NUM):
                tmp.append(self.myInterface.RxU8())
            sectors.append(tmp)
        
        return sectors

    '-----------------------------------------------------------------------------'
    def cmd_setSectorMap(self, sectors):
        for r in range(Par.SECTOR_RANGE_NUM):
            for a in range(Par.SECTOR_ANGLE_NUM):
                self.myInterface.TxU8(sectors[r][a])
        self.Transceive()
            
    '-----------------------------------------------------------------------------'
    def cmd_fwUpdStart(self):
        self.Transceive()
        
    '-----------------------------------------------------------------------------'
    def cmd_fwUpdAbort(self):
        self.Transceive()
    
    '-----------------------------------------------------------------------------'
    def cmd_fwUpdData(self, data):
        # just send bytes in data (length doesn't matter, cmd code reflects it)
        for b in data:
            self.myInterface.TxU8(b)
            
        self.Transceive()
        
    '-----------------------------------------------------------------------------'
    def cmd_fwUpdFlashStart(self, CRCs):
        for crc in CRCs:
            self.myInterface.TxU16(crc)
        
        self.Transceive()

'================================================================================='    
class CommandError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
