'''
Created on 18.11.2022

@author: IMST GmbH

In this example a possibility to find a connected radar module for each interface is shown.
'''

from Communication import CP210X_USB_Interface, EthernetInterfaces


interface_selection = "Ethernet"     # type of interface to be used: "Ethernet" or "USB"

print('<============ Start ============>\n')

if interface_selection == "Ethernet":
    # For an Ethernet connection, the IP address and a port number must be known.
    # In case these values have been forgotten and the module does not have the default values
    # anymore, there are two possibilities: Use the USB interface to read them out or reset 
    # the Ethernet configuration, or to request the configuration via UDP broadcast.
    # The last option is presented here.
    
    MagicWord = 0x494d5354  # IMST as hex with ord('I') << 24 and so on
    
    # Get an Ethernet configuration object and set broadcast options
    cfg = EthernetInterfaces.EnetConfig(OwnPort=4101, UdpBcPort=4444, Timeout=0.5, Broadcast=True)
    # Get all used IP addresses of this host machine
    IPs = EthernetInterfaces.GetAllIpAddresses()
    
    # Open an UDP interface for each possible IP address, send a broadcast message with it and check the answer
    print("Started search...")
    for ip in IPs:
        # update configuration IP
        cfg.IP = ip
        # Get and open an UDP interface
        udp = EthernetInterfaces.EnetUdpInterface(cfg)
        if not udp.Open():
            print("Couldn't open UDP interface with IP %s"%ip)
            continue
        else:
            udp.TxU32(MagicWord)    # Add magicword to buffer which radar expects in a broadcast message
            udp.SendBroadcast()     # Send broadcast
            
            while True:
                nRcvd = udp.Receive(-1)
                if nRcvd < 0:
                    break
                
                # Check magicword
                if udp.RxU32() == MagicWord:
                    print("-----------------------")
                    print("Found radar using host IP %s"%ip)
                    # Read answer packet
                    print("Radar IP:",udp.hostIp)
                    print("Device Number:", udp.RxU32())
                    nTcp = udp.RxU16()
                    tcpPorts = [udp.RxU16() for _ in range(nTcp)]
                    for n in range(nTcp):
                        print("TCP Port #%d: %d"%(n+1, tcpPorts[n]))
                    nUdp = udp.RxU16()
                    udpPorts = [udp.RxU16() for _ in range(nTcp)]
                    for n in range(nUdp):
                        print("UDP Port #%d: %d"%(n+1, udpPorts[n]))
                    # In case of newer firmware versions, more information is sent
                    if nRcvd > 20:
                        nMulti = udp.RxU16()
                        for n in range(nMulti):
                            mc = ""
                            for _ in range(4):
                                mc += str(udp.RxU8()) + "."
                            print("Multicast Group #%d: %s"%(n+1, mc[:-1]))
                    
            udp.Close()

elif interface_selection == 'USB':
    # The USB interface works with a virtual COM port. Here the windows variant is presented.
    
    # With the method GetPorts() all virtual COM ports are checked for the correct vendor and
    # product ID of the USB/UART converter chip which is used on the radar backend.
    # The result is a list of ListPortInfo objects which inherit all needed information to
    # connect to the radar.
    ports = CP210X_USB_Interface.GetPorts()
    
    # Print COM port names and maybe select a certain one
    for p in ports:
        print("Found device on virtual COM port", p.device)
    
    # If a module was found here does not mean that the module is powered because USB has its own supply.
    # To check if the module is online, a command should be sent now, e.g. CMD_INFO.
    # See "Read_Write_Parameters_Example.py" for more information.
            
print('\n>============ End ============<')
input("Press any Key to exit.")

    