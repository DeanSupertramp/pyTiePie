[filename,foldname]=uigetfile('*.mat','select the file(s) to process','MultiSelect','on')
float_elec=1;
homefol=pwd;
cd(foldname);
load(filename)
fS=param.fS;
f0=param.f0;
Ns=param.Ns;
Nharm=param.Nharm;
measType=param.measType;
Ns_cycle=fS/f0;
Ncycles=Ns/Ns_cycle;
% time_axis
time=[0:(Ns-1)]/fS;
delay=0;
time_lockin=[0:(Ns_cycle*(Ncycles-1)-1)]/fS;

modelC =  @(p,x) p(1)+(p(2)-p(1))./(1+(x/p(3)).^p(4));

% generate the input signal "s"
switch measType
    case 0
        sl=sin(2*pi*f0*time_lockin);
        lock_in=1i*exp(-1i*2*pi*f0*time_lockin)/sum(sl.^2);
        freq=f0;
    case 1
        for j_harm=1:Nharm
            s_harml(j_harm,:)=(cos(2*pi*f0*j_harm*time_lockin+pi*(j_harm+1)/Nharm));
            lock_in(j_harm,:)=exp(-1i*pi*(j_harm+1)/Nharm)*exp(-1i*2*pi*f0*(j_harm+1)*time_lockin)/sum(s_harml(j_harm,:).^2);
            freq(j_harm)=f0*j_harm;
        end
    case 2 % f=f0*[1,2,5,10]
       for j_harm=[1:4]
           v_harm=[1,2,5,10];
            s_harm(j_harm,:)=(cos(2*pi*f0*v_harm(j_harm)*time+pi*(v_harm(j_harm)*(v_harm(j_harm)-1))/Nharm));
            s_harml(j_harm,:)=(cos(2*pi*f0*v_harm(j_harm)*time_lockin+pi*(v_harm(j_harm)*(v_harm(j_harm)-1))/Nharm));

            lock_in(j_harm,:)=exp(-1i*pi*(v_harm(j_harm)*(v_harm(j_harm)-1))/Nharm)*exp(-1i*2*pi*f0*v_harm(j_harm)*time_lockin)/sum(s_harml(j_harm,:).^2);
            freq(j_harm)=f0*v_harm(j_harm);
       end
end

CH1=signals.CH1;
CH2=signals.CH2;
[b,a]=butter(2,[0.25 1.5*Nharm]*f0/(fS/2));
CH1f=filtfilt(b,a,CH1);
CH2f=filtfilt(b,a,CH2);

VR=CH1f(4+Ns_cycle*1+delay:3+Ns_cycle*(Ncycles)+delay)';
Vin=CH2f(4+Ns_cycle*1+delay:3+Ns_cycle*(Ncycles)+delay)';

% Vin=amp*s_gen(4+Ns_cycle+delay:3+Ns_cycle*(Ncycles)+delay)';% remove the DC component
  
R=196e3;
clear parameters

Vcoil=Vin-VR;

if float_elec==0

%% calculation of the impedances

phasor_coil=lock_in*Vcoil;
phasorR=lock_in*VR;
phasorVin=lock_in*Vin;

Zcoil=(phasorVin-phasorR)./phasorR*R;
if flag_ref==1
    if exist('results')==1
    else
    load(reference)
    end
    Zcoil=Zcoil-results.Zcoil;
end
Rcoil=real(Zcoil)';
Xcoil=-imag(Zcoil)'; 
Lcoil=1./(2*pi*freq.*Xcoil)*1e12;

model_C=[2*pi*freq',(freq')*0];
param_C=pinv(model_C)*(1./Xcoil)';
Cfit=param_C(1);
Xcoil_stim=1./(model_C*param_C);

figure(1)
subplot(2,1,1)
plot(CH1)
subplot(2,1,2)
plot(freq,Xcoil,'or','markersize',5);
hold on
plot(freq,Xcoil_stim,'k')
l=legend(['C stim=', num2str(Cfit*1e12)])
set(l,'fontsize',20)
fVin=fft(Vin);
fVR=fft(VR);

else
   phasor_coil=lock_in*Vcoil;
    phasorR=lock_in*VR;
    phasorVin=lock_in*Vin;
    Zcoil=(phasorVin-phasorR)./phasorR*R;

    %
    Rcoil=real(phasorR./phasorVin)'
    Xcoil=-imag(phasorR./phasorVin)';     
 %   Rcoil=real(phasorR'); NON NORMALIZZATE
 %   Xcoil=-imag(phasorR'); NON NORMALIZZATE
    Lcoil=1./(2*pi*freq.*Xcoil);

%%% fit logistic
startC= [Xcoil(end) Xcoil(1)-Xcoil(end) 1000 1.5];
coeffC = real(nlinfit(freq,Xcoil, modelC, startC));
Cfit=modelC(coeffC,freq);


figure(1)
subplot(2,1,1)
plot(CH1)
subplot(2,1,2)
plot(freq,Xcoil,'or','markersize',5);
hold on
plot(freq,Cfit,'k')
l=legend({['sat=', num2str(coeffC(1)),',f_t=', num2str(coeffC(3))],['rap=', num2str(coeffC(4))]})
set(l,'fontsize',12,'location','best')
hold off
end    
% Zcoil2=(fVin(Ncycles-1)-fVR(Ncycles-1))./fVR(Ncycles-1)*R;
% Rcoil2=real(Zcoil2)';
% Xcoil2=imag(Zcoil2)'; 
% Lcoil2=Xcoil2./(2*pi*freq)*1000;
% modelR =  @(p,x) p(1)+p(2)*sqrt(x+p(3));
% modelZ =  @(p,x) p(1)*x.^2+p(2)*x+p(3);
% modelL =  @(p,x) p(1)./(x+p(2)).^p(3)+p(4);

model0=Rcoil';
%     model=[model0.^1,model0.^0];
    model=[model0.^2,model0.^1,model0.^0];
    
%     if flag_analysis==1
%     coeffZ=(pinv(model)*Xcoil');
% 
%     startR=[0 Rcoil(end)/sqrt(freq(end)) 0];
%     startL= [Lcoil(1)-Lcoil(end) 0 0.5 Lcoil(end)];
% %     startExp=[real(matrix_results(jfile,end)) freq_ax(end)];
% %     startLog= [real(matrix_results(jfile,end))/log(freq_ax(end)) 0];
%     coeffR = real(nlinfit(freq,Rcoil, modelR, startR));
%     coeffL = real(nlinfit(freq,Lcoil, modelL, startL));
%     Rfit=modelR(coeffR,freq);
%     Lfit=modelL(coeffL,freq);
%     Zfit=(model*coeffZ)';
%     
%     c_st=1./coeffR(2);
%     c_st1=-coeffZ(1);
% 
%     end