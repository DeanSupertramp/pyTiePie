import numpy as np
from matplotlib import pyplot as plt

nstep = 10
dCstep = 10

Vin = 10;
f = 55000.0
w = 2*np.pi*f
C = 1e-12
dC = C/dCstep
R = 1/(w*C)


C_value = np.zeros(nstep);
dC_value = np.zeros([nstep,dCstep]);

V1_num_m = np.zeros([nstep,dCstep]);
V2_num_m = np.zeros(nstep);

V1_den_m = np.zeros([nstep,dCstep]);
V2_den_m = np.zeros(nstep);

V1_m = np.zeros([nstep,dCstep]);
V2_m = np.zeros([nstep,dCstep]);

diff_m = np.zeros([nstep,dCstep]);
ii = np.arange(nstep);

num = complex(0,w*R*C)
den = complex(1, w*R*C)
FdT = num/den


def ciclo():
    for i in range(1,nstep+1):
        for j in range(1,dCstep+1):
            C_value[i-1]=C*i;                           # da 1pF a 10pF
            dC_value[i-1,j-1] = C_value[i-1]/(j*dCstep)    # da C/10 a C/100

def voltageDifference():
    V1_num = w * R * (C + dC);
    V1_den = np.sqrt(1 + pow(w,2) * pow(R,2) * pow(C+dC,2));
    V1 = Vin * V1_num / V1_den;

    V2_num = w * R * C;
    V2_den = np.sqrt(1 + pow(w,2) * pow(R,2) * pow(C,2));
    V2 = Vin * V2_num /V2_den;
    diff = (V1-V2)*1000;    # mVs
    print("V1 = " + str(V1) + " V")
    print("V2 = " + str(V2) + " V")
    print("V1 - V2 = " + str(diff) + " mV")
    out = {'V1_num':V1_num, 'V1_den':V1_den, 'V1':V1, 'V2_num':V2_num, 'V2_den':V2_den, 'V2':V2, 'diff':diff}
    return out


def voltageDifference_CICLO():
    for i in range(nstep):
        for j in range(int(dCstep)):

            V1_num_m[i,j] = w * R * (C_value[i] + dC_value[i,j]);
            V1_den_m[i,j] = np.sqrt(1 + pow(w,2) * pow(R,2) * pow(C_value[i]+dC_value[i,j],2));
            V1_m[i,j] = Vin * V1_num_m[i,j] / V1_den_m[i,j];
            V2_num_m[i] = w * R * C_value[i];
            V2_den_m[i] = np.sqrt(1 + pow(w,2) * pow(R,2) * pow(C_value[i],2));
            V2_m[i,j] = Vin * V2_num_m[i] /V2_den_m[i];
            diff_m[i,j] = (V1_m[i,j]-V2_m[i,j])*1000;    # mVs
            
            
def plotGraph():
    plt.figure()
    fig, axs = plt.subplots(2)
    fig.suptitle('Voltage measurements ')
    axs[0].plot(ii[1:], V1_m[1:,dCstep-1])
    axs[1].plot(ii[1:], V2_m[1:,dCstep-1])
    axs[0].set_title('V1')
    axs[1].set_title('V2')
    axs[1].set_xlabel('n steps')
    axs[0].set_ylabel('voltage (V)')
    axs[1].set_ylabel('voltage (V)')

    plt.figure()
    plt.title("Theorical Voltage Difference")
    plt.ylabel('Voltage Difference [mV]')
    plt.xlabel('n steps')
    plt.plot(ii[:], diff_m[:,:])
    #plt.legend(loc='upper right')
    
    plt.figure()
    plt.title("Theorical Voltage Difference Map")
    plt.ylabel('Cap Value [pF]')
    plt.xlabel('dC')
    plt.imshow(diff_m, origin='upper',
               extent=[dCstep, dCstep*nstep, nstep, 1],
               aspect='auto')
    plt.colorbar()




if __name__ == '__main__':
    o = voltageDifference()
    ciclo()
    voltageDifference_CICLO()
    plotGraph()

