# GeneratorGatedBurst.py
#
# This example generates a 10 kHz square waveform, 10 Vpp when the external trigger input is active.
#
# Find more information on http://www.tiepie.com/LibTiePie .

from __future__ import print_function
import sys
import libtiepie
from printinfo import *

# Print library info:
print_library_info()

# Enable network search:
libtiepie.network.auto_detect_enabled = True

# Search for devices:
libtiepie.device_list.update()

# Try to open a generator with gated burst support:
gen = None
for item in libtiepie.device_list:
    if item.can_open(libtiepie.DEVICETYPE_GENERATOR):
        gen = item.open_generator()
        if (gen.modes_native & libtiepie.GM_GATED_PERIODS) and len(gen.trigger_inputs) > 0:
            break
        else:
            gen = None

if gen:
    try:
        # Set signal type:
        gen.signal_type = libtiepie.ST_SQUARE

        # Set frequency:
        gen.frequency = 10e3  # 10 kHz

        # Set amplitude:
        gen.amplitude = 5  # 5V

        # Set offset:
        gen.offset = 0  # 0 V

        # Set mode:
        gen.mode = libtiepie.GM_GATED_PERIODS

        # Locate trigger input:
        trigger_input = gen.trigger_inputs.get_by_id(libtiepie.TIID_EXT1)

        if trigger_input is None:
            raise Exception('Unknown trigger input!')

        # Enable trigger input:
        trigger_input.enabled = True

        # Enable output:
        gen.output_on = True

        # Print generator info:
        print_device_info(gen)

        # Start signal burst:
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
    print('No generator available with gated burst support!')
    sys.exit(1)

sys.exit(0)
