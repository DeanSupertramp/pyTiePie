


def Z_meter_excitation(f0,Nharm,Tsignal,fS,amp):
    from math import sin
    # f0=4e3                        # freq. fondamentale    4 KHz
    # Nharm=50                      # n° armoniche          50
    # Tsignal=2                     # in [ms]               2ms 
    # fS=1e8                        # in [Hz]               100 MHz
    import numpy as np
    Ns=int(Tsignal*fS/1000)     # n° campioni [ms * MHz / 1000 = 1e-3 * 1e6 / 1e3]                      200 000
    Ns_cycle=int(fS/f0)         # n° campioni per ciclo : freq. campionamento / freq fondamentale       25 000
    Ncycles=int(Ns/Ns_cycle)    # n° campioni                                                           8
    # time_axis
    time=np.arange(0,Ns)/fS;    # array([0.00000e+00, 1.00000e-08, 2.00000e-08, ..., 1.99997e-03, 1.99998e-03, 1.99999e-03])

    time_lockin=np.arange(0,(Ns_cycle*(Ncycles-1)))/fS;     # array([0.00000e+00, 1.00000e-08, 2.00000e-08, ..., 1.74997e-03, 1.74998e-03, 1.74999e-03])
    s=np.zeros([1,int(Ns)+4]);                              # matrice 1 riga, Ns+4 colonne
    s_harm=np.empty((Nharm,Ns),'float')
    s_harml=np.empty((Nharm,Ns_cycle*(Ncycles-1)),'float')
    lock_in=np.ones((Nharm,Ns_cycle*(Ncycles-1)),dtype=np.complex_)
    
    freq=np.empty((Nharm,1),'float')
    ampl=np.ones((Nharm,1),dtype=np.complex_)
    
    for j_harm in range(int(Nharm)):
        s_harm[j_harm,:] = (np.cos(2 * np.pi * f0 * j_harm * time + np.pi * (j_harm * (j_harm - 1)) / Nharm)); # [2 pi f k t + pi(k(k-1)) / Nharm]
        s_harml[j_harm,:] = (np.cos(2 * np.pi * f0 * j_harm * time_lockin + np.pi * (j_harm * (j_harm - 1)) / Nharm));
        lock_in[j_harm,:] = ( np.exp(-1j * np.pi * (j_harm * (j_harm - 1)) / Nharm) * np.exp(-1j * 2 * np.pi * f0 * j_harm * time_lockin) / np.sum(s_harml[j_harm,:]**2) );
        freq[j_harm] = f0 * (j_harm + 1);
        
    # ******* PLOT DEBUG **********
    from matplotlib import pyplot as pl
    pl.plot(time, s_harm[1])
    pl.plot(time_lockin, s_harml[1])    
    pl.plot(time_lockin, lock_in[1])  
    pl.plot(time, s_harm[1], time_lockin, s_harml[1], time_lockin, lock_in[1])
            
    s[0,2:-2]=np.sum(s_harm,0); # sommo l'array per righe, ottengo un unico array somma con la dimensione di una riga
    # il risultato della somma lo colloco nella prima riga, partendo dalla colonna 2 alla colonna -2
    # Praticamente l'array somma inizia due colonne dopo e finisce due colonne prima

    # ******* PLOT DEBUG **********
    times = np.arange(0,Ns+4)/fS;
    pl.plot(times, s[0])
    
    for j_harm in range(int(Nharm)):
        ampl[j_harm,:]=np.sum(s[0,0:Ns_cycle*(Ncycles-1)]*lock_in[j_harm,:])
       
    # ******* PLOT DEBUG **********  
    pl.plot(Nharm, ampl[0])

    params={'Ns':Ns, 'Ns_cycle':Ns_cycle, 'Ncycles':Ncycles, 'freq':freq, 'time':time}
    
    return s, lock_in, params, s_harm, s_harml,
        #  s = segnale multitono generato
        #  lock_in = segnale sinusoidale generato tramite espressione esponenziale


def Z_meter_processing(CH1,CH2,params,lock_in):
    import numpy as np
    Ns=params['Ns']
    Ns_cycle=params['Ns_cycle']
    Ncycles=params['Ncycles']
    freq=params['freq']
    time=params['time']
    VR=(CH1[3+Ns_cycle:3+Ns_cycle*(Ncycles)])
    Vin=(CH2[3+Ns_cycle:3+Ns_cycle*(Ncycles)])
    R=100
    Vcoil=Vin-VR
    # phasor_coil=np.dot(lock_in,Vcoil);
    phasorR=np.dot(lock_in,VR);
    phasorVin=np.dot(lock_in,Vin);
    Zcoil=(phasorVin-phasorR)/phasorR*R
    return Zcoil,Vcoil,VR
