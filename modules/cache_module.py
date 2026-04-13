import threading
import time


def increment_shared(shared, index, loops):
    for _ in range(loops):
        shared[index] += 1


def increment_single(shared_dict, loops, lock):
    for _ in range(loops):
        with lock:
            shared_dict["value"] += 1


def run_cache_experiment():
    print("\nRunning Cache Module...")

    loops = 300000

    shared_false = [0, 0]
    start = time.perf_counter()
    t1 = threading.Thread(target=increment_shared, args=(shared_false, 0, loops))
    t2 = threading.Thread(target=increment_shared, args=(shared_false, 1, loops))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    false_time = time.perf_counter() - start

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

    padded = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    start = time.perf_counter()
    t5 = threading.Thread(target=increment_shared, args=(padded, 0, loops))
    t6 = threading.Thread(target=increment_shared, args=(padded, 64, loops))
    t5.start()
    t6.start()
    t5.join()
    t6.join()
    padded_time = time.perf_counter() - start

    print(f"False Sharing Time : {false_time:.4f}s")
    print(f"True Sharing Time  : {true_time:.4f}s")
    print(f"Padded Baseline Time: {padded_time:.4f}s")