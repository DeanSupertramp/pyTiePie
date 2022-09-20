#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 10:23:32 2022

@author: alecce
"""

import numpy as np
import matplotlib.pyplot as plt
from init import *

def voltageDifference():
    V1_num = w * R * (C + dC);
    V1_den = np.sqrt(1 + pow(w,2) * pow(R,2) * pow(C+dC,2));
    V1 = Vin * V1_num / V1_den;
    V2_num = w * R * C;
    V2_den = np.sqrt(1 + pow(w,2) * pow(R,2) * pow(C,2));
    V2 = Vin * V2_num /V2_den;
    diff = (V1-V2);    
    print("V1 = " + str(V1) + " V")
    print("V2 = " + str(V2) + " V")
    print("V1 - V2 = " + str(diff) + " V")
    out = {'V1_num':V1_num, 'V1_den':V1_den, 'V1':V1, 'V2_num':V2_num, 'V2_den':V2_den, 'V2':V2, 'diff':diff}
    return out

def voltageDifference_CICLO():
    for i in range(nstep):
        for j in range(nstep):
            V1_num_m[i,j] = w * R * (C_value[i] + dC_value[i,j]);
            V1_den_m[i,j] = np.sqrt(1 + pow(w,2) * pow(R,2) * pow(C_value[i]+dC_value[i,j],2));
            V1_m[i,j] = Vin * V1_num_m[i,j] / V1_den_m[i,j];
            V2_num_m[i] = w * R * C_value[i];
            V2_den_m[i] = np.sqrt(1 + pow(w,2) * pow(R,2) * pow(C_value[i],2));
            V2_m[i] = Vin * V2_num_m[i] /V2_den_m[i];
            diff_m[i,j] = (V1_m[i,j]-V2_m[i]);

def voltageDifference_fasore():
    for i in range(nstep):
        for j in range(nstep):
            V1_num_mc[i,j] = w * R * (C_value[i] + dC_value[i,j])
            V1_den_mc[i,j] = - 1j + w * R * (C_value[i]+dC_value[i,j])
            V1_mc[i,j] = Vin * V1_num_mc[i,j] / V1_den_mc[i,j]
            V2_num_mc[i] = w * R * C_value[i]
            V2_den_mc[i] = - 1j + w * R * C_value[i]
            V2_mc[i] = Vin * V2_num_mc[i] /V2_den_mc[i]
            diff_mc[i,j] = (V1_mc[i,j]-V2_mc[i])
    for i in range(nstep):
        for j in range(nstep):
            for k in range(len(w_vec)):
                V1_num_mc_w[i, j, k] = w_vec[k] * R * (C_value[i] + dC_value[i,j])
                V1_den_mc_w[i, j, k] = - 1j + w_vec[k] * R * (C_value[i]+dC_value[i,j])
                V1_mc_w[i, j, k] = Vin * V1_num_mc_w[i,j, k] / V1_den_mc_w[i,j, k]
                V2_num_mc_w[i, k] = w_vec[k] * R * C_value[i]
                V2_den_mc_w[i, k] = - 1j + w_vec[k] * R * C_value[i]
                V2_mc_w[i, k] = Vin * V2_num_mc_w[i, k] /V2_den_mc_w[i, k]
                diff_mc_w[i,j, k] = (V1_mc_w[i,j, k]-V2_mc_w[i, k])
    
    # module of the voltage difference
    plt.figure()
    plt.title("Module of the voltage difference - [abs(diff)]")
    plt.ylabel('Cap Value [pF]')
    plt.xlabel('dC')    
    plt.imshow(abs(diff_mc), origin='upper',
               extent=[1/dCstep, 1/(dCstep*nstep), nstep, 1],
               aspect='auto')
    lbl = plt.colorbar()
    lbl.set_label('[v]', rotation=270, labelpad=15)
    
    plt.figure()
    plt.title("Phase Difference")
    plt.ylabel('Cap Value [pF]')
    plt.xlabel('dC') 
    plt.imshow(np.angle(diff_mc), origin='upper',
           extent=[1/dCstep, 1/(dCstep*nstep), nstep, 1],
           aspect='auto')
    lbl = plt.colorbar()
    lbl.set_label('[phase]', rotation=270, labelpad=15)
    
    # Difference of voltage modules    
    plt.figure()
    plt.title("Difference of voltage modules - abs(V1) - abs(V2)")
    plt.ylabel('Cap Value [pF]')
    plt.xlabel('dC')    
    plt.imshow((abs(V1_mc) - abs(V2_mc)), origin='upper',
               extent=[1/dCstep, 1/(dCstep*nstep), nstep, 1],
               aspect='auto')
    lbl = plt.colorbar()
    lbl.set_label('[v]', rotation=270, labelpad=15)
    
    # Voltage Difference vs. freq. with several C
    plt.figure()
    plt.title("Voltage Difference vs. freq. with several C")
    plt.ylabel('Voltage Difference [V]')
    plt.xlabel('freq [Hz]')
    for i in range(len(C_value)):
        plt.plot(f_vec[0:19], abs(diff_mc_w)[i,0,:], label=C_value[i])
    plt.legend()
    
    max_value = max(abs(diff_mc_w)[0,0,:])
    max_index = np.where(abs(diff_mc_w[0,0,:]) == max_value)
    print('Max value is ', max_value, 'at ', f_vec[max_index], 'Hz')
    
    # Voltage Difference vs. freq.
    plt.figure()
    plt.title("Voltage Difference vs. freq. with several dC")
    plt.ylabel('Voltage Difference [V]')
    plt.xlabel('freq [Hz]')
    for i in range(len(dC_value[0])):
        plt.plot(f_vec[0:19], abs(diff_mc_w)[0,i,:], label=dC_value[0][i])
    plt.legend(title = "dC", loc=1, prop={'size': 7})
    
    return diff_mc, diff_mc_w

def signal_out():
    S1_mc= abs(V1_mc[0,0]) * np.cos(w*t[:period+1] + np.angle(V1_mc[0,0]))
    S2_mc= abs(V2_mc[0]) * np.cos(w*t[:period+1] + np.angle(V2_mc[0]))
    # NOISE
    noise = np.random.uniform(-.2, .2, S1_mc.shape)
    S1_noised = S1_mc + noise
    S2_noised = S2_mc + noise
    # ADC
    # ----- S1 -----
    # Encode S1
    S1_noised_quant_rise_ind = np.floor(S1_noised/q)
    S1_noised_quant_tread_ind = np.round(S1_noised/q)
    # Decode S1
    S1_noised_riseADC = S1_noised_quant_rise_ind * q + q/2
    S1_noised_treadADC = S1_noised_quant_tread_ind * q
    # ----- S2 -----
    # Encode S2
    S2_noised_quant_rise_ind = np.floor(S2_noised/q)
    S2_noised_quant_tread_ind = np.round(S2_noised/q)
    # Decode S2
    S2_noised_riseADC = S2_noised_quant_rise_ind * q + q/2
    S2_noised_treadADC = S2_noised_quant_tread_ind * q
    
    # Stimo il fasore S1
    alpha_S1 = np.sum( S1_noised_riseADC * np.cos(w*t[:period+1]) ) \
        / np.sum( (np.cos(w*t[:period+1] ))**2 )  
    
    beta_S1 = - np.sum(S1_noised_riseADC * np.sin(w*t[:period+1] ) ) \
        / np.sum( (np.sin(w*t[:period+1] ))**2 )
        
    S1_ph = alpha_S1 + 1j*beta_S1
    
    # Stimo il fasore S2
    alpha_S2 = np.sum( S2_noised_riseADC * np.cos(w*t[:period+1] ) ) \
        / np.sum( (np.cos(w*t[:period+1] ))**2 )
    
    beta_S2 = - np.sum(S2_noised_riseADC * np.sin(w*t[:period+1] ) ) \
        / np.sum( (np.sin(w*t[:period+1] ))**2 )
        
    S2_ph = alpha_S2 + 1j*beta_S2
    
    # plt.figure()
    # #plt.plot(t[:period+1], abs(S1_ph[:period+1]), label='S1_ph')
    # #plt.plot(t[:period+1], abs(S2_ph[:period+1]), label='S2_ph')
    # plt.plot(t[:period+1], abs(S2_ph[:period+1]) - abs(S1_ph[:period+1]), label='difference')        
    # plt.legend()
    
    print(abs(S2_ph) - abs(S1_ph))
    print(np.angle(S2_ph, deg = True) - np.angle(S1_ph, deg = True))
    
    # Calcolo DS
    DS = S2_mc - S1_mc
    DS_noise = S2_noised - S1_noised
    DS_noise_ADC = S2_noised_riseADC - S1_noised_riseADC
    
    # Stimo il fasore DS
    alpha_DS = np.sum(DS_noise_ADC * np.cos(w*t[:period+1] ) ) \
        / np.sum( (np.cos(w*t[:period+1] ))**2 )
    
    beta_DS = - np.sum(DS_noise_ADC * np.sin(w*t[:period+1] ) ) \
        / np.sum( (np.sin(w*t[:period+1] ))**2 )
        
    DS_ph = alpha_DS + 1j*beta_DS
    print(abs(DS_ph))
    print(np.angle(DS_ph, deg = True))

    # plt.figure()
    # plt.title("RC series Phasors")
    # plt.ylabel('Voltage difference abs [V]')
    # plt.xlabel('Time [s]')
    # plt.plot(t[:period+1], abs(S2_ph[:period+1]) - abs(S1_ph[:period+1]), label='difference of phasors [S2_ph-S1_ph]')
    # plt.plot(t[:period+1], abs(DS_ph[:period+1]), label='phasor difference [DS_ph]')                
    # plt.legend()

    plt.figure()
    plt.title("S1_mc, S2_mc and original signal")
    plt.ylabel('Voltage Difference [V]')
    plt.xlabel('Time [s]')
    plt.plot(t[:period+1], sinewave[:period+1], label='Original Signal')
    plt.plot(t[:period+1], S1_mc, linestyle='dashed', lw=2, label='Signal V1 from RC Circuit')
    plt.plot(t[:period+1], S2_mc, linestyle='dashed', alpha=0.5, lw=2, label='Signal V2 from RC Circuit')
    plt.legend()

    plt.figure()
    plt.subplot(2,1,1)
    plt.title("Voltage difference DS with quantization and noise", fontsize=10, fontweight = 'bold')
    plt.ylabel('Voltage Difference [V]')
    plt.xlabel('Time [s]')
    plt.plot(t[:period+1], DS_noise_ADC[:period+1], label='DS + noise + quantization')
    plt.plot(t[:period+1], DS_noise[:period+1], label='DS + noise')
    plt.plot(t[:period+1], DS[:period+1], linestyle='dashed', label='DS')
    plt.legend()
    plt.subplot(2,1,2)
    plt.title("Voltage difference DS with quantization and noise - Error", fontsize=10, pad=17, fontweight = 'bold')
    plt.ylabel('Voltage Difference error [V]')
    plt.xlabel('Time [s]')
    plt.plot(t[:period+1], DS_noise_ADC[:period+1] - DS[:period+1], label='DS + noise + quantization (error)')
    plt.plot(t[:period+1], DS_noise[:period+1] - DS[:period+1], label='DS + noise (error)')
    plt.subplots_adjust(hspace = 0.8)
    plt.legend()