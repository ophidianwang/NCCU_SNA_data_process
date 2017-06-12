# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt

num_M = np.array([3., 4.5, .5, 1., 2.]) + np.random.normal(0, 0.2, 5)
num_F = np.array([2., .5, 4.5, 4., 3.]) + np.random.normal(0, 0.2, 5)

print(num_M)
print(num_F)

N = 5
ind = np.arange(N)    # the x locations for the groups
width = 0.35       # the width of the bars: can also be len(x) sequence

inv_h, inv_w = plt.figaspect(2.)
fig = plt.figure(figsize=(inv_w, inv_h))
fig.suptitle('Hidden Fact in Product Sales')

# first figure
ax = fig.add_subplot(1, 2, 1)
ax.set_ylim(0, 6)
ax.bar(ind, num_M + num_F, width, color='k')
ax.set_xticklabels(['', 'G1', 'G2', 'G3', 'G4', 'G5'])

# second figure
ax = fig.add_subplot(1, 2, 2)
ax.set_ylim(0, 6)
p1 = ax.bar(ind, num_M, width, color='b')
p2 = ax.bar(ind, num_F, width, bottom=num_M, color='r')
ax.set_xticklabels(['', 'G1', 'G2', 'G3', 'G4', 'G5'])
ax.legend((p1[0], p2[0]), ('Male', 'Female'))

plt.show()
