import threading
import time
from modules.performance_module import record_result


def increment_shared(shared, index, loops):
    for _ in range(loops):
        shared[index] += 1


def increment_single(shared_dict, loops, lock):
    for _ in range(loops):
        with lock:
            shared_dict["value"] += 1


def run_cache_experiment(loops=None):
    print("\nRunning Cache Module...")
    
    # Allow configurable loops for web UI testing (default to full for CLI)
    if loops is None:
        import os
        # Use faster loops for web UI, full loops for CLI
        loops = int(os.environ.get('CACHE_LOOPS', 100000))

    shared_false = [0, 0]
    start = time.perf_counter()
    t1 = threading.Thread(target=increment_shared, args=(shared_false, 0, loops))
    t2 = threading.Thread(target=increment_shared, args=(shared_false, 1, loops))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    false_time = time.perf_counter() - start
    print(f"  False Sharing completed (loops={loops})", flush=True)

    shared_true = {"value": 0}
    lock = threading.Lock()
    start = time.perf_counter()
    t3 = threading.Thread(target=increment_single, args=(shared_true, loops, lock))
    t4 = threading.Thread(target=increment_single, args=(shared_true, loops, lock))
    t3.start()
    t4.start()
    t3.join()
    t4.join()
    true_time = time.perf_counter() - start
    print(f"  True Sharing completed (loops={loops})", flush=True)

    padded = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    start = time.perf_counter()
    t5 = threading.Thread(target=increment_shared, args=(padded, 0, loops))
    t6 = threading.Thread(target=increment_shared, args=(padded, 64, loops))
    t5.start()
    t6.start()
    t5.join()
    t6.join()
    padded_time = time.perf_counter() - start
    print(f"  Padded Baseline completed (loops={loops})", flush=True)

    print(f"False Sharing Time : {false_time:.4f}s", flush=True)
    print(f"True Sharing Time  : {true_time:.4f}s", flush=True)
    print(f"Padded Baseline Time: {padded_time:.4f}s", flush=True)

    record_result(
        module_name="Cache",
        mode="false_sharing",
        workers=2,
        execution_time=false_time,
        speedup=1.0,
        efficiency=1.0,
        memory_mb=0.0
    )

    record_result(
        module_name="Cache",
        mode="true_sharing",
        workers=2,
        execution_time=true_time,
        speedup=1.0,
        efficiency=1.0,
        memory_mb=0.0
    )

    record_result(
        module_name="Cache",
        mode="padded",
        workers=2,
        execution_time=padded_time,
        speedup=1.0,
        efficiency=1.0,
        memory_mb=0.0
    )