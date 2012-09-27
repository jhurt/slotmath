import itertools

#get the symbols and weights on each reel
symbols_weights = {}
symbols_weights_file = open('reels_weights.csv', 'r')
line = symbols_weights_file.readline()
while line:
    tokens = line.split(',')
    if len(tokens) != 6 or len(tokens[0]) < 1:
        break
    symbol_weights = []
    for weight in tokens[1:]:
        symbol_weights.append(float(weight))
    if tokens[0] in symbols_weights.keys():
        symbols_weights[tokens[0]] = map(lambda x,y: x+y, symbols_weights[tokens[0]], symbol_weights)
    else:
        symbols_weights[tokens[0]] = symbol_weights
    line = symbols_weights_file.readline()
symbols_weights_file.close()

#get the payouts
payouts = []
payouts_file = open('payouts.csv', 'r')
line = payouts_file.readline()
while line:
    tokens = line.split(',')
    payout = {'symbol': tokens[0], 'frequency' : int(tokens[1]), 'value': float(tokens[2])}
    payouts.append(payout)
    line = payouts_file.readline()
payouts_file.close()

def valueOfPermutation(permutation, weights, reel_weights):
    value = 1
    for i in range(len(permutation)):
        if permutation[i] == 0:
            value = value * (reel_weights[i] - weights[i])
        elif permutation[i] == 1:
            value = value * weights[i]
    return value

def expectedValueOfPermutation(permutation, weights, reel_weights, value):
    probability = valueOfPermutation(permutation, weights, reel_weights) / reduce(lambda x,y:x*y, reel_weights)
    return probability * value

#calculate the total symbol weight for each reel
reel_weights = [0,0,0,0,0]
for symbol in symbols_weights.keys():
    symbol_weights = symbols_weights[symbol]
    reel_weights = map(lambda x,y:x+y, reel_weights, symbol_weights)

#find the expected value
expected_value = 0.0
for payout in payouts:
    frequency = payout['frequency']
    permutations = None
    if frequency == 5:
        permutations = [[1,1,1,1,1]]
    elif frequency == 4:
        permutations = set(itertools.permutations([1,1,1,1,0]))
    elif frequency == 3:
        permutations = set(itertools.permutations([1,1,1,0,0]))
    elif frequency == 2:
        permutations = set(itertools.permutations([1,1,0,0,0]))
    elif frequency == 1:
        permutations = set(itertools.permutations([1,0,0,0,0]))
    for permutation in permutations:
        expected_value += expectedValueOfPermutation(permutation, symbols_weights[payout['symbol']], reel_weights, payout['value'])

print "expected value: {0}".format(expected_value)
