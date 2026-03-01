#include <iostream>
#include <fstream>
#include <ctime>
#include <iomanip>
#include <string>

using namespace std;

// Функция для преобразования строки в число (без использования cstdlib)
int stringToInt(const char* str) {
    int result = 0;
    int i = 0;
    
    // Пропускаем пробелы в начале
    while (str[i] == ' ') {
        i++;
    }
    
    // Проверяем знак числа
    int sign = 1;
    if (str[i] == '-') {
        sign = -1;
        i++;
    } else if (str[i] == '+') {
        i++;
    }
    
    // Преобразуем цифры в число
    while (str[i] >= '0' && str[i] <= '9') {
        result = result * 10 + (str[i] - '0');
        i++;
    }
    
    return result * sign;
}

// Функция для сохранения матрицы в файл
template <typename T>
void saveMatrixToFile(const T* Mat, int size, const string& filename, const string& matrixName) {
    ofstream file(filename);
    if (!file.is_open()) {
        cerr << "Ошибка: не удалось открыть файл " << filename << " для записи" << endl;
        return;
    }
    
    // Записываем размерность в первой строке
    file << size << " " << size << endl;
    
    // Записываем матрицу
    for (int i = 0; i < size; i++) {
        for (int j = 0; j < size; j++) {
            file << fixed << setprecision(6) << Mat[i * size + j];
            if (j < size - 1) file << " ";
        }
        file << endl;
    }
    
    file.close();
    cout << "Матрица " << matrixName << " сохранена в файл " << filename << endl;
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        cout << "Программа: " << argv[0] << " <n>" << endl;
        cout << "где <n> - размер квадратной матрицы" << endl;
        return -1;
    }
    
    // Преобразуем аргумент командной строки в число без использования atoi
    int N = stringToInt(argv[1]);
    
    if (N <= 0) {
        cerr << "Ошибка: размер матрицы должен быть положительным числом" << endl;
        return -1;
    }
    
    cout << "Размер матрицы: " << N << "x" << N << endl;
    cout << "Начало инициализации..." << endl;
    
    // Выделение памяти
    float *A = new float[N * N];
    float *B = new float[N * N];
    float *C = new float[N * N];
    
    // Инициализация матриц A и B
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            A[i * N + j] = (i + 1) * (j + 1);
            B[i * N + j] = (i + 1) + 2 * (j + 1);
        }
    }
    
    cout << "Начало вычислений..." << endl;
    
    clock_t start = clock();
    
    // Последовательное перемножение матриц
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            C[i * N + j] = 0;
            for (int k = 0; k < N; k++) {
                C[i * N + j] += A[i * N + k] * B[k * N + j];
            }
        }
    }
    
    double calculationTime = double(clock() - start) / CLOCKS_PER_SEC;
    cout << "Время вычислений: " << calculationTime << " секунд" << endl;
    
    // Сохранение матриц в файлы
    saveMatrixToFile(A, N, "matrix_A.txt", "A");
    saveMatrixToFile(B, N, "matrix_B.txt", "B");
    saveMatrixToFile(C, N, "matrix_C.txt", "C");
    
    // Сохранение времени в общий файл результатов
    ofstream timingFile("timing_results.txt", ios::app);
    if (timingFile.is_open()) {
        timingFile << N << " " << calculationTime << endl;
        timingFile.close();
    } else {
        cerr << "Ошибка: не удалось открыть файл timing_results.txt" << endl;
    }
    
    // Освобождение памяти
    delete[] A;
    delete[] B;
    delete[] C;
    
    cout << "Программа завершена успешно!" << endl;
    return 0;
}