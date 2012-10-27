import random

def shuffle(x):
    for i in range(len(x)-1):
        r = random.randint(0, len(x)-1)
        before = i - 1
        if before < 0:
            before = len(x)-1
        after = i + 1
        if after >= len(x):
            after = 0
        if x[after] != x[r] and x[before] != x[r]:
            temp = x[i]
            x[i] = x[r]
            x[r] = temp

symbols_weights = []
reels_weights_file = open('reels_weights.csv', 'r')
line = reels_weights_file.readline()
while line:
    tokens = line.split(',')
    if len(tokens) != 6 or len(tokens[0]) < 1:
        break
    symbol_weights = []
    for weight in tokens[1:]:
        symbol_weights.append({'symbol':tokens[0], 'weight':float(weight)})
    symbols_weights.append(symbol_weights)
    line = reels_weights_file.readline()
reels_weights_file.close()

shuffled_symbols_weights = []
for sw in symbols_weights:
    shuffled_symbols_weights.append([])
for i in range(len(symbols_weights[0])):
    shuffle(symbols_weights)
    for j in range(len(symbols_weights)):
        sw = symbols_weights[j]
        shuffled_symbols_weights[j].append(sw[i])

reels_weights_shuffled_file = open("reels_weights_shuffled.csv", "w")
for sw in shuffled_symbols_weights:
    for symbol_weight in sw:
        reels_weights_shuffled_file.write("{0}_{1},".format(symbol_weight["symbol"], symbol_weight["weight"]))
    reels_weights_shuffled_file.write("\n")
reels_weights_shuffled_file.flush()
reels_weights_shuffled_file.close()
