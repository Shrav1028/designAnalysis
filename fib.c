
// UNCOMMENT TO STRESS CACHES. THIS WILL SHOW L2 PERFORMANCE IMPROVEMENTS. 
// // large_array.c - working set too big for L1
// #include <stdlib.h>
// #define N 1000000  // 4MB, way bigger than 32KiB L1

// int main() {
//     int *arr = malloc(N * sizeof(int));
//     long sum = 0;
//     for (int i = 0; i < N; i++) arr[i] = i;
//     // random access pattern to stress cache
//     for (int i = 0; i < N; i++) sum += arr[(i * 1000003) % N];
//     return (int)sum;
// }

int fib(int n) { return n < 2 ? n : fib(n-1) + fib(n-2); }
int main() { fib(35); return 0; }