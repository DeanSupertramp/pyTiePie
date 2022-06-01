# OscilloscopeGeneratorTrigger.py
#
# This example sets up the generator to generate a 1 kHz triangle waveform, 4 Vpp.
# It also sets up the oscilloscope to perform a block mode measurement, triggered on "Generator new period".
# A measurement is performed and the data is written to OscilloscopeGeneratorTrigger.csv.
#
# Find more information on http://www.tiepie.com/LibTiePie .

from __future__ import print_function
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

# Try to open an oscilloscope with block measurement support and a generator in the same device:
scp = None
gen = None
for item in libtiepie.device_list:
    if (item.can_open(libtiepie.DEVICETYPE_OSCILLOSCOPE)) and (item.can_open(libtiepie.DEVICETYPE_GENERATOR)):
        scp = item.open_oscilloscope()
        if scp.measure_modes & libtiepie.MM_BLOCK:
            gen = item.open_generator()
            break
        else:
            scp = None

if scp and gen:
    try:
        # Oscilloscope settings:

        # Set measure mode:
        scp.measure_mode = libtiepie.MM_BLOCK

        # Set sample frequency:
        scp.sample_frequency = 1e6  # 1 MHz

        # Set record length:
        scp.record_length = 10000  # 10000 samples

        # Set pre sample ratio:
        scp.pre_sample_ratio = 0  # 0 %

        # For all channels:
        for ch in scp.channels:
            # Enable channel to measure it:
            ch.enabled = True

            # Set range:
            ch.range = 8  # 8 V

            # Set coupling:
            ch.coupling = libtiepie.CK_DCV  # DC Volt

        # Set trigger timeout:
        scp.trigger_time_out = 1  # 1 s

        # Disable all channel trigger sources:
        for ch in scp.channels:
            ch.trigger.enabled = False

        # Locate trigger input:
        trigger_input = scp.trigger_inputs.get_by_id(libtiepie.TIID_GENERATOR_NEW_PERIOD)  # or TIID_GENERATOR_START or TIID_GENERATOR_STOP

        if trigger_input is None:
            raise Exception('Unknown trigger input!')

        # Enable trigger input:
        trigger_input.enabled = True

        # Generator settings:

        # Set signal type:
        gen.signal_type = libtiepie.ST_TRIANGLE

        # Set frequency:
        gen.frequency = 1e3  # 1 kHz

        # Set amplitude:
        gen.amplitude = 2  # 2 V

        # Set offset:
        gen.offset = 0  # 0 V

        # Enable output:
        gen.output_on = True

        # Print oscilloscope info:
        print_device_info(scp)

        # Print generator info:
        print_device_info(gen)

        # Start measurement:
        scp.start()

        # Start signal generation:
        gen.start()

        # Wait for measurement to complete:
        while not scp.is_data_ready:
            time.sleep(0.01)  # 10 ms delay, to save CPU time

        # Stop generator:
        gen.stop()

        # Disable output:
        gen.output_on = False

        # Get data:
        data = scp.get_data()

        # Output CSV data:
        csv_file = open('OscilloscopeGeneratorTrigger.csv', 'w')
        try:
            csv_file.write('Sample')
            for i in range(len(data)):
                csv_file.write(';Ch' + str(i + 1))
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

    # Close generator:
    del gen

else:
    print('No oscilloscope available with block measurement support or generator available in the same unit!')
    sys.exit(1)

sys.exit(0)
