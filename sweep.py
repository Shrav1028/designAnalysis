import subprocess
import os

BASE = os.path.dirname(os.path.abspath(__file__))

GEM5   = "/cshome/ssnayak/CMPUT429/429-resources/gem5/build/ALL/gem5.opt"
SCRIPT = os.path.join(BASE, "evaluate_script.py")

BINARIES = {
    "basicmath": os.path.join(BASE, "mibench/automotive/basicmath/basicmath_small"),
    "fib":       os.path.join(BASE, "fib"),
}

# Core ablation configs: (name, ras_entries, btb_entries)
CORE_CONFIGS = [
    ("baseline", 0,  1),
    ("ras_only",  16, 1),
    ("btb_only",  0,  4096),
    ("both",      16, 4096),
]

# BTB sweep: RAS on, vary BTB size
BTB_SWEEP = [
    ("btb_1",    16, 1),
    ("btb_16",   16, 16),
    ("btb_64",   16, 64),
    ("btb_256",  16, 256),
    ("btb_1024", 16, 1024),
    ("btb_4096", 16, 4096),
]

# RAS sweep: BTB full, vary RAS size
RAS_SWEEP = [
    ("ras_0",  0,  4096),
    ("ras_4",  4,  4096),
    ("ras_8",  8,  4096),
    ("ras_16", 16, 4096),
    ("ras_32", 32, 4096),
]

ALL_CONFIGS = CORE_CONFIGS + BTB_SWEEP + RAS_SWEEP


def run(config_name, ras_entries, btb_entries, binary_name, binary_path, l2=False):
    outdir = os.path.join(BASE, "results/"+str(binary_name)+"/"+str(config_name))
    os.makedirs(outdir, exist_ok=True)

    if os.path.exists(f"{outdir}/stats.txt"):
        print(f"Skipping {binary_name}/{config_name} (already done)")
        return

    cmd = [
        GEM5,
        f"--outdir={outdir}",
        SCRIPT,
        "--ras-entries", str(ras_entries),
        "--btb-entries", str(btb_entries),
        "--binary", binary_path,
    ]
    if l2:
        cmd.append("--l2-cache")

    print(f"Running {binary_name}/{config_name} "
          f"(ras={ras_entries}, btb={btb_entries}, l2={l2})...")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"  FAILED: {result.stderr[-300:]}")
    else:
        print(f"  Done. Stats at {outdir}/stats.txt")


if __name__ == "__main__":
    total = len(ALL_CONFIGS) * len(BINARIES)
    done  = 0

    for binary_name, binary_path in BINARIES.items():
        for config_name, ras_entries, btb_entries in ALL_CONFIGS:
            run(config_name, ras_entries, btb_entries, binary_name, binary_path)
            done += 1
            print(f"Progress: {done}/{total}\n")

    # L2 cache runs
    run("with_l2_cache", 4096, 4096, "basicmath", BINARIES["basicmath"], l2=True)
    run("with_l2_cache", 4096, 4096, "fib",       BINARIES["fib"],       l2=True)

    print("All runs complete.")