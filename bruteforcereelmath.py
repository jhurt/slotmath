#get the symbols and weights on each reel
symbols_weights = []
slot_layout_file = open('layout.csv', 'r')
line = slot_layout_file.readline()
while line:
    tokens = line.split(',')
    if len(tokens) != 6 or len(tokens[0]) < 1:
        break
    symbol_weights = []
    for weight in tokens[1:]:
        symbol_weights.append({'symbol':tokens[0], 'weight':float(weight)})
    symbols_weights.append(symbol_weights)
    line = slot_layout_file.readline()
slot_layout_file.close()

#get the payouts
symbol_to_payouts = {} # map the symbol to a list of dicts of frequency, value
payouts_file = open('payouts.csv', 'r')
line = payouts_file.readline()
while line:
    tokens = line.split(',')
    if tokens[0] in symbol_to_payouts.keys():
        symbol_to_payouts[tokens[0]].append({'frequency': int(tokens[1]),  'value': float(tokens[2])})
    else:
        symbol_to_payouts[tokens[0]] = [{'frequency': int(tokens[1]),  'value': float(tokens[2])}]
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
    probability = valueOfPermutation([0,1,1,1,1], weights, reel_weights) / reduce(lambda x,y: x*y, reel_weights)
    return probability * value

#calculate the total symbol weight for each reel
reel_weights = [0,0,0,0,0]

symbols_per_reel = [len(symbols_weights), len(symbols_weights), len(symbols_weights), len(symbols_weights), len(symbols_weights)]
for symbol_weights in symbols_weights:
    reel_weights = map(lambda x,y:x+y, reel_weights, map(lambda x: x['weight'], symbol_weights))

def makeSymbolToCount(reel):
    symbol_to_count = {}
    for symbol_weights in reel:
        if symbol_weights['symbol'] in symbol_to_count.keys():
            symbol_to_count[symbol_weights['symbol']] += 1
        else:
            symbol_to_count[symbol_weights['symbol']] = 1
    return symbol_to_count

#find the expected value
total_choices = reduce(lambda x,y: x*y, reel_weights)
expected_value = 0.0
for a in range(symbols_per_reel[0]):
    for b in range(symbols_per_reel[1]):
        for c in range(symbols_per_reel[2]):
            for d in range(symbols_per_reel[3]):
                for e in range(symbols_per_reel[4]):
                    reel = []
                    reel.append(symbols_weights[a][0])
                    reel.append(symbols_weights[b][1])
                    reel.append(symbols_weights[c][2])
                    reel.append(symbols_weights[d][3])
                    reel.append(symbols_weights[e][4])
                    #print("reel : {0}{1}{2}{3}{4}", reel[0]['symbol'],reel[1]['symbol'],reel[2]['symbol'],reel[3]['symbol'],reel[4]['symbol'])
                    symbol_to_count = makeSymbolToCount(reel)
                    for symbol in symbol_to_payouts.keys():
                        if symbol in symbol_to_count.keys():
                            for payout in symbol_to_payouts[symbol]:
                                if payout['frequency'] == symbol_to_count[symbol]:
                                    probability = reduce(lambda x,y: x*y, map(lambda x: x['weight'], reel)) / total_choices
                                    expected_value += payout['value'] * probability


print "final expected value: {0}".format(expected_value)
