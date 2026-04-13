import time
import heapq


def static_schedule(tasks, workers):
    buckets = [[] for _ in range(workers)]

    for i, task in enumerate(tasks):
        buckets[i % workers].append(task)

    processor_times = [sum(bucket) for bucket in buckets]
    return max(processor_times)


def dynamic_schedule(tasks, workers):
    heap = [0] * workers
    heapq.heapify(heap)

    for task in tasks:
        earliest = heapq.heappop(heap)
        heapq.heappush(heap, earliest + task)

    return max(heap)


def run_scheduling_experiment():
    print("\nRunning Scheduling Module...")

    tasks = [2, 5, 1, 7, 3, 4, 6, 2, 8, 1]
    for workers in [2, 4, 8]:
        static_time = static_schedule(tasks, workers)
        dynamic_time = dynamic_schedule(tasks, workers)

        print(f"Workers: {workers}")
        print(f"  Static Scheduling Total Time : {static_time}")
        print(f"  Dynamic Scheduling Total Time: {dynamic_time}")