import numpy as np
from matplotlib import pyplot as plt

from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes,mark_inset

# import plotly.tools as tls

# import plotly.io as pio
# pio.renderers.default='browser'

# from plotly.offline import download_plotlyjs, init_notebook_mode,  plot
# from plotly.graph_objs import *
# init_notebook_mode()

import logSpice2Matrix as S2M


# ADC Parameter
Fs = 100e6  # Sampling rate 100 MSa/s
Ts = 1/Fs   # Sampling time

# Input Signal
f = 55000.0
w = 2*np.pi*f
Vin = 10
n_period = 1
period = np.round((1/f)*n_period*Fs).astype(int)
t = np.arange(Fs+1)*Ts # Time vector
sinewave = Vin*np.sin(2*np.pi*f*t)  # Original signal

nstep = 10
dCstep = 100
init_dCstep = 100

# Circuit Parameter
C = 1e-12
dC = C/dCstep
R = 1/(w*C)

C_value = np.zeros(nstep);

dC_value = np.zeros([nstep,nstep]);

V1_num_m = np.zeros([nstep,nstep]);
V2_num_m = np.zeros(nstep);

V1_den_m = np.zeros([nstep,nstep]);
V2_den_m = np.zeros(nstep);

V1_m = np.zeros([nstep,nstep]);
V2_m = np.zeros(nstep);

diff_m = np.zeros([nstep,nstep]);
ii = np.arange(nstep);

matr = np.zeros([10,10])

def quantization():             # https://en.wikipedia.org/wiki/Quantization_(signal_processing) // https://github.com/GuitarsAI/ADSP_Tutorials/blob/master/ADSP_01_Quantization.ipynb
    N = 14 # n bit ADC
    q = (Vin-(-Vin))/(2**N)
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

    
    
def ciclo():
    for i in range(1,nstep+1):
        for j in range(1,nstep+1):
            C_value[i-1]=C*i;                           # da 1pF a 10pF
            dC_value[i-1,j-1] = C_value[i-1]/(j*dCstep)    # da C/100 a C/1000

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
            
            
def plotGraph():
    plt.figure()
    fig, axs = plt.subplots(2)
    fig.suptitle('Voltage measurements')
    axs[0].plot(ii[1:], V1_m[1:,nstep-1])
    axs[1].plot(ii[1:], V2_m[1:])
    axs[0].set_title('V1')
    axs[1].set_title('V2')
    axs[1].set_xlabel('n steps')
    axs[0].set_ylabel('voltage (V)')
    axs[1].set_ylabel('voltage (V)')
    plt.subplots_adjust(hspace = 0.5)

    plt.figure()
    plt.title("Theorical Voltage Difference")
    plt.ylabel('Voltage Difference [V]')
    plt.xlabel('n steps')
    plt.plot(ii[:], diff_m[:,:])
    
    plt.figure()
    plt.title("Theorical Voltage Difference Map")
    plt.ylabel('Cap Value [pF]')
    plt.xlabel('dC')
    plt.imshow(diff_m, origin='upper',
               extent=[dCstep, dCstep*nstep, nstep, 1],
               aspect='auto')
    plt.colorbar()
    
    plt.figure()
    plt.title("Theorical Voltage Difference Map Spice")
    plt.ylabel('Cap Value [pF]')
    plt.xlabel('dC')
    plt.imshow(matr, origin='upper',
               extent=[dCstep, dCstep*nstep, nstep, 1],
               aspect='auto')
    plt.colorbar()
    
    plt.figure()
    plt.title("Spice vs. Simulated Voltage Error")
    plt.ylabel('Cap Value [pF]')
    plt.xlabel('dC')
    plt.imshow(error, #origin='upper',
               extent=[dCstep, dCstep*nstep, nstep, 1],
               aspect='auto')
    plt.colorbar()
    

if __name__ == '__main__':
    o = voltageDifference()
    ciclo()
    voltageDifference_CICLO()
    
    matr = S2M.getMatrix().astype(np.float) # valori simulati su Spice
    
    error = (diff_m - matr)
    
    mse = np.mean((diff_m - matr)**2)     # Mean Square Error
    print("Mean Square Error Spice vs. Theorical Simulation: " + str(mse))
    
    quantization()

    plotGraph()
