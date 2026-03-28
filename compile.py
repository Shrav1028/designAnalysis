"""
Parse gem5 stats.txt files from ablation study results.
Run from the directory containing your results/ folder.

Usage: python3 parse_results.py
"""

import os
import re
import csv
import sys


STATS_TO_EXTRACT = {
    "ipc":              r"system\.cpu\.ipc\s+([\d.]+)",
    "bp_lookups":       r"system\.cpu\.branchPred\.lookups_0::total\s+([\d]+)",
    "bp_squashes":      r"system\.cpu\.branchPred\.squashes_0::total\s+([\d]+)",
    "bp_corrected":     r"system\.cpu\.branchPred\.corrected_0::total\s+([\d]+)",
    "bp_cond_incorrect":r"system\.cpu\.branchPred\.condIncorrect_0\s+([\d]+)",
    "ras_used":         r"system\.cpu\.branchPred\.usedRAS_0\s+([\d]+)",
    "ras_incorrect":    r"system\.cpu\.branchPred\.RASIncorrect_0\s+([\d]+)",
    "btb_lookups":      r"system\.cpu\.branchPred\.BTBLookups_0\s+([\d]+)",
    "btb_mispredicted": r"system\.cpu\.branchPred\.BTBMispredicted_0\s+([\d]+)",
    "committed_insts":  r"system\.cpu\.committedInsts_0\s+([\d]+)",
    "cycles":           r"system\.cpu\.numCycles\s+([\d]+)",
    "l2_hits":          r"system\.l2cache\.hits\s+([\d]+)",
    "l2_misses":        r"system\.l2cache\.misses\s+([\d]+)",
}


def parse_stats(stats_path):
    try:
        with open(stats_path, "r") as f:
            content = f.read()
    except FileNotFoundError:
        return None

    result = {}
    for key, pattern in STATS_TO_EXTRACT.items():
        match = re.search(pattern, content)
        result[key] = float(match.group(1)) if match else None

    # Derived stats
    if result["bp_lookups"] and result["bp_corrected"] and result["bp_lookups"] > 0:
        result["mispredict_rate"] = result["bp_corrected"] / result["bp_lookups"]
    else:
        result["mispredict_rate"] = None

    if result["l2_hits"] and result["l2_misses"]:
        total = result["l2_hits"] + result["l2_misses"]
        result["l2_miss_rate"] = result["l2_misses"] / total if total > 0 else None
    else:
        result["l2_miss_rate"] = None

    return result


def find_results(results_dir="results"):
    rows = []

    if not os.path.exists(results_dir):
        print(f"Error: '{results_dir}' directory not found. Run from the directory containing results/")
        sys.exit(1)

    for binary in sorted(os.listdir(results_dir)):
        binary_path = os.path.join(results_dir, binary)
        if not os.path.isdir(binary_path):
            continue

        for config in sorted(os.listdir(binary_path)):
            config_path = os.path.join(binary_path, config)
            stats_file  = os.path.join(config_path, "stats.txt")

            if not os.path.exists(stats_file):
                print(f"  Missing: {stats_file}")
                continue

            stats = parse_stats(stats_file)
            if stats is None:
                print(f"  Could not parse: {stats_file}")
                continue

            row = {"binary": binary, "config": config}
            row.update(stats)
            rows.append(row)
            print(f"  Parsed: {binary}/{config}  IPC={stats['ipc']}  mispredict_rate={stats['mispredict_rate']:.4f}"
                  if stats['ipc'] and stats['mispredict_rate'] else
                  f"  Parsed: {binary}/{config}  (some stats missing)")

    return rows


def write_csv(rows, out_path="results_summary.csv"):
    if not rows:
        print("No data to write.")
        return

    fieldnames = ["binary", "config"] + list(STATS_TO_EXTRACT.keys()) + ["mispredict_rate", "l2_miss_rate"]
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nWrote {len(rows)} rows to {out_path}")


def print_table(rows):
    if not rows:
        return

    print(f"\n{'Binary':<12} {'Config':<16} {'IPC':>8} {'Mispredict%':>12} {'Squashes':>12} {'Cycles':>14}")
    print("-" * 78)

    for r in rows:
        ipc      = f"{r['ipc']:.4f}"                    if r["ipc"]              else "N/A"
        mrate    = f"{r['mispredict_rate']*100:.2f}%"   if r["mispredict_rate"]  else "N/A"
        squashes = f"{int(r['bp_squashes'])}"            if r["bp_squashes"]      else "N/A"
        cycles   = f"{int(r['cycles'])}"                 if r["cycles"]           else "N/A"

        print(f"{r['binary']:<12} {r['config']:<16} {ipc:>8} {mrate:>12} {squashes:>12} {cycles:>14}")


if __name__ == "__main__":
    print("Parsing results...\n")
    rows = find_results("results")
    print_table(rows)
    write_csv(rows)