import os
import time
import psutil


def ensure_directories():
    os.makedirs("outputs/images", exist_ok=True)
    os.makedirs("outputs/graphs", exist_ok=True)


def calculate_speedup(sequential_time: float, parallel_time: float) -> float:
    if parallel_time == 0:
        return 0.0
    return sequential_time / parallel_time


def calculate_efficiency(speedup: float, workers: int) -> float:
    if workers == 0:
        return 0.0
    return speedup / workers


def get_memory_usage_mb() -> float:
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)


def timed_run(func, *args, **kwargs):
    start_memory = get_memory_usage_mb()
    start_time = time.perf_counter()

    result = func(*args, **kwargs)

    end_time = time.perf_counter()
    end_memory = get_memory_usage_mb()

    elapsed = end_time - start_time
    memory_used = max(0.0, end_memory - start_memory)

    return result, elapsed, memory_used