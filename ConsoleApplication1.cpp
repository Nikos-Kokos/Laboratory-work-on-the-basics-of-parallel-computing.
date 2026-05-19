#include <cstdlib>
#include <iostream>
#include <fstream>
#include <chrono>
#include <omp.h>
#include <vector>

using namespace std;
using namespace std::chrono;

void multiplyMatrices(float* A, float* B, float* C, int N, int num_threads) {
    omp_set_num_threads(num_threads);
#pragma omp parallel for
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            float sum = 0.0f;
            for (int k = 0; k < N; ++k) {
                sum += A[i * N + k] * B[k * N + j];
            }
            C[i * N + j] = sum;
        }
    }
}

int main(int argc, char* argv[]) {
    if (argc != 4) {
        cerr << "Usage: " << argv[0] << " <N> <num_threads> <output_file>" << endl;
        return 1;
    }
    int N = atoi(argv[1]);
    int num_threads = atoi(argv[2]);
    string output_file = argv[3];

    // Разрешаем любой размер, даже 1
    if (N < 1) N = 1;

    vector<float> A(N * N), B(N * N), C(N * N);
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            A[i * N + j] = (i + 1) * (j + 1);
            B[i * N + j] = (i + 1) + 2 * (j + 1);
        }
    }

    auto start = high_resolution_clock::now();
    double wstart = omp_get_wtime();

    multiplyMatrices(A.data(), B.data(), C.data(), N, num_threads);

    auto end = high_resolution_clock::now();
    double wend = omp_get_wtime();
    double elapsed = duration_cast<duration<double>>(end - start).count();

    // Гарантия ненулевого времени (для очень быстрых операций)
    if (elapsed < 1e-12) elapsed = 1e-12;
    if (wend - wstart < 1e-12) wend = wstart + 1e-12;

    ofstream result_file(output_file, ios::app);
    if (result_file.is_open()) {
        result_file << N << "," << num_threads << "," << elapsed << "," << (wend - wstart) << endl;
        result_file.close();
    }

    // Вывод времени в stdout для парсинга
    cout << elapsed << endl;
    return 0;
}