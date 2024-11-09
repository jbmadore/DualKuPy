'''
Created on 03.04.2023

@author: IMST GmbH
'''

import ctypes as c
from os import path, walk
from sys import platform, maxsize

DLL_MANU_32_NAME = "CP210xManufacturing32.dll"
DLL_MANU_64_NAME = "CP210xManufacturing64.dll"
DLL_RT_32_NAME = "CP210xRuntime32.dll"
DLL_RT_64_NAME = "CP210xRuntime64.dll"

class CP210x_GpioConfigurator(object):
    
    def __init__(self):
        # determine system architecture
        if maxsize > 2**32:
            # 64-bit
            dll_manu_name = DLL_MANU_64_NAME
            dll_rt_name = DLL_RT_64_NAME
        else:
            # 32-bit
            dll_manu_name = DLL_MANU_32_NAME
            dll_rt_name = DLL_RT_32_NAME
        
        # find and load DLLs
        pm = None
        prt = None
        # DLLs are searched in current folder and all sub-folders
        for root, _dirs, files in walk(path.abspath(".")):
            for f in files:
                if dll_manu_name == f:
                    pm = path.join(root, f)
                if dll_rt_name == f:
                    prt = path.join(root, f)
                
                if pm and prt:
                    break
            if pm and prt:
                break
            
        if pm is None:
            raise Exception("%s not found!"%dll_manu_name)

        if prt is None:
            raise Exception("%s not found!"%dll_rt_name)
        
        # load DLLs
        if platform == "win32":
            self.mLib = c.WinDLL(pm)
            self.rtLib = c.WinDLL(prt)
        else:
            self.mLib = c.CDLL(pm)
            self.rtLib = c.CDLL(prt)
            
        self.handle = None
            
    '-----------------------------------------------------------------------------'
    def getNumDevices(self):
        num = c.c_uint32()
        if self.mLib.CP210x_GetNumDevices(c.byref(num)) != 0:
            raise Exception("Returned error status!")
        
        return num.value
    
    '-----------------------------------------------------------------------------'
    def openHandle(self, devIndex=None):
        if devIndex is None:
            if self.getNumDevices() > 0:
                devIndex = 0    # always uses the first one by default
                
        if devIndex is None:
            raise Exception("Cannot open handle. No device found!")
        
        handle = c.c_int()
        if self.mLib.CP210x_Open(c.c_uint32(devIndex), c.byref(handle)) != 0:
            raise Exception("Error when opening handle!")
        
        self.handle = handle.value
        
        return self.handle
    
    '-----------------------------------------------------------------------------'
    def closeHandle(self):
        if self.handle is None:
            return
        
        if self.mLib.CP210x_Close(self.handle) != 0:
            raise Exception("Error when closing handle!")
        
        self.handle = None
    
    '-----------------------------------------------------------------------------'
    def readLatch(self):
        if self.handle is None:
            return
        
        latch = c.c_uint16()
        
        if self.rtLib.CP210xRT_ReadLatch(self.handle, c.byref(latch)) != 0:
            raise Exception("Error when reading latch!")
        
        return latch.value
    
    '-----------------------------------------------------------------------------'
    def writeLatch(self, gpio_mask, latch):
        if self.handle is None:
            return
        
        if self.rtLib.CP210xRT_WriteLatch(self.handle, gpio_mask, latch) != 0:
            raise Exception("Error when writing latch!")
        
    '-----------------------------------------------------------------------------'
    def triggerReset(self):
        # toggle external interrupt mapped to GPIO1 of CP2102N
        self.writeLatch(0x2, 0x0)   # set to 0
        self.writeLatch(0x2, 0x2)   # set back to 1
        
    '-----------------------------------------------------------------------------'
    def resetRadar(self):
        # all in one action
        self.openHandle()
        self.triggerReset()
        self.closeHandle()
    
    
            
if __name__ == "__main__":
    # No other connection must be active
    cpCfg = CP210x_GpioConfigurator()
    cpCfg.resetRadar()

