

"""This file creates a barebones system and executes 'hello', a simple Hello
World application. Adds a simple memobj between the CPU and the membus.

This config file assumes that the x86 ISA was built.
"""

# import the m5 (gem5) library created when gem5 is built
import m5
import os
# import all of the SimObjects
from m5.objects import *

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--ras-entries", type=int, default=0)  # 0 = disabled
parser.add_argument("--btb-entries", type=int, default=1)
parser.add_argument("--binary", type=str, default="hello")
parser.add_argument("--l2-cache",action="store_true", default= False)
args, unknown = parser.parse_known_args()

# create the system we are going to simulate
system = System()

# Set the clock frequency of the system (and all of its children)
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = "1GHz"
system.clk_domain.voltage_domain = VoltageDomain()

# Set up the system
system.mem_mode = "timing"  # Use timing accesses
system.mem_ranges = [AddrRange("512MiB")]  # Create an address range

# Create a simple CPU
system.cpu = X86O3CPU()

# Create a memory bus, a coherent crossbar, in this case
system.membus = SystemXBar()


#Caches
system.cpu.icache = Cache(
    size="32KiB",
    assoc=8,
    tag_latency=2,
    data_latency=2,
    response_latency=2,
    mshrs=4,
    tgts_per_mshr=20,
)
system.cpu.dcache = Cache(
    size="32KiB",
    assoc=8,
    tag_latency=2,
    data_latency=2,
    response_latency=2,
    mshrs=4,
    tgts_per_mshr=20,
)

system.cpu.icache.cpu_side = system.cpu.icache_port
system.cpu.dcache.cpu_side = system.cpu.dcache_port


# Enable / Disable l2 cache
if args.l2_cache:
    system.l2bus = L2XBar()
    system.l2cache = Cache(
        size="256KiB",
        assoc=8,
        tag_latency=20,
        data_latency=20,
        response_latency=20,
        mshrs=20,
        tgts_per_mshr=12,
    )
    system.cpu.icache.mem_side = system.l2bus.cpu_side_ports
    system.cpu.dcache.mem_side = system.l2bus.cpu_side_ports
    system.l2cache.cpu_side = system.l2bus.mem_side_ports 
    system.l2cache.mem_side = system.membus.cpu_side_ports 
else:
    system.cpu.icache.mem_side = system.membus.cpu_side_ports
    system.cpu.dcache.mem_side = system.membus.cpu_side_ports



#Branch Predictor
system.cpu.branchPred = TAGE()
if args.ras_entries == 0:
    system.cpu.branchPred.ras = NULL
else:
    system.cpu.branchPred.ras = ReturnAddrStack(numEntries=args.ras_entries)
system.cpu.branchPred.btb = SimpleBTB(numEntries=args.btb_entries)

# create the interrupt controller for the CPU and connect to the membus
system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

# Create a DDR3 memory controller and connect it to the membus
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

# Connect the system up to the membus
system.system_port = system.membus.cpu_side_ports

# Create a process for a simple "Hello World" application
process = Process()
# Set the command

binpath = args.binary
# cmd is a list which begins with the executable (like argv)
process.cmd = [binpath]
# Set the cpu to use the process as its workload and create thread contexts
system.cpu.workload = process
system.cpu.createThreads()

system.workload = SEWorkload.init_compatible(binpath)

# set up the root SimObject and start the simulation
root = Root(full_system=False, system=system)
# instantiate all of the objects we've created above
m5.instantiate()

print(f"Beginning simulation!")
exit_event = m5.simulate()
print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")
