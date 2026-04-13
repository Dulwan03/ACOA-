import threading
import time


def bus_worker(lock, transfer_time, controlled=False):
    if controlled:
        time.sleep(0.01)

    with lock:
        time.sleep(transfer_time)


def simulate_bus_access(num_processors, controlled=False):
    lock = threading.Lock()
    threads = []

    start = time.perf_counter()

    for _ in range(num_processors):
        t = threading.Thread(target=bus_worker, args=(lock, 0.05, controlled))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    end = time.perf_counter()
    return end - start


def run_bus_experiment():
    print("\nRunning Bus Module...")

    for processors in [1, 2, 4, 8]:
        normal = simulate_bus_access(processors, controlled=False)
        controlled = simulate_bus_access(processors, controlled=True)

        print(f"Processors: {processors}")
        print(f"  Contended Bus Time : {normal:.4f}s")
        print(f"  Controlled Bus Time: {controlled:.4f}s")