payouts_probabilities = []
payouts_probabilities_file = open('select_bonus.csv', 'r')
line = payouts_probabilities_file.readline()
expected_value = 0.0
while line:
    tokens = line.split(',')
    if len(tokens) != 2 or len(tokens[0]) < 1:
        break
    payout = float(tokens[0])
    probability = float(tokens[1])
    expected_value += payout * probability
    line = payouts_probabilities_file.readline()
payouts_probabilities_file.close()

print "expected value: {0}".format(expected_value)
