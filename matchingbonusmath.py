matches_payouts_probabilities_file = open('matching_bonus.csv', 'r')
line = matches_payouts_probabilities_file.readline()
expected_value = 0.0
while line:
    tokens = line.split(',')
    if len(tokens) != 3 or len(tokens[1]) < 1:
        break
    payout = float(tokens[1])
    probability = float(tokens[2])
    expected_value += payout * probability
    line = matches_payouts_probabilities_file.readline()
matches_payouts_probabilities_file.close()

print "expected value: {0}".format(expected_value)
