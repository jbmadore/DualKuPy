Here’s an updated version of your **README.md** reflecting the recent changes and improvements in your project:

---

# **DualKu Radar Measurement System**

This project provides a **Python-based system for controlling, measuring, and displaying radar data** from a **dual-radar setup (13GHz and 17GHz)**.  
Originally designed for **snow monitoring**, this system enables **real-time data acquisition, visualization, and storage** via an interactive **LCD interface** and **automated data logging**.

## **Table of Contents**
- [Features](#features)
- [Directory Structure](#directory-structure)
- [Hardware Setup](#hardware-setup)
- [Dependencies](#dependencies)
- [Getting Started](#getting-started)
- [Running the Application](#running-the-application)
- [User Interface](#user-interface)
- [Files Overview](#files-overview)
- [License](#license)

---

## **Features**
✅ **Automatic Radar Initialization** – The system detects and initializes **both 13GHz & 17GHz radars** on boot.  
✅ **Standalone LCD Menu** – A **128x64 pixel LCD screen** allows users to configure measurements **without a keyboard or monitor**.  
✅ **Measurement Logging** – Data is **automatically saved** with metadata such as **site name, measurement ID, polarization, and angle**.  
✅ **Real-time Graph Display** – After a measurement, **small-scale amplitude graphs** for both frequencies appear on the LCD screen.  
✅ **Ethernet Routing** – The Raspberry Pi **automatically configures network routing** for radar communication.  
✅ **Offline Operation** – The system can **function independently** and store data locally on a **USB drive**.

---

## **Directory Structure**
```
project-root/
├── data_io/                 # File handling and data recording modules
│   ├── file_writer.py       # Handles measurement data storage
│
├── plotting/                # Functions for rendering data on LCD display
│   ├── lcd_graph.py         # Generates small graphs for LCD output
│
├── radar/                   # Radar communication and data acquisition
│   ├── radar.py             # Initializes radar, fetches data, and manages connections
│
├── buttons.py               # Handles physical button inputs for the menu
├── lcd_display.py           # Manages LCD screen rendering
├── menu.py                  # Controls the interactive LCD menu
├── network_setup.sh         # Script for automatic network routing
├── main.py                  # Main script for running the radar system
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

---

## **Hardware Setup**
### **Required Components**
- **Raspberry Pi 4 or 5**
- **Waveshare 128x64 SPI LCD**
- **Physical Buttons** (for navigation)
- **13GHz & 17GHz Radars** (Ethernet-connected)
- **USB Drive** (for data storage)

### **Wiring Overview**
| Component   | GPIO Pin  |
|------------|----------|
| LCD CS     | GPIO 8   |
| LCD Reset  | GPIO 25  |
| LCD A0     | GPIO 24  |
| Button UP  | GPIO 17  |
| Button DOWN | GPIO 27  |
| Button OK  | GPIO 22  |
| Button CANCEL | GPIO 23 |

### **Radar Network Configuration**
- The **Raspberry Pi acts as a router** between the radars and external devices.
- Automatic routing ensures correct connectivity at boot.
Sure! Here’s an updated section on **Ethernet Configuration (eth0 & eth1)**:

---

## **Ethernet Configuration (eth0 & eth1)**

The **Raspberry Pi acts as a router** between the radars and external devices, ensuring proper communication. To achieve this, the system automatically configures **eth0 and eth1** at startup. The eth1 is made possible with the use of a usb/Ethernet dongle

### **Static IP Configuration**
Each network interface is assigned a **static IP** to ensure connectivity:
- **eth0** → `192.168.0.100` (Handles Radar 17GHz)
- **eth1** → `192.168.0.101` (Handles Radar 13GHz)

To manually set up static IP addresses, modify the **network configuration**:
```bash
sudo nano /etc/dhcpcd.conf
```
Add the following lines:
```
interface eth0
static ip_address=192.168.0.100/24
static routers=192.168.0.1
static domain_name_servers=8.8.8.8

interface eth1
static ip_address=192.168.0.101/24
static routers=192.168.0.1
static domain_name_servers=8.8.8.8
```
Save and apply changes:
```bash
sudo systemctl restart dhcpcd
```

### **Automated Routing**
To ensure both radars communicate properly, **IP routes are set automatically** on startup.  
This is handled by `network_setup.sh`, which is **executed at boot**.

#### **Routing Commands**
If no external computer is detected, the system **adds routes**:
```bash
sudo ip route add 192.168.0.17 via 192.168.0.100 dev eth0
sudo ip route add 192.168.0.13 via 192.168.0.101 dev eth1
```
This ensures that **each radar is accessible through its respective interface**.



> **Important:**  
> - When **developing** on the Raspberry Pi **via SSH or VNC**, ensure **your PC is on the same subnet** (e.g., `192.168.0.X`).  
> - If an external computer is detected (`192.168.0.X`), **routing is skipped** to allow manual configuration.


---

## **Dependencies**
Install required Python packages:
```bash
pip install -r requirements.txt
```

### **Required Packages**
- `matplotlib` (for data visualization)
- `PIL` (for LCD rendering)
- `RPi.GPIO` (for button handling)
- `spidev` (for SPI communication with the LCD)
- `numpy` (for data processing)

---

## **Getting Started**
### **1. Clone the Repository**
```bash
git clone https://github.com/your-username/DualKuRadar.git
cd DualKuRadar
```

### **2. Configure Radar Settings**
Edit `main.py` if necessary:
```python
radar1_ip = '192.168.0.13'
radar2_ip = '192.168.0.17'
radar1_host_port = 4100
radar2_host_port = 4101
```

### **3. Set Up Network Routing on Boot**
```bash
sudo cp network_setup.sh /etc/network/interfaces.d/radar_routes.sh
sudo chmod +x /etc/network/interfaces.d/radar_routes.sh
```

### **4. Enable Auto-Startup**
```bash
sudo systemctl enable dualkupy.service
sudo systemctl start dualkupy.service
```

---

## **Running the Application**
```bash
python main.py
```
> The LCD menu will launch, showing radar connection status.

---

## **User Interface**
### **LCD Menu Navigation**
- **UP / DOWN** – Navigate through menu options.
- **OK** – Edit a selected entry or start a measurement.
- **CANCEL** – Return to the previous menu.

### **Main Menu**
| Option        | Description |
|--------------|------------|
| **Site Name**  | Enter a 4-character site code. |
| **Measure #**  | Assign a 2-digit measurement ID (01-99). |
| **Angle**      | Set the radar angle (01-99 degrees). |
| **Pol**        | Select **Vertical (V) or Horizontal (H) polarization**. |
| **Measurement** | Start a measurement and log data. |

---

## **Files Overview**
### **`main.py`**
- **Initializes radars** and **checks network routing**.
- Launches the **LCD menu** for measurement setup.
- Displays radar data **on the LCD screen** after a measurement.

### **`menu.py`**
- Handles **menu navigation and data entry**.
- Records measurements **based on user input**.
- Displays **graphs of the latest measurement**.

### **`lcd_display.py`**
- Draws **real-time graphs** on the **128x64 LCD**.
- Displays **menu options, time, and measurement details**.

### **`radar/radar.py`**
- `init_radar()` – Connects to the radar devices.
- `fetch_radar_data()` – Retrieves measurement data.
- `close_radar()` – Closes the radar connection.

### **`data_io/file_writer.py`**
- `record_measurement()` – Saves radar data **to USB storage** with metadata.

### **`plotting/lcd_graph.py`**
- Generates **small graphs** for the **LCD screen**.
- Displays **amplitude vs. distance** for **13GHz & 17GHz** after a measurement.

---

## **Graphical Display**
### **Real-Time Measurement Graphs**
- **After a measurement**, the LCD displays two small-scale graphs.
- **X-axis** = **Amplitude**  
- **Y-axis (Inverted)** = **Distance**  

🔹 **Press "OK"** to return to the menu.

---

## **Future Improvements**
🔸 Implement **real-time radar data streaming** on the LCD.  
🔸 Add **a settings menu** for network configuration.  
🔸 Optimize **graph rendering** for better visibility.
🔸 A backup of the sd card os of the raspberry pi


---