Here's the updated `README.md` tailored for the `feature/get-fe-sensors` branch based on the `radar_scheduler.py` we worked on.

---

# DualKu Radar Measurement System - Feature/Get-FE-Sensors

This branch extends the **DualKu Radar Measurement System** to include a **scheduled measurement system**. The radar measurements can now be automated with configurable start and stop times, and intervals, while retaining the flexibility of manual sensor handling.

## Table of Contents
- [Directory Structure](#directory-structure)
- [Dependencies](#dependencies)
- [Getting Started](#getting-started)
- [Running the Scheduler](#running-the-scheduler)
- [Configuration File Format](#configuration-file-format)
- [Files Overview](#files-overview)
- [License](#license)

---

## Directory Structure

```
project-root/
├── data_io/                 # Contains file handling modules
│   ├── file_writer.py       # Module for recording measurements
│
├── data/                    # Data folder
│
├── radar/                   # Radar communication modules
│   ├── radar.py             # Functions for initializing and fetching radar data
│
├── feature/                 # Feature-specific scripts
│   ├── radar_scheduler.py   # Scheduled radar measurement script
│
├── config/                  # Configuration files for experiments
│   ├── example_config.json  # Example configuration file for scheduling
│
├── requirements.txt         # Python dependencies
└── README.md                # Documentation for this branch
```

---

## Dependencies

This project requires the following Python packages:
- `matplotlib`
- `json`
- `datetime`

To install the dependencies, run:
```bash
pip install -r requirements.txt
```

---

## Getting Started

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/DualKuRadar.git
   cd DualKuRadar
   git checkout feature/get-fe-sensors
   ```

2. **Prepare Configuration Files**:
   - Create a configuration file for your experiment. Use the provided `config/example_config.json` as a template.
   - Specify the start and stop times, radar parameters, and intervals for the scheduled measurements.

3. **Ensure Radar Connectivity**:
   - Confirm that the radar devices are accessible on the specified IP addresses and ports.

---

## Running the Scheduler

To run the scheduled radar measurement system:
```bash
python feature/radar_scheduler.py config/example_config.json
```

This command:
1. Loads the experiment configuration file.
2. Waits for the specified start time (if provided).
3. Collects radar data at the configured intervals until the stop time or manual interruption.

---

## Configuration File Format

The scheduler uses a JSON configuration file to manage radar measurement parameters. Below is an example:

```json
{
    "num_records": 150,
    "site_name": "SnowMonitoringSite",
    "radar_angle": "45",
    "polarization": "H",
    "measure_id": "experiment_001",
    "additional_info": "Initial test run",
    "foldername": "./data/",
    "interval_minutes": 15,
    "start_time": "2025-01-10 14:00:00",
    "stop_time": "2025-01-10 15:00:00"
}
```

### Key Parameters:
- **`num_records`**: Number of radar pulses to record per measurement.
- **`site_name`**: Name of the measurement site.
- **`radar_angle`**: Radar tilt angle in degrees.
- **`polarization`**: Polarization of the radar (e.g., "H" or "V").
- **`measure_id`**: Identifier for the experiment.
- **`additional_info`**: Free-form notes about the experiment.
- **`foldername`**: Path to the folder where data will be stored.
- **`interval_minutes`**: Time interval (in minutes) between measurements.
- **`start_time`**: Optional; start time for the scheduler in `YYYY-MM-DD HH:MM:SS` format.
- **`stop_time`**: Optional; stop time for the scheduler in `YYYY-MM-DD HH:MM:SS` format.

---

## Files Overview

### `feature/radar_scheduler.py`
This script automates radar measurements based on the provided configuration:
- Waits for the specified start time.
- Executes radar measurements at regular intervals.
- Stops measurements at the configured stop time or when interrupted manually.

### `radar/radar.py`
Contains core functions for interacting with the radar hardware:
- `init_radar`: Initializes the radar connection.
- `fetch_radar_data`: Fetches radar data for display and recording.

### `data_io/file_writer.py`
Manages file-based data recording:
- `record_measurement`: Saves radar measurements along with metadata.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

This branch focuses on **automating radar measurements** while allowing flexibility for future extensions. Let me know if further adjustments are needed! 😊