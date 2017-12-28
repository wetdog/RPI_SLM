
# coding: utf-8

### Filtros de Octavas y tercios con pyfilterbank segun IEC 61260


import numpy as np
from pyfilterbank.octbank import FractionalOctaveFilterbank
from pyfilterbank.splweighting import a_weighting_coeffs_design
from pyfilterbank.octbank import frequencies_fractional_octaves
import pyaudio
import time
import datetime
from scipy.signal import lfilter
from sys import argv


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

if len(argv) > 1:
    C = float(argv[1])
else:
    C = -61.6

freq, foo = frequencies_fractional_octaves(-6,4,1000,1)

p = pyaudio.PyAudio()
levels = []
date = datetime.datetime.now()
filename = str(date.year) + str(date.month) + str(date.day) + '_' + str(date.hour) + str(date.minute) + str(date.second) + '.txt'
f = open(filename, 'ab')

def callback(in_data, frame_count, time_info, status):
    audio_data = np.fromstring(in_data, dtype=np.float32)
    y = lfilter(b, a, audio_data)
    y_oct, states = octave.filter(y)
    i = 0
    for e in y_oct.T:
        oct_level = db_level(e,T,C)
        print('{0:.2f} Hz -- {1:.2f} dBA'.format(freq[i],oct_level))
        i += 1
    L = db_level(y,T,C)
    f.write('{0:.2f} \n'.format(L))
    levels.append(L)
    print('{0:.2f}  dBA'.format(L))
    print('Leq {0:.2f} dBA'.format(leq(levels)))
    return (in_data, pyaudio.paContinue)

def db_level(pa, T, C):
    po = 0.000002
    level = 10*np.log10(np.nansum((pa/po)**2)/T) + C
    return level

def leq(levels):
    e_sum = (np.sum(np.power(10, np.multiply(0.1, levels))))/len(levels)
    eq_level = 10*np.log10(e_sum)
    return eq_level


stream = p.open(format=pyaudio.paFloat32,
                channels=CHANNELS,
                rate=RATE,
                frames_per_buffer=44100,
                input=True,
                output=False,
                stream_callback=callback)

stream.start_stream()

print str(stream.get_time)

while stream.is_active():
    time.sleep(0.1)


stream.stop_stream()
stream.close()
p.terminate()



