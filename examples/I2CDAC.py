# I2CDAC.py
#
# This example demonstrates how to use an I2C host supported by LibTiePie.
# It shows how to control an Analog Devices AD5667 dual 16-bit DAC on I2C address 12.
#
# Find more information on http://www.tiepie.com/LibTiePie .

from __future__ import print_function
import sys
import libtiepie
from printinfo import *

AD5667_ADDRESS = 12

# AD5667 registers:
AD5667_REG_DAC_A = 0x00
AD5667_REG_DAC_B = 0x01
AD5667_REG_DAC_ALL = 0x07

# AD5667 commands:
AD5667_CMD_WRITE = 0x00
AD5667_CMD_UPDATE = 0x08
AD5667_CMD_WRITE_UPDATE_ALL = 0x10
AD5667_CMD_WRITE_UPDATE = 0x18
AD5667_CMD_POWER = 0x20
AD5667_CMD_RESET = 0x28
AD5667_CMD_LDAC_SETUP = 0x30
AD5667_CMD_REF_SETUP = 0x38

# Print library info:
print_library_info()

# Enable network search:
libtiepie.network.auto_detect_enabled = True

# Search for devices:
libtiepie.device_list.update()

# Try to open an I2C host:
i2c = None
for item in libtiepie.device_list:
    if item.can_open(libtiepie.DEVICETYPE_I2CHOST):
        i2c = item.open_i2c_host()
        if i2c:
            break

if i2c:
    try:
        # Print I2C info:
        print_device_info(i2c)

        # Turn on internal reference for DAC A:
        i2c.write_byte_word(AD5667_ADDRESS, AD5667_CMD_REF_SETUP or AD5667_REG_DAC_A, 1)

        # Set DAC A to mid level:
        i2c.write_byte_word(AD5667_ADDRESS, AD5667_CMD_WRITE_UPDATE or AD5667_REG_DAC_A, 0x8000)
    except Exception as e:
        print('Exception: ' + e.message)
        sys.exit(1)

    # Close I2C host:
    del i2c

else:
    print('No I2C host available!')
    sys.exit(1)

sys.exit(0)
