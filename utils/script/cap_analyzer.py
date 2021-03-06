#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  1 11:17:28 2022

@author: alecce
"""

import tkinter as tk
from tkinter import filedialog
import scipy.io
import numpy as np
import time # debug

from matplotlib import pyplot as plt
from scipy.signal import butter
from scipy import signal

from scipy.optimize import curve_fit

R=196*1e3;
float_elec=1

# def modelCR(x, p0, p1, p2, p3, p4, p5, p6):
#     return p0+p1*x+p2*x**2+p3*x**3+p4*x**4+p5*x**5+p6*x**6 # poly
    #return p0 - p1 * p2**x
    
def modelCR(x, p0, p1, p2, p3, p4, p5, p6):
    return p0+p1*x+p2*x**2+p3*x**3+p4*x**4+p5*x**5+p6*x**6 # poly

def modelCX_float(x, p1, p2):
    return p2+p1/np.sqrt(x)

def modelCX(x, p1, p2):
    # return p2+1/(2*np.pi*x*p1)
    return p2+(1/x)*1/(2*np.pi*p1)

# def modelCX(x, p1):
#     # return p2+1/(2*np.pi*x*p1)
#     return (1/x)*1/(2*np.pi*p1)

root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename()

if file_path:
    mat = scipy.io.loadmat(file_path)

    f0 = mat['param']['f0'][0][0][0][0]
    fS = mat['param']['fS'][0][0][0][0]
    Ns = mat['param']['Ns'][0][0][0][0]
    Nharm = mat['param']['Nharm'][0][0][0][0]
    measType = mat['param']['measType'][0][0][0][0]
    VR=mat['signals']['VR'][0][0]
    Vin=mat['signals']['Vin'][0][0]
    CH1 = mat['signals']['CH1'][0][0]
    CH2 = mat['signals']['CH2'][0][0]
    
    Ns_cycle=fS/f0
    Ncycles=Ns/Ns_cycle
    
    # Time axis
    t = np.arange(Ns-1)/fS # Time vector
    delay = 0
    time_lockin = np.arange(Ns_cycle*(Ncycles-1))/fS # Time vector
    len_time_lockin = len(time_lockin)
else:
    print("no file")
    
s_harml = np.zeros([Nharm,len_time_lockin])
    
if measType == 0:
    sl=np.sin(2*np.pi*f0*time_lockin)
    lock_in=1j*np.exp(-1j*2*np.pi*f0*time_lockin)/sum(sl**2)
    freq=f0
    print("Measurement Type: MONO")
elif measType == 1:
    print("Measurement Type: MULTI")
    lock_in = np.zeros([Nharm,len_time_lockin], dtype = 'complex_')
    freq = np.zeros(Nharm)
    
    start = time.time()
    for j_harm in range(Nharm):
            s_harml[j_harm, :] = np.cos(2*np.pi*f0*(j_harm+1)*time_lockin+np.pi*((j_harm+1)*j_harm)/Nharm)
            lock_in[j_harm, :] = np.exp(-1j*np.pi*((j_harm+1)*j_harm)/Nharm) \
                * np.exp(-1j*2*np.pi*f0*(j_harm+1)*time_lockin) \
                    / np.sum(pow(s_harml[j_harm], 2))
                  #  / np.sum(s_harml[j_harm]**2)
                    
            freq[j_harm]=f0*(j_harm+1)
    print ("total time: %s" % (time.time() - start)) 
    VC = Vin - VR
#elif measType == 2:
    plt.figure()
    plt.title("Vin")
    plt.ylabel('Amplitude [V]')
    plt.xlabel('samples')
    plt.plot(Vin)

    plt.figure()
    plt.title("VR")
    plt.ylabel('Amplitude [V]')
    plt.xlabel('samples')
    plt.plot(VR)

    plt.figure()
    plt.title("VC")
    plt.ylabel('Amplitude [V]')
    plt.xlabel('samples')
    plt.plot(VC)
    
    # lock-in operation
    Vin_lockin = np.dot(lock_in, Vin)
    VR_lockin = np.dot(lock_in, VR)

    plt.figure()
    plt.title("Lock-in output Real part")
    plt.plot(freq, Vin_lockin.real, label = 'Vin')
    plt.plot(freq, VR_lockin.real, label='VR')
    plt.ylabel('Real part value')
    plt.xlabel('Frequency [Hz]')
    plt.legend()

    plt.figure()
    plt.title("Lock-in output Imag part")
    plt.plot(freq, Vin_lockin.imag, label = 'Vin')
    plt.plot(freq, VR_lockin.imag, label = 'VR')
    plt.ylabel('Real part value')
    plt.xlabel('Frequency [Hz]')
    plt.legend()
    
    #b,a = butter(2, [0.25, 1.5*Nharm]*f0/(fS/2), btype='bandpass')
    b,a = butter(2, 2*Nharm*f0/(fS/2), btype='lowpass') # ref: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.butter.html

    CH1f = signal.filtfilt(b, a, CH1, padtype = None) # ref: https://dsp.stackexchange.com/questions/11466/differences-between-python-and-matlab-filtfilt-function
    CH2f = signal.filtfilt(b, a, CH2, padtype = None)
    
    VRf=CH1f.transpose()[int(4+Ns_cycle*1+delay) : int(4+Ns_cycle*(Ncycles)+delay)]
    Vin_f=CH2f.transpose()[int(4+Ns_cycle*1+delay) : int(4+Ns_cycle*(Ncycles)+delay)]
    
    plt.figure()
    plt.title("Signals Filtered")
    plt.plot(VRf, label = 'VRf')
    plt.plot(Vin_f, label = 'Vin_f')
    plt.ylabel('Amplitude [V]')
    plt.xlabel('samples')
    plt.legend()

    plt.figure()
    plt.title("Signals Filtered")
    plt.plot(CH1f.transpose(), label = 'CH1f')
    plt.plot(CH2f.transpose(), label = 'CH2f')
    plt.ylabel('Amplitude [V]')
    plt.xlabel('samples')
    plt.legend()

    plt.figure()
    plt.title("Zoom of Signals Filtered")
    plt.plot(CH1.transpose(), label = 'CH1')
    plt.plot(CH1f.transpose(), label = 'CH1f')
    plt.ylabel('Amplitude [V]')
    plt.xlabel('samples')
    plt.xlim([0,200])
    plt.legend()
    
    # PHASOR lock-in operation
    phasorVin = np.dot(lock_in, Vin_f)
    phasorVR = np.dot(lock_in, VRf)
    
    plt.figure()
    plt.title("abs value of Phasor signal Filtered")
    plt.plot(freq, abs(phasorVin), label = 'phasorVin')
    plt.plot(freq, abs(phasorVR), label = 'phasorVR')
    plt.ylabel('Amplitude [V]')
    plt.xlabel('Frequency [Hz]')
    plt.legend()
    
    if float_elec == 0:
        phasorVC = phasorVin - phasorVR
        ZC = phasorVC/phasorVR*R
        RC = ZC.real
        XC = -ZC.imag
        Cestimated = 1/(2*np.pi*freq*np.squeeze(XC))*1e12
        Cestimated_mean = np.mean(Cestimated)
        print("Cestimated_mean: ",Cestimated_mean, "pF")
        
        plt.figure()
        plt.subplot(2,2,1)
        plt.title("phasorVC.real", fontsize=10, fontweight = 'bold', pad=5)
        plt.ylabel('Amplitude [V]')
        plt.xlabel('Frequency [Hz]')
        plt.plot(freq, phasorVC.real)
        plt.subplot(2,2,2)
        plt.ylabel('Amplitude [V]')
        plt.xlabel('Frequency [Hz]')
        plt.title("phasorVC.imag", fontsize=10, fontweight = 'bold', pad=5)
        plt.plot(freq, phasorVC.imag)
        plt.subplot(2,2,3)
        plt.ylabel('Amplitude [V]')
        plt.xlabel('Frequency [Hz]')
        plt.title("RC", fontsize=10, fontweight = 'bold', pad=5)
        plt.plot(freq, RC)
        plt.subplot(2,2,4)
        plt.ylabel('Amplitude [V]')
        plt.xlabel('Frequency [Hz]')
        plt.title("XC", fontsize=10, fontweight = 'bold', pad=5)
        plt.plot(freq, XC)
        plt.subplots_adjust(hspace = 0.55, wspace=0.45)

        
        plt.figure()
        plt.title("C estimated", fontsize=10, fontweight = 'bold', pad=5)
        plt.ylabel('Capacitance [pF]')
        plt.xlabel('Frequency [Hz]')
        plt.plot(freq, Cestimated)
        
        plt.figure()
        plt.subplot(2,1,1)
        plt.title("Phasor VC", fontsize=10, fontweight = 'bold', pad=5)
        plt.ylabel('ABS phasor VC')
        plt.xlabel('Frequency [Hz]')
        plt.plot(freq, abs(phasorVC))
        plt.subplot(2,1,2)
        plt.title("Phasor VC", fontsize=10, fontweight = 'bold', pad=5)
        plt.ylabel('angle phasor VC')
        plt.xlabel('Frequency [Hz]')
        plt.plot(freq, np.angle(phasorVC))
        plt.subplots_adjust(hspace = 0.55, wspace=0.45)

        plt.figure()
        plt.subplot(2,1,1)
        plt.title("Impedance ZC", fontsize=10, fontweight = 'bold', pad=5)
        plt.ylabel('abs(ZC)')
        plt.xlabel('Frequency [Hz]')
        plt.plot(freq, abs(ZC))
        plt.subplot(2,1,2)
        plt.ylabel('abs(ZC)')
        plt.xlabel('Frequency [Hz]')
        plt.plot(freq, np.angle(ZC))
        
        # FITTING
        popt, pcov = curve_fit(modelCX, freq, np.squeeze(XC), p0 = [2e-11, 0]) 
        Cestimated2 = popt[0]*1e12
        print("C estimated from fitting: ", Cestimated2, "pF")

        plt.figure()
        plt.title("Capacitive reactance XC", fontsize=10, fontweight = 'bold', pad=5)
        plt.plot(freq, XC, label = 'XC')
        plt.plot(freq, modelCX(freq, *popt), label = 'XC fitted')
        plt.ylabel('value (ohm)')
        plt.xlabel('Frequency [Hz]')
        plt.legend()
        
        popt2, pcov2 = curve_fit(modelCR, freq, np.squeeze(RC))
        plt.figure()
        plt.title("Capacitive reactance XC", fontsize=10, fontweight = 'bold', pad=5)
        plt.ylabel("RC [ohm]")
        plt.xlabel("frequency [Hz]")
        plt.plot(freq, RC, label = "RC")
        plt.plot(freq, modelCR(freq, *popt2), label = "RC fitted")
        plt.legend()
        
    else:
        phasorVC = phasorVR
        ZC = phasorVC/phasorVin
        RC = ZC.real
        XC = ZC.imag
        Cestimated = 1/(2*np.pi*freq*np.squeeze(XC))*1e12
        Cestimated_mean = np.mean(Cestimated)
        print("Cestimated_mean: ", Cestimated_mean, "pF")

        
        plt.figure()
        plt.subplot(2,2,1)
        plt.title("phasorVC.real", fontsize=10, fontweight = 'bold', pad=5)
        plt.ylabel('Amplitude [V]')
        plt.xlabel('Frequency [Hz]')
        plt.plot(freq, phasorVC.real)
        plt.subplot(2,2,2)
        plt.ylabel('Amplitude [V]')
        plt.xlabel('Frequency [Hz]')
        plt.title("phasorVC.imag", fontsize=10, fontweight = 'bold', pad=5)
        plt.plot(freq, phasorVC.imag)
        plt.subplot(2,2,3)
        plt.ylabel('Amplitude [V]')
        plt.xlabel('Frequency [Hz]')
        plt.title("RC", fontsize=10, fontweight = 'bold', pad=5)
        plt.plot(freq, RC)
        plt.subplot(2,2,4)
        plt.ylabel('Amplitude [V]')
        plt.xlabel('Frequency [Hz]')
        plt.title("XC", fontsize=10, fontweight = 'bold', pad=5)
        plt.plot(freq, XC)
        plt.subplots_adjust(hspace = 0.55, wspace=0.45)
        
        plt.figure()
        plt.title("C estimated", fontsize=10, fontweight = 'bold', pad=5)
        plt.ylabel('Capacitance [pF]')
        plt.xlabel('Frequency [Hz]')
        plt.plot(freq, Cestimated)
        
        plt.figure()
        plt.subplot(2,1,1)
        plt.title("Phasor VC", fontsize=10, fontweight = 'bold', pad=5)
        plt.ylabel('ABS phasor VC')
        plt.xlabel('Frequency [Hz]')
        plt.plot(freq, abs(phasorVC))
        plt.subplot(2,1,2)
        plt.title("Phasor VC", fontsize=10, fontweight = 'bold', pad=5)
        plt.ylabel('angle phasor VC')
        plt.xlabel('Frequency [Hz]')
        plt.plot(freq, np.angle(phasorVC))
        plt.subplots_adjust(hspace = 0.55, wspace=0.45)
        
        plt.figure()
        plt.subplot(2,1,1)
        plt.title("Impedance ZC", fontsize=10, fontweight = 'bold', pad=5)
        plt.ylabel('abs(ZC)')
        plt.xlabel('Frequency [Hz]')
        plt.plot(freq, abs(ZC))
        plt.subplot(2,1,2)
        plt.ylabel('abs(ZC)')
        plt.xlabel('Frequency [Hz]')
        plt.plot(freq, np.angle(ZC))
        
        popt, pcov = curve_fit(modelCX_float, freq, np.squeeze(XC)) 
        
        plt.figure()
        plt.title("Capacitive reactance XC", fontsize=10, fontweight = 'bold', pad=5)
        plt.plot(freq, XC, label = 'XC')
        plt.plot(freq, modelCX(freq, *popt), label = 'XC fitted')
        plt.ylabel('value (ohm)')
        plt.xlabel('Frequency [Hz]')
        plt.legend()
        
        popt2, pcov2 = curve_fit(modelCR, freq, np.squeeze(RC))
        plt.figure()
        plt.title("Capacitive reactance XC", fontsize=10, fontweight = 'bold', pad=5)
        plt.ylabel("RC [ohm]")
        plt.xlabel("frequency [Hz]")
        plt.plot(freq, RC, label = "RC")
        plt.plot(freq, modelCR(freq, *popt2), label = "RC fitted")
        plt.legend()

else:
    print("measType is not defined")        