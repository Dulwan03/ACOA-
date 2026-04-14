from PIL import Image
import numpy as np
import threading
import multiprocessing
import os
import sys
from utils import timed_run, calculate_speedup, calculate_efficiency, ensure_directories, PROJECT_DIR
from modules.performance_module import record_result

# Set multiprocessing start method for Windows compatibility
if sys.platform == 'win32' and multiprocessing.get_start_method(allow_none=True) != 'spawn':
    try:
        multiprocessing.set_start_method('spawn', force=True)
    except RuntimeError:
        pass  # Already set


def load_image(path: str):
    image = Image.open(path).convert("RGB")
    return np.array(image)


def save_image(array: np.ndarray, path: str):
    image = Image.fromarray(array.astype(np.uint8))
    image.save(path)


def grayscale_chunk(chunk: np.ndarray) -> np.ndarray:
    gray = np.mean(chunk, axis=2).astype(np.uint8)
    gray_rgb = np.stack((gray, gray, gray), axis=2)
    return gray_rgb


def grayscale_sequential(image: np.ndarray) -> np.ndarray:
    return grayscale_chunk(image)


def grayscale_thread_worker(image, start_row, end_row, result_list, index):
    chunk = image[start_row:end_row]
    result_list[index] = grayscale_chunk(chunk)


def grayscale_threaded(image: np.ndarray, num_threads: int) -> np.ndarray:
    height = image.shape[0]
    chunk_size = height // num_threads

    threads = []
    results = [None] * num_threads

    for i in range(num_threads):
        start_row = i * chunk_size
        end_row = height if i == num_threads - 1 else (i + 1) * chunk_size

        t = threading.Thread(
            target=grayscale_thread_worker,
            args=(image, start_row, end_row, results, i)
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    return np.vstack(results)


def grayscale_process_chunk(chunk: np.ndarray) -> np.ndarray:
    """Process a chunk of image data - must be picklable for multiprocessing"""
    return grayscale_chunk(chunk)


def grayscale_multiprocessing(image: np.ndarray, num_processes: int) -> np.ndarray:
    """
    Process image using multiprocessing with Windows compatibility.
    Falls back to threading if multiprocessing fails.
    """
    height = image.shape[0]
    chunk_size = height // num_processes
    chunks = []

    for i in range(num_processes):
        start_row = i * chunk_size
        end_row = height if i == num_processes - 1 else (i + 1) * chunk_size
        chunks.append(image[start_row:end_row])

    try:
        # Try multiprocessing with Windows compatibility settings
        ctx = multiprocessing.get_context('spawn')
        with ctx.Pool(processes=num_processes, maxtasksperchild=1) as pool:
            # Use map_async to handle timeout properly
            async_result = pool.map_async(grayscale_process_chunk, chunks)
            # Get results with 30 second timeout
            results = async_result.get(timeout=30)
        return np.vstack(results)
    except (TimeoutError, KeyboardInterrupt, BrokenPipeError, OSError, Exception) as e:
        # Fallback to threading if multiprocessing fails
        print(f"    [Note: Multiprocessing encountered issue ({type(e).__name__}), using threading instead]")
        return grayscale_threaded(image, num_processes)


def run_parallelism_experiment(input_image_path=None):
    """
    Run the parallelism experiment.
    If input_image_path is provided, use that image; otherwise use default data/input.jpg
    """
    ensure_directories()

    # Use provided image path or default
    if input_image_path is None:
        input_path = os.path.join(PROJECT_DIR, "data/input.jpg")
    else:
        input_path = input_image_path
    
    # Verify the image exists
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input image not found: {input_path}")
    
    output_seq = os.path.join(PROJECT_DIR, "outputs/images/output_sequential.jpg")

    print("\nRunning Parallelism Module...")

    image = load_image(input_path)

    seq_result, seq_time, seq_memory = timed_run(grayscale_sequential, image)
    save_image(seq_result, output_seq)

    record_result(
        module_name="Parallelism",
        mode="sequential",
        workers=1,
        execution_time=seq_time,
        speedup=1.0,
        efficiency=1.0,
        memory_mb=seq_memory
    )

    print(f"Sequential Time: {seq_time:.4f}s")

    for workers in [2, 6, 4, 8]:
        thread_result, thread_time, thread_memory = timed_run(grayscale_threaded, image, workers)
        save_image(thread_result, os.path.join(PROJECT_DIR, f"outputs/images/output_thread_{workers}.jpg"))

        thread_speedup = calculate_speedup(seq_time, thread_time)
        thread_eff = calculate_efficiency(thread_speedup, workers)

        record_result(
            module_name="Parallelism",
            mode="threading",
            workers=workers,
            execution_time=thread_time,
            speedup=thread_speedup,
            efficiency=thread_eff,
            memory_mb=thread_memory
        )

        print(
            f"Threading ({workers}): Time={thread_time:.4f}s, "
            f"Speedup={thread_speedup:.4f}, Efficiency={thread_eff:.4f}"
        )

    for workers in [2, 4, 8]:
        proc_result, proc_time, proc_memory = timed_run(grayscale_multiprocessing, image, workers)
        save_image(proc_result, os.path.join(PROJECT_DIR, f"outputs/images/output_process_{workers}.jpg"))

        proc_speedup = calculate_speedup(seq_time, proc_time)
        proc_eff = calculate_efficiency(proc_speedup, workers)

        record_result(
            module_name="Parallelism",
            mode="multiprocessing",
            workers=workers,
            execution_time=proc_time,
            speedup=proc_speedup,
            efficiency=proc_eff,
            memory_mb=proc_memory
        )

        print(
            f"Multiprocessing ({workers}): Time={proc_time:.4f}s, "
            f"Speedup={proc_speedup:.4f}, Efficiency={proc_eff:.4f}"
        )