# RPI_SLM

## Basic sound level meter in raspberry using pyfilterbank library

As we use pyfilterbank library you need first to install it.

1. Clone repository 

`git clone https://github.com/SiggiGue/pyfilterbank.git`

2. If you have numpy => 1.13.3 in your raspberry as being pointed out by @spors you
need to replace a line in butterworth.py

Erase
- L2 = L / 2.0

Replace with
+ L2 = L// 2

3. Compile C functions

`gcc -c -std=c99 -O3 sosfilt.c
gcc -shared -o sosfilt.so sosfilt.o`

4. Build

`python setup.py build`

5. Install

`python setup.py install`

## Basic Usage

with ` python slm.py` will run with a default calibration constant and a slow weighting.

You can specify a calibration constant and F or S time weighting.

`python slm.py -c <calibration constant> -t <F or S>`
