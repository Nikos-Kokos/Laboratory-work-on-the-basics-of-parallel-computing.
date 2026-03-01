#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import numpy as np
import matplotlib.pyplot as plt
import os
import time
from collections import defaultdict
import sys
import shutil

CXX_PROGRAM_PATH = r"D:\Projects\C++\main.exe"

WORKING_DIR = os.path.dirname(os.path.abspath(__file__))  # текущая папка
SIZES_TO_TEST = [10, 50, 200, 400, 600, 800, 1000, 1200, 1600, 1800, 2000]  # можно изменить
NUM_RUNS = 6  # количество запусков для каждого размера

def check_exe_exists():
    """Проверяет существование exe-файла"""
    if not os.path.exists(CXX_PROGRAM_PATH):
        print(f"ОШИБКА: Не найден файл '{CXX_PROGRAM_PATH}'")
        print("Пожалуйста, укажите правильный путь к matrix_mult.exe")
        print("Измените переменную CXX_PROGRAM_PATH в начале скрипта")
        return False
    
    print(f"Найден exe-файл: {CXX_PROGRAM_PATH}")
    return True

def run_matrix_mult(size):
    """Запускает программу на C++ для заданного размера"""
    try:
        # Запускаем exe-файл из его папки или с полным путем
        result = subprocess.run([CXX_PROGRAM_PATH, str(size)], 
                               capture_output=True, text=True, 
                               timeout=300,  # таймаут 5 минут
                               cwd=os.path.dirname(CXX_PROGRAM_PATH) if os.path.dirname(CXX_PROGRAM_PATH) else None)
        
        if result.returncode != 0:
            print(f"  Программа вернула код ошибки: {result.returncode}")
            print(f"  stderr: {result.stderr}")
            return False
        
        # После выполнения программы, копируем файлы результатов в текущую папку
        copy_result_files(os.path.dirname(CXX_PROGRAM_PATH) if os.path.dirname(CXX_PROGRAM_PATH) else ".")
        
        return True
        
    except subprocess.TimeoutExpired:
        print(f"  Таймаут для размера {size}")
        return False
    except Exception as e:
        print(f"  Ошибка при запуске: {e}")
        return False

def copy_result_files(source_dir):
    """Копирует файлы результатов из папки с exe в текущую папку"""
    files_to_copy = ["matrix_A.txt", "matrix_B.txt", "matrix_C.txt", "timing_results.txt"]
    
    for file in files_to_copy:
        source_path = os.path.join(source_dir, file)
        dest_path = os.path.join(WORKING_DIR, file)
        
        if os.path.exists(source_path):
            # Если файл уже существует в текущей папке, добавляем к нему, а не перезаписываем
            if file == "timing_results.txt" and os.path.exists(dest_path):
                # Для timing_results.txt добавляем содержимое
                with open(source_path, 'r') as src, open(dest_path, 'a') as dst:
                    dst.write(src.read())
                os.remove(source_path)  # удаляем исходный
            else:
                # Для остальных файлов просто копируем с заменой
                shutil.copy2(source_path, dest_path)
                os.remove(source_path)  # удаляем исходный
            print(f"    Файл {file} скопирован в текущую папку")

def read_matrix_from_file(filename):
    """Читает матрицу из файла (формат из вашей C++ программы)"""
    try:
        with open(filename, 'r') as f:
            # Пропускаем первую строку с размерностью (в вашей программе она есть)
            first_line = f.readline().strip()
            if not first_line:
                return None
            
            # Пытаемся определить формат
            parts = first_line.split()
            if len(parts) == 2:
                # Формат: размерность в первой строке
                rows, cols = map(int, parts)
                matrix = []
                for _ in range(rows):
                    line = f.readline()
                    if not line:
                        return None
                    row = list(map(float, line.strip().split()))
                    if len(row) != cols:
                        return None
                    matrix.append(row)
                return np.array(matrix)
            else:
                # Формат: сразу данные матрицы
                f.seek(0)
                matrix = np.loadtxt(f)
                return matrix
    except Exception as e:
        print(f"  Ошибка чтения файла {filename}: {e}")
        return None

def verify_multiplication(size):
    """Проверяет корректность умножения для заданного размера"""
    # Читаем матрицы из файлов
    A = read_matrix_from_file("matrix_A.txt")
    B = read_matrix_from_file("matrix_B.txt")
    C = read_matrix_from_file("matrix_C.txt")
    
    if A is None or B is None or C is None:
        return False, None
    
    # Проверяем размерности
    if A.shape != (size, size) or B.shape != (size, size) or C.shape != (size, size):
        print(f"    Несоответствие размерностей: A {A.shape}, B {B.shape}, C {C.shape}")
        return False, None
    
    # Вычисляем произведение с помощью numpy
    C_expected = np.dot(A, B)
    
    # Сравниваем результаты
    if np.allclose(C, C_expected, rtol=1e-5, atol=1e-8):
        max_diff = np.max(np.abs(C - C_expected))
        return True, max_diff
    else:
        # Находим максимальное расхождение для диагностики
        max_diff = np.max(np.abs(C - C_expected))
        print(f"    Максимальное расхождение: {max_diff:.2e}")
        return False, None

def read_timing_results():
    """Читает результаты времени из файла"""
    times_by_size = defaultdict(list)
    
    if not os.path.exists("timing_results.txt"):
        print("Файл timing_results.txt не найден")
        return times_by_size
    
    with open("timing_results.txt", 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if line and not line.startswith('#'):
                try:
                    parts = line.split()
                    if len(parts) >= 2:
                        size = int(float(parts[0]))  # преобразуем в int на случай, если сохранено как float
                        time_val = float(parts[1])
                        times_by_size[size].append(time_val)
                except ValueError as e:
                    print(f"Предупреждение: строка {line_num} имеет неверный формат: {line}")
                    continue
    
    return times_by_size

def plot_results(times_by_size):
    """Строит графики зависимости времени от размера"""
    if not times_by_size:
        print("Нет данных для построения графиков")
        return
    
    sizes = []
    avg_times = []
    std_times = []
    
    print("\n" + "="*60)
    print("РЕЗУЛЬТАТЫ ИЗМЕРЕНИЙ:")
    print("="*60)
    
    for size in sorted(times_by_size.keys()):
        times = times_by_size[size]
        if len(times) >= 1:
            avg_time = np.mean(times)
            std_time = np.std(times) if len(times) > 1 else 0
            sizes.append(size)
            avg_times.append(avg_time)
            std_times.append(std_time)
            
            print(f"Размер {size:4d}: {len(times)} измерений, "
                  f"среднее = {avg_time:.6f} ± {std_time:.6f} сек")
    
    if not sizes:
        return
    
    # Создаем два графика рядом
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # График 1: линейный масштаб
    ax1.errorbar(sizes, avg_times, yerr=std_times, 
                 fmt='bo-', capsize=5, capthick=2,
                 markersize=8, linewidth=2, label='Экспериментальные данные')
    ax1.set_xlabel('Размер матрицы (N)', fontsize=12)
    ax1.set_ylabel('Время выполнения (сек)', fontsize=12)
    ax1.set_title('Линейный масштаб', fontsize=14)
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # График 2: логарифмический масштаб с аппроксимацией
    sizes_array = np.array(sizes)
    times_array = np.array(avg_times)
    
    ax2.errorbar(sizes_array, times_array, yerr=std_times,
                 fmt='ro-', capsize=5, capthick=2,
                 markersize=8, linewidth=2, label='Экспериментальные данные')
    
    # Аппроксимация O(n^3)
    if len(sizes) > 2:
        log_sizes = np.log(sizes_array)
        log_times = np.log(times_array)
        coeff = np.polyfit(log_sizes, log_times, 1)
        theoretical = np.exp(coeff[1]) * sizes_array**coeff[0]
        ax2.plot(sizes_array, theoretical, 'g--', 
                linewidth=2, label=f'Аппроксимация O(n^{coeff[0]:.2f})')
        
        print(f"\nАппроксимация сложности: O(n^{coeff[0]:.2f})")
    
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.set_xlabel('Размер матрицы (N) - лог. шкала', fontsize=12)
    ax2.set_ylabel('Время выполнения (сек) - лог. шкала', fontsize=12)
    ax2.set_title('Логарифмический масштаб', fontsize=14)
    ax2.grid(True, alpha=0.3, which='both')
    ax2.legend()
    
    plt.suptitle('Зависимость времени перемножения матриц от их размера', 
                 fontsize=16, y=1.02)
    plt.tight_layout()
    
    # Сохраняем график
    plot_filename = 'matrix_multiplication_timing.png'
    plt.savefig(plot_filename, dpi=150, bbox_inches='tight')
    print(f"\nГрафик сохранен в файл '{plot_filename}'")
    
    plt.show()

def cleanup():
    """Удаляет временные файлы"""
    files_to_remove = ["matrix_A.txt", "matrix_B.txt", "matrix_C.txt"]
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
            print(f"Удален временный файл: {file}")

def print_config():
    """Выводит текущую конфигурацию"""
    print("\n" + "="*60)
    print("КОНФИГУРАЦИЯ:")
    print("="*60)
    print(f"Путь к exe: {CXX_PROGRAM_PATH}")
    print(f"Рабочая папка: {WORKING_DIR}")
    print(f"Тестируемые размеры: {SIZES_TO_TEST}")
    print(f"Запусков на размер: {NUM_RUNS}")
    print("="*60)

def main():
    print("="*60)
    print("АВТОМАТИЗИРОВАННОЕ ТЕСТИРОВАНИЕ ПЕРЕМНОЖЕНИЯ МАТРИЦ")
    print("="*60)
    
    # Проверяем наличие exe-файла
    if not check_exe_exists():
        sys.exit(1)
    
    # Показываем конфигурацию
    print_config()
    
    # Очищаем старые файлы результатов в текущей папке
    if os.path.exists("timing_results.txt"):
        user_input = input("\nФайл timing_results.txt уже существует. Перезаписать? (y/n): ")
        if user_input.lower() == 'y':
            os.remove("timing_results.txt")
            print("Старый файл результатов удален")
    
    # Тестируем для разных размеров
    correct_sizes = []
    incorrect_sizes = []
    
    for size in SIZES_TO_TEST:
        print(f"\n--- Тестирование размера {size}x{size} ---")
        
        size_correct = True
        
        for run in range(NUM_RUNS):
            print(f"  Запуск {run + 1}/{NUM_RUNS}...")
            
            # Запускаем C++ программу
            if run_matrix_mult(size):
                # Проверяем корректность умножения
                is_correct, max_diff = verify_multiplication(size)
                
                if is_correct:
                    print(f"    ✓ Умножение выполнено правильно (макс. разница: {max_diff:.2e})")
                else:
                    print(f"    ✗ ОШИБКА: умножение выполнено неправильно!")
                    size_correct = False
            else:
                print(f"    ✗ ОШИБКА: программа не выполнилась")
                size_correct = False
        
        if size_correct:
            correct_sizes.append(size)
        else:
            incorrect_sizes.append(size)
        
        # Небольшая пауза между размерами
        time.sleep(1)
    
    # Читаем и анализируем результаты
    times_by_size = read_timing_results()
    
    # Строим графики
    plot_results(times_by_size)
    
    # Выводим сводку
    print("\n" + "="*60)
    print("ИТОГОВАЯ СВОДКА:")
    print("="*60)
    print(f"Всего тестов: {len(SIZES_TO_TEST)} размеров × {NUM_RUNS} запусков")
    print(f"Корректные размеры: {correct_sizes}")
    if incorrect_sizes:
        print(f"Проблемные размеры: {incorrect_sizes}")
    
    # Спрашиваем, нужно ли удалить временные файлы
    print("\n" + "="*60)
    cleanup_choice = input("Удалить временные файлы матриц? (y/n): ")
    if cleanup_choice.lower() == 'y':
        cleanup()
    
    print("\nПрограмма завершена!")

if __name__ == "__main__":
    main()