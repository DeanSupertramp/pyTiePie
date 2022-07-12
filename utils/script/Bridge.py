#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 10:37:20 2022

@author: alecce
"""

from init import *
import numpy as np
import matplotlib.pyplot as plt

def W_Bridge():
    #Cair = 50e-12
    Cair = C_value
    for i in range(nstep):
        for j in range(nstep):
            B_num[i,j] = 1/(w*(C_value[i] + dC_value[i,j]))
            B_den[i,j] = np.sqrt( R**2 + pow(B_num[i,j],2) )
            A_num[i] = 1/(w*Cair[i])
            # A_num = 1/(w*Cair)
            A_den[i,j] = np.sqrt( R**2 + pow(A_num[i],2) )
            # A_den[i,j] = np.sqrt( R**2 + pow(A_num,2) )
            Vab1_abs[i,j] = ( (B_num[i,j]/B_den[i,j]) - (A_num[i]/A_den[i,j]) ) * Vin # Volt
            # Vab1_abs[i,j] = ( (B_num[i,j]/B_den[i,j]) - (A_num/A_den[i,j]) ) * Vin # Volt
            
    plt.figure()
    plt.title("Wheatstone Bridge Voltage Output")
    plt.ylabel('Cap Value [pF]')
    plt.xlabel('dC')
    plt.imshow(Vab1_abs, origin='upper',
               extent=[1/dCstep, 1/(dCstep*nstep), nstep, 1],
               aspect='auto')
    lbl = plt.colorbar()
    lbl.set_label('[V]', rotation=270, labelpad=15)
    return Vab1_abs
    
def get_dC(Vab, Cair):
    Cair = C_value[0]
    for i in range(nstep):
        for j in range(nstep):
            a[i,j] = R * Vab[i,j]/Vin
            b = ( R / (w*Cair) ) / (np.sqrt(R**2 + 1/(w*Cair)**2) )
            c[i,j] = 1 - ( Vab[i,j]/Vin )
            d = ( 1 / (w*Cair) ) / (np.sqrt((R**2) + 1/(w*Cair)**2) )
            #e[i] = 1/(w*C_value[i])
            e[i] = -((w**2)*C_value[i])
            #dC_Bridge_num[i,j] = np.subtract(a[i,j],  b)
            dC_Bridge_num[i,j] = a[i,j] -  b
            dC_Bridge_den[i,j] = c[i,j] + d
            dC_Bridge[i,j] = 1 / ( e[i] *  dC_Bridge_num[i,j] /  dC_Bridge_den[i,j] ) 
    plt.figure()
    plt.title("Wheatstone Bridge Voltage Output")
    plt.ylabel('Cap Value [pF]')
    plt.xlabel('dC')
    plt.imshow(dC_Bridge, origin='upper',
               extent=[1/dCstep, 1/(dCstep*nstep), nstep, 1],
               aspect='auto')
    lbl = plt.colorbar()
    lbl.set_label('[Farad]', rotation=270, labelpad=15)
    return dC_Bridge
    
def signal_out_bridge():
    Vout =    abs(V2_mc[0] - V1_mc[0,0]) * np.sin(w*t[:period+1] + np.angle(V2_mc[0] - V1_mc[0,0]))
    # NOISE
    noise = np.random.uniform(-.002, .002, Vout.shape)
    Vout_noised = Vout + noise
    # ADC
    # ----- Vout -----
    # Encode Vout
    Vout_noised_quant_rise_ind = np.floor(Vout_noised/q)
    Vout_noised_quant_tread_ind = np.round(Vout_noised/q)
    # Decode Vout
    Vout_noised_riseADC = Vout_noised_quant_rise_ind * q + q/2
    Vout_noised_treadADC = Vout_noised_quant_tread_ind * q
    
    # Stimo il fasore Vout
    alpha_Vout = np.sum(Vout) * np.cos(w*t[:period+1] + np.angle(Vout)) \
        / np.sum( (np.cos(w*t[:period+1] + np.angle(Vout)))**2 )
    
    beta_Vout = - np.sum(Vout) * np.sin(w*t[:period+1] + np.angle(Vout)) \
        / np.sum( (np.sin(w*t[:period+1] + np.angle(Vout)))**2 )
        
    Vout_ph = alpha_Vout + 1j*beta_Vout
    
    # Stimo il fasore Vout + noise + quantization
    alpha_Vout_nq = np.sum(Vout_noised_riseADC) * np.cos(w*t[:period+1] + np.angle(Vout_noised_riseADC)) \
        / np.sum( (np.cos(w*t[:period+1] + np.angle(Vout_noised_riseADC)))**2 )
    
    beta_Vout_nq = - np.sum(Vout_noised_riseADC) * np.sin(w*t[:period+1] + np.angle(Vout_noised_riseADC)) \
        / np.sum( (np.sin(w*t[:period+1] + np.angle(Vout_noised_riseADC)))**2 )
        
    Vout_ph_nq = alpha_Vout_nq + 1j*beta_Vout_nq
    
    plt.figure()
    plt.title("Bridge Vout")
    plt.ylabel('Vout [V]')
    plt.xlabel('Time [s]')
    #plt.plot(t[:period+1], abs(Vout_ph_nq), label='Vout_ph + noise + quantization')
    plt.plot(t[:period+1], abs(Vout_ph), label='Vout_ph')        
    #plt.plot(t[:period+1], abs(Vout), label='Vout') 
    plt.legend(loc = 1)