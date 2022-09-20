import numpy as np
from matplotlib import pyplot as plt
import logSpice2Matrix as S2M
from init import * # analysis:ignore
from quantization import quantization
from RC_series import voltageDifference, voltageDifference_CICLO, voltageDifference_fasore, signal_out
from Bridge import W_Bridge, get_dC, signal_out_bridge
    
# create arrays for C and dC value    
def ciclo():
    for i in range(1,nstep+1):
        for j in range(1,nstep+1):
            C_value[i-1]=C*i;                           # da 1pF a 10pF
            dC_value[i-1,j-1] = C_value[i-1]/(j*dCstep)    # da C/100 a C/1000

def surface_plot (matrix, **kwargs):
    # x cols, y rows
    #(x, y) = np.meshgrid(np.arange(matrix.shape[0]), np.arange(matrix.shape[1]))
    (x, y) = np.meshgrid(C_value, dC_value[0])
    fig_s = plt.figure()
    ax = fig_s.add_subplot(111, projection='3d')
    fig_s.suptitle('Absolute voltage differences by varying the frequency')
    for s in range(0, len(w_vec), 5):
        surf = ax.plot_surface(x, y, matrix[:,:,s], **kwargs)
    return (fig_s, ax, surf)      

    plt.figure()
    plt.title("Absolute voltage differences at specific frequency")
    plt.ylabel('Cap Value [pF]')
    plt.xlabel('dC')    
    plt.imshow(abs(diff_mc_w_out)[:,:,0])
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
    ax.set_ylabel('dC')
    ax.set_xlabel('C [pF]')
    ax.set_zlabel('Voltage Difference [V]')
    plt.show()
    
    signal_out()
    # Vab = W_Bridge()
    # get_dC(Vab, C_value[0])
    signal_out_bridge()