import json
import statistics
import sys
from numpy import mean

# read file
with open(sys.argv[1], 'r') as myfile:
    data = myfile.read()

# parse file
obj = json.loads(data)

confidences = []

for x in obj["results"]["items"]:
    # print(x)
    if x["type"] == "pronunciation":
        # print(x)
        val = float(x["alternatives"][0]["confidence"])
        # print(val)
        confidences.append(val)

# avg = sum(confidences)/len(confidences)
avg = mean(confidences)
print("The average is ", round(avg, 2))

median = statistics.median(confidences)
print("The median is ", round(median, 2))

# FIXME: compare resulting transcriptions of es_US and es_ES

# FIXME: output chart of confidence values frequency
# import matplotlib
# matplotlib.use('Agg')
# import matplotlib.pyplot as plt
# fig = plt.figure()
# ax = fig.add_subplot(111)
# ax.plot([1,2,3])
# fig.savefig('test.png')
