#get the symbols and weights on each reel
import math

symbols = []
symbols_weights = {}
symbols_weights_file = open('symbols_weights.csv', 'r')
line = symbols_weights_file.readline()
while line:
    tokens = line.split(',')
    if len(tokens) != 6 or len(tokens[0]) < 1:
        break
    symbols.append(tokens[0])
    symbol_weights = []
    for weight in tokens[1:]:
        symbol_weights.append(float(weight))
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

def add(x,y):
    return x + y

def multiply(x,y):
    return x * y

def valueOfPermutation(permutation, weights, reel_weights):
    value = 1
    for i in range(len(permutation)):
        if permutation[i] == 0:
            value = value * (reel_weights[i] - weights[i])
        elif permutation[i] == 1:
            value = value * weights[i]
    return value

def expectedValueOfPermutation(permutation, weights, reel_weights, value):
    probability = valueOfPermutation([0,1,1,1,1], weights, reel_weights) / reduce(multiply, reel_weights)
    return probability * value

def binomialCoefficient(n,k):
    return math.factorial(n) / (math.factorial(k) * math.factorial(n-k))

#calculate the total symbol weight for each reel
reel_weights = [0,0,0,0,0]
for symbol in symbols:
    symbol_weights = symbols_weights[symbol]
    reel_weights = map(add, reel_weights, symbol_weights)

#find the expected value
expected_value = 0.0
for payout in payouts:
    frequency = payout['frequency']
    if frequency == 5:
        probability = reduce(multiply, symbols_weights[payout['symbol']]) / reduce(multiply, reel_weights)
        expected_value += probability * payout['value']
    elif frequency == 4:
        expected_value += expectedValueOfPermutation([0,1,1,1,1], symbols_weights[payout['symbol']], reel_weights, payout['value'])
        expected_value += expectedValueOfPermutation([1,0,1,1,1], symbols_weights[payout['symbol']], reel_weights, payout['value'])
        expected_value += expectedValueOfPermutation([1,1,0,1,1], symbols_weights[payout['symbol']], reel_weights, payout['value'])
        expected_value += expectedValueOfPermutation([1,1,1,0,1], symbols_weights[payout['symbol']], reel_weights, payout['value'])
        expected_value += expectedValueOfPermutation([1,1,1,1,0], symbols_weights[payout['symbol']], reel_weights, payout['value'])
    elif frequency == 3:
        expected_value += expectedValueOfPermutation([0,0,1,1,1], symbols_weights[payout['symbol']], reel_weights, payout['value'])
        expected_value += expectedValueOfPermutation([1,0,0,1,1], symbols_weights[payout['symbol']], reel_weights, payout['value'])
        expected_value += expectedValueOfPermutation([1,1,0,0,1], symbols_weights[payout['symbol']], reel_weights, payout['value'])
        expected_value += expectedValueOfPermutation([1,1,1,0,0], symbols_weights[payout['symbol']], reel_weights, payout['value'])
        expected_value += expectedValueOfPermutation([0,1,1,1,0], symbols_weights[payout['symbol']], reel_weights, payout['value'])
        expected_value += expectedValueOfPermutation([1,0,1,1,0], symbols_weights[payout['symbol']], reel_weights, payout['value'])
        expected_value += expectedValueOfPermutation([0,1,0,1,1], symbols_weights[payout['symbol']], reel_weights, payout['value'])
        expected_value += expectedValueOfPermutation([1,0,1,0,1], symbols_weights[payout['symbol']], reel_weights, payout['value'])
        expected_value += expectedValueOfPermutation([1,1,0,1,0], symbols_weights[payout['symbol']], reel_weights, payout['value'])
        expected_value += expectedValueOfPermutation([0,1,1,0,1], symbols_weights[payout['symbol']], reel_weights, payout['value'])

print "expected value: {0}".format(expected_value)
#print "5 choose 3: {0}".format(binomialCoefficient(5,3))