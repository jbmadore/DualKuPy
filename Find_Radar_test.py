from Communication import CP210X_USB_Interface, EthernetInterfaces

interface_selection = "Ethernet"  # Choose between "Ethernet" or "USB"

print('<============ Start ============>\n')

if interface_selection == "Ethernet":
    MagicWord = 0x494d5354  # IMST as hex (I = 0x49, M = 0x4D, etc.)

    # Create Ethernet configuration with broadcast enabled
    cfg = EthernetInterfaces.EnetConfig(
        OwnPort=4101, UdpBcPort=4444, Timeout=2.0, Broadcast=True
    )

    # Get all valid IPs on the host machine
    IPs = EthernetInterfaces.GetAllIpAddresses()
    print(f"Detected IPs: {IPs}")

    # Start searching for radar devices via UDP broadcast
    print("Started search...")
    for ip in IPs:
        cfg.IP = ip  # Update configuration with the current IP
        udp = EthernetInterfaces.EnetUdpInterface(cfg)  # Create UDP interface

        # Open UDP interface and check for errors
        if not udp.Open():
            print(f"Couldn't open UDP interface with IP {ip}")
            continue  # Try the next IP

        print(f"UDP interface opened with IP {ip}")

        try:
            # Send the broadcast packet with the magic word
            udp.TxU32(MagicWord)  # Add the magic word to the buffer
            udp.SendBroadcast()  # Send broadcast packet

            while True:
                nRcvd = udp.Receive(-1)  # Wait for a response
                if nRcvd < 0:
                    print("No more data received. Breaking...")
                    break

                # Verify the received magic word
                if udp.RxU32() == MagicWord:
                    print("-----------------------")
                    print(f"Found radar using host IP {ip}")
                    print(f"Radar IP: {udp.hostIp}")
                    print(f"Device Number: {udp.RxU32()}")

                    # Read TCP and UDP ports from the response
                    nTcp = udp.RxU16()
                    tcpPorts = [udp.RxU16() for _ in range(nTcp)]
                    for i, port in enumerate(tcpPorts):
                        print(f"TCP Port #{i + 1}: {port}")

                    nUdp = udp.RxU16()
                    udpPorts = [udp.RxU16() for _ in range(nUdp)]
                    for i, port in enumerate(udpPorts):
                        print(f"UDP Port #{i + 1}: {port}")

                    # Check for multicast groups if more data is available
                    if nRcvd > 20:
                        nMulti = udp.RxU16()
                        for i in range(nMulti):
                            group = ".".join(str(udp.RxU8()) for _ in range(4))
                            print(f"Multicast Group #{i + 1}: {group}")

        except Exception as e:
            print(f"Error during radar search: {e}")

        finally:
            # Close the UDP socket safely
            try:
                udp.Close()
                print("UDP interface closed.")
            except OSError as e:
                if e.errno == 107:  # Transport endpoint not connected
                    print("Warning: UDP interface not connected.")
                else:
                    raise  # Re-raise unexpected errors

elif interface_selection == 'USB':
    print("Using USB interface...")
    com = CP210X_USB_Interface.CP210X_USB_Interface()  # Initialize USB interface
    ports = com.GetFoundPorts()  # Find available COM ports

    for port in ports:
        print(f"Found device on virtual COM port {port.device}")

print('\n>============ End ============<')
input("Press any Key to exit.")

