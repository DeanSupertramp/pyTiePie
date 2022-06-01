# GeneratorArbitrary.py
#
# This example generates an arbitrary waveform.
#
# Find more information on http://www.tiepie.com/LibTiePie .

from __future__ import print_function
from array import array
from math import sin
import sys
import libtiepie
from printinfo import *

# Print library info:
print_library_info()

# Enable network search:
libtiepie.network.auto_detect_enabled = True

# Search for devices:
libtiepie.device_list.update()

# Try to open a generator with arbitrary support:
gen = None
for item in libtiepie.device_list:
    if item.can_open(libtiepie.DEVICETYPE_GENERATOR):
        gen = item.open_generator()
        if gen.signal_types & libtiepie.ST_ARBITRARY:
            break
        else:
            gen = None

if gen:
    try:
        # Set signal type:
        gen.signal_type = libtiepie.ST_ARBITRARY

        # Select frequency mode:
        gen.frequency_mode = libtiepie.FM_SAMPLEFREQUENCY

        # Set sample frequency:
        gen.frequency = 100e3  # 100 kHz

        # Set amplitude:
        gen.amplitude = 2  # 2 V

        # Set offset:
        gen.offset = 0  # 0 V

        # Enable output:
        gen.output_on = True

        # Create signal array, and load it into the generator:
        data = array('f')

        for x in range(8192):
            data.append(sin(float(x) / 100) * (1 - (float(x) / 8192)))

        gen.set_data(data)

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
    print('No generator available with arbitrary support!')
    sys.exit(1)

sys.exit(0)
