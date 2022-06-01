# Generator.py
#
# This example generates a 100 kHz triangle waveform, 4 Vpp.
#
# Find more information on http://www.tiepie.com/LibTiePie .

from __future__ import print_function
import sys
import libtiepie
from printinfo import *

# Print library info:
print_library_info() # print Version, Configuration

# Enable network search:
#libtiepie.network.auto_detect_enabled = True

# Search for devices:
libtiepie.device_list.update()

# Try to open a generator:
gen = None
for item in libtiepie.device_list:
    if item.can_open(libtiepie.DEVICETYPE_GENERATOR):
        gen = item.open_generator()
        if gen:
            break

if gen:
    try:
        # Set signal type:
        gen.signal_type = libtiepie.ST_TRIANGLE

        # Set frequency:
        gen.frequency = 100e3  # 100 kHz

        # Set amplitude:
        gen.amplitude = 2  # 2 V

        # Set offset:
        gen.offset = 0  # 0 V

        # Enable output:
        gen.output_on = True

        # Print generator info:
        print_device_info(gen)

        # Start signal generation:
        gen.start()

        # Wait for keystroke:
        print('Press Enter to stop signal generation...')
        if sys.version_info < (3, 0):  # Python 2.x
            raw_input()
        else:  # Python 3.x
            input()

        # Stop generator:
        gen.stop()

        # Disable output:
        gen.output_on = False

    except Exception as e:
        print('Exception: ' + e.message)
        sys.exit(1)

    # Close generator:
    del gen

else:
    print('No generator available!')
    sys.exit(1)

sys.exit(0)
