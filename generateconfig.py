from optparse import OptionParser
import random
from subprocess import Popen, PIPE
import re

#get the upper and lower bound from the command line
parser = OptionParser()
parser.add_option('--lower_bound', dest='lower_bound', help='lower bound payout percentage',)
parser.add_option('--upper_bound', dest='upper_bound', help='lower bound payout percentage')
parser.add_option('--weight', dest='total_reel_weight', help='total weight of each reel')
parser.add_option('--reels', dest='reels', help='total number of reel strips')
parser.add_option('--highsymbols', dest='high_symbols', help='high payout symbols')

(options, args) = parser.parse_args()

lower_bound = float(options.lower_bound)
upper_bound = float(options.upper_bound)
total_reel_weight = float(options.total_reel_weight)
reel_count = int(options.reels)

assert 0.0 < lower_bound < upper_bound < 1.0

#read the symbols from file
reel_symbols = []
reel_symbols_file = open('reel_symbols.txt', 'r')
line = reel_symbols_file.readline()
while line:
    if len(line) > 0:
        reel_symbols.append(line.strip())
    line = reel_symbols_file.readline()
reel_symbols_file.close()

#read the payouts from file
symbol_to_biggest_payout = {} #map the symbol to its payout for the highest frequency number of symbols
symbol_to_payouts = {} # map the symbol to a list of dicts of frequency, value
payouts_file = open('payouts.csv', 'r')
line = payouts_file.readline()
while line:
    tokens = line.split(',')
    symbol = tokens[0]
    frequency = int(tokens[1])
    value = float(tokens[2])
    if symbol in symbol_to_payouts.keys():
        symbol_to_payouts[symbol].append({'frequency': frequency,  'value': value})
    else:
        symbol_to_payouts[symbol] = [{'frequency': frequency,  'value': value}]
    if frequency == reel_count:
        symbol_to_biggest_payout[symbol] = value
    line = payouts_file.readline()
payouts_file.close()

#build two sets, one for high paying symbols and one for low paying symbols
high_paying_symbols = set(options.high_symbols.split(','))
low_paying_symbols = set()
for symbol in symbol_to_payouts.keys():
    if symbol not in high_paying_symbols:
        low_paying_symbols.add(symbol)

#shuffle a list of symbols, making sure to not put duplicates next to each other
def shuffle(x):
    for i in range(len(x)):
        r = random.randint(0, len(x)-1)
        before_i = i - 1
        if before_i < 0:
            before_i = len(x)-1
        after_i = i + 1
        if after_i >= len(x):
            after_i = 0
        before_r = r - 1
        if before_r < 0:
            before_r = len(x)-1
        after_r = r + 1
        if after_r >= len(x):
            after_r = 0
        if x[after_i] != x[r] and x[before_i] != x[r] and x[after_r] != x[i] and x[before_r] != x[i]:
            temp = x[i]
            x[i] = x[r]
            x[r] = temp

def buildRandomStrip():
    #build a random reel strip of symbols
    shuffle(reel_symbols)
    strip = []
    for symbol in reel_symbols:
        strip.append(symbol)

    #randomize a set of weights across the reel symbols
    #start with all 1's
    strip_weights = []
    for i in range(len(strip)):
        strip_weights.append(1.0)

    #for each strip, randomly increment until we reach the total strip weight
    available_weight = total_reel_weight - len(strip)
    while available_weight > 0:
        random_index = random.randint(0, len(strip) - 1)
        strip_weights[random_index] += 1
        available_weight -= 1

    return strip, strip_weights

def buildRandomStrips():
    reels = []
    weights = []
    for i in range(reel_count):
        strip, strip_weights = buildRandomStrip()
        reels.append(strip)
        weights.append(strip_weights)

    return reels, weights

def writeConfigFile(reels, weights):
    #write this config to file
    config_file = open('symbols_weights.csv', 'w')
    for i in range(len(reels[0])):
        for j in range(len(reels)):
            symbol = reels[j][i]
            weight = weights[j][i]
            if j > 0:
                config_file.write(',')
            config_file.write(symbol)
            config_file.write('_')
            config_file.write(str(weight))
        config_file.write('\n')
    config_file.flush()
    config_file.close()

def callBinaryAndGetOutput():
    #call the binary that calculates the expected values of each line
    line_re = re.compile(r'EV line (\d+): ([0-9]*\.?[0-9]+).*')
    output = Popen(['./a.out'], stdout=PIPE).communicate()[0]
    output_lines = output.split('\n')
    expected_values = []
    for output_line in output_lines:
        match = line_re.search(output_line)
        if match:
            expected_values.append(float(match.group(2)))
    return expected_values

def checkAllLinesDelta():
    expected_values = callBinaryAndGetOutput()

    if len(expected_values) > 1:
        last_expected_value = expected_values[0]
        for i in range(1,len(expected_values)):
            expected_value = expected_values[i]
            delta = abs(expected_value - last_expected_value)
            last_expected_value = expected_value
            if delta > 0.6:
                print 'boo! difference between line {0} and line {1} is {2}.'.format(i-1, i, delta)
                reel_index = random.randint(0,len(reels)-1)
                print 'shuffling symbols in reel strip {0}'.format(reel_index)
                strip, strip_weights = buildRandomStrip()
                reels[reel_index] = strip
                weights[reel_index] = strip_weights
                writeConfigFile(reels, weights)
                checkAllLinesDelta()

def checkExpectedPayouts(reels, weights):
    expected_values = callBinaryAndGetOutput()

    def getSymbolIndices(reels, paying_symbols):
        while True:
            i = random.randint(0, len(reels[0])-1)
            j = random.randint(0, len(reels)-1)
            symbol = reels[j][i]
            if symbol in paying_symbols:
                return i,j

    def increaseHighSymbolWeight():
        high_paying_indices = getSymbolIndices(reels, high_paying_symbols)
        low_paying_indices = getSymbolIndices(reels, low_paying_symbols)
        weights[high_paying_indices[1]][high_paying_indices[0]] += 1
        weights[low_paying_indices[1]][low_paying_indices[0]] -= 1

    def increaseLowSymbolWeight():
        high_paying_indices = getSymbolIndices(reels, high_paying_symbols)
        low_paying_indices = getSymbolIndices(reels, low_paying_symbols)
        weights[high_paying_indices[1]][high_paying_indices[0]] -= 1
        weights[low_paying_indices[1]][low_paying_indices[0]] += 1

    #check the expected value for each line
    all_good = True
    for i in range(len(expected_values)):
        expected_value = expected_values[i]
        if expected_value < lower_bound:
            all_good = False
            print 'boo! expected value for line {0} is too low: {1}. adjusting weights'.format(i+1, expected_value)
            #expected value is too low
            #increase the weight of a high paying symbol, decrease the weight of a low paying symbol
            increaseHighSymbolWeight()
            break
        elif expected_value > upper_bound:
            all_good = False
            print 'boo! expected value for line {0} is too high: {1}. adjusting weights'.format(i+1, expected_value)
            #expected value is too high
            #increase the weight of a low paying symbol, decrease the weight of a high paying symbol
            increaseLowSymbolWeight()
            break
        else:
            print 'yay! expected value for line {0} is good: {1}'.format(i+1, expected_value)

    if not all_good:
        writeConfigFile(reels, weights)
        checkExpectedPayouts(reels, weights)

reels, weights = buildRandomStrips()
writeConfigFile(reels, weights)
checkAllLinesDelta()
checkExpectedPayouts(reels, weights)