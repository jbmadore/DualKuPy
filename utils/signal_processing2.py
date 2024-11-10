import pandas as pd
import numpy as np
from scipy.fft import fft, fftfreq

scaling_factor_adc = (3.3+3.3)/(2**12)
frequence_echantillonage = 10e6          
T = 1.0 / frequence_echantillonage


def freq_to_dist(xf):
    c = 299792458
    B = 2e9   #bandwith
    ramptime = 102400e-9       
    dist = xf*c*ramptime/(2*B)
    return(dist)

def hft95 (N):
    window = np.zeros((N))
    for j in range(N):
        z = 2*np.pi*j/N
        window[j] = 1 - 1.9383379*np.cos(z) + 1.3045202*np.cos(2*z) - 0.4028270*np.cos(3*z) + 0.0350665*np.cos(4*z)
    
    S1 = np.sum(window)
    S2 = np.sum(window*window)
    nenbw = N*S2/(S1**2)                                    #normalized equivalent noise bandwidth  
    enbw = frequence_echantillonage*S2/(S1**2)              #effective noise bandwidth
    return(window,S1,S2)

def ham (N):
    window = np.hamming(N)
    
    S1 = np.sum(window)
    S2 = np.sum(window*window)
    nenbw = N*S2/(S1**2)                                    #normalized equivalent noise bandwidth  
    enbw = frequence_echantillonage*S2/(S1**2)              #effective noise bandwidth
    return(window,S1,S2)



df = pd.read_csv(dat,skiprows=62,index_col=0)

e_copol = df[0] + 1j*df[1]
e_crosspol = df[2] + 1j*df[3]
N = len(e_copol)
window,s1,s2 = hft95(N)
xf = fftfreq(N, T)
dist = freq_to_dist(xf[0:N//2])


e_copol_f = fft(np.array((e_copol-e_copol.mean())*window))
e_crosspol_f = fft(np.array((e_crosspol-e_crosspol.mean())*window))


ps_rms_cp = (2*np.abs(e_copol_f[0:N//2])**2)/(s1**2)
usefull_cp = ps_rms_cp*scaling_factor_adc

ps_rms_cr = (2*np.abs(e_crosspol_f[0:N//2])**2)/(s1_h**2)
usefull_cr = ps_rms_cr*scaling_factor_adc


