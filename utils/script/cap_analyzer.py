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
float_elec=0

def modelCR(x, p1, p2, p3, p4):
    return p1+(p2-p1)/(1+(x/p3)**p4)

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
elif measType == 1:
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
    plt.plot(Vin)

    plt.figure()
    plt.title("VR")
    plt.plot(VR)

    plt.figure()
    plt.title("VC")
    plt.plot(VC)
    
    Vin_lockin = np.dot(lock_in, Vin)
    VR_lockin = np.dot(lock_in, VR)

    plt.figure()
    plt.title("Real")
    plt.plot(np.arange(10), Vin_lockin.real, label = 'Vin')
    plt.plot(np.arange(10), VR_lockin.real, label='VR')
    plt.legend()

    plt.figure()
    plt.title("Imag")
    plt.plot(np.arange(10), Vin_lockin.imag, label = 'Vin')
    plt.plot(np.arange(10), VR_lockin.imag, label = 'VR')   
    plt.legend()
    
    #b,a = butter(2, [0.25, 1.5*Nharm]*f0/(fS/2), btype='bandpass')
    b,a = butter(2, 2*Nharm*f0/(fS/2), btype='lowpass')

    CH1f = signal.filtfilt(b, a, CH1, padtype = None) # ref: https://dsp.stackexchange.com/questions/11466/differences-between-python-and-matlab-filtfilt-function
    CH2f = signal.filtfilt(b, a, CH2, padtype = None)
    
    VRf=CH1f.transpose()[int(4+Ns_cycle*1+delay) : int(4+Ns_cycle*(Ncycles)+delay)]
    Vin_f=CH2f.transpose()[int(4+Ns_cycle*1+delay) : int(4+Ns_cycle*(Ncycles)+delay)]
    
    plt.figure()
    plt.plot(VRf, label = 'VRf')
    plt.plot(Vin_f, label = 'Vin_f')
    plt.legend()

    plt.figure()
    plt.plot(CH1f.transpose(), label = 'CH1f')
    plt.plot(CH2f.transpose(), label = 'CH2f')
    plt.legend()

    plt.figure()
    plt.plot(CH1.transpose(), label = 'CH1')
    plt.plot(CH1f.transpose(), label = 'CH1f')
    plt.xlim([0,200])
    plt.legend()
    
    phasorVin = np.dot(lock_in, Vin_f)
    phasorVR = np.dot(lock_in, VRf)
    
    plt.figure()
    plt.plot(phasorVin, label = 'phasorVin')
    plt.plot(phasorVR, label = 'phasorVR')
    plt.legend()
    
    if float_elec == 0:
        phasorVC = phasorVin - phasorVR
        ZC = phasorVC/phasorVR*R
        RC = ZC.real
        XC = -ZC.imag
        Cestimated = 1/(2*np.pi*freq*np.squeeze(XC))*1e12
        Cestimated_mean = np.mean(Cestimated)
        print(Cestimated_mean, "pF")
        
        plt.figure()
        plt.subplot(2,2,1)
        plt.plot(phasorVC.real)
        plt.subplot(2,2,2)
        plt.plot(phasorVC.imag)
        plt.subplot(2,2,3)
        plt.plot(RC)
        plt.subplot(2,2,4)
        plt.plot(XC)
        
        plt.figure()
        plt.plot(Cestimated[0:40])
        
        plt.figure()
        plt.subplot(2,1,1)
        plt.plot(abs(phasorVC))
        plt.subplot(2,1,2)
        plt.plot(np.angle(phasorVC))
        
        plt.figure()
        plt.subplot(2,1,1)
        plt.plot(abs(ZC))
        plt.subplot(2,1,2)
        plt.plot(np.angle(ZC))
        
        popt, pcov = curve_fit(modelCX, freq, np.squeeze(XC), p0 = [2e-11, 0]) 
        Cestimated2 = popt[0]*1e12
        print(Cestimated2, "pF")

        plt.figure()
        plt.plot(freq, XC)
        plt.plot(freq, modelCX(freq, *popt))
        
        popt, pcov = curve_fit(modelCR, freq, np.squeeze(RC))
        plt.figure()
        plt.plot(freq, RC)
        plt.plot(freq, modelCR(freq, *popt))
        
    else:
        phasorVC = phasorVR
        ZC = phasorVC/phasorVin
        RC = ZC.real
        XC = ZC.imag
        Cestimated = 1/(2*np.pi*freq*np.squeeze(XC))*1e12 

        
        plt.figure()
        plt.subplot(2,2,1)
        plt.plot(phasorVC.real)
        plt.subplot(2,2,2)
        plt.plot(phasorVC.imag)
        plt.subplot(2,2,3)
        plt.plot(RC)
        plt.subplot(2,2,4)
        plt.plot(XC)
        
        plt.figure()
        plt.plot(Cestimated[0:40])
        
        plt.figure()
        plt.subplot(2,1,1)
        plt.plot(abs(phasorVC))
        plt.subplot(2,1,2)
        plt.plot(np.angle(phasorVC))
        
        plt.figure()
        plt.subplot(2,1,1)
        plt.plot(abs(ZC))
        plt.subplot(2,1,2)
        plt.plot(np.angle(ZC))
        
        popt, pcov = curve_fit(modelCX_float, freq, np.squeeze(XC)) 
        
        plt.figure()
        plt.plot(freq, XC)
        plt.plot(freq, modelCX_float(freq, *popt))
        
        popt, pcov = curve_fit(modelCR, freq, np.squeeze(RC))
        plt.figure()
        plt.plot(freq, RC)
        plt.plot(freq, modelCR(freq, *popt))



else:
    print("measType is not defined")        