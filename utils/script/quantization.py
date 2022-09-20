#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 10:17:51 2022

@author: alecce
"""
from init import *
import numpy as np
from matplotlib import pyplot as plt

def quantization():             
# https://en.wikipedia.org/wiki/Quantization_(signal_processing)
# https://github.com/GuitarsAI/ADSP_Tutorials/blob/master/ADSP_01_Quantization.ipynb    
    # Encode
    sinewave_quant_rise_ind = np.floor(sinewave/q)
    sinewave_quant_tread_ind = np.round(sinewave/q)
    # Decode
    sinewave_quant_rise_rec = sinewave_quant_rise_ind * q + q/2
    sinewave_quant_tread_rec = sinewave_quant_tread_ind * q
    # Shape for plotting
    t_q = np.delete(np.repeat(t[:period+1],2),-1)
    sinewave_quant_rise_rec_plot = np.delete(np.repeat(sinewave_quant_rise_rec[:period+1],2),0)
    sinewave_quant_tread_rec_plot = np.delete(np.repeat(sinewave_quant_tread_rec[:period+1],2),0)
    # Quantization Error
    quant_error_tread = sinewave_quant_tread_rec - sinewave
    quant_error_rise = sinewave_quant_rise_rec - sinewave

    # NOISE
    noise = np.random.uniform(-.2, .2, sinewave.shape)
    sinewave_noised = sinewave + noise
    # Encode
    sinewave_noised_quant_rise_ind = np.floor(sinewave_noised/q)
    sinewave_noised_quant_tread_ind = np.round(sinewave_noised/q)
    # Decode
    sinewave_noised_quant_rise_rec = sinewave_noised_quant_rise_ind * q + q/2
    sinewave_noised_quant_tread_rec = sinewave_noised_quant_tread_ind * q
    
    mse_sine_noise = np.mean((sinewave - sinewave_noised)**2)     # Mean Square Error
    mse_sine_quant = np.mean((sinewave - sinewave_quant_rise_rec)**2)
    mse_sine_noise_quant = np.mean((sinewave - sinewave_noised_quant_rise_rec)**2)
    
    print("mse_sine_noise : ", mse_sine_noise)
    print("mse_sine_quant : ", mse_sine_quant)
    print("mse_sine_noise_quant : ", mse_sine_noise_quant)
        
    # Plot
    plt.figure(figsize=(12,8))
    plt.subplot(2,1,1)
    # fig, ax = plt.subplots(1, figsize=(10,6))
    plt.plot(t[:period+1], sinewave[:period+1], label='Original Signal')
    #plt.plot(t_q, sinewave_quant_rise_rec_plot, label='Quantized Signal (Mid-Rise)')
    fig = plt.plot(t_q, sinewave_quant_tread_rec_plot, label='Quantized Signal (Mid-Tread)')
    plt.title('Original and Quantized Signals', fontsize = 18)
    plt.xlabel('Time [s]')
    plt.ylabel('Amplitude')
    #plt.yticks(np.arange((-1-q)*Vin, (1+q)*Vin, q))
       
    plt.subplot(2,1,2)
    plt.plot(t[:period+1], quant_error_tread[:period+1], label='Quantization Error')
    plt.grid()
    plt.title('Quantization Error (Mid-Tread)', fontsize = 18)
    plt.xlabel('Time [s]')
    plt.ylabel('Amplitude')
    plt.subplots_adjust(hspace = 0.5)

    plt.figure(figsize=(12,8))
    plt.subplot(2,1,1)
    plt.plot(t[1350:1370], sinewave[1350:1370], label='Original Signal')
    #plt.plot(t_q, sinewave_quant_rise_rec_plot, label='Quantized Signal (Mid-Rise)')
    fig = plt.plot(t_q[2*1350:2*1370], sinewave_quant_tread_rec_plot[2*1350:2*1370], label='Quantized Signal (Mid-Tread)')
    plt.title('Zoom on Signal', fontsize = 18)
    plt.xlabel('Time [s]')
    plt.ylabel('Amplitude [V]')
    
    plt.subplot(2,1,2)
    plt.plot(t[1350:1370], quant_error_tread[1350:1370], label='Quantization Error')
    plt.grid()
    plt.title('Quantization Error (Mid-Tread)', fontsize = 18)
    plt.xlabel('Time [s]')
    plt.ylabel('Amplitude [V]')
    plt.subplots_adjust(hspace = 0.5)
    
    plt.figure()
    plt.title("Distribution")
    plt.ylabel('Occurrency')
    plt.xlabel('Error value')
    # rif: https://stackoverflow.com/questions/33203645/how-to-plot-a-histogram-using-matplotlib-in-python-with-a-list-of-data
    # rif: https://en.wikipedia.org/wiki/Freedman%E2%80%93Diaconis_rule
    q25, q75 = np.percentile(quant_error_rise, [25, 75])
    bin_width = 2 * (q75 - q25) * len(quant_error_rise) ** (-1/3)
    bins = round((quant_error_rise.max() - quant_error_rise.min()) / bin_width)
    print("Freedman–Diaconis number of bins:", bins)
    plt.hist(quant_error_rise, bins=bins)
    plt.show()

    # NOISE PLOT
    plt.figure(figsize=(12,8))
    #plt.subplot(2,1,1)
    # fig, ax = plt.subplots(1, figsize=(10,6))
    plt.plot(t[:period+1], sinewave_noised[:period+1], label='Original Signal with noise')
    #plt.plot(t_q, sinewave_quant_rise_rec_plot, label='Quantized Signal (Mid-Rise)')
    plt.plot(t_q, sinewave_quant_tread_rec_plot, label='Quantized Signal (Mid-Tread) with noise')
    plt.title('Original and Quantized Signals with noise', fontsize = 18)
    plt.xlabel('Time [s]')
    plt.ylabel('Amplitude')
    plt.legend()