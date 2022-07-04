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

def modelC(p, x):
    return p(1)+(p(2)-p(1))/(1+(x/p(3))**p(4))

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
        for l in range(len_time_lockin):
           # s_harml[j_harm, l] = np.cos(2*np.pi*f0*j_harm*time_lockin[l]+np.pi*(j_harm*(j_harm))/Nharm)
            lock_in[j_harm, l] = np.exp(-1j*np.pi*(j_harm*(j_harm-1))/Nharm) \
                * np.exp(-1j*2*np.pi*f0*j_harm*time_lockin[l]) \
                    / np.sum(pow(s_harml[j_harm], 2))
                  #  / np.sum(s_harml[j_harm]**2)
                    
            freq[j_harm]=f0*j_harm
    print ("total time: %s" % (time.time() - start)) 

#elif measType == 2:

else:
    print("measType is not defined")        