import numpy as np
from matplotlib import pyplot as plt

nstep = 10
dCstep = 50

Vin = 10;
R = 2893726.238
f = 55000.0
w = 2*np.pi*f
C = 1e-12
dC = C/dCstep

C_value = np.zeros(nstep);
dC_value = np.zeros([nstep,dCstep]);

V1_num_m = np.zeros([nstep,dCstep]);
V2_num_m = np.zeros([nstep,dCstep]);

V1_den_m = np.zeros([nstep,dCstep]);
V2_den_m = np.zeros([nstep,dCstep]);

V1_m = np.zeros([nstep,dCstep]);
V2_m = np.zeros([nstep,dCstep]);

diff_m = np.zeros([nstep,dCstep]);
ii = np.arange(nstep);

matrice = np.zeros([nstep,dCstep]);


def ciclo():
    for i in range(1,nstep):
        for j in range(dCstep):
            C_value[i]=C*i;
            dC_value[i,j] = C_value[i]/(j+1)


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
        for j in range(dCstep):

            V1_num_m[i,j] = w * R * (C_value[i] + dC_value[i,j]);
            V1_den_m[i,j] = np.sqrt(1 + pow(w,2) * pow(R,2) * pow(C_value[i]+dC_value[i,j],2));
            V1_m[i,j] = Vin * V1_num_m[i,j] / V1_den_m[i,j];
            V2_num_m[i,j] = w * R * C_value[i];
            V2_den_m[i,j] = np.sqrt(1 + pow(w,2) * pow(R,2) * pow(C_value[i],2));
            V2_m[i,j] = Vin * V2_num_m[i,j] /V2_den_m[i,j];
            diff_m[i,j] = (V1_m[i,j]-V2_m[i,j])*1000;    # mVs




if __name__ == '__main__':
    o = voltageDifference()
    ciclo()
    voltageDifference_CICLO()

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
    plt.plot(ii[1:], diff_m[1:,dCstep-1])
    
    plt.figure()
    plt.title("Theorical Voltage Difference Map")
    plt.ylabel('Cap Value [pF]')
    plt.xlabel('n steps')
    plt.imshow(diff_m)
    plt.colorbar()
    plt.show()