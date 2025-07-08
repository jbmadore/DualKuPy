import pandas as pd
import numpy as np
from scipy.fft import fft, fftfreq
from scipy import signal


def freq_to_dist(xf):
    c = 299792458
    B = 2e9   #bandwith
    ramptime = 102400e-9       
    dist = xf*c*ramptime/(2*B)
    return(dist)

def kai(N, beta):
    window = signal.windows.kaiser(N, beta=beta)
    S1 = np.sum(window)
    S2 = np.sum(window * window)
    return window, S1, S2

def fft_no_scaling(data_array,beta=0,pad_factor=1):
    frequence_echantillonage = 10e6
    N = 1024
    T = 1 / frequence_echantillonage
    N_padded = N * pad_factor

    kaiwindow, s1, s2 = kai(N, self.beta)
    
    data_padded_windowed = np.pad(data_array * kaiwindow, (0, N_padded - N), 'constant')
    
    fft_result = fft(data_padded_windowed)
    
    #xf = fftfreq(N_padded, T)
    #dist = freq_to_dist(xf[:N_padded // 2])
    #output = pd.DataFrame({fft_result[:N_padded // 2]}, index=dist)

    return fft_result[:N_padded // 2]
