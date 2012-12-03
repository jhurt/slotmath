#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <string.h>

#define NUM_REELS 5

typedef struct {
   char *symbol;
   double weight;
} symbol_weight_t;

typedef struct {
    char *symbol;
    int frequency;
    double value;
} payout_t;

typedef struct {
    char *symbol;
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
        result = malloc(sizeof(char*) * *count);
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

int isWin(payout_t payout, symbol_weight_t *line) {
    int payout_symbol_count = 0;
    int index = 0;
    for (index = 0; index < NUM_REELS; index++) {
        symbol_weight_t symbol_weight = line[index];
        if(strcmp(symbol_weight.symbol, payout.symbol) == 0) {
            payout_symbol_count += 1;
        }
    }
    if (payout_symbol_count == payout.frequency) {
        return 1;
    }
    return 0;
}

int main(void) {
    printf("**Reading symbols and weights file\n");

    //get the symbols and weights on each reel
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

    symbol_weight_t **symbols_weights = malloc(sizeof(symbol_weight_t*) * num_symbols_per_reel);
    rewind(reels_weights_file);
    int index = 0;
    while (fgets(line, 512, reels_weights_file) != NULL) {
        size_t num_tokens = 0;
        char **tokens = str_split(line, ",", &num_tokens);
        if (num_tokens != NUM_REELS) {
            break;
        }
        symbol_weight_t *symbol_weights = malloc(sizeof(symbol_weight_t) * NUM_REELS);
        int i = 0;
        for(i = 0; i < num_tokens; i++) {
            size_t num_strs = 0;
            char **strs = str_split(tokens[i], "_", &num_strs);
            if(num_strs == 2) {
                char *symbol = strs[0];
                double weight = strtod(strs[1], NULL);
                symbol_weight_t symbol_weight = {symbol, weight};
                symbol_weights[i] = symbol_weight;
            }
        }
        symbols_weights[index] = symbol_weights;
        index += 1;
    }
    fclose (reels_weights_file);
    
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

    payout_t *payouts = malloc(sizeof(payout_t) * num_payouts);
    rewind(payouts_file);
    int payout_index = 0;
    while (fgets(line, 512, payouts_file) != NULL) {
        size_t num_tokens = 0;
        char **tokens = str_split(line, ",", &num_tokens);
        char *symbol = tokens[0];
        int frequency = atoi(tokens[1]);
        double value = strtod(tokens[2], NULL);
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
        symbol_weight_t *symbol_weights = symbols_weights[i];
        int j = 0;
        for(j = 0; j < NUM_REELS; j++) {
            reel_weights[j] += symbol_weights[j].weight;
        }
    }

    printf("**Initializing lines\n");
    int possible_lines[9][NUM_REELS] = { {0,0,0,0,0},
                                 {-1,-1,-1,-1,-1},
                                 {1,1,1,1,1},
                                 {-1,0,1,0,-1},
                                 {1,0,-1,0,1},
                                 {0,-1,-1,-1,0},
                                 {0,1,1,1,0},
                                 {-1,-1,0,1,1},
                                 {1,1,0,-1,-1}};

    printf("**Finding expected value\n");
    int total_choices = 1;
    for(i = 0; i < NUM_REELS; i++) {
        total_choices *= reel_weights[i];
    }
    double expected_value = 0.0;
    int a,b,c,d,e;
    int ai,bi,ci,di,ei;
    for (a = 0; a < num_symbols_per_reel; a++) {
        for (b = 0; b < num_symbols_per_reel; b++) {
            for (c = 0; c < num_symbols_per_reel; c++) {
                for (d = 0; d < num_symbols_per_reel; d++) {
                    for (e = 0; e < num_symbols_per_reel; e++) {
                        symbol_weight_t lines[9][NUM_REELS];
                        for(i = 0; i < 9; i++) {
                            int possible_line[NUM_REELS];
                            int j = 0;
                            for(j = 0; j < NUM_REELS; j++) {
                                possible_line[j] = possible_lines[i][j];
                            }

                            ai = a + possible_line[0];
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
                            lines[i][0] = symbols_weights[ai][0];
                            lines[i][1] = symbols_weights[bi][1];
                            lines[i][2] = symbols_weights[ci][2];
                            lines[i][3] = symbols_weights[di][3];
                            lines[i][4] = symbols_weights[ei][4];                            
                        }
                        for(i = 0; i < 9; i++) {
                            int j = 0;
                            for(j = 0; j < payout_index; j++) {
                                if(isWin(payouts[j], lines[i])) {
                                    int k = 0;
                                    double probability = 1.0;
                                    for(k = 0; k < NUM_REELS; k++) {
                                        probability *= lines[0][k].weight;
                                    }
                                    probability /= total_choices;
                                    expected_value += payouts[j].value * probability;
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    printf("expected value %f\n", expected_value/9);

    return 0;
}