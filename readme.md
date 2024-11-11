
# DualKu Radar Measurement System

This project provides a Python-based solution for controlling and recording measurements from a dual-radar setup, primarily for data acquisition and display in real-time. The system is designed for snow monitoring and development, and it supports two radars at different frequencies (13GHz and 17GHz) that can operate simultaneously.

## Table of Contents
- [Directory Structure](#directory-structure)
- [Dependencies](#dependencies)
- [Getting Started](#getting-started)
- [Running the Application](#running-the-application)
- [Files Overview](#files-overview)
- [License](#license)

## Directory Structure

```
project-root/
├── data_io/                 # Contains file handling modules
│   ├── file_writer.py       # Module for recording measurements
│
├── plotting/                # Contains plotting functions
│   ├── plotting.py          # Functions for initializing and updating plots
│
├── radar/                   # Radar communication modules
│   ├── radar.py             # Functions for initializing and fetching radar data
│
├── main.py                  # Main script to run the radar measurement and display system
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

## Dependencies

This project requires the following Python packages:
- `matplotlib`
- `threading`
- `queue`
- Any radar communication libraries needed by the radar devices (e.g., `radar_sdk`)

To install the dependencies, run:
```bash
pip install -r requirements.txt
```

## Getting Started

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/DualKuRadar.git
   cd DualKuRadar
   ```

2. Configure radar IP addresses and ports in the `main.py` script:
   ```python
   radar1_ip = '192.168.0.13'
   radar2_ip = '192.168.0.17'
   radar1_host_port = 4100
   radar2_host_port = 4101
   ```

3. Ensure that the radar devices are correctly connected and reachable on the configured IP addresses.

   ```

## Running the Application

To run the application, simply execute:
```bash
python main.py
```

The application will:
1. Initialize the two radars.
2. Display the real-time radar data for both frequencies in separate subplots.
3. Allow users to control data recording and display toggling via keyboard commands.

## Files Overview

### `main.py`
The main control script that orchestrates the radar initialization, data fetching, real-time display, and recording functionality. It includes:
- **Radar Initialization**: Sets up two radars at specified IP addresses.
- **Plotting**: Initializes a dual-panel plot for real-time data display.
- **Data Recording**: Enables users to record radar data via keyboard commands.

### `radar/radar.py`
Contains core functions for interacting with the radar hardware:
- `init_radar`: Initializes the radar connection.
- `fetch_radar_data`: Fetches radar data for display and recording.
- `close_radar`: Closes the radar connection.

### `plotting/plotting.py`
Contains functions for initializing and updating the radar data display:
- `init_plot`: Sets up plots for real-time data display.
- `update_plot`: Updates plot with real-time radar data.
- `update_record_plot`: Adds dashed lines to the plot to mark recorded data.

### `data_io/file_writer.py`
Manages file-based data recording for each radar:
- `record_measurement`: Records radar measurements into CSV format or other specified format, storing each radar pulse with data and metadata.

## Controls

The `keyboard_listener` function in `main.py` enables the following keyboard controls:
- **Enter**: Toggles the display between running and paused states.
- **1**: Records data for the 13GHz radar (if available).
- **2**: Records data for the 17GHz radar (if available).
- **b**: Records data from both radars simultaneously.


---
