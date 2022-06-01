# OscilloscopeBlockSegmented.py
#
# This example performs a block mode measurement of 5 segments and writes the data to OscilloscopeBlockSegmented.csv.
#
# Find more information on http://www.tiepie.com/LibTiePie .

from __future__ import print_function
from array import array
import time
import os
import sys
import libtiepie
from printinfo import *

# Print library info:
print_library_info()

# Enable network search:
libtiepie.network.auto_detect_enabled = True

# Search for devices:
libtiepie.device_list.update()

# Try to open an oscilloscope with block measurement support and segmented triggering:
scp = None
for item in libtiepie.device_list:
    if item.can_open(libtiepie.DEVICETYPE_OSCILLOSCOPE):
        scp = item.open_oscilloscope()
        if (scp.measure_modes & libtiepie.MM_BLOCK) and (scp.segment_count_max > 1):
            break
        else:
            scp = None

if scp:
    try:
        # Set measure mode:
        scp.measure_mode = libtiepie.MM_BLOCK

        # Set sample frequency:
        scp.sample_frequency = 1e6  # 1 MHz

        # Set record length:
        scp.record_length = 1000  # 1000 samples

        # Set pre sample ratio:
        scp.pre_sample_ratio = 0  # 0 %

        # Set number of segments:
        scp.segment_count = 5  # 5 segments

        # For all channels:
        for ch in scp.channels:
            # Disble channel
            ch.enabled = False

        # Setup Channel 1
        ch = scp.channels[0]  # Ch 1

        # Enable channel to measure it:
        ch.enabled = True

        # Set range:
        ch.range = 8  # 8 V

        # Set coupling:
        ch.coupling = libtiepie.CK_DCV  # DC Volt

        # Set trigger timeout:
        scp.trigger_time_out = 100e-3  # 100 ms

        # Disable all channel trigger sources:
        for ch in scp.channels:
            ch.trigger.enabled = False

        # Setup channel trigger:
        ch = scp.channels[0]  # Ch 1

        # Enable trigger source:
        ch.trigger.enabled = True

        # Kind:
        ch.trigger.kind = libtiepie.TK_RISINGEDGE  # Rising edge

        # Level:
        ch.trigger.levels[0] = 0.5  # 50 %

        # Hysteresis:
        ch.trigger.hystereses[0] = 0.05  # 5 %

        # Print oscilloscope info:
        print_device_info(scp)

        # Start measurement:
        scp.start()

        # Wait for measurement to complete:
        while not scp.is_data_ready:
            time.sleep(0.01)  # 10 ms delay, to save CPU time

        # Create data arrays,
        data = []

        # Get all data from the scope:
        while scp.is_data_ready:
            data.append(scp.get_data()[0])  # only collect data from Ch 1

        # Output CSV data:
        csv_file = open('OscilloscopeBlockSegmented.csv', 'w')
        try:
            csv_file.write('Sample')
            for i in range(len(data)):
                csv_file.write(';Segment ' + str(i + 1))
            csv_file.write(os.linesep)
            for i in range(len(data[0])):
                csv_file.write(str(i))
                for j in range(len(data)):
                    csv_file.write(';' + str(data[j][i]))
                csv_file.write(os.linesep)

            print()
            print('Data written to: ' + csv_file.name)

        finally:
            csv_file.close()

    except Exception as e:
        print('Exception: ' + e.message)
        sys.exit(1)

    # Close oscilloscope:
    del scp

else:
    print('No oscilloscope available with block measurement and segmented trigger support!')
    sys.exit(1)

sys.exit(0)
