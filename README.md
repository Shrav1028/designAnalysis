# CPU design choices evaluations

### Before running anything else sure to set up the environment and install the following if you haven't already

```bash
pip install matplotlib pandas --user

git clone https://github.com/embecosm/mibench
```

This will make sure your runtime environment is up-to date and the necessary benchmarks are installed. Once you are done with the above, follow as below:

- In sweep.py , change the GEM5 constant to point to where gem5.opt. If you haven't yet compiled gem5 on your system, make sure to do that first before anything.
- Also make sure to change outdir on line 45 in sweep.py. This is where all results will be stored. 
- Your repo structure should look like:
```
designAnalysis/
├── evaluate_script.py
├── sweep.py
├── compile.py
├── plot.py
├── run_all.sh
├── fib.c
├── mibench/
└── README.md
```

This simulation will take a while to run on most machines. It is recommended to run it within a tmux session. 
- Just run \'_tmux_\' in the terminal, and if you want to open it again just type \'_tmux attach_\'. This will make sure the script runs uninterrupted.

<br>

#### Once that is set up, run:
```
chmod +x run_all.sh
./run_all.sh
```

This will run all 30  config permutations; a baseline with everything disabled, different sizes for the Branch Target Buffer and the Return Address Stack, etc. In the end, there will be a total of 30 different configs run. 

Simulation System Info: 
- CPU - x86O3CPU 1 GHz
- L1I and L1D - __32KiB, 8 way__
- L2 (if enabled with ___--l2-cache___ when running evaluate_script.py) - __256 KiB, 8 way__
- The latencies for all these caches can be found (and changed) within evaluate_script.py
- Note : For the simulations we run here, the L2 cache is not enabled. 
- Branch Predictor - TAGE()



## Example commmand
```
gem5 evaluate_script.py --ras-entries=4096 --btb-entries=4096 --binary="<path_to/mibench/automotive/basicmath/basicmath_small>" --l2-cache
```


# Result Analysis 

