import subprocess
import numpy as np
import matplotlib.pyplot as plt
import os
import time
import sys

# ========== НАСТРОЙКИ (ИЗМЕНИТЕ ПРИ НЕОБХОДИМОСТИ) ==========
CPP_EXE_PATH = r"D:\Projects\ConsoleApplication1\Debug\ConsoleApplication1.exe"
MATRIX_SIZES = [10, 50, 100, 200, 400, 600, 800, 1000, 1200, 1600, 1800, 2000]
THREAD_COUNTS = [1, 2, 4, 8, 16]
OUTPUT_CSV = "timing_results.csv"
PLOT_FILE = "performance_plot_linear.png"
MAX_RETRIES = 2
# ===========================================================

def run_cpp(size, threads):
    """Запуск C++ программы, возвращает время или None."""
    if not os.path.exists(CPP_EXE_PATH):
        print(f"ОШИБКА: не найден {CPP_EXE_PATH}", file=sys.stderr)
        return None
    cmd = [CPP_EXE_PATH, str(size), str(threads), OUTPUT_CSV]
    for attempt in range(MAX_RETRIES):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                lines = result.stdout.strip().split()
                if lines:
                    try:
                        return float(lines[-1])
                    except:
                        pass
        except Exception as e:
            print(f"Ошибка: {e}", file=sys.stderr)
    return None

def numpy_multiply(size):
    """Вычисление через NumPy, возвращает время."""
    A = np.zeros((size, size), dtype=np.float32)
    B = np.zeros((size, size), dtype=np.float32)
    for i in range(size):
        for j in range(size):
            A[i, j] = (i+1)*(j+1)
            B[i, j] = (i+1) + 2*(j+1)
    start = time.perf_counter()
    np.dot(A, B)
    return time.perf_counter() - start

def compare_with_numpy(size, threads):
    """Сравнение результатов C++ и NumPy (только для малых размеров)."""
    cpp_file = f"matrix_C_{size}_threads_{threads}.txt"
    if not os.path.exists(cpp_file):
        return False
    try:
        with open(cpp_file, 'r') as f:
            lines = f.readlines()[1:]
            cpp_result = []
            for line in lines:
                if line.strip():
                    cpp_result.append([float(x) for x in line.strip().split()])
            cpp_result = np.array(cpp_result)
    except:
        return False

    A = np.zeros((size, size), dtype=np.float32)
    B = np.zeros((size, size), dtype=np.float32)
    for i in range(size):
        for j in range(size):
            A[i, j] = (i+1)*(j+1)
            B[i, j] = (i+1) + 2*(j+1)
    numpy_result = np.dot(A, B)
    max_diff = np.max(np.abs(cpp_result - numpy_result))
    return max_diff < 1e-4

def main():
    # Инициализация CSV
    with open(OUTPUT_CSV, 'w') as f:
        f.write("size,threads,cpp_time,numpy_time\n")

    results = {}
    total_tests = len(MATRIX_SIZES) * len(THREAD_COUNTS)
    test_idx = 0

    for size in MATRIX_SIZES:
        print(f"\n=== Размер {size} ===")
        results[size] = {'numpy': None, 'cpp': {}}

        # NumPy время
        numpy_time = numpy_multiply(size)
        results[size]['numpy'] = numpy_time
        with open(OUTPUT_CSV, 'a') as f:
            f.write(f"{size},0,0,{numpy_time}\n")
        print(f"  NumPy: {numpy_time:.6f} сек")

        for threads in THREAD_COUNTS:
            test_idx += 1
            print(f"  Тест {test_idx}/{total_tests}: потоки={threads}", end='', flush=True)
            cpp_time = run_cpp(size, threads)
            if cpp_time is not None:
                results[size]['cpp'][threads] = cpp_time
                print(f", время C++ = {cpp_time:.6f} сек")
                # Проверка корректности для маленьких матриц
                if size <= 100:
                    correct = compare_with_numpy(size, threads)
                    if not correct:
                        print(f"    -> ПРЕДУПРЕЖДЕНИЕ: несовпадение с NumPy", file=sys.stderr)
                # Запись в CSV
                with open(OUTPUT_CSV, 'a') as f:
                    f.write(f"{size},{threads},{cpp_time},{numpy_time}\n")
            else:
                print(f", ОШИБКА: C++ не выполнен", file=sys.stderr)

    # Построение графика в линейном масштабе
    plt.figure(figsize=(12, 8))
    sizes = MATRIX_SIZES

    # NumPy линия
    numpy_times = [results[s]['numpy'] for s in sizes]
    plt.plot(sizes, numpy_times, 'ro-', label='NumPy (однопоточный)', linewidth=2, markersize=6)

    # Линии для разных потоков
    colors = ['b', 'g', 'c', 'm', 'y', 'k']
    for idx, threads in enumerate(THREAD_COUNTS):
        cpp_times = [results[s]['cpp'].get(threads, np.nan) for s in sizes]
        # Убираем NaN для отрисовки
        valid_pairs = [(s, t) for s, t in zip(sizes, cpp_times) if not np.isnan(t)]
        if valid_pairs:
            xs, ys = zip(*valid_pairs)
            plt.plot(xs, ys, f'{colors[idx % len(colors)]}s-',
                     label=f'C++ OpenMP ({threads} threads)', linewidth=2, markersize=5)

    # Линейный масштаб
    plt.xscale('linear')
    plt.yscale('linear')
    plt.xlabel('Размер матрицы (N)', fontsize=12)
    plt.ylabel('Время (секунды)', fontsize=12)
    plt.title('Сравнение производительности умножения матриц (линейный масштаб)', fontsize=14)
    plt.legend(loc='upper left', fontsize=10)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.tight_layout()
    plt.savefig(PLOT_FILE, dpi=150)
    print(f"\nГрафик сохранён в {PLOT_FILE}")
    print("Все тесты завершены.")

if __name__ == "__main__":
    main()