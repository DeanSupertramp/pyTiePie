import numpy as np

Vin = 10;
R = 2893726.238
f = 55000.0
w = 2*np.pi*f
C = 1e-12
dC = C/100


V1_num = w * R * (C + dC);
V1_den = np.sqrt(1 + pow(w,2) * pow(R,2) * pow(C+dC,2));
V1 = Vin * V1_num / V1_den;

V2_num = w * R * C;
V2_den = np.sqrt(1 + pow(w,2) * pow(R,2) * pow(C,2));
V2 = Vin * V2_num /V2_den;

print("V1 = " + str(V1) + " Volt")
print("V2 = " + str(V2) + " Volt")

print("V1 - V2 = " + str((V1-V2)*1000) + " mV")
