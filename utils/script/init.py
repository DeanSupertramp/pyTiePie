#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  8 17:54:12 2022

@author: alecce
"""
import numpy as np

# ADC Parameter
Fs = 100e6  # Sampling rate 100 MSa/s
Ts = 1/Fs   # Sampling time
N = 14 # n bit ADC

# Input Signal
f_vec = np.arange(10000, 110000, 5000)
f = 55000.0
w = 2*np.pi*f
w_vec = np.arange(2*np.pi*f_vec[0], 2*np.pi*f_vec[f_vec.size-1], 2*np.pi*5000)
Vin = 10
n_period = 1
period = np.round((1/f)*n_period*Fs).astype(int)
t = np.arange(Fs+1)*Ts # Time vector
sinewave = Vin*np.sin(2*np.pi*f*t)  # Original signal

q = (Vin-(-Vin))/(2**N) # quantization step

nstep = 10
dCstep = 100
init_dCstep = 100
fstep = len(f_vec)
wstep = len(w_vec)

# Circuit Parameter
C = 1e-12
dC = C/dCstep
R = 1/(w*C)

# Init value
C_value = np.zeros(nstep)
dC_value = np.zeros([nstep,nstep])
V1_num_m = np.zeros([nstep,nstep])
V2_num_m = np.zeros(nstep);
V1_den_m = np.zeros([nstep,nstep])
V2_den_m = np.zeros(nstep)
V1_m = np.zeros([nstep,nstep])
V2_m = np.zeros(nstep)
diff_m = np.zeros([nstep,nstep])
ii = np.arange(nstep);

# Complex
V1_num_mc = np.zeros([nstep,nstep], dtype=complex)
V2_num_mc = np.zeros(nstep, dtype=complex)
V1_den_mc = np.zeros([nstep,nstep], dtype=complex)
V2_den_mc = np.zeros(nstep, dtype=complex)
V1_mc = np.zeros([nstep,nstep], dtype=complex)
V2_mc = np.zeros(nstep, dtype=complex)
diff_mc = np.zeros([nstep,nstep], dtype=complex)

# 3-D
V1_num_mc_w = np.zeros([nstep,nstep, wstep], dtype=complex)
V2_num_mc_w = np.zeros([nstep, wstep], dtype=complex)
V1_den_mc_w = np.zeros([nstep,nstep, wstep], dtype=complex)
V2_den_mc_w = np.zeros([nstep, wstep], dtype=complex)
V1_mc_w = np.zeros([nstep,nstep, wstep], dtype=complex)
V2_mc_w = np.zeros([nstep, wstep], dtype=complex)
diff_mc_w = np.zeros([nstep,nstep, wstep], dtype=complex)

# Spice matrix
matr = np.zeros([nstep,nstep])

# Bridge parameter
B_num = np.zeros([nstep,nstep])
B_den = np.zeros([nstep,nstep])
A_num = np.zeros(nstep)
A_den = np.zeros([nstep,nstep])
Vab1_abs = np.zeros([nstep,nstep])

a = np.zeros([nstep,nstep])
#b = np.zeros(nstep)
c = np.zeros([nstep,nstep])
#d = np.zeros(nstep)
e = np.zeros(nstep)
dC_Bridge = np.zeros([nstep,nstep])
dC_Bridge_num = np.zeros([nstep,nstep])
dC_Bridge_den = np.zeros([nstep,nstep])