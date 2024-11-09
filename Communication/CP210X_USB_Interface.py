# -*- coding: utf-8 -*-
'''
Created on 17.04.2020

@author: IMST GmbH
'''

import serial
from serial.tools.list_ports import comports
from Communication.Interface import Interface

VID = 0x10C4    # Vendor ID
PID = 0xEA60    # Product ID

BAUDRATE = 2000000

def GetPorts():
    'Look for connected CP210X chips and return COMx strings'
    res = []
    for p in comports():
        if p.vid == VID and p.pid == PID:
            res.append(p)
    return res

class CP210X_USB_Interface(Interface):
    
    def __init__(self):
        
        Interface.__init__(self, name="CP210X Interface", interfaceType="USB")

        self.com = None
        self.foundPorts = []
        self.usedPort = None
        
        self.Check()
        
    '-----------------------------------------------------------------------------'
    def Open(self):
        self.resetErrors()
        try:
            self.Close()
            if self.usedPort is None:
                raise Exception("No port selected to open.")            
            self.com = serial.Serial(self.usedPort.device, BAUDRATE, serial.EIGHTBITS, serial.PARITY_EVEN, serial.STOPBITS_ONE, timeout=1, write_timeout=1)            
            return self.com.isOpen()
            
        except Exception as E:
            self.errorCode |= self.ERR_IF_OPEN
            self.errorString = "CP210X Interface open error: "+str(E)
            self.Close()
            return False
    
    '-----------------------------------------------------------------------------'
    def Close(self):
        if self.com is not None:
            self.com.close()
            self.com = None
    
    '-----------------------------------------------------------------------------'
    def Write(self, data):        
        return self.com.write(data)
    
    '-----------------------------------------------------------------------------'
    def Read(self, n):
        return self.com.read(n)
    
    '-----------------------------------------------------------------------------'
    def ResetBuffer(self):
        self.com.reset_input_buffer()
        self.com.reset_output_buffer()
        
    '-----------------------------------------------------------------------------'
    def SetSpeed(self, speed=None):
        if speed is None:
            speed = BAUDRATE    # restore
        self.com.baudrate = speed
        
    '-----------------------------------------------------------------------------'
    def Check(self):
        'Checks for connected devices and returns number of found.'
        'If more than one, a device should be selected to be used.'
        self.foundPorts = GetPorts()
        
        if len(self.foundPorts) > 0:
            self.usedPort = self.foundPorts[0]  # save port object
            
        return len(self.foundPorts)
    
    '-----------------------------------------------------------------------------'
    'Method to use if more than one valid port was found by "Check".'
    def UsePort(self, port):        
        'The value of port must be an "ListPortInfo" object from the "foundPorts" list or'
        'returned by "GetFoundPorts"'
        try:
            port.device
            self.usedPort = port
        except:
            raise Exception("No valid port value!")
        
    '-----------------------------------------------------------------------------'
    def HasPort(self):
        'Returns if a COM port was found or selected'                
        return self.usedPort is not None
    
    '-----------------------------------------------------------------------------'
    def ClearPort(self):
        'Just marks usedPort as not available'
        self.usedPort = None
        
    '-----------------------------------------------------------------------------'
    def IsOpen(self):
        'Returns if COM port is currently open'
        if self.com is None:
            return False
        else:
            return self.com.isOpen()
        
    '-----------------------------------------------------------------------------'
    def GetFoundPorts(self):
        return self.foundPorts

