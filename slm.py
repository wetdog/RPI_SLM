
# coding: utf-8

### Filtros de Octavas y tercios con pyfilterbank segun IEC 61260

import argparse
import numpy as np
from pyfilterbank.octbank import FractionalOctaveFilterbank
from pyfilterbank.splweighting import a_weighting_coeffs_design
from pyfilterbank.octbank import frequencies_fractional_octaves
import pyaudio
import time
import datetime
from scipy.signal import lfilter
from sys import argv

# Argumentos del script

parser = argparse.ArgumentParser(description='Basic SLM with linear weighting, default sampling rate is 44100')
parser.add_argument("-c", "--constant", help="Calibration constant", type=float)
parser.add_argument("-t", "--time", help="type -t F for fast or -t S for Slow", type=str)
args = parser.parse_args()

if  args.constant:
    C = args.constant
else:
    print "Calibration constant set to default -54.2"
    C = -54.2

if args.time == 'F':
    T = 0.125
    frames = 5513
elif args.time == 'S':
    T = 1
    frames = 44100
else:
    print "Time weigthing set to Slow"
    T = 1
    frames = 44100

# parametros Stream de audio
CHANNELS = 1
fs = 44100
RATE = fs


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

freq, foo = frequencies_fractional_octaves(-6,4,1000,1)

p = pyaudio.PyAudio()
levels = []
date = datetime.datetime.now()
filename = str(date.year) + str(date.month) + str(date.day) + '_' + str(date.hour) + str(date.minute) + str(date.second) + '.txt'
f = open(filename, 'ab')

def db_level(pa, T, C):
    po = 0.000002
    level = 10*np.log10(np.nansum((pa/po)**2)/T) + C
    return level

def leq(levels):
    e_sum = (np.sum(np.power(10, np.multiply(0.1, levels))))/len(levels)
    eq_level = 10*np.log10(e_sum)
    return eq_level

def callback(in_data, frame_count, time_info, status):
    audio_data = np.fromstring(in_data, dtype=np.float32)
    y = lfilter(b, a, audio_data)
    y_oct, states = octave.filter(y)
    i = 0
    for e in y_oct.T:
        oct_level = db_level(e,T,C)
        print('{0:.2f} Hz -- {1:.2f} dBA'.format(freq[i],oct_level))
        i += 1
    La = db_level(y,T,C)
    L = db_level(audio_data,T,C)
    f.write('{0:.2f} \n'.format(La))
    levels.append(La)
    print('{0:.2f}  dBA'.format(La))
    print('{0:.2f}  dBZ'.format(L))
    print('Leq {0:.2f} dBA'.format(leq(levels)))
    return (in_data, pyaudio.paContinue)

stream = p.open(format=pyaudio.paFloat32,
                channels=CHANNELS,
                rate=RATE,
                frames_per_buffer=frames,
                input=True,
                output=False,
                stream_callback=callback)

stream.start_stream()

record = True


while record:
    time.sleep(0.1)


stream.stop_stream()
stream.close()
p.terminate()



