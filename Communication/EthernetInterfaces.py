# -*- coding: utf-8 -*-
'''
Created on 31.07.2018

@author: rainer.jetten

Interfaces for TCP and UDP Ethernet
'''

import socket
from Communication.Interface import Interface

def GetAllIpAddresses():
    # returns a list of all IP addresses used by this machine
    return [ip[-1][0] for ip in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET)]

'================================================================================='
class EnetConfig(object):
    'Configuration parameters that can be used for both Ethernet interfaces'
    def __init__(self, IP_str="", Port=-1, OwnPort=-1, UdpBcPort=-1, Timeout=1.0, Broadcast=False):
        self.IP = IP_str
        self.Port = Port
        self.OwnPort = OwnPort
        self.UdpBcPort = UdpBcPort
        self.Timeout = Timeout
        self.Broadcast = Broadcast
        
'================================================================================='        
class EnetStreamConfig(object):
    'Stream configuration parameters to start a certain Ethernet stream'
    TYPE_TCP = 1
    TYPE_UDP = 2
    DATA_MODE_SINGLE = 0
    DATA_MODE_MULTIPLE = 1
    MEAS_MODE_CONT = 0
    MEAS_MODE_TRIGGERED_START = 1
    MEAS_MODE_TRIGGERED_MEAS = 2
    
    def __init__(self, IP_str="", Port=-1, OwnPort=-1, EnetType=TYPE_UDP, DataMode=0, MeasMode=0, Mask=0, Delays=[0,0,0,0]):
        self.IP = IP_str
        self.Port = Port
        self.OwnPort = OwnPort
        self.EnetType = EnetType
        self.DataMode = DataMode
        self.MeasMode = MeasMode
        self.Delays = Delays
        self.Mask = Mask
        self.DataMask = 0
        self.ChirpRaw = 0
        self.ChirpRange = 0
        self.RangeBin = 0
        self.DopplerFormat = 0
        
    def getIpAsList(self):
        return [int(val) for val in self.IP.split(".")]

'================================================================================='    
class EnetTcpInterface(Interface):
    
    def __init__(self, enetConfig):
        
        Interface.__init__(self, name="EthernetTcpInterface", interfaceType="Ethernet")
        
        self.config = enetConfig
        
        self.socket = None
        self._opened = False
        
    '-----------------------------------------------------------------------------'
    def Open(self):
        'Open TCP connection'
        self.resetErrors()
        try:            
            self.Close()
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.config.Timeout)
            self.socket.connect((self.config.IP, self.config.Port))
            self._opened = True
        except Exception as E:
            self.errorCode |= self.ERR_IF_OPEN
            self.errorString = "TCP connect error: "+str(E)
            self.Close()
        return self._opened
            
    '-----------------------------------------------------------------------------'
    def Close(self):
        'Close TCP connection'
        if self.socket is not None:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
                self.socket.close()
                self.socket = None
            except:
                pass
        self._opened = False
    
    '-----------------------------------------------------------------------------'
    def IsOpen(self):
        return self._opened
            
    '-----------------------------------------------------------------------------'
    def Write(self, data):
        return self.socket.send(data)
        
    '-----------------------------------------------------------------------------'
    def Read(self, n):
        return self.socket.recv(n)
        
    '-----------------------------------------------------------------------------'
               

'================================================================================='
class EnetUdpInterface(Interface):
    
    def __init__(self, enetConfig):
        
        Interface.__init__(self, name="EthernetUdpInterface", interfaceType="Ethernet")
        
        self.config = enetConfig
        
        self.socket = None
        self._opened = False
        
        self.hostIp = ""
        self.hostPort = 0
        
    '-----------------------------------------------------------------------------'
    def Open(self):        
        'Open UDP socket'
        self.resetErrors()
        try:
            self.Close()
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            self.socket.settimeout(self.config.Timeout)
            if self.config.Broadcast:
                self.socket.bind((self.config.IP,self.config.OwnPort))
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            else:
                self.socket.bind(('',self.config.OwnPort))                    
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)            
            self._opened = True
        except Exception as E:
            self.errorCode |= self.ERR_IF_OPEN
            self.errorString = "Error while opening UDP socket: "+str(E)
            self.Close()
        return self._opened
        
    '-----------------------------------------------------------------------------'
    # def Close(self):        
    #     'Close UDP socket'
    #     if self.socket is not None:
    #         self.socket.shutdown(socket.SHUT_RDWR)
    #         self.socket.close()
    #         self.socket = None
    #     self._opened = False

    def Close(self):        
        'Close UDP socket safely.'
        if self.socket is not None:
            try:
                print("Closing UDP socket...")
                self.socket.close()  # Close the socket directly without shutdown()
            except Exception as e:
                print(f"Error closing socket: {e}")
            finally:
                self.socket = None  # Ensure proper cleanup
        self._opened = False
        print("UDP socket closed.")
    '-----------------------------------------------------------------------------'
    def IsOpen(self):
        return self._opened
            
    '-----------------------------------------------------------------------------'
    def Write(self, data):
        return self.socket.sendto(data, (self.config.IP, self.config.Port))
    
    '-----------------------------------------------------------------------------'
    def SendBroadcast(self, data=None):
        if self.config.Broadcast:
            if data is None:
                data = self.getTxBuf()[:self.getTxCount()]
            return self.socket.sendto(data, ("255.255.255.255", self.config.UdpBcPort))
    
    '-----------------------------------------------------------------------------'
    def Read(self, n):
        recv = self.socket.recvfrom(n)
        self.hostIp, self.hostPort = recv[1]
        return recv[0]
        
                