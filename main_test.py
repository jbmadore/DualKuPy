import threading
import time
from radar.radar import init_radar, fetch_radar_data, close_radar
from plotting.plotting import init_plot, update_plot, update_record_plot
import matplotlib.pyplot as plt
from data_io.file_writer import record_measurement
from queue import Queue
import matplotlib
import os
os.environ["QT_QPA_PLATFORM"] = "xcb"

matplotlib.use("TkAgg")
# Global flags and settings
#running = False  # Controls display running state
#recording_lock = threading.Lock()
plot_update_queue = Queue()
num_record_=150

radar1_ip = '192.168.0.13'
radar1_host_port = 4100
com1, cmd1, ok1 = init_radar(radar1_ip, host_port=radar1_host_port)
print(ok1)
if ok1:
    print('radar connected')
    

options_1 = {
"cmd": cmd1,
"site_name": '',  # Placeholder values
"measure_id": '',
"polarization": '',
"additional_info": "",
"radar_angle":""
}

#options_1.update(recording_info)

record_measurement(num_records=num_record_, foldername="./", measure_number=1, options=options_1)
# record_measurement(num_records=num_record_, foldername="./data/", measure_number=1, options=options_2)
        
  
