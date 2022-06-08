from __future__ import print_function
import time
# import os
import sys
import libtiepie
# from printinfo import *
import numpy as np
from matplotlib import pyplot as plt
from array import array
# from math import sin
import Z_meter

f0=4e3              #freq. fondamentale
Nharm=50            # n° armoniche
Tsignal=2           # in [ms]
fS=1e8              # in [Hz] 100 MHz

# s, lock_in, params,__,__ = Z_meter.Z_meter_excitation(f0,Nharm,Tsignal,fS,5)
segnale, lock_in, params = Z_meter.Z_meter_excitation(f0,Nharm,Tsignal,fS,5)[0:3] # più pulito (rif: https://stackoverflow.com/a/431868 )


def tiepieList():
    if len(libtiepie.device_list) > 0:
        print()
        print('Available devices:')
    
        for item in libtiepie.device_list:
            print('  Name: ' + item.name)
            print('    Serial number  : ' + str(item.serial_number))
            print('    Available types: ' + libtiepie.device_type_str(item.types))
    
            if item.has_server:
                print('    Server         : ' + item.server.url + ' (' + item.server.name + ')')
    else:
        print('No devices found!')


# Print library info:
# print_library_info()

# Enable network search:
# libtiepie.network.auto_detect_enabled = True

# Search for devices:
libtiepie.device_list.update()

tiepieList() # Mostra una lista dei dispositivi collegati e le loro funzioni

# Try to open an oscilloscope with block measurement support and a generator in the same device:
scp = None  # INPUT OSCILLOSCOPIO
gen = None  # OUTPUT GENERATORE
for item in libtiepie.device_list:
    if (item.can_open(libtiepie.DEVICETYPE_OSCILLOSCOPE)) and (item.can_open(libtiepie.DEVICETYPE_GENERATOR)):
        scp = item.open_oscilloscope()
        if scp.measure_modes & libtiepie.MM_BLOCK:
            gen = item.open_generator()
            break
        else:
            scp = None
Nsamples=segnale.size
if scp and gen:
    try:
        # ********** Oscilloscope settings: **********      # Proprietà scp: https://github.com/TiePie/python-libtiepie/blob/d2a9875855298a58d6a16be5b61aaa89a558e7d8/libtiepie/oscilloscope.py#L505
        # Set measure mode:
        scp.measure_mode = libtiepie.MM_BLOCK               # riferim: https://api.tiepie.com/libtiepie/0.9.16/group__scp__measurements__mode.html
        # Set sample frequency:
        scp.sample_frequency = fS  # 100 MHz
        # Set record length:
        scp.record_length = Nsamples  # 10000 samples
        # Set pre sample ratio:
        scp.pre_sample_ratio = 0  # 0 %
        # For all channels:
        for ch in scp.channels:                             # per i 2 canali disponibili
            # Enable channel to measure it:
            ch.enabled = True
            # Set range:
            # ch.ranges                                     # mostra i possibili range = [0.2, 0.4, 0.8, 2.0, 4.0, 8.0, 20.0, 40.0, 80.0]
            ch.range = 0.2                                  # min 200mV, max 80V
            ch.auto_ranging = True                          # range riferim: https://api.tiepie.com/libtiepie/0.9.15/group__scp__ch__range.html
            # Set coupling:
            # ch.couplings                                  # 3 Opzioni CK_DCV (1), CK_ACV (2) . NON supporta invece CK_ACA (8), CK_DCA (4), CK_OHM (16) e CK_UNKNOWN (0)
            ch.coupling = libtiepie.CK_DCV                  # DC Volt
        # Set trigger timeout:
        scp.trigger_time_out = 1  # 1 s
        # Disable all channel trigger sources:
        for ch in scp.channels:
            ch.trigger.enabled = False
        # Locate trigger input:
        trigger_input = scp.trigger_inputs.get_by_id(libtiepie.TIID_GENERATOR_START)  # or TIID_GENERATOR_NEW_PERIOD or TIID_GENERATOR_STOP
        if trigger_input is None:
            raise Exception('Unknown trigger input!')
        # Enable trigger input:
        trigger_input.enabled = True

        # ********** Generator settings: **********
        # Set signal type:
        gen.signal_type = libtiepie.ST_ARBITRARY
 # Select frequency mode:
        gen.frequency_mode = libtiepie.FM_SAMPLEFREQUENCY
        # Set sample frequency:
        gen.frequency = fS  # 100 kHz
        # Set amplitude:
        gen.amplitude =1# 2 V
        # Set offset:
        gen.offset = 0  # 0 V
        # Enable output:
        gen.output_on = True
        gen.mode = libtiepie.GM_BURST_COUNT
        # Set burst count:
        gen.burst_count = 1  # 100 periods
        # Create signal array, and load it into the generator:
        dataIN= array('f')
        dataOUT= array('f')

        for jx in range(segnale.size):
            dataIN.append(segnale[0,jx])

        gen.set_data(dataIN)
        # Print oscilloscope info:
        # print_device_info(scp)

        # Print generator info:
        # print_device_info(gen)

        for j in range(10):
            # Start measurement:
            scp.start()
            # Start signal generation:
            gen.start()
            # Wait for measurement to complete:
            while not scp.is_data_ready:
                time.sleep(0.002)  # 10 ms delay, to save CPU time
            # Stop generator:
            gen.stop()
            # Disable output:
            # Get data:
            dataOUT = scp.get_data()
            # y[0,:]=dataOUT[0]
            # y[1,:]=dataOUT[1]

            # PLOT
            plt.plot(np.arange(0,np.size(dataOUT,1),1),np.transpose(dataOUT))
            time.sleep(.1)
            plt.show()
            time.sleep(.1)
            print(j)
            if j <9:
                plt.cla()

        gen.output_on = False

        # Output CSV data:
        # csv_file = open('OscilloscopeGeneratorTrigger.csv', 'w')
        # try:
        #     csv_file.write('Sample')
        #     for i in range(len(data)):
        #         csv_file.write(';Ch' + str(i + 1))
        #     csv_file.write(os.linesep)
        #     for i in range(len(data[0])):
        #         csv_file.write(str(i))
        #         for j in range(len(data)):
        #             csv_file.write(';' + str(data[j][i]))
        #         csv_file.write(os.linesep)
        #     print()
        #     print('Data written to: ' + csv_file.name)
        # finally:
        #     csv_file.close()
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
