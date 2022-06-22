import numpy as np
from matplotlib import pyplot as plt

#from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes,mark_inset

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

C_value = np.zeros(nstep)

dC_value = np.zeros([nstep,nstep])

V1_num_m = np.zeros([nstep,nstep])
V2_num_m = np.zeros(nstep);

V1_den_m = np.zeros([nstep,nstep])
V2_den_m = np.zeros(nstep)

V1_m = np.zeros([nstep,nstep])
V2_m = np.zeros(nstep)

# complex

V1_num_mc = np.zeros([nstep,nstep], dtype=complex)
V2_num_mc = np.zeros(nstep, dtype=complex)

V1_den_mc = np.zeros([nstep,nstep], dtype=complex)
V2_den_mc = np.zeros(nstep, dtype=complex)

V1_mc = np.zeros([nstep,nstep], dtype=complex)
V2_mc = np.zeros(nstep, dtype=complex)

diff_mc = np.zeros([nstep,nstep], dtype=complex)




diff_m = np.zeros([nstep,nstep])
ii = np.arange(nstep);

matr = np.zeros([10,10])

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

    # NOISE
    noise = np.random.uniform(-.2, .2, sinewave.shape)
    sinewave_noised = sinewave + noise
    
    plt.figure(figsize=(12,8))
    #plt.subplot(2,1,1)
    # fig, ax = plt.subplots(1, figsize=(10,6))
    plt.plot(t[:period+1], sinewave_noised[:period+1], label='Original Signal with noise')
    #plt.plot(t_q, sinewave_quant_rise_rec_plot, label='Quantized Signal (Mid-Rise)')
    fig = plt.plot(t_q, sinewave_quant_tread_rec_plot, label='Quantized Signal (Mid-Tread) with noise')
    plt.title('Original and Quantized Signals with noise', fontsize = 18)
    plt.xlabel('Time [s]')
    plt.ylabel('Amplitude')
    

    
    
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
            
            
def voltageDifference_fasore():
    for i in range(nstep):
        for j in range(nstep):
            V1_num_mc[i,j] = w * R * (C_value[i] + dC_value[i,j]);
            V1_den_mc[i,j] = - 1j + w * R * (C_value[i]+dC_value[i,j])
            V1_mc[i,j] = Vin * V1_num_mc[i,j] / V1_den_mc[i,j];
            V2_num_mc[i] = w * R * C_value[i];
            V2_den_mc[i] = - 1j + w * R * C_value[i]
            V2_mc[i] = Vin * V2_num_mc[i] /V2_den_mc[i];
            diff_mc[i,j] = (V1_mc[i,j]-V2_mc[i]);
    
    plt.imshow(abs(diff_mc), origin='upper',
               extent=[dCstep, dCstep*nstep, nstep, 1],
               aspect='auto')
    lbl = plt.colorbar()
    lbl.set_label('[v]', rotation=270, labelpad=15)
    
    plt.imshow(np.angle(diff_mc), origin='upper',
           extent=[dCstep, dCstep*nstep, nstep, 1],
           aspect='auto')
    lbl = plt.colorbar()
    lbl.set_label('[v]', rotation=270, labelpad=15)
            
            
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
               extent=[dCstep, dCstep*nstep, nstep, 1],
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
               extent=[dCstep, dCstep*nstep, nstep, 1],
               aspect='auto')
    lbl = plt.colorbar()
    lbl.set_label('[Farad]', rotation=270, labelpad=15)

    return dC_Bridge
    
    

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
    
    Vab = W_Bridge()
    get_dC(Vab, C_value[0])
