#!/bin/bash

gcc -static -O1 -o fib fib.c

cd mibench/automotive/basicmath
make
cd ../../..
echo "Running sweep..."
python3 sweep.py

echo "Parsing stats..."
python3 compile.py

echo "Plotting..."
python3 plot.py
echo "Plotting done. Check the plot folder"