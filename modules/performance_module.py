import os
import math
import matplotlib.pyplot as plt

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
        print("No parallelism results found to plot.")
        return

    thread_results = [r for r in parallelism_results if r["mode"] == "threading"]
    process_results = [r for r in parallelism_results if r["mode"] == "multiprocessing"]

    if not thread_results and not process_results:
        print("No threading or multiprocessing results found.")
        return

    workers = sorted(set(r["workers"] for r in parallelism_results if r["workers"] > 0))
    amdahl = amdahl_prediction(workers)

    os.makedirs("outputs/graphs", exist_ok=True)

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
    plt.savefig("outputs/graphs/parallelism_execution_time.png")
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
    plt.savefig("outputs/graphs/parallelism_speedup.png")
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
    plt.savefig("outputs/graphs/parallelism_efficiency.png")
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
    plt.savefig("outputs/graphs/parallelism_memory.png")
    plt.close()

    print("Graphs saved in outputs/graphs/")


def print_results():
    if not RESULTS:
        print("No results recorded.")
        return

    print("\nRecorded Results")
    print("-" * 80)
    for r in RESULTS:
        print(
            f"Module: {r['module']}, Mode: {r['mode']}, Workers: {r['workers']}, "
            f"Time: {r['execution_time']:.4f}s, Speedup: {r['speedup']:.4f}, "
            f"Efficiency: {r['efficiency']:.4f}, Memory: {r['memory_mb']:.4f} MB"
        )