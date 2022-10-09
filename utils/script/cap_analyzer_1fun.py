#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  1 11:17:28 2022

@author: alecce
"""

import tkinter as tk
from tkinter import filedialog
import scipy.io
import numpy as np
from matplotlib import pyplot as plt
from scipy.signal import butter
from scipy import signal
from scipy.optimize import curve_fit
import sys
import os
import pandas as pd
import json

from mpl_toolkits.mplot3d import Axes3D
from matplotlib.collections import PolyCollection
from matplotlib import colors as mcolors

def clear_all():
    """Clears all the variables from the workspace of the spyder application."""
    gl = globals().copy()
    for var in gl:
        if var[0] == '_': continue
        if 'func' in str(globals()[var]): continue
        if 'module' in str(globals()[var]): continue
        del globals()[var]

clear_all()

R=196*1e3; # [Ohm]
XC = 0

def modelCR(x, p0, p1, p2, p3, p4, p5, p6):
    return p0+p1*x+p2*x**2+p3*x**3+p4*x**4+p5*x**5+p6*x**6 # poly
    #return p0 - p1 * p2**x

def modelCX_float(x, p1, p2):
    return p2+p1/np.sqrt(x)

def modelCX(x, p1, p2):
    # return p2+1/(2*np.pi*x*p1)
    return p2+(1/x)*1/(2*np.pi*p1)

def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='valid')
    return y_smooth

def funPhasor(float_elec, plotFlag):
    global Cestimated
    if float_elec == 0:
        phasorVC = phasorVin - phasorVR
        ZC = (phasorVC/phasorVR)*R
        RC = ZC.real
        XC = -ZC.imag
        Cestimated = 1/(2*np.pi*freq*np.squeeze(XC))*1e12

        Cestimated_mean = np.mean(Cestimated[1:9]) #ad alte freq la cap varia molto
        # Cestimated_mean = Cestimated[0] #ad alte freq la cap varia molto
        RCestimated_mean = np.mean(RC[0:40]) #ad alte freq la cap varia molto
        # RCestimated_mean = RC[0] #ad alte freq la cap varia molto
        # print("Cestimated_mean: ",Cestimated_mean, "pF")
    elif float_elec == 1:
        phasorVC = phasorVR
        ZC = phasorVC/phasorVin
        RC = ZC.real
        XC = ZC.imag
        Cestimated = 1/(2*np.pi*freq*np.squeeze(XC))*1e12
        Cestimated_mean = np.mean(Cestimated[0:40]) #ad alte freq la cap varia molto
        # Cestimated_mean = Cestimated[0] #ad alte freq la cap varia molto
        RCestimated_mean = np.mean(RC[0:40]) #ad alte freq la cap varia molto
        # RCestimated_mean = RC[0] #ad alte freq la cap varia molto
        # print("Cestimated_mean: ", Cestimated_mean, "pF")
        Cmeas = np.average(np.abs(phasorVR[1:5]))
    else:
        print("invalid")
    # FITTING
    popt, pcov = curve_fit(modelCX, freq, np.squeeze(XC), p0 = [2e-11, 0]) 
    Cestimated2 = popt[0]*1e12
    # print("C estimated from fitting: ", Cestimated2, "pF")
    popt2, pcov2 = curve_fit(modelCR, freq, np.squeeze(RC))
    Restimated2 = popt2[0]

    # print("R estimated from fitting: ", popt2, "ohm")
    
    abs_phasorVC_mean = np.mean(abs(phasorVC))
    angle_phasorVC_mean  = np.mean(np.angle(phasorVC))
    
    abs_slope = np.polyfit(freq, abs(ZC),1)[0]
    angle_slope = np.polyfit(freq, np.angle(ZC),1)[0]
    
    # plt.figure()
    # plt.title("Cestimated n: " + str(file))
    # plt.ylabel('cap [pF]')
    # plt.xlabel('samples')
    # plt.plot(Cestimated)
    
    if plotFlag == 1:
        plt.figure()
        plt.subplot(2,2,1)
        plt.title("phasorVC.real", fontsize=10, fontweight = 'bold', pad=5)
        plt.ylabel('Amplitude')
        plt.xlabel('Frequency [Hz]')
        plt.plot(freq[:-1], phasorVC.real[:-1])  
        plt.subplot(2,2,2)
        plt.ylabel('Amplitude')
        plt.xlabel('Frequency [Hz]')
        plt.title("phasorVC.imag", fontsize=10, fontweight = 'bold', pad=5)
        plt.plot(freq[:-1], phasorVC.imag[:-1])
        plt.subplot(2,2,3)
        plt.ylabel('Resistance')
        plt.xlabel('Frequency [Hz]')
        plt.title("RC", fontsize=10, fontweight = 'bold', pad=5)
        plt.plot(freq[:-1], RC[:-1])
        plt.subplot(2,2,4)
        plt.ylabel('Reactance')
        plt.xlabel('Frequency [Hz]')
        plt.title("XC", fontsize=10, fontweight = 'bold', pad=5)
        plt.plot(freq[:-1], XC[:-1])
        plt.subplots_adjust(hspace = 0.55, wspace=0.45)
    
        plt.figure()
        plt.title("C estimated", fontsize=10, fontweight = 'bold', pad=5)
        plt.ylabel('Capacitance [pF]')
        plt.xlabel('Frequency [Hz]')
        plt.plot(freq[:-1], Cestimated[:-1])
        
        plt.figure()
        plt.subplot(2,1,1)
        plt.title("Phasor VC", fontsize=10, fontweight = 'bold', pad=5)
        plt.ylabel('ABS phasor VC')
        plt.xlabel('Frequency [Hz]')
        plt.plot(freq, abs(phasorVC))
        plt.subplot(2,1,2)
        plt.title("Phasor VC", fontsize=10, fontweight = 'bold', pad=5)
        plt.ylabel('angle phasor VC')
        plt.xlabel('Frequency [Hz]')
        plt.plot(freq, np.angle(phasorVC))
        plt.subplots_adjust(hspace = 0.55, wspace=0.45)
    
        plt.figure()
        plt.subplot(2,1,1)
        plt.title("Impedance ZC", fontsize=10, fontweight = 'bold', pad=5)
        plt.ylabel('abs(ZC)')
        plt.xlabel('Frequency [Hz]')
        plt.plot(freq, abs(ZC))
        plt.subplot(2,1,2)
        plt.ylabel('angle(ZC)')
        plt.xlabel('Frequency [Hz]')
        plt.plot(freq, np.angle(ZC))
        
        plt.figure()
        plt.title("Capacitive reactance XC", fontsize=10, fontweight = 'bold', pad=5)
        plt.plot(freq[:-1], XC[:-1], label = 'XC')
        plt.plot(freq[:-1], modelCX(freq, *popt)[:-1], label = 'XC fitted')
        plt.ylabel('value (ohm)')
        plt.xlabel('Frequency [Hz]')
        plt.legend()
    
        plt.figure()
        plt.title("Capacitive resistance RC", fontsize=10, fontweight = 'bold', pad=5)
        plt.ylabel("RC [ohm]")
        plt.xlabel("frequency [Hz]")
        plt.plot(freq[:-1], RC[:-1], label = "RC")
        plt.plot(freq[:-1], modelCR(freq, *popt2)[:-1], label = "RC fitted")
        plt.legend()
    return Cmeas, Cestimated, Cestimated[0], Cestimated_mean, RCestimated_mean, abs_phasorVC_mean, angle_phasorVC_mean, abs_slope, angle_slope

def countFilef():
    countFile = 0
    for path in os.listdir(os.path.dirname(file_path)):
    # check if current path is a file
        if os.path.isfile(os.path.join(os.path.dirname(file_path), path)):
            countFile += 1
    if file_path.split('.')[1] == "csv" or file_path.split('.')[1] == "npy":
        countFile -= 1
    print('File count:', countFile)
    return countFile

def checkMeasType():
    try:
        if file_path.split('.')[1] == "mat":
            mat = scipy.io.loadmat(file_path)
            measType = mat['param']['measType'][0][0][0][0]
            Nc = mat['param']['Ns'][0][0][0][0]
        elif file_path.split('.')[1] == "csv" or file_path.split('.')[1] == "npy":
            config = readJSON(file_path)
            measType = config['measType']
            Nc = config['Ns']
        if measType == 0:
            print("Measurement Type: MONO")
        elif measType == 1:
            print("Measurement Type: MULTI")
        else:
            print("Measurement Type: NONE, quit...")
            sys.exit(1)            
        return measType, Nc
    except Exception as e:
        print('Exception: ', e)

def readJSON(filepath):
    config_file = os.path.dirname(filepath) + "/config.json"
    with open(config_file, "r") as read_content:
        return json.load(read_content)

float_elec= int(input("measurement config: [0: RC series, 1: float] \t" ))
if float_elec == 0:
    print("RC series CONFIGURATION")
elif float_elec == 1:
    print("FLOAT CONFIGURATION")
else:
    print("NO configuration")
    sys.exit(1)
    
plotFlag = int(input("Plot graphs? [0: NO, 1: YES (it will take a few minutes)] \t"))
if plotFlag == 0:
    print("NO PLOT")
elif plotFlag == 1:
    print("PLOTTING...")
else:
    print("Command not found")
    sys.exit(1)

def renameFile():
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askopenfilename()
    for count, filename in enumerate(os.listdir(os.path.dirname(folder))):
        row_new = (filename.split("x")[0])
        column_new = filename.split("x")[1].split(".")[0]
        frmt= filename.split("x")[1].split(".")[1]
        dst = f"{str(column_new)}x{str(row_new)}.{str(frmt)}"
        src =f"{folder}/{filename}"  # foldername/filename, if .py file is outside folder
        dst =f"{folder}/nuova cartella/{dst}"
        # rename() function will
        # rename all the files
        os.rename(src, dst)


def selectFiles():
    global file_path, matrixList
    global matrix_C, matrix_R, matrix_abs_phasorVC_mean, matrix_angle_phasorVC_mean, matrix_M, matrix_total, M
    global matrix_abs_slope, matrix_angle_slope, Cmeas_output
    global column, row, Nharm
    root = tk.Tk()
    # root.lift()
    # root.wm_attributes('-topmost', 1)
    root.withdraw()
    file_path = filedialog.askopenfilename()
    matrixList = sorted(os.listdir(os.path.dirname(file_path)))
    if file_path.split('.')[1] == "csv" or file_path.split('.')[1] == "npy":                            
        matrixList.pop() # delete last file (config)
    last_matrixList = matrixList[-1]
    row = int(last_matrixList.split("x")[0])
            
    # column = int(last_matrixList.split("x")[1].split(".")[0])
    column = 100
    matrix_C = np.zeros(row*column)
    matrix_R = np.zeros(row*column)
    matrix_abs_phasorVC_mean = np.zeros(row*column)
    matrix_angle_phasorVC_mean = np.zeros(row*column)
    matrix_abs_slope = np.zeros(row*column)
    matrix_angle_slope = np.zeros(row*column)
    
    matrix_M = np.zeros(10*column)
    matrix_M = matrix_M.reshape(10, column)
    
    matrix_total = np.zeros(row*column)
    
    M = np.zeros((row*column, 10))
    Cmeas_output = np.zeros(row*column)


def loadParameters():
    global npy
    global f0, fS, Ns, Nharm, VR, Vin, CH1, CH2, Zcoil, Ccoil
    global len_time_lockin, time_lockin, Ns_cycle, Ncycles, delay, Nharm
    if file_path:
        if file_path.split('.')[1] == "mat":
            mat = scipy.io.loadmat(os.path.dirname(file_path) + "/" + matrixList[file])
            f0 = mat['param']['f0'][0][0][0][0]
            fS = mat['param']['fS'][0][0][0][0]
            Ns = mat['param']['Ns'][0][0][0][0]
            Nharm = mat['param']['Nharm'][0][0][0][0]
            VR=mat['signals']['VR'][0][0]
            Vin=mat['signals']['Vin'][0][0]
            CH1 = mat['signals']['CH1'][0][0]
            CH2 = mat['signals']['CH2'][0][0]
            Zcoil = mat['results']['Zcoil'][0][0]
            Ccoil = mat['results']['Lcoil'][0][0][0]
        elif file_path.split('.')[1] == "csv":
            df = pd.read_csv(os.path.dirname(file_path) + "/" + matrixList[file])
            CH1 = df.Ch1
            CH2 = df.Ch2
            config = readJSON(file_path)
            f0 = config['f0']
            fS = config['fS']
            Ns = config['Ns']
            Nharm = config['Nharm']
        elif file_path.split('.')[1] == "npy":
            npy = np.load(os.path.dirname(file_path) + "/" + matrixList[file])
            CH1 = npy[0]
            CH2 = npy[1]
            config = readJSON(file_path)
            f0 = config['f0']
            fS = config['fS']
            Ns = config['Ns']
            Nharm = config['Nharm']

        Ns_cycle=int(fS/f0)
        Ncycles=int(Ns/Ns_cycle)
        
        # Time axis
        t = np.arange(Ns-1)/fS # Time vector
        delay = 0
        time_lockin = np.arange(Ns_cycle*(Ncycles-1))/fS # Time vector
        len_time_lockin = len(time_lockin)
    else:
        print("no file")
        sys.exit(1)
        
    return CH1, CH2
        
def plotFun():
    plt.figure()
    plt.title("Vin")
    plt.ylabel('Amplitude [V]')
    plt.xlabel('samples')
    plt.plot(CH2)
    
    plt.figure()
    plt.title("VR")
    plt.ylabel('Amplitude [V]')
    plt.xlabel('samples')
    plt.plot(CH1)
    
    plt.figure()
    plt.subplot(1,2,1)
    plt.title("Vin")
    plt.ylabel('Amplitude [V]')
    plt.xlabel('samples')
    plt.plot(CH2.transpose())
    plt.subplot(1,2,2)
    plt.title("VR")
    plt.ylabel('Amplitude [V]')
    plt.xlabel('samples')
    plt.plot(CH1.transpose())
    plt.tight_layout(pad=1.0)
    
    plt.figure()
    plt.subplot(1,2,1)
    plt.title("Vin filtered")
    plt.ylabel('Amplitude [V]')
    plt.xlabel('samples')
    plt.plot(CH2f)
    plt.subplot(1,2,2)
    plt.title("VR filtered")
    plt.ylabel('Amplitude [V]')
    plt.xlabel('samples')
    plt.plot(CH1f)
    plt.tight_layout(pad=1.0)
    
    # plt.figure()
    # plt.title("VC")
    # plt.ylabel('Amplitude [V]')
    # plt.xlabel('samples')
    # plt.plot(VC)
    
    # plt.figure()
    # plt.title("Lock-in output Real part")
    # plt.plot(freq, Vin_lockin.real, label = 'Vin')
    # plt.plot(freq, VR_lockin.real, label='VR')
    # plt.ylabel('Real part value')
    # plt.xlabel('Frequency [Hz]')
    # plt.legend()
    
    # plt.figure()
    # plt.title("Lock-in output Imag part")
    # plt.plot(freq, Vin_lockin.imag, label = 'Vin')
    # plt.plot(freq, VR_lockin.imag, label = 'VR')
    # plt.ylabel('Real part value')
    # plt.xlabel('Frequency [Hz]')
    # plt.legend()
      
    plt.figure()
    plt.title("Signals Filtered")
    plt.plot(VRf, label = 'VRf')
    plt.plot(Vin_f, label = 'Vin_f')
    plt.ylabel('Amplitude [V]')
    plt.xlabel('samples')
    plt.legend()
    
    plt.figure()
    plt.title("Signals Filtered")
    plt.plot(CH1f.transpose(), label = 'CH1f')
    plt.plot(CH2f.transpose(), label = 'CH2f')
    plt.ylabel('Amplitude [V]')
    plt.xlabel('samples')
    plt.legend()
    
    plt.figure()
    plt.title("Zoom of Signals Filtered")
    plt.plot(CH1.transpose(), label = 'CH1')
    plt.plot(CH1f.transpose(), label = 'CH1f')
    plt.ylabel('Amplitude [V]')
    plt.xlabel('samples')
    plt.xlim([0,200])
    plt.legend()
    
    plt.figure()
    plt.title("abs value of Phasor signal Filtered")
    plt.plot(freq[:-1], abs(phasorVin)[:-1], label = 'phasorVin')
    plt.plot(freq[:-1], abs(phasorVR)[:-1], label = 'phasorVR')
    plt.ylabel('Amplitude')
    plt.xlabel('Frequency [Hz]')
    plt.legend()

if __name__ == '__main__':
    selectFiles()
    measType, Ns = checkMeasType()

    # CH1_total = np.zeros((row,column,Ns))
    # CH2_total = np.zeros((row,column,Ns))
    
    e1 = np.zeros((Ns, row*column))
    e2 = np.zeros((Ns, row*column))


    # for file in range(countFilef()):
    for file in range(row*column):

        # CH1_total[file], CH2_total[file] = loadParameters()
        e1[:,file], e2[:,file] = loadParameters()
            
        s_harml = np.zeros([Nharm,len_time_lockin])
        # s_harml=np.empty((Nharm,Ns_cycle*(Ncycles-1)),'float')
            
        if measType == 0:
            sl=np.sin(2*np.pi*f0*time_lockin)
            lock_in=1j*np.exp(-1j*2*np.pi*f0*time_lockin)/sum(sl**2)
            freq=f0
        elif measType == 1:
            lock_in = np.zeros([Nharm,len_time_lockin], dtype = 'complex_')
            #lock_in=np.ones((Nharm,Ns_cycle*(Ncycles-1)),dtype=np.complex_)

            freq = np.zeros(Nharm)
            
            for j_harm in range(Nharm):
                    s_harml[j_harm, :] = np.cos(2*np.pi*f0*(j_harm+1)*time_lockin+np.pi*((j_harm+1)*j_harm)/Nharm)
                    lock_in[j_harm, :] = np.exp(-1j*np.pi*((j_harm+1)*j_harm)/Nharm) \
                        * np.exp(-1j*2*np.pi*f0*(j_harm+1)*time_lockin) \
                            / np.sum(pow(s_harml[j_harm], 2))
                          #  / np.sum(s_harml[j_harm]**2)
                            
                    freq[j_harm]=f0*(j_harm+1)
            # VC = Vin - VR
            
            # lock-in operation
            # Vin_lockin = np.dot(lock_in, CH2.transpose()[0:len_time_lockin])
            # VR_lockin = np.dot(lock_in, CH1.transpose()[0:len_time_lockin])
        
            #b,a = butter(2, [0.25, 1.5*Nharm]*f0/(fS/2), btype='bandpass')
            b,a = butter(4, 4*Nharm*f0/(fS), btype='lowpass') # ref: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.butter.html
        
            # CH1f = signal.filtfilt(b, a, e1[:,file], padtype = None) # ref: https://dsp.stackexchange.com/questions/11466/differences-between-python-and-matlab-filtfilt-function
            # CH2f = signal.filtfilt(b, a, e2[:,file], padtype = None)

            CH1f = signal.filtfilt(b, a, CH1, padtype = None) # ref: https://dsp.stackexchange.com/questions/11466/differences-between-python-and-matlab-filtfilt-function
            CH2f = signal.filtfilt(b, a, CH2, padtype = None)            
            
            # CH1ff = signal.filtfilt(bb, aa, CH1[4:-4], padtype = None) # ref: https://dsp.stackexchange.com/questions/11466/differences-between-python-and-matlab-filtfilt-function
            # CH2ff = signal.filtfilt(bb, aa, CH2[4:-4], padtype = None)
            
            VRf=CH1f.transpose()[int(4+Ns_cycle*1+delay) : int(4+Ns_cycle*(Ncycles)+delay)]
            Vin_f=CH2f.transpose()[int(4+Ns_cycle*1+delay) : int(4+Ns_cycle*(Ncycles)+delay)]

            # VRf=CH1f.transpose()[4: int(4+Ns_cycle*(Ncycles)+delay)]
            # Vin_f=CH2f.transpose()[4 : int(4+Ns_cycle*(Ncycles)+delay)]

            
            # PHASOR lock-in operation
            phasorVin = np.dot(lock_in, Vin_f)
            phasorVR = np.dot(lock_in, VRf)
                        
            if plotFlag == 1:
                plotFun()
            
            Cmeas_output[file], M[file,:], matrix_total[file], matrix_C[file], matrix_R[file], \
            matrix_abs_phasorVC_mean[file], matrix_angle_phasorVC_mean[file], \
            matrix_abs_slope[file], matrix_angle_slope[file] =  funPhasor(float_elec, plotFlag)

        else:
            print("measType is not defined")
    
    # M_reshape = np.zeros((row,column,10))
    # for i in range(M.shape[1]):
    #     for j in range(M.shape[0]):
    #         M_reshape[i] = M[j].reshape()
    
    # Cmeas_output = smooth(Cmeas_output, 10)
    Cmeas_matrix = Cmeas_output.reshape(row,column)
    
    # fig = plt.figure()
    # ax = fig.gca(projection='3d')
    # def cc(arg):
    #     return mcolors.to_rgba(arg, alpha=0.0)

    # xs = np.arange(0, column)
    # verts = []
    # zs = np.arange(0, row)
    # for z in zs:
    #     ys = Cmeas_matrix[z,:]
    #     # ys[0], ys[-1] = 0, 0
    #     verts.append(list(zip(xs, ys)))
    # poly = PolyCollection(verts,
    #                       facecolors=[cc('r')],
    #                       edgecolors=("black",)
    #                       # facecolors=[cc('r'), cc('g'), cc('b'),
    #                       #                     cc('y')]
    #                       )
    # poly.set_alpha(0.7)
    # ax.add_collection3d(poly, zs=zs, zdir='y')
    # ax.set_xlabel('X')
    # ax.set_xlim3d(0, column)
    # ax.set_ylabel('Y')
    # ax.set_ylim3d(-1, row+1)
    # ax.set_zlabel('Z')
    # ax.set_zlim3d(0.00025, 0.0005)
    # plt.show()

    
    matrix_C_unreshaped = matrix_C
    matrix_R_unreshaped = matrix_R
    
    matrix_C = matrix_C.reshape(column, row)
    matrix_R = matrix_R.reshape(column, row)
    
    matrix_total = matrix_total.reshape(column, row)
    

    # plt.plot(np.convolve(matrix_M[1,20:],[1,1,1,1,1,1],"same"))

    matrix_abs_phasorVC_mean = matrix_abs_phasorVC_mean.reshape(column, row)
    matrix_angle_phasorVC_mean = matrix_angle_phasorVC_mean.reshape(column, row)
    
    matrix_abs_slope = matrix_abs_slope.reshape(column, row)
    matrix_angle_slope = matrix_angle_slope.reshape(column, row)
      

    # plt.figure()
    # # ref: https://docs.python.org/3/library/os.path.html#os.path.normpath
    # plt.title("Scan results for C @ freq = 5000Hz")
    # plt.imshow(matrix_total, aspect = "auto")
    # lbl = plt.colorbar(pad = 0.15)
    # lbl.set_label('[pF]', rotation=270, labelpad=15)
    
    # matrix_total2 = matrix_total
    # # for i in range(len(matrix_total)):
    # #     if abs(matrix_total[i])  > 60:
    # #         matrix_total2[i] = matrix_total[i-1]
            
    # for i in range(matrix_total.shape[0]):
    #     for j in range(matrix_total.shape[1]):
    #         if abs(matrix_total[i][j])  > 60:
    #             matrix_total2[i][j] = 60
            
    # plt.figure()
    # # ref: https://docs.python.org/3/library/os.path.html#os.path.normpath
    # plt.title("matrix")
    # plt.imshow(matrix_total2, aspect = "auto")
    # lbl = plt.colorbar(pad = 0.15)
    # lbl.set_label('[pF]', rotation=270, labelpad=15)

    # plt.figure()
    # # ref: https://docs.python.org/3/library/os.path.html#os.path.normpath
    # plt.title("Scan results for C, material: " + os.path.basename(os.path.normpath(os.path.dirname(file_path))))
    # plt.imshow(matrix_C[:,1:], aspect = "auto")
    # lbl = plt.colorbar(pad = 0.15)
    # lbl.set_label('[pF]', rotation=270, labelpad=15)
    
    # plt.figure()
    # plt.title("Scan results for R, material: " + os.path.basename(os.path.normpath(os.path.dirname(file_path))))
    # plt.imshow(matrix_R, aspect = "auto")
    # lbl = plt.colorbar(pad = 0.15)
    # lbl.set_label('[ohm]', rotation=270, labelpad=15)
    
    # plt.figure()
    # plt.imshow(matrix_M[5:6,30:-30], aspect="auto")
    # lbl = plt.colorbar(pad = 0.15)
    # lbl.set_label('[pF]', rotation=270, labelpad=15)
    
    # plt.figure()
    # plt.title("Scan results for matrix_abs_phasorVC_mean, material: " + os.path.basename(os.path.normpath(os.path.dirname(file_path))))
    # plt.imshow(matrix_abs_phasorVC_mean, aspect = "auto")
    # lbl = plt.colorbar(pad = 0.15)
    # lbl.set_label('[ohm]', rotation=270, labelpad=15) 
    
    # plt.figure()
    # plt.title("Scan results for matrix_angle_phasorVC_mean, material: " + os.path.basename(os.path.normpath(os.path.dirname(file_path))))
    # plt.imshow(matrix_angle_phasorVC_mean, aspect = "auto")
    # lbl = plt.colorbar(pad = 0.15)
    # lbl.set_label('[ohm]', rotation=270, labelpad=15) 
    
    # plt.figure()
    # plt.title("Scan results for matrix_abs_slope, material: " + os.path.basename(os.path.normpath(os.path.dirname(file_path))))
    # plt.imshow(matrix_abs_slope, aspect = "auto")
    # lbl = plt.colorbar(pad = 0.15)
    # lbl.set_label('slope', rotation=270, labelpad=15) 
    
    # plt.figure()
    # plt.title("Scan results for matrix_angle_slope, material: " + os.path.basename(os.path.normpath(os.path.dirname(file_path))))
    # plt.imshow(matrix_angle_slope, aspect = "auto")
    # lbl = plt.colorbar(pad = 0.15)
    # lbl.set_label('slope', rotation=270, labelpad=15) 
    
    
    
    
    # (x, y) = np.meshgrid(row*column, Ns)
    # ax = plt.axes(projection='3d')
    # ax.plot_surface(x,y,e1)
    
    # (x, y) = np.meshgrid(row*column, Ns)
    # ax = plt.axes(projection='3d')
    # ax.plot_surface(row,column,e2)
    
    # from mpl_toolkits.mplot3d.axes3d import Axes3D
    # fig = plt.figure()
    # ax=Axes3D(fig)
    # ax.plot_surface(row,column,e2)
    # plt.show()
    # # e1 = e1.reshape((row,column,Ns))
    
    # plt.figure()
    # plt.subplot(2,1,1)
    # plt.title("CH1")
    # plt.ylabel("acquisizione")
    # plt.plot(e1[:,5])
    # plt.subplot(2,1,2)
    # plt.title("CH2")
    # plt.ylabel("acquisizione")
    # plt.xlabel("samples")
    # plt.plot(e2[:,5])
    # plt.subplots_adjust(hspace = 0.5)
    
    # plt.figure()
    # plt.subplot(2,1,1)
    # plt.title("CH1")
    # plt.ylabel("acquisizione")
    # plt.imshow(e1.transpose(),aspect="auto")
    # lbl = plt.colorbar(pad = 0.05)
    # lbl.set_label('[V]', rotation=270, labelpad=5)
    # plt.subplot(2,1,2)
    # plt.title("CH2")
    # plt.ylabel("acquisizione")
    # plt.xlabel("samples")
    # plt.imshow(e2.transpose(),aspect="auto")
    # lbl = plt.colorbar(pad = 0.05)
    # lbl.set_label('[V]', rotation=270, labelpad=5)
    # plt.subplots_adjust(hspace = 0.5)

    # plt.figure()
    # plt.subplot(2,1,1)
    # plt.title("CH1")
    # plt.magnitude_spectrum(e1[:,164], Fs=fS)
    # plt.xlim(0,300000)
    # plt.subplot(2,1,2)
    # plt.title("CH2")
    # plt.magnitude_spectrum(e2[:,164], Fs=fS)
    # plt.xlim(0,300000)
    # plt.ylim(0,0.7)
    # plt.subplots_adjust(hspace = 0.6)
    
    # plt.figure()
    # plt.subplot(2,1,1)
    # plt.title("CH1")
    # plt.magnitude_spectrum(e1.transpose()[5,:], Fs=fS)
    # plt.xlim(0,300000)
    # plt.subplot(2,1,2)
    # plt.title("CH2")
    # plt.magnitude_spectrum(e2.transpose()[5,:], Fs=fS)
    # plt.xlim(0,300000)
    # # plt.ylim(0,0.7)
    # plt.subplots_adjust(hspace = 0.6)
    
    # b,a = butter(4, 4*Nharm*f0/(fS), btype='lowpass') # ref: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.butter.html
    # b,a = butter(2, [0.01*Nharm*f0/fS, 3.5*Nharm*f0/fS], btype='bandpass')

    # e1f = signal.filtfilt(b, a, e1[:,164], padtype = None) # ref: https://dsp.stackexchange.com/questions/11466/differences-between-python-and-matlab-filtfilt-function
    # e2f = signal.filtfilt(b, a, e2[:,164], padtype = None) 
    
    # M[1:-1,0]
    
    # matrix_total2_f=smooth(np.squeeze(matrix_total2.transpose()),5)

    
    # plt.plot(matrix_total2_f)    
    # plt.figure()
    # plt.subplot(2,1,1)
    # plt.title("CH1f")
    # plt.magnitude_spectrum(e1f, Fs=fS)
    # plt.xlim(0,6000)
    # plt.subplot(2,1,2)
    # plt.title("CH2f")
    # plt.magnitude_spectrum(e2f, Fs=fS)
    # plt.xlim(0,6000)
    # # plt.ylim(0,0.7)
    # plt.subplots_adjust(hspace = 0.6)
    
    # plt.figure()
    # plt.subplot(2,1,1)
    # plt.title("C center", fontsize=10, fontweight = 'bold', pad=5)
    # plt.ylabel('Capacitance [pF]')
    # # plt.xlabel('Frequency [Hz]')
    # plt.plot(freq[:-1], M[10,:-1])
    # plt.subplot(2,1,2)
    # plt.title("C metal", fontsize=10, fontweight = 'bold', pad=5)
    # plt.ylabel('Capacitance [pF]')
    # plt.xlabel('Frequency [Hz]')
    # plt.plot(freq[:-1], M[0,:-1])
    # plt.subplots_adjust(hspace = 0.4)
    
    # M2 = smooth(M[100,:-1],5)
    
    # plt.figure()
    # plt.title("C")
    # plt.plot(freq[:-5], M2*1e-10)
    # plt.ylabel('Capacitance [F]')
    # plt.xlabel('Frequency [Hz]')

    print(" ### --- END --- ###")
    

    # # x cols, y rows
    # #(x, y) = np.meshgrid(np.arange(matrix.shape[0]), np.arange(matrix.shape[1]))
    # (x, y) = np.meshgrid(np.arange(e1.shape[0]), np.arange(e1.shape[1]))
    # fig_s = plt.figure()
    # ax = fig_s.add_subplot(111, projection='3d')
    # fig_s.suptitle('Absolute voltage differences by varying the frequency')
    # # for s in range(0, len(w_vec), 5):
    # surf = ax.plot_surface(x, y, e1, cmap=plt.cm.coolwarm)
    # fig_s.show()


