# OscilloscopeCombineHS3HS4.py
#
# This example demonstrates how to create and open a combined instrument of all found Handyscope HS3, Handyscope HS4 and/or Handyscope HS4 DIFF's.
#
# Find more information on http://www.tiepie.com/LibTiePie .

from __future__ import print_function
import sys
import libtiepie
from printinfo import *

# Print library info:
print_library_info()

# Search for devices:
libtiepie.device_list.update()

# Try to open all HS3/HS4(D) oscilloscopes:
allowedProductIDs = [libtiepie.PID_HS3, libtiepie.PID_HS4, libtiepie.PID_HS4D]
scps = []
for item in libtiepie.device_list:
    if item.product_id in allowedProductIDs and item.can_open(libtiepie.DEVICETYPE_OSCILLOSCOPE):
        scp = item.open_oscilloscope()
        if scp:
            print('Found: ' + scp.name + ', s/n: ' + str(scp.serial_number))
            scps.append(scp)

if len(scps) > 1:
    try:
        # Create and open combined instrument:
        scp = libtiepie.device_list.create_and_open_combined_device(scps)

        # Remove HS3/HS4(D) objects, not required anymore:
        del scps

        # Print combined oscilloscope info:
        print_device_info(scp)

        # Get serial number, required for removing:
        serial_number = scp.serial_number

        # Close combined oscilloscope:
        del scp

        # Remove combined oscilloscope from the device list:
        libtiepie.device_list.remove_device(serial_number)
    except Exception as e:
        print('Exception: ' + e.message)
        sys.exit(1)

else:
    print('Not enough HS3/HS4(D)\'s found (' + str(len(scps)) + '), at least two required!')
    sys.exit(1)

sys.exit(0)
