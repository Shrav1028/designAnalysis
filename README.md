# CPU design choices evaluations

### Before running anything else sure to set up the environment and install the following if you haven't already

```bash
pip install matplotlib pandas --user

git clone https://github.com/embecosm/mibench
```

This will make sure your runtime environment is up-to date and the necessary benchmarks are installed. Once you are done with the above, follow as below:

- In sweep.py , change the `GEM5` constant to point to where gem5.opt. If you haven't yet compiled gem5 on your system, make sure to do that first before anything.
- Also make sure to change `outdir` on line 45 in `sweep.py`. This is where all results will be stored. 
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
- Just run `tmux` in the terminal, and if you want to open it again just type `tmux attach`. This will make sure the script runs uninterrupted.

<br>

#### Once that is set up, run:
```
chmod +x run_all.sh
./run_all.sh
```

This will run all 30  config permutations; a baseline with everything disabled, different sizes for the Branch Target Buffer and the Return Address Stack, etc. In the end, there will be a total of 30 different configs run. 

Simulation System Info: 
- CPU - `x86O3CPU 1 GHz`. This is the most up-to date out-of-order CPU I could test at the time on gem5.
- L1I and L1D - `32KiB, 8 way`
- L2 (if enabled with `--l2-cache` when running evaluate_script.py) - `256 KiB, 8 way`
- The latencies for all these caches can be found (and changed) within evaluate_script.py
- Note : For the simulations we run here, the L2 cache is not enabled. 
- Branch Predictor - TAGE()



## Example commmand
```
gem5 evaluate_script.py --ras-entries=4096 --btb-entries=4096 --binary="<path_to/mibench/automotive/basicmath/basicmath_small>" --l2-cache
```

# Result Analysis

### We see the below trends when we run the simulations for the `basicmath` and `fib` benchmarks.

## Core Sweeps (RAS and BTB)

Enabling both the RAS and BTB together show the largest IPC gains across both benchmarks.
For `basicmath`, IPC improves from 0.63 (baseline) to 1.50 (both enabled), a 2.4x speedup.
For `fib`, the improvement is even more dramatic, going from 0.46 to 1.93, a 4.2x speedup.

The results show that neither component alone is sufficient. With only RAS enabled, `fib` sees
almost no improvement (0.46 to 0.94) since it relies heavily on the BTB to locate branch targets.
With only BTB enabled, `basicmath` improves to 1.11 IPC but plateaus without RAS to handle returns.

## BTB Size Sweep

For `basicmath`, IPC scales steadily with BTB size, from 0.75 at 1 entry up to 1.50 at 4096 entries.
This indicates a large and varied set of branch targets that benefit from a bigger BTB.

For `fib`, IPC jumps almost immediately to its peak of 1.93 with just 16 BTB entries and barely
changes beyond that. This makes sense since fibonacci has a very small and repetitive branch
target set that fits in even a tiny BTB.

## RAS Size Sweep

`fib` is highly sensitive to RAS size due to its deeply recursive call structure. IPC climbs
from 0.64 with no RAS, to 1.64 with 4 entries, 1.87 with 8 entries, and saturates at 1.93
with 16 entries. This reflects the recursion depth of `fib(35)` -- once the RAS is deep
enough to cover the call stack, additional entries add no benefit.

`basicmath` is less sensitive to RAS size, reaching near-peak IPC of 1.48 with just 4 entries
and fully saturating at 8. Its call depth is shallower, so a small RAS is sufficient.

## L2 Cache

Adding an L2 cache produces no measurable IPC change for either benchmark. Both `basicmath`
and `fib` have small enough working sets to fit entirely within the 32KiB L1 cache, meaning
L1 miss rates are near zero and L2 is never meaningfully utilized. L2 cache benefits would
only be visible with memory-intensive workloads whose data exceeds the L1 capacity.

## Key Takeaway

The results highlight that the impact of microarchitectural features is highly workload-dependent.
A call-heavy recursive workload like `fib` is dominated by RAS and BTB correctness, while a
branch-heavy iterative workload like `basicmath` benefits more gradually from BTB capacity.
Disabling either structure hurts performance significantly, but the marginal contribution of
each depends on the execution profile of the workload.