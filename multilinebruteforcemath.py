#get the symbols and weights on each reel
symbols_weights = []
slot_layout_file = open('reels_weights.csv', 'r')
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

possible_lines = []
possible_lines.append([0,0,0,0,0])
possible_lines.append([-1,-1,-1,-1,-1])
possible_lines.append([1,1,1,1,1])

#find the expected value
total_choices = reduce(lambda x,y: x*y, reel_weights)
expected_value = 0.0
for a in range(symbols_per_reel[0]):
    for b in range(symbols_per_reel[1]):
        for c in range(symbols_per_reel[2]):
            for d in range(symbols_per_reel[3]):
                for e in range(symbols_per_reel[4]):
                    lines = []
                    for possible_line in possible_lines:
                        ai = a + possible_line[0]
                        if ai == symbols_per_reel[0]:
                            ai = 0
                        bi = b + possible_line[1]
                        if bi == symbols_per_reel[1]:
                            bi = 0
                        ci = c + possible_line[2]
                        if ci == symbols_per_reel[2]:
                            ci = 0
                        di = d + possible_line[3]
                        if di == symbols_per_reel[3]:
                            di = 0
                        ei = e + possible_line[4]
                        if ei == symbols_per_reel[4]:
                            ei = 0
                        line = []
                        line.append(symbols_weights[ai][0])
                        line.append(symbols_weights[bi][1])
                        line.append(symbols_weights[ci][2])
                        line.append(symbols_weights[di][3])
                        line.append(symbols_weights[ei][4])
                        lines.append(line)
                    for line in lines:
                        symbol_to_count = makeSymbolToCount(line)
                        for symbol in symbol_to_payouts.keys():
                            if symbol in symbol_to_count.keys():
                                for payout in symbol_to_payouts[symbol]:
                                    if payout['frequency'] == symbol_to_count[symbol]:
                                        probability = reduce(lambda x,y: x*y, map(lambda x: x['weight'], line)) / total_choices
                                        expected_value += payout['value'] * probability

print "expected value: {0}".format(expected_value/len(possible_lines))
