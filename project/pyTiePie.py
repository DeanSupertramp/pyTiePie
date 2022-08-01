from __future__ import print_function
import time
import os
import sys
import libtiepie
from libtiepie.const import SIGNAL_TYPES, STM_AMPLITUDE, STM_OFFSET
from libtiepie.const import ST_UNKNOWN, ST_SINE, ST_TRIANGLE, ST_SQUARE, ST_DC, ST_NOISE, ST_ARBITRARY, ST_PULSE
import numpy as np
from matplotlib import pyplot as plt
from array import array
import Z_meter
import argparse
from MyArgParser import MyArgParser
import json

def command(args):
    global k2v
    global f
    global Nsamples
    global a
    global o
    print('Running %s with args:' % command.__name__,*args.values(),sep=' ')
    # controllo se il comando è presente tra i segnali della libreria
    # ref: https://www.geeksforgeeks.org/python-get-key-from-value-in-dictionary/
    try:
        if args["signal"].capitalize() in SIGNAL_TYPES.values():
            print("Command", args["signal"].capitalize(), "found!")
            k2v = list(SIGNAL_TYPES.keys())[list(SIGNAL_TYPES.values()).index(args["signal"].capitalize())] # key to value      
            f = args["freq"]
            print("frequency setted at :\t", str(f), " Hz")
            # controllo se il segnale accetta il parametro offset
            if bool(STM_OFFSET & k2v ): # MASK
                print("Set Offset:\t", args["offset"])
                if args["offset"] > gen.offset_min:
                    if args["offset"] < gen.offset_max:
                        o = args["offset"]
                    else:
                        print("offset out of MAX range")
                        sys.exit(1)
                else:
                    print("offset out of MIN range")
                    sys.exit(1)
            
            if SIGNAL_TYPES[k2v].upper() == "ARBITRARY":
                Nsamples=segnale.size
            else:
                Nsamples=int(fS/f)
    except:
        if args["signalDC"].upper() in SIGNAL_TYPES.values(): # Only DC signal
            print("Command", args["signalDC"].upper(), "found!")
            k2v = list(SIGNAL_TYPES.keys())[list(SIGNAL_TYPES.values()).index(args["signalDC"].upper())]
            # o = args["offsetDC"]
            
            # controllo se il segnale accetta il parametro offset
            if bool(STM_OFFSET & k2v ): # MASK
                print("Set OffsetDC:\t", args["offsetDC"])
                if args["offsetDC"] > gen.offset_min:
                    if args["offsetDC"] < gen.offset_max:
                        o = args["offsetDC"]
                    else:
                        print("offsetDC out of MAX range")
                        sys.exit(1)
                else:
                    print("offsetDC out of MIN range")
                    sys.exit(1)
            Nsamples = int(fS*1e-3) # 1 sec 
    # gen.signal_type = SIGNAL_TYPES[k2v]    # ref: https://api.tiepie.com/libtiepie/0.4.3/group___s_t__.html
    # controllo se il segnale accetta il parametro ampiezza
    if bool(STM_AMPLITUDE & k2v ): # MASK
        print("Set Amplitude: ", args["ampl"])
        if args["ampl"] > gen.amplitude_min:
            if args["ampl"] < gen.amplitude_max:
                a = args["ampl"]
            else:
                print("amplitude out of MAX range")
                sys.exit(1)
        else:
            print("amplitude out of MIN range")
            sys.exit(1)

    # # controllo se il segnale accetta il parametro offset
    # if bool(STM_OFFSET & k2v ): # MASK
    #     print("Set Offset: ", args["offset"])
    #     if args["offset"] > gen.offset_min:
    #         if args["offset"] < gen.offset_max:
    #             o = args["offset"]
    #         else:
    #             print("offset out of MAX range")
    #             sys.exit(1)
    #     else:
    #         print("offset out of MIN range")
    #         sys.exit(1)
           
signal_dict = {"UNKNOWN" : libtiepie.ST_UNKNOWN,        # 0
               "SINE" : libtiepie.ST_SINE,              # 1
               "TRIANGLE" : libtiepie.ST_TRIANGLE,      # 2
               "SQUARE" : libtiepie.ST_SQUARE,          # 4
               "DC" : libtiepie.ST_DC,                  # 8
               "NOISE" : libtiepie.ST_NOISE,            # 16
               "ARBITRARY" : libtiepie.ST_ARBITRARY}    # 32
        
def gen_settings():
    global signalType
    # ********** Generator settings: **********
    try:
        # gen.signal_type = signal_dict[signalType]    # ref: https://api.tiepie.com/libtiepie/0.4.3/group___s_t__.html
        gen.signal_type = k2v
        # see const.py for signal definitions and types
        if SIGNAL_TYPES[k2v].upper() == "ARBITRARY":
            # Select frequency mode:
            gen.frequency_mode = libtiepie.FM_SAMPLEFREQUENCY
            # Set sample frequency:
            gen.frequency = fS  # 100 MHz
            # Set amplitude:
            gen.amplitude = a # 1Vpp
            # Set offset:
            gen.offset = o  # 0 V
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
        # Print generator info:
        # print_device_info(gen)

        # if signalType == "DC":
        elif SIGNAL_TYPES[k2v].upper() in "SINE TRIANGLE SQUARE NOISE":
            # Set frequency:
            gen.frequency = f  # 1 kHz
            # Set amplitude:
            gen.amplitude = a  # 1 V
            # Set offset:
            gen.offset = o  # 0 V
            # Enable output:
            gen.output_on = True
            gen.mode = libtiepie.GM_CONTINUOUS

        elif SIGNAL_TYPES[k2v].upper() == "DC":
            # Set offset:
            gen.offset = o  # 0 V
            # Enable output:
            gen.output_on = True
        print("signal type selected: ", SIGNAL_TYPES[k2v])
        return True
    except Exception as e:
        print('gen Exception: ', e)
        # sys.exit(1)
        return False
    # else:
    #     print("signalType not correct")
    #     return False

# gen.signal_types restituisce maschera in bit dei segnali
# from libtiepie.utils import signal_type_str # funzione builtin in libtiepie.utils
# print('  Signal types              : ' + signal_type_str(gen.signal_types))
# Commands configuration
tiepie_setSignal = MyArgParser("set", description = "select signal") # check in libtiepie.const
tiepie_setSignal.add_argument("signal", type=str, help='Signal Type')
tiepie_setSignal.add_argument("ampl", nargs='?', default = 1.0, type=float, help='Amplitude')
tiepie_setSignal.add_argument("freq", nargs='?', default = 100, type=float, help='Frequency')
tiepie_setSignal.add_argument("offset", nargs='?', default = 0, type=float, help='Offset') 

tiepie_setDC = MyArgParser("setDC", description = "set DC") # check in libtiepie.const
tiepie_setDC.add_argument("offsetDC", type=float, help='offset') 
tiepie_setDC.add_argument("signalDC", nargs='?', default = "DC", type=str, help='DC label')

# Add all commands to an instruction set dictionary
commands = {}
commands['set'] = {'parser': tiepie_setSignal ,'execution': command}
commands['setDC'] = {'parser': tiepie_setDC ,'execution': command}

# Parse a line and in case execute a command
def process(line):
    sline = line.strip() # string
    if not sline:
        return True
    l = sline.split() # list
    the_command = l[0]
    if the_command == 'exit':
        return False
    if the_command in commands:
        parser = commands.get(the_command)['parser']
        funzione = commands.get(the_command)['execution']
        try:
            argomenti = parser.parse_args(l[1:])
            # do something with this command and these arguments
            funzione(vars(argomenti)) # vars return a dict
        except Exception as message:
            print('%s: error: %s' % (the_command,message))
    else:
        print('%s: command not found' % the_command)
    return True

def prompt():
    print("\nCommand CLI options:")
    print("set <SIGNAL> <AMPLITUDE> <FREQUENCY> <OFFSET>")
    print("setDC <OFFSET>")
    print("exit")
    return ">>"

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
        return item.name
    else:
        print('No devices found!')
        
def tiepieInit():
    # Print library info:
    # print_library_info()
    # Try to open an oscilloscope with block measurement support and a generator in the same device:
    global scp, gen
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
    return scp, gen

def reset_tiepie():
    #!/usr/bin/python
    from usb.core import find as finddev
    for dev in finddev(find_all=True):
        print(dev)
    dev = finddev(idVendor=0x0e36, idProduct=0x001b) # individuato usando lsusb da terminale ubuntu
    dev.reset()
    # import usb
    # busses = usb.busses()
    # for bus in busses:
    #     devices = bus.devices
    #     for dev in devices:
    #         print("Device:", dev.filename)
    #         print("  idVendor: %d (0x%04x)" % (dev.idVendor, dev.idVendor))
    #         print("  idProduct: %d (0x%04x)" % (dev.idProduct, dev.idProduct))
    
    # from usb.util import dispose_resource
    # dispose_resources(dev)
    
def osc_settings(): 
     # ********** Oscilloscope settings: **********      # Proprietà scp: https://github.com/TiePie/python-libtiepie/blob/d2a9875855298a58d6a16be5b61aaa89a558e7d8/libtiepie/oscilloscope.py#L505
     # Set measure mode:
     scp.measure_mode = libtiepie.MM_BLOCK               # riferim: https://api.tiepie.com/libtiepie/0.9.16/group__scp__measurements__mode.html
     # Set sample frequency:
     scp.sample_frequency = fS  # 100 MHz
     # Set record length:
     scp.record_length = Nsamples  # 10000 samples
     # Set pre sample ratio:
     scp.pre_sample_ratio = 0  # 0 %
     # Set respolution
     scp.resolution = 14
     # For all channels:
     for ch in scp.channels:                             # per i 2 canali disponibili
         # Enable channel to measure it:
         ch.enabled = True
         # Set range:
         # ch.ranges                                     # mostra i possibili range = [0.2, 0.4, 0.8, 2.0, 4.0, 8.0, 20.0, 40.0, 80.0]
         ch.range = 2                                  # min 200mV, max 80V
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
         return False
     # Enable trigger input:
     trigger_input.enabled = True
    # Print oscilloscope info:
    # print_device_info(scp)
     return True

def acquire_data():
    #if signalType == "ARBITRARY":
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
        # else:
        #     # Wait for keystroke:
        #     print('Press Enter to stop signal generation...')
        #     if sys.version_info < (3, 0):  # Python 2.x
        #         raw_input()
        #     else:  # Python 3.x
        #         input()
        # Disable output:
        # Get data:
        dataOUT = scp.get_data()
        # y[0,:]=dataOUT[0]
        # y[1,:]=dataOUT[1]
        
        saveCSV(dataOUT)
        
        # PLOT
        plt.plot(np.arange(0,np.size(dataOUT,1),1),np.transpose(dataOUT))
        time.sleep(.1)
        plt.show()
        time.sleep(.1)
        print(j)
        if j <9:
            plt.cla() # Clear current axes
    gen.output_on = False

def saveCSV(dataOUT):
    # Output CSV data:
    csv_file = open('1.csv', 'w')
    try:
        csv_file.write('Sample')
        for i in range(len(dataOUT)):
            csv_file.write(',Ch' + str(i + 1))
        csv_file.write(os.linesep)
        for i in range(len(dataOUT[0])):
            csv_file.write(str(i))
            for j in range(len(dataOUT)):
                csv_file.write(',' + str(dataOUT[j][i]))
            csv_file.write(os.linesep)
        print()
        print('Data written to: ' + csv_file.name)
    finally:
        csv_file.close()
        
def saveJSON():
    data = {"f0" : f0,
         "Nharm" : Nharm,
         "Tsignal" : Tsignal,
         "fS" : fS}
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Search for devices:
libtiepie.device_list.update()
tiepieList() # Mostra una lista dei dispositivi collegati e le loro funzioni
scp, gen = tiepieInit()

f0=4e3              #freq. fondamentale
Nharm=50            # n° armoniche
Tsignal=2           # in [ms]

# fS=1e8              # in [Hz] 100 MHz
if "220" in tiepieList().split()[1] : # resolution: 14 bit
    fS = scp.sample_frequency_max/4
else:
    fS = scp.sample_frequency_max/5

# s, lock_in, params,__,__ = Z_meter.Z_meter_excitation(f0,Nharm,Tsignal,fS,5)
segnale, lock_in, params = Z_meter.Z_meter_excitation(f0,Nharm,Tsignal,fS)[0:3] # più pulito (rif: https://stackoverflow.com/a/431868 )

saveJSON()

def main():
    global scp, gen
    while process(input(prompt())):
    # pass
        if scp and gen:
            try:
                if osc_settings() and gen_settings():
                    acquire_data()
            except Exception as e:
                print('Exception: ', e)
                sys.exit(1)    
            # Close oscilloscope:
            del scp
            # Close generator:
            del gen
        else:
            print('No oscilloscope available with block measurement support or generator available in the same unit!')
            sys.exit(1)
        sys.exit(0) # ref: https://docs.python.org/3/library/sys.html#sys.exit
                    # ZERO: "successful termination”
                    # NONZERO: "abnormal termination"

if __name__ == '__main__':
    main()
