fileIn = open('log.txt', 'r')
data = {}
for line in fileIn:
  stm = line.strip()
  if stm not in data:
    data[stm] = 0
  data[stm] += 1

for i in data:
    print i, data[i]
