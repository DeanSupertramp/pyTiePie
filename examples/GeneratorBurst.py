# Generator.py
#
# This example generates a 50 Hz sine waveform, 4 Vpp, 100 periods.
#
# Find more information on http://www.tiepie.com/LibTiePie .

from __future__ import print_function
import time
import sys
import libtiepie
from printinfo import *

# Print library info:
print_library_info()

# Enable network search:
libtiepie.network.auto_detect_enabled = True

# Search for devices:
libtiepie.device_list.update()

# Try to open a generator with burst support:
gen = None
for item in libtiepie.device_list:
    if item.can_open(libtiepie.DEVICETYPE_GENERATOR):
        gen = item.open_generator()
        if gen.modes_native & libtiepie.GM_BURST_COUNT:
            break
        else:
            gen = None

if gen:
    try:
        # Set signal type:
        gen.signal_type = libtiepie.ST_SINE

        # Set frequency:
        gen.frequency = 50  # 50 Hz

        # Set amplitude:
        gen.amplitude = 2  # 2 V

        # Set offset:
        gen.offset = 0  # 0 V

        # Set mode:
        gen.mode = libtiepie.GM_BURST_COUNT

        # Set burst count:
        gen.burst_count = 100  # 100 periods

        # Enable output:
        gen.output_on = True

        # Print generator info:
        print_device_info(gen)

        # Start signal burst:
        gen.start()

        # Wait for burst to complete:
        while gen.is_burst_active:
            time.sleep(0.01)  # 10 ms delay, to save CPU time.

        # Disable output:
        gen.output_on = False

    except Exception as e:
        print('Exception: ' + e.message)
        sys.exit(1)

    # Close generator:
    del gen

else:
    print('No generator available with burst support!')
    sys.exit(1)

sys.exit(0)
