import threading
import time
import os
from modules.performance_module import record_result


def bus_worker(lock, transfer_time, controlled=False):
    if controlled:
        time.sleep(0.01)

    with lock:
        time.sleep(transfer_time)


def simulate_bus_access(num_processors, controlled=False, transfer_time=0.05):
    lock = threading.Lock()
    threads = []

    start = time.perf_counter()

    for _ in range(num_processors):
        t = threading.Thread(target=bus_worker, args=(lock, transfer_time, controlled))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    end = time.perf_counter()
    return end - start


def run_bus_experiment():
    print("\nRunning Bus Module...")
    
    # Allow faster execution for web UI
    transfer_time = float(os.environ.get('BUS_TRANSFER_TIME', 0.05))

    for processors in [1, 2, 4, 8]:
        print(f"Testing with {processors} processors (transfer_time={transfer_time}s)...", flush=True)
        normal = simulate_bus_access(processors, controlled=False, transfer_time=transfer_time)
        controlled = simulate_bus_access(processors, controlled=True, transfer_time=transfer_time)

        print(f"Processors: {processors}", flush=True)
        print(f"  Contended Bus Time : {normal:.4f}s", flush=True)
        print(f"  Controlled Bus Time: {controlled:.4f}s", flush=True)

        record_result(
            module_name="Bus",
            mode="contended",
            workers=processors,
            execution_time=normal,
            speedup=1.0,
            efficiency=1.0,
            memory_mb=0.0
        )

        record_result(
            module_name="Bus",
            mode="controlled",
            workers=processors,
            execution_time=controlled,
            speedup=1.0,
            efficiency=1.0,
            memory_mb=0.0
        )