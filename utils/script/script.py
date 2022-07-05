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
from mpl_toolkits.mplot3d import Axes3D


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


def quantization():             
# https://en.wikipedia.org/wiki/Quantization_(signal_processing)
# https://github.com/GuitarsAI/ADSP_Tutorials/blob/master/ADSP_01_Quantization.ipynb    
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

    # NOISE
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




def surface_plot (matrix, **kwargs):
    # x is cols, y is rows
    #(x, y) = np.meshgrid(np.arange(matrix.shape[0]), np.arange(matrix.shape[1]))
    (x, y) = np.meshgrid(C_value, 1/dC_value[0])
    fig_s = plt.figure()
    ax = fig_s.add_subplot(111, projection='3d')
    fig_s.suptitle('Absolute voltage differences by varying the frequency')
    for s in range(3):
        surf = ax.plot_surface(x, y, matrix[:,:,s], **kwargs)
        #surf = ax.plot_surface(x, y, abs(diff_mc_w_out)[:,:,s])

    return (fig_s, ax, surf)            





# import numpy as np
# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D

# def surface_plot (matrix, **kwargs):
#     # acquire the cartesian coordinate matrices from the matrix
#     # x is cols, y is rows
#     (x, y) = np.meshgrid(np.arange(matrix.shape[0]), np.arange(matrix.shape[1]))
#     fig = plt.figure()
#     ax = fig.add_subplot(111, projection='3d')
#     surf = ax.plot_surface(x, y, matrix[:,:,0], **kwargs)
#     return (fig, ax, surf)






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
     
        
    
    # Vin_fasore = Vin * np.exp(1j * np.angle(sinewave))
    
    # for i in range(nstep):
    #     for j in range(nstep):
    #         V1_num_mc[i,j] = w * R * (C_value[i] + dC_value[i,j])
    #         V1_den_mc[i,j] = - 1j + w * R * (C_value[i]+dC_value[i,j])
    #         V1_mc[i,j] = Vin_fasore[0] * V1_num_mc[i,j] / V1_den_mc[i,j]
    #         V2_num_mc[i] = w * R * C_value[i]
    #         V2_den_mc[i] = - 1j + w * R * C_value[i]
    #         V2_mc[i] = Vin_fasore[0] * V2_num_mc[i] /V2_den_mc[i]
    #         diff_mc[i,j] = (V1_mc[i,j]-V2_mc[i])
    
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
               extent=[1/dCstep, 1/(dCstep*nstep), nstep, 1],
               aspect='auto')
    plt.colorbar()
    
    plt.figure()
    plt.title("Theorical Voltage Difference Map Spice")
    plt.ylabel('Cap Value [pF]')
    plt.xlabel('dC')
    plt.imshow(matr, origin='upper',
               extent=[1/dCstep, 1/(dCstep*nstep), nstep, 1],
               aspect='auto')
    plt.colorbar()
    
    plt.figure()
    plt.title("Spice vs. Simulated Voltage Error")
    plt.ylabel('Cap Value [pF]')
    plt.xlabel('dC')
    plt.imshow(error, #origin='upper',
               extent=[1/dCstep, 1/(dCstep*nstep), nstep, 1],
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
        
    diff_mc_out, diff_mc_w_out = voltageDifference_fasore()

    (fig_s, ax, surf) = surface_plot(abs(diff_mc_w_out), cmap=plt.cm.coolwarm)
    fig_s.colorbar(surf, pad = 0.15) # use pad for separate to plot
    ax.set_xlabel('C [pF]')
    ax.set_ylabel('dC')
    ax.set_zlabel('Voltage Difference [V]')
    plt.show()
    
        
    Vab = W_Bridge()
    get_dC(Vab, C_value[0])
