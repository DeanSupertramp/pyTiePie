# -*- coding: utf-8 -*-
"""
Created on Sun Jul  3 15:45:59 2022

@author: andry
"""

import numpy as np
import scipy.io
import time

file_path = "C:/Users/andry/Desktop/Alecce/repo/pyTiePie/data/config_Float/general/aria.mat"

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

s_harml = np.zeros([Nharm,len_time_lockin])
lock_in = np.zeros([Nharm,len_time_lockin], dtype = 'complex_')
freq = np.zeros(Nharm)


k = np.zeros(Nharm, dtype = 'complex_')
for j_harm in range(Nharm):
    k[j_harm] = np.exp(-2j*np.pi*j_harm)

start = time.time()
           
for j_harm in range(Nharm):
    for l in range(len_time_lockin):
        s_harml[j_harm, l] = np.cos(2*np.pi*f0*j_harm*time_lockin[l]+np.pi*(j_harm*(j_harm))/Nharm)
        # lock_in[j_harm, l] = np.exp(-1j*np.pi*(j_harm*(j_harm-1))/Nharm) \
        #     * np.exp(-1j*2*np.pi*f0*j_harm*time_lockin[l]) \
        #         / np.sum(np.square(s_harml[j_harm])) \
        #             / np.sum(s_harml[j_harm]**2)
        
        lock_in[j_harm, l] = k[j_harm] * np.exp( ((j_harm-1)/Nharm) + f0*time_lockin[l]) / np.sum(np.square(s_harml[j_harm]))
                
        freq[j_harm]=f0*j_harm
print ("total time: %s" % (time.time() - start)) 