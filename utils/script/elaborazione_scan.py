# -*- coding: utf-8 -*-
"""
Created on Tue Sep 27 09:02:12 2022

@author: Marco
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Sep 27 09:02:12 2022

@author: Marco
"""

import numpy as np
from matplotlib import pyplot as plt
from scipy.signal import butter
from scipy import signal
from scipy.optimize import curve_fit
import sys
import os
import pandas as pd
import json
# import AST_Z_meter_v2 as AST_Z_meter

def modelX(x, p1, p2):
    # return p2+1/(2*np.pi*x*p1)
    return p1+(1/x)*1/(2*np.pi*p2)

def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='valid')
    return y_smooth

def Z_meter_excitation(f0,Nharm,Tsignal,fS,amp):
    Ns=int(Tsignal*fS/1000) # n° campioni
    Ns_cycle=int(fS/f0)
    Ncycles=int(Ns/Ns_cycle)
    # time_axis
    time_s=np.arange(0,Ns)/fS;
    time_lockin=np.arange(0,(Ns_cycle*(Ncycles-1)))/fS;
    s=np.zeros([int(Ns)+4]);
    s_harm=np.empty((Nharm,Ns),'float')
    s_harml=np.empty((Nharm,Ns_cycle*(Ncycles-1)),'float')
    lock_in=np.ones((Nharm,Ns_cycle*(Ncycles-1)),dtype=np.complex_)
    
    freq=np.empty((Nharm,1),'float')
    ampl=np.ones((Nharm,1),dtype=np.complex_)
    
    for j_harm in range(int(Nharm)):
        s_harm[j_harm,:]=(np.cos(2*np.pi*f0*(j_harm+1)*time_s+np.pi*((j_harm+1)*(j_harm+1))/Nharm));
        s_harml[j_harm,:]=(np.cos(2*np.pi*f0*(j_harm+1)*time_lockin+np.pi*((j_harm+1)*(j_harm+1))/Nharm));
        lock_in[j_harm,:]=np.exp(-1j*np.pi*((j_harm+1)*(j_harm+1))/Nharm)*np.exp(-1j*2*np.pi*f0*(j_harm+1)*time_lockin)/np.sum(s_harml[j_harm,:]**2);
        freq[j_harm]=f0*(j_harm+1);
    
            
    s[2:-2]=np.sum(s_harm,0);
    #s=s-s.mean()
    a=1/max(s.max(),-s.min())
    s=s*a*amp
    for j_harm in range(int(Nharm)):
        ampl[j_harm,:]=np.sum(s[0:Ns_cycle*(Ncycles-1)]*lock_in[j_harm,:])
        
    params={'Ns':Ns, 'Ns_cycle':Ns_cycle,'Ncycles':Ncycles,'freq':freq,'time':time_s}
    
    return s, lock_in, params, s_harm, s_harml,

def Cap_meter_processing(CH1,CH2,params,lock_in):
    Ns=params['Ns']
    Ns_cycle=params['Ns_cycle']
    Ncycles=params['Ncycles']
    freq=params['freq']
    time_s=params['time']
    VR=(CH1[2+Ns_cycle:2+Ns_cycle*(Ncycles)])
    Vin=(CH2[2+Ns_cycle:2+Ns_cycle*(Ncycles)])
    R=1.98e3
    
    # phasor_coil=np.dot(lock_in,Vcoil);
    phasorVR=np.dot(lock_in,VR);
    phasorVin=np.dot(lock_in,Vin);
    phasorVC = phasorVin - phasorVR
    ZC = phasorVC/phasorVR*R
    RC = ZC.real
    XC = -ZC.imag
    return ZC,RC,XC,phasorVin,phasorVR,phasorVC

f0=5000.0
a=10.0
Nharm=50
Tsignal=2.0
fS=10000000.0
Ns=20004
s, lock_in, params,__,__=Z_meter_excitation(f0,Nharm,Tsignal,fS,a)
freq=params['freq']
freq=np.squeeze(freq)
Nx=132
Ny=1
b,a = butter(2, 2*Nharm*f0/(fS), btype='low') # ref: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.butter.html

str0='0000x0000.npy'
fig0=plt.figure()
rangex= range(4,Nx)
Nx_eff=np.size(rangex)
C_meas=np.zeros((Nx_eff))
RC_meas=np.zeros((Nx_eff))
ZC_meas=np.zeros((Nx_eff))
XC_meas=np.zeros((Nx_eff))

jj=0
for jx in rangex:
    for jy in range(1,Ny+1):
        xstr=str(jx)
        nxstr=len(xstr)
        ystr=str(jy)
        nystr=len(ystr)
        filename=str0[:4-nxstr]+xstr+str0[4:9-nystr]+ystr+str0[9:]
        data=np.load(filename)
        

        CH1=data[0,:]
        CH2=data[1,:]
        # CH1f = signal.filtfilt(b, a, CH1, padtype = None) # ref: https://dsp.stackexchange.com/questions/11466/differences-between-python-and-matlab-filtfilt-function
        # CH2f = signal.filtfilt(b, a, CH2, padtype = None)

        ZC,RC,XC,phasorVin,phasorVR,phasorVC=Cap_meter_processing(CH1,CH2,params,lock_in)
        
        plt.plot(CH1[0:2000])
        try:
            pR,pCov = curve_fit(modelX,freq[0:10], XC[0:10],  p0 = [0, 1/(2*np.pi*XC[0]*freq[0])],maxfev=10000)
            C_meas[jj]=pR[1]
            RC_meas[jj]=np.average(np.abs(RC[0:5]))
            ZC_meas[jj]=np.average(np.abs(ZC[0:5]))
            XC_meas[jj]=np.average(np.abs((XC[0:10]*freq[0:10]*2*np.pi))**-1)

            flag_fit=True
            
        except RuntimeError:
            pR=[1/(XC[0]*freq[0]), 0]
   
            flag_fit=False
        jj=jj+1

C_meas=smooth(C_meas,3)
RC_meas=smooth(RC_meas,3)
XC_meas=smooth(XC_meas,3)
ZC_meas=smooth(ZC_meas,3)

plt.show()
fig1=plt.figure()
plt.subplot(221)
plt.plot(C_meas)
plt.subplot(222)
plt.plot(RC_meas)
plt.subplot(223)
plt.plot(XC_meas)
plt.subplot(224)
plt.plot(ZC_meas)


