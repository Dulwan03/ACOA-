import os
import math
import matplotlib.pyplot as plt
import sys

# Add parent directory to path to import utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import PROJECT_DIR

RESULTS = []


def record_result(module_name, mode, workers, execution_time, speedup, efficiency, memory_mb):
    RESULTS.append({
        "module": module_name,
        "mode": mode,
        "workers": workers,
        "execution_time": execution_time,
        "speedup": speedup,
        "efficiency": efficiency,
        "memory_mb": memory_mb
    })


def amdahl_prediction(workers_list, parallel_fraction=0.95):
    predictions = []
    for n in workers_list:
        speedup = 1 / ((1 - parallel_fraction) + (parallel_fraction / n))
        predictions.append(speedup)
    return predictions


def plot_parallelism_results():
    parallelism_results = [r for r in RESULTS if r["module"] == "Parallelism"]

    if not parallelism_results:
        print("No parallelism results found to plot.", flush=True)
        return

    thread_results = [r for r in parallelism_results if r["mode"] == "threading"]
    process_results = [r for r in parallelism_results if r["mode"] == "multiprocessing"]

    if not thread_results and not process_results:
        print("No threading or multiprocessing results found.", flush=True)
        return

    workers = sorted(set(r["workers"] for r in parallelism_results if r["workers"] > 0))
    amdahl = amdahl_prediction(workers)

    os.makedirs(os.path.join(PROJECT_DIR, "outputs/graphs"), exist_ok=True)

    if thread_results:
        tw = [r["workers"] for r in thread_results]
        tt = [r["execution_time"] for r in thread_results]
        ts = [r["speedup"] for r in thread_results]
        te = [r["efficiency"] for r in thread_results]
    else:
        tw, tt, ts, te = [], [], [], []

    if process_results:
        pw = [r["workers"] for r in process_results]
        pt = [r["execution_time"] for r in process_results]
        ps = [r["speedup"] for r in process_results]
        pe = [r["efficiency"] for r in process_results]
    else:
        pw, pt, ps, pe = [], [], [], []

    plt.figure(figsize=(8, 5))
    if tw:
        plt.plot(tw, tt, marker="o", label="Threading")
    if pw:
        plt.plot(pw, pt, marker="o", label="Multiprocessing")
    plt.xlabel("Number of Workers")
    plt.ylabel("Execution Time (seconds)")
    plt.title("Execution Time vs Number of Workers")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(PROJECT_DIR, "outputs/graphs/parallelism_execution_time.png"))
    plt.close()

    plt.figure(figsize=(8, 5))
    if tw:
        plt.plot(tw, ts, marker="o", label="Threading")
    if pw:
        plt.plot(pw, ps, marker="o", label="Multiprocessing")
    plt.plot(workers, amdahl, marker="x", linestyle="--", label="Amdahl Prediction")
    plt.xlabel("Number of Workers")
    plt.ylabel("Speedup")
    plt.title("Speedup vs Number of Workers")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(PROJECT_DIR, "outputs/graphs/parallelism_speedup.png"))
    plt.close()

    plt.figure(figsize=(8, 5))
    if tw:
        plt.plot(tw, te, marker="o", label="Threading")
    if pw:
        plt.plot(pw, pe, marker="o", label="Multiprocessing")
    plt.xlabel("Number of Workers")
    plt.ylabel("Efficiency")
    plt.title("Efficiency vs Number of Workers")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(PROJECT_DIR, "outputs/graphs/parallelism_efficiency.png"))
    plt.close()

    memory_results_thread = [r["memory_mb"] for r in thread_results]
    memory_results_proc = [r["memory_mb"] for r in process_results]

    plt.figure(figsize=(8, 5))
    if tw:
        plt.plot(tw, memory_results_thread, marker="o", label="Threading")
    if pw:
        plt.plot(pw, memory_results_proc, marker="o", label="Multiprocessing")
    plt.xlabel("Number of Workers")
    plt.ylabel("Memory Usage Increase (MB)")
    plt.title("Memory Usage vs Number of Workers")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(PROJECT_DIR, "outputs/graphs/parallelism_memory.png"))
    plt.close()

    print("Graphs saved in outputs/graphs/", flush=True)


def print_results():
    if not RESULTS:
        print("No results recorded.", flush=True)
        return

    print("\n", flush=True)
    print("=" * 100, flush=True)
    print("PERFORMANCE ANALYSIS RESULTS".center(100), flush=True)
    print("=" * 100, flush=True)

    # Group results by module
    modules = {}
    for r in RESULTS:
        module = r['module']
        if module not in modules:
            modules[module] = []
        modules[module].append(r)

    # Print results for each module
    for module_name in sorted(modules.keys()):
        module_results = modules[module_name]
        
        print(f"\n{'█' * 100}", flush=True)
        print(f"  MODULE: {module_name}", flush=True)
        print(f"{'█' * 100}\n", flush=True)
        
        # Table header
        print(f"{'Mode':<20} {'Workers':<10} {'Time (s)':<15} {'Speedup':<12} {'Efficiency':<12} {'Memory (MB)':<15}", flush=True)
        print("-" * 100, flush=True)
        
        # Table rows
        for r in module_results:
            mode = str(r['mode'])[:20]
            workers = str(r['workers'])
            exec_time = f"{r['execution_time']:.4f}"
            speedup = f"{r['speedup']:.4f}"
            efficiency = f"{r['efficiency']:.4f}"
            memory = f"{r['memory_mb']:.2f}"
            
            print(f"{mode:<20} {workers:<10} {exec_time:<15} {speedup:<12} {efficiency:<12} {memory:<15}", flush=True)
        
        print("", flush=True)

    print("=" * 100, flush=True)
    print(f"Total Results Recorded: {len(RESULTS)}".center(100), flush=True)
    print("=" * 100 + "\n", flush=True)