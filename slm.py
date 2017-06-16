
# coding: utf-8

# ### Filtros de Octavas y tercios con pyfilterbank segun IEC 61260


import numpy as np
from pyfilterbank.octbank import FractionalOctaveFilterbank
from pyfilterbank.splweighting import a_weighting_coeffs_design
from pyfilterbank.octbank import frequencies_fractional_octaves
import pyaudio
import time
from scipy.signal import lfilter

fs = 44100
# Construir banco de filtros de tercio y octava
third_oct = FractionalOctaveFilterbank(
    sample_rate=fs,
    order=4,
    nth_oct=3.0,
    norm_freq=1000.0,
    start_band=-19,
    end_band=13,
    edge_correction_percent=0.01,
    filterfun='cffi')

octave = FractionalOctaveFilterbank(
    sample_rate=fs,
    order=4,
    nth_oct=1.0,
    norm_freq=1000.0,
    start_band=-6,
    end_band=4,
    edge_correction_percent=0.01,
    filterfun='cffi')

# Filtro tipo A
b, a = a_weighting_coeffs_design(fs)

# Stream de audio
CHANNELS = 1
RATE = 44100
po = 0.000002
T = 1
C = -66.8

freq, foo = frequencies_fractional_octaves(-6,4,1000,1)

p = pyaudio.PyAudio()


def callback(in_data, frame_count, time_info, status):
    global full_data
    audio_data = np.fromstring(in_data, dtype=np.float32)
    y = lfilter(b, a, audio_data)
    y_oct, states = octave.filter(y)
    i = 0
    for e in y_oct.T:
        print str(freq[i]) + " Hz -- " + str(10*np.log10(np.nansum((e/po)**2)/T)+C)+" dBA"
        i += 1
        # L = 20 * np.log10(np.sqrt(np.sum(audio_data**2))/po)
    print str(10*np.log10(np.nansum((y/po)**2)/T)+C) + " dBA"
    return (in_data, pyaudio.paContinue)

stream = p.open(format=pyaudio.paFloat32,
                channels=CHANNELS,
                rate=RATE,
                frames_per_buffer=44100,
                input=True,
                output=False,
                stream_callback=callback)

stream.start_stream()

while stream.is_active():
    time.sleep(0.1)

stream.stop_stream()
stream.close()
p.terminate()
