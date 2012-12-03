#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <string.h>

// For the CUDA runtime routines (prefixed with "cuda_")
#include <cuda_runtime.h>

#define NUM_REELS 5
#define NUM_LINES 9

typedef struct {
   char symbol;
   float weight;
} symbol_weight_t;

typedef struct {
    char symbol;
    int frequency;
    float value;
} payout_t;

typedef struct {
    char symbol;
    int count;
} symbol_count_t;

char** str_split(char* str, const char* delimiterStr, size_t *count) {
    const char delimiter = delimiterStr[0];
    char** result = NULL;
    *count = 0;

    /* Count how many elements will be extracted. */
    char* tmp = str;
    while (*tmp) {
        if (delimiter == *tmp) {
            *count += 1;
        }
        tmp++;
    }
    if(*count > 0) {
        *count += 1;
        result = (char**) malloc(sizeof(char*) * *count);
        size_t idx = 0;
        char* token = strtok(str, delimiterStr);
        while (token) {
            *(result + idx) = strdup(token);
            idx += 1;
            token = strtok(0, delimiterStr);
        }
    }
    return result;
}
__device__ int isWin(payout_t payout, symbol_weight_t *line) {
    int payout_symbol_count = 0;
    int index = 0;
    for (index = 0; index < NUM_REELS; index++) {
        symbol_weight_t symbol_weight = line[index];
        if(symbol_weight.symbol == payout.symbol) {
            payout_symbol_count += 1;
        }
    }
    if (payout_symbol_count == payout.frequency) {
        return 1;
    }
    return 0;
}

__global__ void calculateExpectedValue(const int num_symbols_per_reel, const int num_payouts, const int total_choices,
									   int *device_possible_lines, symbol_weight_t *device_symbols_weights, payout_t *device_payouts, float *device_expected_values) {
    int a_index = threadIdx.x;
    if (a_index < num_symbols_per_reel) {
		float expected_value = 0.0;
		int b,c,d,e;
		int ai,bi,ci,di,ei;
		for (b = 0; b < num_symbols_per_reel; b++) {
			for (c = 0; c < num_symbols_per_reel; c++) {
				for (d = 0; d < num_symbols_per_reel; d++) {
					for (e = 0; e < num_symbols_per_reel; e++) {
						symbol_weight_t lines[NUM_LINES][NUM_REELS];
						int i = 0;
						for(i = 0; i < NUM_LINES; i++) {
							int possible_line[NUM_REELS];
							int j = 0;
							for(j = 0; j < NUM_REELS; j++) {
								possible_line[j] = device_possible_lines[i*NUM_REELS + j];
							}

							ai = a_index + possible_line[0];
							if (ai == num_symbols_per_reel) {
								ai = 0;
							}
							if (ai < 0) {
								ai = num_symbols_per_reel-1;
							}
							bi = b + possible_line[1];
							if (bi == num_symbols_per_reel) {
								bi = 0;
							}
							if (bi < 0) {
								bi = num_symbols_per_reel-1;
							}
							ci = c + possible_line[2];
							if (ci == num_symbols_per_reel) {
								ci = 0;
							}
							if (ci < 0) {
								ci = num_symbols_per_reel-1;
							}
							di = d + possible_line[3];
							if (di == num_symbols_per_reel) {
								di = 0;
							}
							if (di < 0) {
								di = num_symbols_per_reel-1;
							}
							ei = e + possible_line[4];
							if (ei == num_symbols_per_reel) {
								ei = 0;
							}
							if (ei < 0) {
								ei = num_symbols_per_reel-1;
							}
							lines[i][0] = device_symbols_weights[ai*NUM_REELS];
							lines[i][1] = device_symbols_weights[bi*NUM_REELS + 1];
							lines[i][2] = device_symbols_weights[ci*NUM_REELS + 2];
							lines[i][3] = device_symbols_weights[di*NUM_REELS + 3];
							lines[i][4] = device_symbols_weights[ei*NUM_REELS + 4];
						}
						for(i = 0; i < NUM_LINES; i++) {
							int j = 0;
							for(j = 0; j < num_payouts; j++) {
								if(isWin(device_payouts[j], lines[i])) {
									int k = 0;
									float probability = 1.0;
									for(k = 0; k < NUM_REELS; k++) {
										probability *= lines[0][k].weight;
									}
									probability /= total_choices;
									expected_value += device_payouts[j].value * probability; 
								}
							}
						}
					}
				}
			}
		}
		device_expected_values[a_index] = expected_value;
    }
}

int main(void) {
    
    //get the symbols and weights on each reel
    printf("**Reading symbols and weights file\n");
    FILE *reels_weights_file = fopen("reels_weights_shuffled.csv", "rb");
    if (reels_weights_file == NULL) {
        printf("cannot open reels/weights file\n");
        return 1;
    }
    char line [512];
    int num_symbols_per_reel = 0;
    while (fgets(line, 512, reels_weights_file) != NULL) {
        size_t num_tokens = 0;
        char **tokens = str_split(line, ",", &num_tokens);
        if (num_tokens != NUM_REELS) {
            break;
        }
        num_symbols_per_reel += 1;
    }

    symbol_weight_t *symbols_weights = (symbol_weight_t*) malloc(sizeof(symbol_weight_t) * num_symbols_per_reel * NUM_REELS);
    rewind(reels_weights_file);
    int index = 0;
    while (fgets(line, 512, reels_weights_file) != NULL) {
        size_t num_tokens = 0;
        char **tokens = str_split(line, ",", &num_tokens);
        if (num_tokens != NUM_REELS) {
            break;
        }
        int i = 0;
        for(i = 0; i < num_tokens; i++) {
            size_t num_strs = 0;
            char **strs = str_split(tokens[i], "_", &num_strs);
            if(num_strs == 2) {
                char symbol = strs[0][0];
                float weight = strtof(strs[1], NULL);
                symbol_weight_t symbol_weight = {symbol, weight};
                symbols_weights[index * NUM_REELS + i] = symbol_weight;
            }
        }
        index += 1;
    }
    fclose (reels_weights_file);

    //get the payouts
    printf("**Reading payouts file\n");
    FILE *payouts_file = fopen("payouts.csv", "rb");
    if (payouts_file == NULL) {
        printf("cannot open payouts file\n");
        return 1;
    }
    int num_payouts = 0;
    while (fgets(line, 512, payouts_file) != NULL) {
        num_payouts += 1;
    }

    payout_t *payouts = (payout_t*) malloc(sizeof(payout_t) * num_payouts);
    rewind(payouts_file);
    int payout_index = 0;
    while (fgets(line, 512, payouts_file) != NULL) {
        size_t num_tokens = 0;
        char **tokens = str_split(line, ",", &num_tokens);
        char symbol = tokens[0][0];
        int frequency = atoi(tokens[1]);
        float value = strtof(tokens[2], NULL);
        payout_t payout = {symbol, frequency, value};
        payouts[payout_index] = payout;
        payout_index += 1;
    }
    fclose(payouts_file);

    printf("**Calculating the total symbol weight for each reel\n");
    int reel_weights[NUM_REELS];
    int i = 0;
    for(i = 0; i < NUM_REELS; i++) {
        reel_weights[i] = 0;
    }
    for(i = 0; i < num_symbols_per_reel; i++) {
        int j = 0;
        for(j = 0; j < NUM_REELS; j++) {
        	symbol_weight_t symbol_weight = symbols_weights[i*NUM_REELS + j];
            reel_weights[j] += symbol_weight.weight;
        }
    }

    printf("**Initializing lines\n");
    int possible_lines[NUM_LINES * NUM_REELS] = {
    							 0,0,0,0,0,
                                 -1,-1,-1,-1,-1,
                                 1,1,1,1,1,
                                 -1,0,1,0,-1,
                                 1,0,-1,0,1,
                                 0,-1,-1,-1,0,
                                 0,1,1,1,0,
                                 -1,-1,0,1,1,
                                 1,1,0,-1,-1};

    printf("**Finding expected value\n");
    int total_choices = 1;
    for(i = 0; i < NUM_REELS; i++) {
        total_choices *= reel_weights[i];
    }

    //copy host possible lines to device possible lines
    int *device_possible_lines = NULL;
    size_t size = sizeof(int) * NUM_LINES * NUM_REELS;
    cudaError_t error = cudaMalloc((void **)&device_possible_lines, size);
    if (error != cudaSuccess) {
    	printf("cudaMalloc device_possible_lines returned error code %d, line(%d)\n", error, __LINE__);
        exit(EXIT_FAILURE);
    }
    error = cudaMemcpy(device_possible_lines, possible_lines, size, cudaMemcpyHostToDevice);
    if (error != cudaSuccess) {
    	printf("cudaMemcpy device_possible_lines returned error code %d, line(%d)\n", error, __LINE__);
        exit(EXIT_FAILURE);
    }

    //copy host symbols weights to device symbols weights
    symbol_weight_t *device_symbols_weights = NULL;
    size = num_symbols_per_reel * NUM_REELS * sizeof(symbol_weight_t);
    error = cudaMalloc((void **)&device_symbols_weights, size);
    if (error != cudaSuccess) {
       	printf("cudaMalloc device_symbols_weights returned error code %d, line(%d)\n", error, __LINE__);
        exit(EXIT_FAILURE);
    }
    error = cudaMemcpy(device_symbols_weights, symbols_weights, size, cudaMemcpyHostToDevice);
    if (error != cudaSuccess) {
    	printf("cudaMemcpy device_symbols_weights returned error code %d, line(%d)\n", error, __LINE__);
    	exit(EXIT_FAILURE);
    }

    //copy host payouts to device payouts
    payout_t *device_payouts = NULL;
    size = num_payouts * sizeof(payout_t);
    error = cudaMalloc((void**)&device_payouts, size);
    if (error != cudaSuccess) {
    	printf("cudaMalloc device_payouts returned error code %d, line(%d)\n", error, __LINE__);
    	exit(EXIT_FAILURE);
    }
    error = cudaMemcpy(device_payouts, payouts, size, cudaMemcpyHostToDevice);
    if (error != cudaSuccess) {
    	printf("cudaMemcpy device_payouts returned error code %d, line(%d)\n", error, __LINE__);
    	exit(EXIT_FAILURE);
    }

    //initialize expected value array, this will hold the expected value calculated by each thread
    size = num_symbols_per_reel * sizeof(float);
    float *expected_values = (float*) malloc(size);
    float *device_expected_values = NULL;
    error = cudaMalloc((void**)&device_expected_values, size);
    if (error != cudaSuccess) {
       	printf("cudaMalloc device_expected_values returned error code %d, line(%d)\n", error, __LINE__);
       	exit(EXIT_FAILURE);
    }

    //invoke the device code
    int threadsPerBlock = num_symbols_per_reel;
    int blocksPerGrid = 1;//(numElements + threadsPerBlock - 1) / threadsPerBlock;
    printf("CUDA kernel launch with %d blocks of %d threads\n", blocksPerGrid, threadsPerBlock);
    calculateExpectedValue<<<blocksPerGrid, threadsPerBlock>>>(num_symbols_per_reel, num_payouts, total_choices,
    		device_possible_lines, device_symbols_weights, device_payouts, device_expected_values);
    error = cudaGetLastError();
    if (error != cudaSuccess) {
    	fprintf(stderr, "Failed to launch calculateExpectedValue kernel (error code %s)!\n", cudaGetErrorString(error));
    	exit(EXIT_FAILURE);
    }

    //copy expected values from CUDA device to host memory
    error = cudaMemcpy(expected_values, device_expected_values, size, cudaMemcpyDeviceToHost);
    if (error != cudaSuccess){
    	fprintf(stderr, "Failed to copy vector expected values from device to host (error code %s)!\n", cudaGetErrorString(error));
    	exit(EXIT_FAILURE);
    }

    //sum each of the device expected values into one sum
    float expected_value = 0.0;
    for(i = 0; i < num_symbols_per_reel; i++) {
    	expected_value += expected_values[i];
    }
    printf("expected value %f\n", expected_value/NUM_LINES);

    //free host and device memory
    free(symbols_weights);
    free(payouts);
    free(expected_values);
    cudaFree(device_possible_lines);
    cudaFree(device_symbols_weights);
    cudaFree(device_payouts);
    cudaFree(device_expected_values);

    cudaDeviceReset();

    return 0;
}
